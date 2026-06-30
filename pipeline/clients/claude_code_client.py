"""LLM backend that drives the Claude Code CLI in headless mode.

This authenticates with a Claude Pro/Max **subscription** instead of a
pay-per-token API key, so it draws on the subscription's rate limits rather
than an API balance. Set up once with:

    claude setup-token        # generates a long-lived OAuth token
    export CLAUDE_CODE_OAUTH_TOKEN=...

Crucially, ANTHROPIC_API_KEY must be UNSET when using this backend - if it is
set, Claude Code uses it and bills as API usage, bypassing the subscription.
This client defensively strips it from the subprocess environment.

Exposes the same complete()/complete_json() interface as ClaudeClient so the
stages don't care which backend is in use.
"""
from __future__ import annotations

import json
import os
import subprocess

from pipeline.clients.claude_client import _extract_json
from pipeline.config import Config
from pipeline.retry import with_backoff


class ClaudeCodeClient:
    def __init__(self, config: Config):
        self._config = config

    def _env(self) -> dict[str, str]:
        env = dict(os.environ)
        # Force subscription auth: a stray API key would silently switch billing
        # to pay-per-token, defeating the whole point of this backend.
        env.pop("ANTHROPIC_API_KEY", None)
        return env

    @with_backoff(attempts=4)
    def complete(self, *, model: str, system: str, user: str, max_tokens: int = 4096) -> str:
        # Headless Claude Code has no separate system-prompt slot for -p, so we
        # fold the system instruction into the prompt text. max_tokens is accepted
        # for interface parity but the CLI manages output length itself.
        prompt = f"{system}\n\n{user}" if system else user
        cmd = [
            "claude",
            "-p",
            prompt,
            "--output-format",
            "json",
            "--model",
            model,
        ]
        result = subprocess.run(
            cmd, capture_output=True, text=True, timeout=600, env=self._env()
        )
        if result.returncode != 0:
            raise RuntimeError(
                f"claude CLI failed (exit {result.returncode}): {result.stderr.strip()}"
            )
        payload = json.loads(result.stdout)
        return payload.get("result", "")

    def complete_json(self, *, model: str, system: str, user: str, max_tokens: int = 4096) -> dict | list:
        raw = self.complete(model=model, system=system, user=user, max_tokens=max_tokens)
        return _extract_json(raw)
