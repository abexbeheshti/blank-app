"""Notion client: write blueprint pages and poll for human approval."""
from __future__ import annotations

from dataclasses import dataclass

from pipeline.config import Config
from pipeline.retry import with_backoff

STATUS_AWAITING_REVIEW = "Awaiting Review"
STATUS_APPROVED = "Approved"


@dataclass
class BlueprintPage:
    page_id: str
    url: str


class NotionClient:
    def __init__(self, config: Config):
        config.require("notion_api_token", "notion_database_id_blueprints")
        self._config = config
        self._client = None

    def _get_client(self):
        if self._client is not None:
            return self._client
        from notion_client import Client

        self._client = Client(auth=self._config.notion_api_token)
        return self._client

    @with_backoff(attempts=4)
    def create_blueprint_page(self, *, meeting_name: str, markdown: str) -> BlueprintPage:
        client = self._get_client()
        page = client.pages.create(
            parent={"database_id": self._config.notion_database_id_blueprints},
            properties={
                "Name": {"title": [{"text": {"content": f"{meeting_name} - Blueprint"}}]},
                "Status": {"select": {"name": STATUS_AWAITING_REVIEW}},
            },
            children=_markdown_to_blocks(markdown),
        )
        return BlueprintPage(page_id=page["id"], url=page.get("url", ""))

    @with_backoff(attempts=4)
    def get_page_status(self, page_id: str) -> str | None:
        client = self._get_client()
        page = client.pages.retrieve(page_id=page_id)
        select = page.get("properties", {}).get("Status", {}).get("select")
        return select["name"] if select else None

    def is_approved(self, page_id: str) -> bool:
        return self.get_page_status(page_id) == STATUS_APPROVED


def _markdown_to_blocks(markdown: str) -> list[dict]:
    """Convert markdown into Notion paragraph/heading blocks.

    Simple line-based conversion - good enough for PRD-style documents with
    headings, bullets, and paragraphs. Code blocks (e.g. the Mermaid diagram)
    are preserved as Notion code blocks.
    """
    blocks: list[dict] = []
    lines = markdown.split("\n")
    i = 0
    while i < len(lines):
        line = lines[i]
        if line.startswith("```"):
            language = line[3:].strip() or "plain text"
            code_lines = []
            i += 1
            while i < len(lines) and not lines[i].startswith("```"):
                code_lines.append(lines[i])
                i += 1
            blocks.append(
                {
                    "object": "block",
                    "type": "code",
                    "code": {
                        "rich_text": [{"text": {"content": "\n".join(code_lines)[:2000]}}],
                        "language": language if language in NOTION_LANGUAGES else "plain text",
                    },
                }
            )
        elif line.startswith("### "):
            blocks.append(_text_block("heading_3", line[4:]))
        elif line.startswith("## "):
            blocks.append(_text_block("heading_2", line[3:]))
        elif line.startswith("# "):
            blocks.append(_text_block("heading_1", line[2:]))
        elif line.strip().startswith(("- ", "* ")):
            blocks.append(_text_block("bulleted_list_item", line.strip()[2:]))
        elif line.strip():
            blocks.append(_text_block("paragraph", line))
        i += 1
    return blocks


def _text_block(block_type: str, content: str) -> dict:
    return {
        "object": "block",
        "type": block_type,
        block_type: {"rich_text": [{"text": {"content": content[:2000]}}]},
    }


NOTION_LANGUAGES = {"mermaid", "json", "python", "javascript", "plain text", "sql", "yaml"}
