from pipeline.storage import Storage


def test_transcript_round_trip(tmp_path):
    storage = Storage(tmp_path)
    storage.save_transcript("abc123", "hello world")
    assert storage.load_transcript("abc123") == "hello world"


def test_requirements_round_trip(tmp_path):
    storage = Storage(tmp_path)
    data = {"problem_statement": "x", "features": ["a", "b"]}
    storage.save_requirements("abc123", data)
    assert storage.load_requirements("abc123") == data


def test_processed_tracking(tmp_path):
    storage = Storage(tmp_path)
    assert not storage.is_processed("abc123")

    storage.upsert_record("abc123", status="captured", meeting_name="Sync")
    assert storage.is_processed("abc123")
    assert storage.get_record("abc123")["status"] == "captured"

    storage.upsert_record("abc123", status="requirements_extracted")
    record = storage.get_record("abc123")
    assert record["status"] == "requirements_extracted"
    assert record["meeting_name"] == "Sync"  # earlier fields preserved


def test_all_records_returns_everything(tmp_path):
    storage = Storage(tmp_path)
    storage.upsert_record("a", status="captured")
    storage.upsert_record("b", status="captured")
    assert set(storage.all_records().keys()) == {"a", "b"}
