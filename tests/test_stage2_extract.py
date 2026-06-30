from unittest.mock import patch

from pipeline.config import Config
from pipeline.stages import stage2_extract
from pipeline.storage import Storage

VALID_RESPONSE = {
    "problem_statement": "Users can't find the export button",
    "features": ["Add export to CSV"],
    "decisions": ["Use existing button bar"],
    "questions": ["Should we support XLSX too?"],
    "non_goals": ["Real-time export"],
    "constraints": ["Ship by Q3"],
    "acceptance_criteria": ["Export button visible on dashboard"],
    "stakeholders": ["Jane (PM)", "Alex (Eng)"],
}


def test_extract_requirements_saves_and_returns(tmp_path):
    config = Config(anthropic_api_key="fake-key", data_dir=tmp_path)
    storage = Storage(tmp_path)
    storage.save_transcript("t1", "some transcript text")

    with patch("pipeline.clients.claude_client.ClaudeClient.complete_json", return_value=VALID_RESPONSE):
        result = stage2_extract.extract_requirements("t1", config, storage)

    assert result == VALID_RESPONSE
    assert storage.load_requirements("t1") == VALID_RESPONSE
    assert storage.get_record("t1")["status"] == "requirements_extracted"


def test_extract_requirements_raises_on_missing_keys(tmp_path):
    config = Config(anthropic_api_key="fake-key", data_dir=tmp_path)
    storage = Storage(tmp_path)
    storage.save_transcript("t1", "some transcript text")

    incomplete = {k: v for k, v in VALID_RESPONSE.items() if k != "stakeholders"}
    with patch("pipeline.clients.claude_client.ClaudeClient.complete_json", return_value=incomplete):
        try:
            stage2_extract.extract_requirements("t1", config, storage)
            assert False, "expected ValueError"
        except ValueError as exc:
            assert "stakeholders" in str(exc)
