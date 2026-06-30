"""Factory that returns the configured LLM client.

Both ClaudeClient (direct API) and ClaudeCodeClient (subscription via the
Claude Code CLI) expose the same complete()/complete_json() interface, so
stages call get_llm_client(config) and stay backend-agnostic.
"""
from __future__ import annotations

from pipeline.config import Config


def get_llm_client(config: Config):
    if config.llm_backend == "claude_code":
        from pipeline.clients.claude_code_client import ClaudeCodeClient

        return ClaudeCodeClient(config)
    if config.llm_backend == "api":
        from pipeline.clients.claude_client import ClaudeClient

        return ClaudeClient(config)
    raise RuntimeError(
        f"Unknown LLM_BACKEND={config.llm_backend!r}; expected 'api' or 'claude_code'."
    )
