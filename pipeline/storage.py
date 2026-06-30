"""Local filesystem storage for pipeline artifacts.

Layout (relative to Config.data_dir):
    transcripts/{transcript_id}.txt
    requirements/{transcript_id}_requirements.json
    blueprints/{transcript_id}_blueprint.md
    processed.json   - {transcript_id: {...status, timestamps...}}
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any


class Storage:
    def __init__(self, data_dir: Path):
        self.data_dir = Path(data_dir)
        self.transcripts_dir = self.data_dir / "transcripts"
        self.requirements_dir = self.data_dir / "requirements"
        self.blueprints_dir = self.data_dir / "blueprints"
        self.processed_path = self.data_dir / "processed.json"
        for d in (self.transcripts_dir, self.requirements_dir, self.blueprints_dir):
            d.mkdir(parents=True, exist_ok=True)
        if not self.processed_path.exists():
            self.processed_path.write_text("{}")

    # ---- transcripts ----
    def save_transcript(self, transcript_id: str, text: str) -> Path:
        path = self.transcripts_dir / f"{transcript_id}.txt"
        path.write_text(text, encoding="utf-8")
        return path

    def load_transcript(self, transcript_id: str) -> str:
        return (self.transcripts_dir / f"{transcript_id}.txt").read_text(encoding="utf-8")

    # ---- requirements ----
    def save_requirements(self, transcript_id: str, requirements: dict[str, Any]) -> Path:
        path = self.requirements_dir / f"{transcript_id}_requirements.json"
        path.write_text(json.dumps(requirements, indent=2), encoding="utf-8")
        return path

    def load_requirements(self, transcript_id: str) -> dict[str, Any]:
        path = self.requirements_dir / f"{transcript_id}_requirements.json"
        return json.loads(path.read_text(encoding="utf-8"))

    # ---- blueprints ----
    def save_blueprint(self, transcript_id: str, markdown: str) -> Path:
        path = self.blueprints_dir / f"{transcript_id}_blueprint.md"
        path.write_text(markdown, encoding="utf-8")
        return path

    def load_blueprint(self, transcript_id: str) -> str:
        return (self.blueprints_dir / f"{transcript_id}_blueprint.md").read_text(encoding="utf-8")

    # ---- processed/state tracking ----
    def _read_processed(self) -> dict[str, Any]:
        return json.loads(self.processed_path.read_text(encoding="utf-8"))

    def _write_processed(self, data: dict[str, Any]) -> None:
        self.processed_path.write_text(json.dumps(data, indent=2), encoding="utf-8")

    def is_processed(self, transcript_id: str) -> bool:
        return transcript_id in self._read_processed()

    def get_record(self, transcript_id: str) -> dict[str, Any] | None:
        return self._read_processed().get(transcript_id)

    def all_records(self) -> dict[str, Any]:
        return self._read_processed()

    def upsert_record(self, transcript_id: str, **fields: Any) -> dict[str, Any]:
        data = self._read_processed()
        record = data.get(transcript_id, {"transcript_id": transcript_id})
        record.update(fields)
        data[transcript_id] = record
        self._write_processed(data)
        return record
