"""Stage 4: break the approved blueprint down into GitHub issues."""
from __future__ import annotations

import json
import logging

from pipeline.clients.github_client import GitHubClient
from pipeline.clients.llm import get_llm_client
from pipeline.config import Config
from pipeline.storage import Storage

logger = logging.getLogger("pipeline.stage4")

SYSTEM_PROMPT = (
    "You are an engineering lead breaking a project blueprint down into "
    "actionable GitHub issues. Respond with ONLY a JSON array - no preamble, "
    "no markdown fences."
)

USER_PROMPT_TEMPLATE = """\
Break this blueprint down into GitHub-style issues (epics, user stories,
tasks). Return a JSON array where each item has exactly these keys:
- title (string)
- body (string, include a description and an "Acceptance Criteria" checklist)
- labels (array of strings, e.g. "epic"/"story"/"task" plus "estimate-N")
- story_points (number)
- depends_on (array of strings, titles of issues this depends on, may be empty)
- acceptance_criteria (array of strings)

Blueprint:
---
{blueprint}
---

Requirements context:
---
{requirements}
---
"""


def generate_tickets(transcript_id: str, config: Config, storage: Storage) -> list[dict]:
    blueprint = storage.load_blueprint(transcript_id)
    requirements = storage.load_requirements(transcript_id)
    client = get_llm_client(config)

    tickets = client.complete_json(
        model=config.ticket_model,
        system=SYSTEM_PROMPT,
        user=USER_PROMPT_TEMPLATE.format(
            blueprint=blueprint, requirements=json.dumps(requirements, indent=2)
        ),
        max_tokens=8192,
    )

    if not isinstance(tickets, list):
        raise ValueError("Ticket breakdown did not return a JSON array")

    storage.upsert_record(transcript_id, status="tickets_generated", ticket_count=len(tickets))
    logger.info("Generated %d tickets for %s", len(tickets), transcript_id)
    return tickets


def create_github_issues(transcript_id: str, tickets: list[dict], config: Config, storage: Storage) -> list[dict]:
    github = GitHubClient(config)
    created = []

    for ticket in tickets:
        labels = list(ticket.get("labels", []))
        if ticket.get("story_points") is not None:
            labels.append(f"estimate-{ticket['story_points']}")

        body = _format_issue_body(ticket)
        issue = github.create_issue(title=ticket["title"], body=body, labels=labels)
        created.append({"title": ticket["title"], "number": issue.number, "url": issue.url})
        logger.info("Created issue #%d: %s", issue.number, issue.url)

    storage.upsert_record(transcript_id, status="issues_created", github_issues=created)
    return created


def _format_issue_body(ticket: dict) -> str:
    lines = [ticket.get("body", "").strip(), ""]
    criteria = ticket.get("acceptance_criteria") or []
    if criteria:
        lines.append("## Acceptance Criteria")
        lines.extend(f"- [ ] {c}" for c in criteria)
        lines.append("")
    depends_on = ticket.get("depends_on") or []
    if depends_on:
        lines.append("## Depends On")
        lines.extend(f"- {d}" for d in depends_on)
    return "\n".join(lines).strip()
