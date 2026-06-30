import pytest

from pipeline.config import Config


def test_require_passes_when_set():
    config = Config(anthropic_api_key="sk-fake")
    config.require("anthropic_api_key")  # should not raise


def test_require_raises_when_missing():
    config = Config(anthropic_api_key=None)
    with pytest.raises(RuntimeError, match="anthropic_api_key"):
        config.require("anthropic_api_key")
