"""Google Drive client: find and export meeting transcript documents.

Requires a service account JSON key with domain-wide delegation and the
Drive API scope. The service account impersonates a Workspace user so it
can see documents in that user's (or a shared) Drive.
"""
from __future__ import annotations

import io
from dataclasses import dataclass

from pipeline.config import Config
from pipeline.retry import with_backoff

SCOPES = ["https://www.googleapis.com/auth/drive.readonly"]


@dataclass
class TranscriptFile:
    file_id: str
    name: str
    created_time: str


class DriveClient:
    def __init__(self, config: Config):
        config.require("google_service_account_json")
        self._config = config
        self._service = None  # built lazily so import-time has no network/auth cost

    def _get_service(self):
        if self._service is not None:
            return self._service

        from google.oauth2 import service_account
        from googleapiclient.discovery import build

        credentials = service_account.Credentials.from_service_account_file(
            self._config.google_service_account_json, scopes=SCOPES
        )
        if self._config.google_workspace_domain:
            credentials = credentials.with_subject(
                f"transcript-bot@{self._config.google_workspace_domain}"
            )
        self._service = build("drive", "v3", credentials=credentials, cache_discovery=False)
        return self._service

    @with_backoff(attempts=4)
    def list_recent_transcripts(self, page_size: int = 10) -> list[TranscriptFile]:
        """List Google Docs whose name contains 'Transcript', newest first."""
        service = self._get_service()
        response = (
            service.files()
            .list(
                q="mimeType='application/vnd.google-apps.document' and name contains 'Transcript' and trashed=false",
                pageSize=page_size,
                orderBy="createdTime desc",
                fields="files(id, name, createdTime)",
            )
            .execute()
        )
        return [
            TranscriptFile(file_id=f["id"], name=f["name"], created_time=f["createdTime"])
            for f in response.get("files", [])
        ]

    @with_backoff(attempts=4)
    def export_text(self, file_id: str) -> str:
        """Export a Google Doc as plain text."""
        from googleapiclient.http import MediaIoBaseDownload

        service = self._get_service()
        request = service.files().export_media(fileId=file_id, mimeType="text/plain")
        buffer = io.BytesIO()
        downloader = MediaIoBaseDownload(buffer, request)
        done = False
        while not done:
            _, done = downloader.next_chunk()
        return buffer.getvalue().decode("utf-8")


def extract_meeting_name(file_name: str) -> str:
    """'Q3 Planning - Transcript' -> 'Q3 Planning'."""
    return file_name.split(" - Transcript")[0].split(" Transcript")[0].strip()
