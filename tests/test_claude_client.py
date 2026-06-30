from pipeline.clients.claude_client import _extract_json


def test_extract_json_plain():
    assert _extract_json('{"a": 1}') == {"a": 1}


def test_extract_json_fenced():
    text = 'Here you go:\n```json\n{"a": 1, "b": [1, 2]}\n```\nDone.'
    assert _extract_json(text) == {"a": 1, "b": [1, 2]}


def test_extract_json_fenced_no_language():
    text = '```\n[1, 2, 3]\n```'
    assert _extract_json(text) == [1, 2, 3]
