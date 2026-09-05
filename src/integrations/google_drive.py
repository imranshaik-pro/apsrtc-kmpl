"""Google Drive helpers for GitHub-hosted APSRTC automation.

Authentication uses OAuth client credentials and a refresh token supplied only
through environment variables / GitHub Actions secrets. No credentials belong
in this repository.
"""

import os
from pathlib import Path
from typing import Optional

from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload


DRIVE_SCOPE = "https://www.googleapis.com/auth/drive"
GOOGLE_SHEET_MIME = "application/vnd.google-apps.spreadsheet"


def _credentials() -> Credentials:
    required = {
        "GOOGLE_CLIENT_ID": os.getenv("GOOGLE_CLIENT_ID"),
        "GOOGLE_CLIENT_SECRET": os.getenv("GOOGLE_CLIENT_SECRET"),
        "GOOGLE_REFRESH_TOKEN": os.getenv("GOOGLE_REFRESH_TOKEN"),
    }
    missing = [name for name, value in required.items() if not value]
    if missing:
        raise RuntimeError(
            "Missing Google OAuth environment variables: " + ", ".join(missing)
        )

    return Credentials(
        token=None,
        refresh_token=required["GOOGLE_REFRESH_TOKEN"],
        token_uri="https://oauth2.googleapis.com/token",
        client_id=required["GOOGLE_CLIENT_ID"],
        client_secret=required["GOOGLE_CLIENT_SECRET"],
        scopes=[DRIVE_SCOPE],
    )


def drive_service():
    return build("drive", "v3", credentials=_credentials(), cache_discovery=False)


def find_file(folder_id: str, filename: str) -> Optional[dict]:
    """Return an existing non-trashed file with the same name in the folder."""
    safe_name = filename.replace("'", "\\'")
    query = (
        f"name = '{safe_name}' and '{folder_id}' in parents and trashed = false"
    )
    response = (
        drive_service()
        .files()
        .list(
            q=query,
            spaces="drive",
            fields="files(id,name,mimeType,webViewLink)",
            pageSize=10,
        )
        .execute()
    )
    files = response.get("files", [])
    return files[0] if files else None


def upload_file(file_path: str | Path, folder_id: str) -> dict:
    """Upload a text report once; return existing file when the name already exists."""
    path = Path(file_path)
    if not path.exists():
        raise FileNotFoundError(path)

    existing = find_file(folder_id=folder_id, filename=path.name)
    if existing:
        existing["already_existed"] = True
        return existing

    metadata = {"name": path.name, "parents": [folder_id]}
    media = MediaFileUpload(str(path), mimetype="text/plain", resumable=False)
    created = (
        drive_service()
        .files()
        .create(body=metadata, media_body=media, fields="id,name,mimeType,webViewLink")
        .execute()
    )
    created["already_existed"] = False
    return created


def upload_xlsx_as_google_sheet(
    file_path: str | Path, folder_id: str, sheet_name: str | None = None
) -> dict:
    """Upload an XLSX and convert it to a native Google Sheet, idempotently by name."""
    path = Path(file_path)
    if not path.exists():
        raise FileNotFoundError(path)

    target_name = sheet_name or path.stem
    existing = find_file(folder_id=folder_id, filename=target_name)
    if existing:
        existing["already_existed"] = True
        return existing

    metadata = {
        "name": target_name,
        "parents": [folder_id],
        "mimeType": GOOGLE_SHEET_MIME,
    }
    media = MediaFileUpload(
        str(path),
        mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        resumable=False,
    )
    created = (
        drive_service()
        .files()
        .create(body=metadata, media_body=media, fields="id,name,mimeType,webViewLink")
        .execute()
    )
    created["already_existed"] = False
    return created
