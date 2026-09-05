#!/usr/bin/env python3
"""Cloud-safe daily APSRTC report runner.

Scheduled runs always target yesterday in Asia/Kolkata. Manual runs may supply
an explicit historical date. Successful uploads are idempotent because Google
Drive is checked for the target filename before uploading.
"""

import argparse
import json
import os
import subprocess
import sys
from datetime import date, datetime, timedelta
from pathlib import Path
from zoneinfo import ZoneInfo

from src.integrations.google_drive import find_file, upload_file


ROOT = Path(__file__).resolve().parent
SETTINGS_PATH = ROOT / "config" / "automation_settings.json"
MAPPING_PATH = ROOT / "depot_mapping.json"


def load_json(path: Path) -> dict:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def resolve_report_date(selected: str | None, scheduled: bool) -> date:
    today_ist = datetime.now(ZoneInfo("Asia/Kolkata")).date()
    if scheduled or not selected:
        return today_ist - timedelta(days=1)

    requested = date.fromisoformat(selected)
    if requested > today_ist:
        raise ValueError("LOL! Can't retrieve future-date data. Please select today or an earlier date.")
    if requested == today_ist:
        return today_ist - timedelta(days=1)
    return requested


def depot_info(mapping: dict, requested: str) -> tuple[str, dict]:
    key = requested.lower().strip()
    if key in mapping and not key.startswith("_"):
        return key, mapping[key]

    for candidate, info in mapping.items():
        if candidate.startswith("_"):
            continue
        if info.get("display_name", "").lower() == requested.lower().strip():
            return candidate, info
    raise KeyError(f"Unknown depot: {requested}")


def run_report(display_name: str, info: dict, report_date: date) -> Path:
    command = [
        sys.executable,
        str(ROOT / "run_daily_report.py"),
        "--date",
        report_date.isoformat(),
        "--depot",
        display_name,
        "--vehicle-depot",
        info["vehicle_depot"],
        "--region-code",
        info["region_code"],
    ]
    result = subprocess.run(command, cwd=ROOT, text=True, capture_output=True)
    print(result.stdout)
    if result.stderr:
        print(result.stderr, file=sys.stderr)
    if result.returncode != 0:
        raise RuntimeError("APSRTC report generation failed or source data is not ready yet.")

    output = ROOT / "reports" / f"{display_name}_{report_date.isoformat()}.txt"
    if not output.exists():
        raise RuntimeError(f"Expected report file was not created: {output}")
    return output


def main() -> int:
    parser = argparse.ArgumentParser(description="Automate APSRTC daily report generation and Drive upload")
    parser.add_argument("--depot", default=None, help="Depot key/display name; defaults to configured depot")
    parser.add_argument("--date", help="Manual selected date in YYYY-MM-DD")
    parser.add_argument("--scheduled", action="store_true", help="Force scheduled-run date rule: yesterday IST")
    parser.add_argument("--generate-only", action="store_true", help="Skip Google Drive upload")
    args = parser.parse_args()

    settings = load_json(SETTINGS_PATH)
    mapping = load_json(MAPPING_PATH)
    daily = settings["daily"]

    requested_depot = args.depot or daily["default_depot"]
    _, info = depot_info(mapping, requested_depot)
    display_name = info.get("display_name", requested_depot.upper())
    report_date = resolve_report_date(args.date, scheduled=args.scheduled)
    filename = f"{display_name}_{report_date.isoformat()}.txt"

    print(f"Depot: {display_name}")
    print(f"Report date: {report_date.isoformat()}")
    print(f"Target filename: {filename}")

    folder_id = os.getenv("DAILY_DRIVE_FOLDER_ID", daily["drive_folder_id"])

    if not args.generate_only:
        existing = find_file(folder_id=folder_id, filename=filename)
        if existing:
            print(f"ALREADY_DELIVERED: {existing.get('webViewLink', existing['id'])}")
            return 0

    report_path = run_report(display_name=display_name, info=info, report_date=report_date)

    if args.generate_only:
        print(f"GENERATED_ONLY: {report_path}")
        return 0

    uploaded = upload_file(report_path, folder_id=folder_id)
    print(f"DRIVE_FILE_ID: {uploaded['id']}")
    if uploaded.get("webViewLink"):
        print(f"DRIVE_LINK: {uploaded['webViewLink']}")
    print("DAILY_AUTOMATION_SUCCESS")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:
        print(f"DAILY_AUTOMATION_RETRYABLE_FAILURE: {exc}", file=sys.stderr)
        raise SystemExit(1)
