"""Stage 1: poll Google Drive for new meeting transcripts and store them locally."""
from __future__ import annotations

import logging

from pipeline.clients.drive_client import DriveClient, extract_meeting_name
from pipeline.config import Config
from pipeline.storage import Storage

logger = logging.getLogger("pipeline.stage1")


def poll_for_transcripts(config: Config, storage: Storage) -> list[str]:
    """Check Drive for transcripts not yet seen, save them, and return their IDs.

    Idempotent: relies on storage.is_processed() so re-running never
    re-downloads or re-triggers a transcript already recorded.
    """
    drive = DriveClient(config)
    new_transcript_ids: list[str] = []

    for file in drive.list_recent_transcripts():
        if storage.is_processed(file.file_id):
            continue

        logger.info("New transcript found: %s (%s)", file.name, file.file_id)
        text = drive.export_text(file.file_id)
        storage.save_transcript(file.file_id, text)
        storage.upsert_record(
            file.file_id,
            meeting_name=extract_meeting_name(file.name),
            drive_created_time=file.created_time,
            status="captured",
        )
        new_transcript_ids.append(file.file_id)

    return new_transcript_ids
