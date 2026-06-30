"""Thin wrapper around the Anthropic SDK used by every LLM stage."""
from __future__ import annotations

import json
import re

from pipeline.config import Config
from pipeline.retry import with_backoff


class ClaudeClient:
    def __init__(self, config: Config):
        config.require("anthropic_api_key")
        self._config = config
        self._client = None

    def _get_client(self):
        if self._client is not None:
            return self._client
        import anthropic

        self._client = anthropic.Anthropic(api_key=self._config.anthropic_api_key)
        return self._client

    @with_backoff(attempts=4)
    def complete(self, *, model: str, system: str, user: str, max_tokens: int = 4096) -> str:
        client = self._get_client()
        message = client.messages.create(
            model=model,
            max_tokens=max_tokens,
            system=system,
            messages=[{"role": "user", "content": user}],
        )
        return "".join(block.text for block in message.content if block.type == "text")

    def complete_json(self, *, model: str, system: str, user: str, max_tokens: int = 4096) -> dict | list:
        """Call complete() and parse the response as JSON, tolerating a
        ```json fenced code block (models often wrap JSON in one even when
        told not to)."""
        raw = self.complete(model=model, system=system, user=user, max_tokens=max_tokens)
        return _extract_json(raw)


def _extract_json(text: str) -> dict | list:
    fenced = re.search(r"```(?:json)?\s*(.*?)```", text, re.DOTALL)
    candidate = fenced.group(1) if fenced else text
    return json.loads(candidate.strip())
