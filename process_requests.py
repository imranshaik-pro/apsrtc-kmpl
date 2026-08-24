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
GDRIVE_FOLDER = "1tU9aw7Cdw-Q-7mr9BMhayORKMy61_DOz"  # daily folder
SHEET_ID_DAILY = "1wt8UQ7_U5OgGpiCW30UF9Sl9BxMlWwg3NrYfQEvtEQM"
SHEET_ID_MONTHLY = "1kyxBOqa98pll_NeJrLQVDuuCUUhVoupE7JW_HiupPFs"
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
    for fmt in ('%m/%d/%Y', '%Y-%m-%d', '%d/%m/%Y'):
        try:
            dt = datetime.strptime(date_str.strip(), fmt)
            return dt.strftime('%Y-%m-%d')
        except ValueError:
            continue
    raise ValueError(f"Unknown date: {date_str}")

def format_month(month_str):
    """Convert a date-like string to YYYY-MM, or return as-is if already YYYY-MM."""
    month_str = month_str.strip()
    # If it contains '/', treat as date and extract YYYY-MM
    if '/' in month_str:
        try:
            # Try common date formats
            for fmt in ('%m/%d/%Y', '%d/%m/%Y', '%Y/%m/%d'):
                try:
                    dt = datetime.strptime(month_str, fmt)
                    return dt.strftime('%Y-%m')
                except ValueError:
                    continue
            # If all fail, try to parse with dateutil? We'll just raise.
            raise ValueError(f"Cannot parse date: {month_str}")
        except Exception as e:
            raise ValueError(f"Invalid month/date: {month_str} - {e}")
    # If it's already YYYY-MM, return as-is
    if re.match(r'^\d{4}-\d{2}$', month_str):
        return month_str
    # If it's just YYYY-MM-DD (hyphen-separated), extract first 7 chars
    if re.match(r'^\d{4}-\d{2}-\d{2}$', month_str):
        return month_str[:7]
    raise ValueError(f"Invalid month format: {month_str} (expected YYYY-MM)")

def process_sheet(service, sheet_id, is_monthly=False):
    range_name = "Sheet1!A:E"
    result = service.spreadsheets().values().get(spreadsheetId=sheet_id, range=range_name).execute()
    rows = result.get('values', [])
    if not rows:
        return
    pending = []
    for idx, row in enumerate(rows[1:], start=2):
        status = row[3] if len(row) > 3 else ""
        if not status.strip() or status.strip().lower() == "pending":
            depot = row[1] if len(row) > 1 else ""
            if not depot:
                continue
            if is_monthly:
                month_raw = row[2] if len(row) > 2 else ""
                if month_raw:
                    try:
                        month = format_month(month_raw)
                        pending.append({"row": idx, "depot": depot, "month": month, "type": "monthly"})
                    except ValueError as e:
                        update_sheet_cell(service, sheet_id, idx, "D", f"❌ Invalid month: {e}")
            else:
                date = row[2] if len(row) > 2 else ""
                if date:
                    try:
                        date = format_date(date)
                        pending.append({"row": idx, "depot": depot, "date": date, "type": "daily"})
                    except ValueError as e:
                        update_sheet_cell(service, sheet_id, idx, "D", f"❌ Invalid date: {e}")

    for req in pending:
        print(f"Processing {req['type']} request: {req['depot']} on {req.get('date') or req.get('month')}")
        if req['type'] == 'daily':
            cmd = [
                "python", os.path.join(PROJECT_DIR, "generate_report.py"),
                "--depot", req['depot'],
                "--date", req['date']
            ]
        else:
            cmd = [
                "python", os.path.join(PROJECT_DIR, "monthly_vehicle_report.py"),
                "--depot", req['depot'],
                "--month", req['month']
            ]
        result = subprocess.run(cmd, cwd=PROJECT_DIR, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)
        if result.returncode != 0:
            error_msg = result.stderr[:300] if result.stderr else "Unknown error"
            # Also include stdout if it has useful info
            if result.stdout:
                error_msg += f" | stdout: {result.stdout[:200]}"
            update_sheet_cell(service, sheet_id, req["row"], "D", f"❌ Failed: {error_msg}")
            print(f"  Failed: {error_msg}")
            continue

        # Extract Drive link from output
        match = re.search(r'🔗 (https://drive\.google\.com/file/d/[^\s]+)', result.stdout) or re.search(r'ViewUrl:\s*(https://drive\.google\.com/file/d/[^\s]+)', result.stdout)
        if match:
            drive_link = match.group(1)
        else:
            # fallback: search for any Drive link
            m2 = re.search(r'https://drive\.google\.com/file/d/[^\s]+', result.stdout)
            drive_link = m2.group(0) if m2 else "Link not found (check Drive folder)"

        update_sheet_cell(service, sheet_id, req["row"], "D", "✅ Processed")
        update_sheet_cell(service, sheet_id, req["row"], "E", drive_link)
        print(f"  Success! Link: {drive_link}")

def update_sheet_cell(service, sheet_id, row_num, col, value):
    range_name = f"Sheet1!{col}{row_num}"
    body = {"values": [[value]]}
    service.spreadsheets().values().update(
        spreadsheetId=sheet_id,
        range=range_name,
        valueInputOption="RAW",
        body=body
    ).execute()

def main():
    print(f"Polling at {datetime.now()}...")
    try:
        service = get_sheets_service()
    except Exception as e:
        print(f"Authentication failed: {e}")
        sys.exit(1)

    # Process daily sheet
    try:
        process_sheet(service, SHEET_ID_DAILY, is_monthly=False)
    except Exception as e:
        print(f"Error processing daily sheet: {e}")

    # Process monthly sheet
    try:
        process_sheet(service, SHEET_ID_MONTHLY, is_monthly=True)
    except Exception as e:
        print(f"Error processing monthly sheet: {e}")

if __name__ == "__main__":
    main()
