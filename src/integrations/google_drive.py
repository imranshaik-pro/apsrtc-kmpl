"""Google Drive helpers for GitHub-hosted APSRTC automation.

Authentication uses OAuth client credentials and a refresh token supplied only
through environment variables / GitHub Actions secrets. No credentials belong
in this repository.
"""

import io
import os
from pathlib import Path
from typing import Optional

from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload, MediaIoBaseDownload


DRIVE_SCOPE = "https://www.googleapis.com/auth/drive"
GOOGLE_SHEET_MIME = "application/vnd.google-apps.spreadsheet"
XLSX_MIME = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"


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
    query = f"name = '{safe_name}' and '{folder_id}' in parents and trashed = false"
    response = drive_service().files().list(
        q=query, spaces="drive", fields="files(id,name,mimeType,webViewLink)", pageSize=10
    ).execute()
    files = response.get("files", [])
    return files[0] if files else None


def download_file(file_id: str, destination: str | Path) -> Path:
    """Download a regular Drive file to destination."""
    request = drive_service().files().get_media(fileId=file_id)
    buffer = io.BytesIO()
    downloader = MediaIoBaseDownload(buffer, request)
    done = False
    while not done:
        _, done = downloader.next_chunk()
    path = Path(destination)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(buffer.getvalue())
    return path


def download_latest_prior_monthly_sheet(folder_id: str, depot_name: str, selected_yyyy_mm: str, destination: str | Path) -> Optional[dict]:
    """Export the latest earlier depot monthly Google Sheet as XLSX.

    Monthly sheet names are DEPOT_YYYY-MM. Only an earlier month for the same
    depot is eligible, so a future/current workbook can never seed history.
    """
    prefix = f"{depot_name}_"
    safe_prefix = prefix.replace("'", "\\'")
    query = (
        f"name contains '{safe_prefix}' and '{folder_id}' in parents and "
        f"mimeType = '{GOOGLE_SHEET_MIME}' and trashed = false"
    )
    files = drive_service().files().list(
        q=query, spaces="drive", fields="files(id,name,mimeType,modifiedTime,webViewLink)", pageSize=100
    ).execute().get("files", [])

    eligible = []
    for item in files:
        name = item.get("name", "")
        if not name.startswith(prefix):
            continue
        suffix = name[len(prefix):]
        if len(suffix) == 7 and suffix[4] == "-" and suffix < selected_yyyy_mm:
            eligible.append(item)
    if not eligible:
        return None

    prior = max(eligible, key=lambda x: x["name"])
    request = drive_service().files().export_media(fileId=prior["id"], mimeType=XLSX_MIME)
    buffer = io.BytesIO()
    downloader = MediaIoBaseDownload(buffer, request)
    done = False
    while not done:
        _, done = downloader.next_chunk()
    path = Path(destination)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(buffer.getvalue())
    return prior


def upload_file(file_path: str | Path, folder_id: str) -> dict:
    path = Path(file_path)
    if not path.exists():
        raise FileNotFoundError(path)
    existing = find_file(folder_id=folder_id, filename=path.name)
    if existing:
        existing["already_existed"] = True
        return existing
    metadata = {"name": path.name, "parents": [folder_id]}
    media = MediaFileUpload(str(path), mimetype="text/plain", resumable=False)
    created = drive_service().files().create(body=metadata, media_body=media, fields="id,name,mimeType,webViewLink").execute()
    created["already_existed"] = False
    return created


def upload_xlsx_as_google_sheet(file_path: str | Path, folder_id: str, sheet_name: str | None = None) -> dict:
    """Upload/refresh a native Google Sheet by stable depot-month name.

    Monthly reports are lifecycle documents: an open-month provisional workbook
    must be refreshable during the month and later superseded by the closed-month
    official workbook.  Reusing the existing Drive file ID keeps bookmarks/links
    stable while replacing its spreadsheet content from the newly generated XLSX.
    """
    path = Path(file_path)
    if not path.exists():
        raise FileNotFoundError(path)
    target_name = sheet_name or path.stem
    existing = find_file(folder_id=folder_id, filename=target_name)
    media = MediaFileUpload(str(path), mimetype=XLSX_MIME, resumable=False)

    if existing:
        updated = drive_service().files().update(
            fileId=existing["id"],
            media_body=media,
            fields="id,name,mimeType,webViewLink",
        ).execute()
        updated["already_existed"] = True
        updated["content_updated"] = True
        return updated

    metadata = {"name": target_name, "parents": [folder_id], "mimeType": GOOGLE_SHEET_MIME}
    created = drive_service().files().create(
        body=metadata,
        media_body=media,
        fields="id,name,mimeType,webViewLink",
    ).execute()
    created["already_existed"] = False
    created["content_updated"] = True
    return created
