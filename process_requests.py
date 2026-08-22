#!/usr/bin/env python3
import os
import sys
import json
import subprocess
import re
from datetime import datetime
import requests
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from googleapiclient.discovery import build

PROJECT_DIR = "/home/imran/apsrtc-kmpl"
GDRIVE_FOLDER = "1tU9aw7Cdw-Q-7mr9BMhayORKMy61_DOz"
SHEET_ID = "1wt8UQ7_U5OgGpiCW30UF9Sl9BxMlWwg3NrYfQEvtEQM"
REFRESH_TOKEN_FILE = "/home/imran/apsrtc-kmpl/refresh_token.json"

def get_sheets_service():
    with open(REFRESH_TOKEN_FILE, 'r') as f:
        data = json.load(f)
    creds = Credentials(
        token=None,
        refresh_token=data['refresh_token'],
        client_id=data['client_id'],
        client_secret=data['client_secret'],
        token_uri='https://oauth2.googleapis.com/token'
    )
    creds.refresh(Request())
    return build('sheets', 'v4', credentials=creds)

def format_date(date_str):
    """Convert various date formats to YYYY-MM-DD."""
    for fmt in ('%m/%d/%Y', '%Y-%m-%d', '%d/%m/%Y'):
        try:
            dt = datetime.strptime(date_str.strip(), fmt)
            return dt.strftime('%Y-%m-%d')
        except ValueError:
            continue
    raise ValueError(f"Unknown date format: {date_str}")

def get_pending_requests(service):
    sheet = service.spreadsheets()
    result = sheet.values().get(
        spreadsheetId=SHEET_ID,
        range="Sheet1!A:E"
    ).execute()
    rows = result.get('values', [])
    if not rows:
        return []
    pending = []
    for idx, row in enumerate(rows[1:], start=2):
        status = row[3] if len(row) > 3 else ""
        if not status.strip() or status.strip().lower() == "pending":
            depot = row[1] if len(row) > 1 else ""
            date_raw = row[2] if len(row) > 2 else ""
            if depot and date_raw:
                try:
                    date = format_date(date_raw)
                    pending.append({"row": idx, "depot": depot, "date": date})
                except ValueError as e:
                    update_sheet_cell(service, idx, "D", f"❌ Invalid date: {e}")
    return pending

def update_sheet_cell(service, row_num, col, value):
    range_name = f"Sheet1!{col}{row_num}"
    body = {"values": [[value]]}
    service.spreadsheets().values().update(
        spreadsheetId=SHEET_ID,
        range=range_name,
        valueInputOption="RAW",
        body=body
    ).execute()

def upload_to_drive(file_path):
    cmd = ["gdrive", "files", "upload", "--parent", GDRIVE_FOLDER, file_path]
    result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)
    if result.returncode != 0:
        raise RuntimeError(f"Upload failed: {result.stderr}")
    match = re.search(r"ViewUrl: (https://drive\.google\.com/file/d/[^\s]+)", result.stdout)
    if match:
        return match.group(1)
    return "Uploaded (link not found)"

def main():
    print(f"Polling at {datetime.now()}...")
    try:
        service = get_sheets_service()
    except Exception as e:
        print(f"Authentication failed: {e}")
        sys.exit(1)

    try:
        pending = get_pending_requests(service)
    except Exception as e:
        print(f"Failed to read sheet: {e}")
        sys.exit(1)

    if not pending:
        print("No pending requests.")
        return

    for req in pending:
        print(f"Processing: {req['depot']} on {req['date']}")
        cmd = [
            "python", os.path.join(PROJECT_DIR, "generate_report.py"),
            "--depot", req["depot"],
            "--date", req["date"]
        ]
        result = subprocess.run(cmd, cwd=PROJECT_DIR, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)

        if result.returncode != 0:
            error_msg = result.stderr[:200] if result.stderr else "Unknown error"
            update_sheet_cell(service, req["row"], "D", f"❌ Failed: {error_msg}")
            print(f"  Failed: {error_msg}")
            continue

        match = re.search(r"Saved to: (reports/[^\s]+)", result.stdout)
        if not match:
            update_sheet_cell(service, req["row"], "D", "❌ File not found")
            print("  File not found in output")
            continue

        file_path = os.path.join(PROJECT_DIR, match.group(1))
        if not os.path.exists(file_path):
            update_sheet_cell(service, req["row"], "D", "❌ File missing")
            print("  File missing on disk")
            continue

        try:
            drive_link = upload_to_drive(file_path)
            update_sheet_cell(service, req["row"], "D", "✅ Processed")
            update_sheet_cell(service, req["row"], "E", drive_link)
            print(f"  Success! Link: {drive_link}")
        except Exception as e:
            update_sheet_cell(service, req["row"], "D", f"❌ Upload failed: {e}")
            print(f"  Upload failed: {e}")

if __name__ == "__main__":
    main()
