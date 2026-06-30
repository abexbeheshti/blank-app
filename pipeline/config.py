"""Environment-driven configuration for the pipeline.

All credentials and tunables are read from environment variables (see
.env.example). Nothing is hardcoded so the same code runs locally,
in a cron job, or as a Cloud Function.
"""
from __future__ import annotations

import os
from dataclasses import dataclass, field
from pathlib import Path

try:
    from dotenv import load_dotenv

    load_dotenv()
except ImportError:
    pass

# Model selection per stage. Override via env vars if costs/quality need tuning.
DEFAULT_EXTRACTION_MODEL = "claude-haiku-4-5-20251001"
DEFAULT_BLUEPRINT_MODEL = "claude-sonnet-5"
DEFAULT_TICKET_MODEL = "claude-haiku-4-5-20251001"
DEFAULT_CODEGEN_MODEL = "claude-opus-4-8"


def _int_env(name: str, default: int) -> int:
    value = os.environ.get(name)
    return int(value) if value else default


@dataclass
class Config:
    # Google Drive / Workspace
    google_service_account_json: str | None = field(
        default_factory=lambda: os.environ.get("GOOGLE_SERVICE_ACCOUNT_JSON")
    )
    google_workspace_domain: str | None = field(
        default_factory=lambda: os.environ.get("GOOGLE_WORKSPACE_DOMAIN")
    )

    # Anthropic
    anthropic_api_key: str | None = field(
        default_factory=lambda: os.environ.get("ANTHROPIC_API_KEY")
    )
    # "claude_code" (default) -> drive the Claude Code CLI in headless mode,
    # which authenticates with a Claude Pro/Max subscription (no API billing).
    # "api" -> call the Anthropic API directly (needs ANTHROPIC_API_KEY, billed
    # per token).
    llm_backend: str = field(default_factory=lambda: os.environ.get("LLM_BACKEND", "claude_code"))
    extraction_model: str = field(
        default_factory=lambda: os.environ.get("EXTRACTION_MODEL", DEFAULT_EXTRACTION_MODEL)
    )
    blueprint_model: str = field(
        default_factory=lambda: os.environ.get("BLUEPRINT_MODEL", DEFAULT_BLUEPRINT_MODEL)
    )
    ticket_model: str = field(
        default_factory=lambda: os.environ.get("TICKET_MODEL", DEFAULT_TICKET_MODEL)
    )
    codegen_model: str = field(
        default_factory=lambda: os.environ.get("CODEGEN_MODEL", DEFAULT_CODEGEN_MODEL)
    )

    # Notion
    notion_api_token: str | None = field(
        default_factory=lambda: os.environ.get("NOTION_API_TOKEN")
    )
    notion_database_id_blueprints: str | None = field(
        default_factory=lambda: os.environ.get("NOTION_DATABASE_ID_BLUEPRINTS")
    )

    # GitHub
    github_token: str | None = field(default_factory=lambda: os.environ.get("GITHUB_TOKEN"))
    github_repo_owner: str | None = field(
        default_factory=lambda: os.environ.get("GITHUB_REPO_OWNER")
    )
    github_repo_name: str | None = field(
        default_factory=lambda: os.environ.get("GITHUB_REPO_NAME")
    )

    # GCP (deploy stage, used by external tooling not implemented here)
    gcp_project_id: str | None = field(default_factory=lambda: os.environ.get("GCP_PROJECT_ID"))
    gcp_region: str | None = field(default_factory=lambda: os.environ.get("GCP_REGION"))

    # Behavior tuning
    polling_interval_seconds: int = field(
        default_factory=lambda: _int_env("POLLING_INTERVAL_SECONDS", 120)
    )
    transcript_retry_limit: int = field(
        default_factory=lambda: _int_env("TRANSCRIPT_RETRY_LIMIT", 6)
    )
    approval_timeout_hours: int = field(
        default_factory=lambda: _int_env("APPROVAL_TIMEOUT_HOURS", 24)
    )

    # Local storage
    data_dir: Path = field(default_factory=lambda: Path(os.environ.get("DATA_DIR", "data")))

    def require(self, *names: str) -> None:
        """Raise if any of the named attributes are unset. Call at the top of a
        stage so missing credentials fail fast with a clear message instead of
        a confusing error deep inside a client library."""
        missing = [n for n in names if not getattr(self, n, None)]
        if missing:
            raise RuntimeError(
                f"Missing required configuration: {', '.join(missing)}. "
                "Set the corresponding environment variable(s); see .env.example."
            )


def load_config() -> Config:
    return Config()
