"""Stage 2: extract structured requirements from a transcript via Claude."""
from __future__ import annotations

import logging

from pipeline.clients.claude_client import ClaudeClient
from pipeline.config import Config
from pipeline.storage import Storage

logger = logging.getLogger("pipeline.stage2")

SYSTEM_PROMPT = (
    "You are a technical requirements analyst. Extract structured requirements "
    "from meeting transcripts. Respond with ONLY a single JSON object - no "
    "preamble, no markdown fences, no commentary."
)

REQUIRED_KEYS = (
    "problem_statement",
    "features",
    "decisions",
    "questions",
    "non_goals",
    "constraints",
    "acceptance_criteria",
    "stakeholders",
)

USER_PROMPT_TEMPLATE = """\
Extract the following from this meeting transcript and return it as JSON with
exactly these keys:
- problem_statement (string)
- features (array of strings)
- decisions (array of strings)
- questions (array of strings, open questions)
- non_goals (array of strings)
- constraints (array of strings, e.g. budget/timeline/tech)
- acceptance_criteria (array of strings)
- stakeholders (array of strings)

Transcript:
---
{transcript}
---
"""


def extract_requirements(transcript_id: str, config: Config, storage: Storage) -> dict:
    transcript = storage.load_transcript(transcript_id)
    client = ClaudeClient(config)

    requirements = client.complete_json(
        model=config.extraction_model,
        system=SYSTEM_PROMPT,
        user=USER_PROMPT_TEMPLATE.format(transcript=transcript),
        max_tokens=4096,
    )

    missing = [k for k in REQUIRED_KEYS if k not in requirements]
    if missing:
        raise ValueError(f"Extraction output missing keys: {missing}")

    storage.save_requirements(transcript_id, requirements)
    storage.upsert_record(transcript_id, status="requirements_extracted")
    logger.info("Extracted requirements for %s", transcript_id)
    return requirements
