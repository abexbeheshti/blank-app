"""Stage 5: generate code for a ticket and open a pull request for human review."""
from __future__ import annotations

import json
import logging
import re

from pipeline.clients.claude_client import ClaudeClient
from pipeline.clients.github_client import GitHubClient
from pipeline.config import Config
from pipeline.storage import Storage

logger = logging.getLogger("pipeline.stage5")

SYSTEM_PROMPT = (
    "You are a senior software engineer implementing a single ticket. "
    "Generate clean, tested code. Respond with ONLY a JSON object - no "
    "preamble, no markdown fences."
)

USER_PROMPT_TEMPLATE = """\
Implement this ticket. Return a JSON object with exactly these keys:
- files (array of objects with "path" and "content" - the full content of
  each file to create or update, including unit tests)
- commit_message (string, conventional-commits style)
- pr_summary (string, 2-4 sentences describing the change for a PR description)

Ticket: {title}

Description:
{body}

Acceptance Criteria:
{acceptance_criteria}
"""


def slugify(title: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", title.lower()).strip("-")
    return slug[:50]


def generate_code_for_ticket(
    *, ticket: dict, issue_number: int, config: Config
) -> dict:
    """Call Claude to produce file contents for a ticket. Pure function - does
    not touch GitHub, so it's easy to unit test / review output before pushing."""
    client = ClaudeClient(config)
    criteria = "\n".join(f"- {c}" for c in ticket.get("acceptance_criteria", []))

    result = client.complete_json(
        model=config.codegen_model,
        system=SYSTEM_PROMPT,
        user=USER_PROMPT_TEMPLATE.format(
            title=ticket["title"],
            body=ticket.get("body", ""),
            acceptance_criteria=criteria or "(none specified)",
        ),
        max_tokens=8192,
    )

    if "files" not in result or not isinstance(result["files"], list):
        raise ValueError("Code generation output missing 'files' array")

    return result


def open_pull_request_for_ticket(
    *, ticket: dict, issue_number: int, generated: dict, config: Config
) -> dict:
    """Create a feature branch, commit the generated files, and open a PR.
    Never merges - a human always reviews generated code before it lands."""
    github = GitHubClient(config)
    branch = f"feature/{issue_number}-{slugify(ticket['title'])}"

    github.create_branch(branch)
    commit_message = generated.get("commit_message") or f"feat: {ticket['title']} (#{issue_number})"
    for file in generated["files"]:
        github.write_file(
            branch=branch, path=file["path"], content=file["content"], message=commit_message
        )

    pr_body = (
        f"{generated.get('pr_summary', '')}\n\n"
        f"Closes #{issue_number}\n\n"
        f"_Generated automatically from ticket #{issue_number}. Review carefully before merging._"
    )
    pr = github.create_pull_request(
        branch=branch, title=f"{ticket['title']} (#{issue_number})", body=pr_body
    )
    logger.info("Opened PR #%d for ticket #%d: %s", pr.number, issue_number, pr.url)
    return {"number": pr.number, "url": pr.url, "branch": pr.branch}


def run_codegen_for_tickets(
    transcript_id: str, tickets_with_issues: list[dict], config: Config, storage: Storage
) -> list[dict]:
    """tickets_with_issues: list of {**ticket, "number": issue_number}"""
    results = []
    for ticket in tickets_with_issues:
        try:
            generated = generate_code_for_ticket(
                ticket=ticket, issue_number=ticket["number"], config=config
            )
            pr = open_pull_request_for_ticket(
                ticket=ticket, issue_number=ticket["number"], generated=generated, config=config
            )
            results.append({"issue_number": ticket["number"], "pr": pr, "status": "ok"})
        except Exception as exc:  # noqa: BLE001 - one bad ticket shouldn't abort the batch
            logger.error("Code generation failed for ticket #%s: %s", ticket.get("number"), exc)
            results.append({"issue_number": ticket.get("number"), "status": "failed", "error": str(exc)})

    storage.upsert_record(transcript_id, status="code_generated", pull_requests=results)
    return results
