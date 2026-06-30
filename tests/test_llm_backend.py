import json
from unittest.mock import patch

import pytest

from pipeline.clients.claude_client import ClaudeClient
from pipeline.clients.claude_code_client import ClaudeCodeClient
from pipeline.clients.llm import get_llm_client
from pipeline.config import Config


def test_factory_returns_api_client_by_default():
    config = Config(anthropic_api_key="sk-fake", llm_backend="api")
    assert isinstance(get_llm_client(config), ClaudeClient)


def test_factory_returns_claude_code_client():
    config = Config(llm_backend="claude_code")
    assert isinstance(get_llm_client(config), ClaudeCodeClient)


def test_factory_rejects_unknown_backend():
    config = Config(llm_backend="bogus")
    with pytest.raises(RuntimeError, match="Unknown LLM_BACKEND"):
        get_llm_client(config)


class _FakeCompleted:
    def __init__(self, stdout, returncode=0, stderr=""):
        self.stdout = stdout
        self.returncode = returncode
        self.stderr = stderr


def test_claude_code_complete_parses_result_field():
    config = Config(llm_backend="claude_code")
    client = ClaudeCodeClient(config)
    fake = _FakeCompleted(json.dumps({"result": "hello from claude code"}))

    with patch("subprocess.run", return_value=fake) as run:
        out = client.complete(model="claude-sonnet-5", system="sys", user="hi")

    assert out == "hello from claude code"
    # The CLI is invoked headlessly with the configured model.
    args = run.call_args.args[0]
    assert args[0] == "claude"
    assert "-p" in args and "--model" in args
    assert "claude-sonnet-5" in args


def test_claude_code_strips_api_key_from_subprocess_env():
    """A stray ANTHROPIC_API_KEY would switch billing to the API; the
    subscription backend must remove it before invoking the CLI."""
    config = Config(llm_backend="claude_code")
    client = ClaudeCodeClient(config)
    fake = _FakeCompleted(json.dumps({"result": "ok"}))

    with patch.dict("os.environ", {"ANTHROPIC_API_KEY": "sk-should-be-stripped"}):
        with patch("subprocess.run", return_value=fake) as run:
            client.complete(model="claude-haiku-4-5-20251001", system="", user="x")

    passed_env = run.call_args.kwargs["env"]
    assert "ANTHROPIC_API_KEY" not in passed_env


def test_claude_code_complete_json_unwraps_fenced_block():
    config = Config(llm_backend="claude_code")
    client = ClaudeCodeClient(config)
    result_text = '```json\n{"features": ["a"]}\n```'
    fake = _FakeCompleted(json.dumps({"result": result_text}))

    with patch("subprocess.run", return_value=fake):
        out = client.complete_json(model="claude-sonnet-5", system="", user="x")

    assert out == {"features": ["a"]}


def test_claude_code_raises_on_cli_failure():
    config = Config(llm_backend="claude_code")
    client = ClaudeCodeClient(config)
    fake = _FakeCompleted("", returncode=1, stderr="not authenticated")

    with patch("pipeline.retry.time.sleep"):  # don't actually wait through backoff
        with patch("subprocess.run", return_value=fake):
            with pytest.raises(RuntimeError, match="not authenticated"):
                client.complete(model="claude-sonnet-5", system="", user="x")
