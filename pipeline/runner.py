"""Orchestrates the pipeline: capture -> extract -> blueprint -> (approval gate)
-> tickets -> code generation.

Designed to be called repeatedly (every POLLING_INTERVAL_SECONDS) by a
scheduler - either an APScheduler loop, cron/systemd timer, or a Cloud
Function triggered by Cloud Scheduler. Each call is a single idempotent pass:
it picks up wherever transcripts/blueprints left off based on the status
recorded in storage, so a crash mid-run just gets retried on the next tick.
"""
from __future__ import annotations

import logging

from pipeline.config import Config, load_config
from pipeline.stages import stage1_capture, stage2_extract, stage3_blueprint, stage4_tickets, stage5_codegen
from pipeline.storage import Storage

logger = logging.getLogger("pipeline.runner")


def run_once(config: Config | None = None) -> dict:
    """Run a single pass over every transcript, advancing each one as far as
    its current status allows. Returns a summary dict for logging/dashboarding."""
    config = config or load_config()
    storage = Storage(config.data_dir)
    summary = {"new_transcripts": [], "advanced": [], "errors": []}

    try:
        new_ids = stage1_capture.poll_for_transcripts(config, storage)
        summary["new_transcripts"] = new_ids
    except Exception as exc:  # noqa: BLE001
        logger.error("Stage 1 polling failed: %s", exc)
        summary["errors"].append({"stage": "capture", "error": str(exc)})

    for transcript_id, record in storage.all_records().items():
        try:
            advanced = _advance(transcript_id, record["status"], config, storage)
            if advanced:
                summary["advanced"].append({"transcript_id": transcript_id, "to": advanced})
        except Exception as exc:  # noqa: BLE001 - one transcript failing must not block others
            logger.error("Pipeline step failed for %s: %s", transcript_id, exc)
            storage.upsert_record(transcript_id, status="failed", error=str(exc))
            summary["errors"].append({"transcript_id": transcript_id, "error": str(exc)})

    return summary


def _advance(transcript_id: str, status: str, config: Config, storage: Storage) -> str | None:
    """State machine: each status maps to the next stage to run. Returns the
    new status if work happened, else None (e.g. still waiting on approval)."""
    if status == "captured":
        stage2_extract.extract_requirements(transcript_id, config, storage)
        return "requirements_extracted"

    if status == "requirements_extracted":
        stage3_blueprint.generate_blueprint(transcript_id, config, storage)
        return "blueprint_generated"

    if status == "blueprint_generated":
        stage3_blueprint.publish_blueprint_for_review(transcript_id, config, storage)
        return "awaiting_approval"

    if status == "awaiting_approval":
        if stage3_blueprint.check_approval(transcript_id, config, storage):
            return "approved"
        return None  # still waiting on a human

    if status == "approved":
        tickets = stage4_tickets.generate_tickets(transcript_id, config, storage)
        issues = stage4_tickets.create_github_issues(transcript_id, tickets, config, storage)
        storage.upsert_record(transcript_id, tickets=tickets)
        return "issues_created"

    if status == "issues_created":
        record = storage.get_record(transcript_id) or {}
        tickets = record.get("tickets", [])
        issues = record.get("github_issues", [])
        tickets_with_issues = [
            {**ticket, "number": issue["number"]}
            for ticket, issue in zip(tickets, issues)
        ]
        stage5_codegen.run_codegen_for_tickets(transcript_id, tickets_with_issues, config, storage)
        return "code_generated"

    # "code_generated" and "failed" are terminal for this state machine.
    return None
