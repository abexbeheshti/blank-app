"""Stage 3: generate a project blueprint and publish it to Notion for human approval."""
from __future__ import annotations

import json
import logging

from pipeline.clients.claude_client import ClaudeClient
from pipeline.clients.notion_client import NotionClient
from pipeline.config import Config
from pipeline.storage import Storage

logger = logging.getLogger("pipeline.stage3")

SYSTEM_PROMPT = (
    "You are a staff software architect. Generate a complete, clear project "
    "blueprint in Markdown from a structured requirements document."
)

USER_PROMPT_TEMPLATE = """\
Generate a project blueprint from these requirements. Include these sections:
1. PRD (problem statement, goals, non-goals, success criteria)
2. Architecture overview, with a Mermaid diagram in a ```mermaid fenced block
3. Database schema (tables/fields, or "N/A" if not applicable)
4. API contracts (endpoints, request/response shapes)
5. Tech stack rationale

Requirements:
---
{requirements}
---

Return only the Markdown document.
"""


def generate_blueprint(transcript_id: str, config: Config, storage: Storage) -> str:
    requirements = storage.load_requirements(transcript_id)
    client = ClaudeClient(config)

    markdown = client.complete(
        model=config.blueprint_model,
        system=SYSTEM_PROMPT,
        user=USER_PROMPT_TEMPLATE.format(requirements=json.dumps(requirements, indent=2)),
        max_tokens=8192,
    )

    storage.save_blueprint(transcript_id, markdown)
    storage.upsert_record(transcript_id, status="blueprint_generated")
    logger.info("Generated blueprint for %s", transcript_id)
    return markdown


def publish_blueprint_for_review(transcript_id: str, config: Config, storage: Storage) -> str:
    """Write the blueprint to Notion as 'Awaiting Review' and record the page id
    so the approval poller knows what to check."""
    record = storage.get_record(transcript_id) or {}
    meeting_name = record.get("meeting_name", transcript_id)
    markdown = storage.load_blueprint(transcript_id)

    notion = NotionClient(config)
    page = notion.create_blueprint_page(meeting_name=meeting_name, markdown=markdown)

    storage.upsert_record(
        transcript_id,
        status="awaiting_approval",
        notion_page_id=page.page_id,
        notion_page_url=page.url,
    )
    logger.info("Published blueprint for %s to Notion: %s", transcript_id, page.url)
    return page.page_id


def check_approval(transcript_id: str, config: Config, storage: Storage) -> bool:
    """Poll Notion for approval status; flip local state to 'approved' once the
    human has changed the page's Status property."""
    record = storage.get_record(transcript_id)
    if not record or not record.get("notion_page_id"):
        return False

    notion = NotionClient(config)
    if notion.is_approved(record["notion_page_id"]):
        storage.upsert_record(transcript_id, status="approved")
        logger.info("Blueprint approved for %s", transcript_id)
        return True
    return False
