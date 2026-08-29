#!/usr/bin/env python3
"""
Flexible depot report generator with Google Drive upload.
"""

import os
import sys
import json
import subprocess
import re
import argparse
from datetime import datetime, timedelta

PROJECT_DIR = "/home/imran/apsrtc-kmpl"
GDRIVE_FOLDER = "1tU9aw7Cdw-Q-7mr9BMhayORKMy61_DOz"

def load_mapping():
    mapping_path = os.path.join(PROJECT_DIR, "depot_mapping.json")
    with open(mapping_path, 'r', encoding='utf-8') as f:
        return json.load(f)

def upload_to_drive(file_path):
    """Upload file to Google Drive and return the ViewUrl."""
    cmd = ["gdrive", "files", "upload", "--parent", GDRIVE_FOLDER, file_path]
    result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)
    if result.returncode != 0:
        raise RuntimeError(f"Upload failed: {result.stderr}")
    match = re.search(r"ViewUrl: (https://drive\.google\.com/file/d/[^\s]+)", result.stdout)
    if match:
        return match.group(1)
    # Fallback: search for any Drive link
    match2 = re.search(r"https://drive\.google\.com/file/d/[^\s]+", result.stdout)
    if match2:
        return match2.group(0)
    return "Link not found (upload may still have succeeded)"

def main():
    parser = argparse.ArgumentParser(description="Generate APSRTC report for any depot")
    parser.add_argument("--depot", required=True, help="Human-readable depot name (e.g., proddutur, kurnool)")
    parser.add_argument("--date", help="Report date in YYYY-MM-DD (default: yesterday)")
    args = parser.parse_args()

    mapping = load_mapping()
    key = args.depot.lower().strip()
    if key not in mapping:
        print(f"Depot '{args.depot}' not found. Available depots:")
        for k, v in mapping.items():
            if not k.startswith('_'):
                print(f"  - {v.get('display_name', k.title())} (use: {k})")
        sys.exit(1)

    info = mapping[key]
    vehicle_depot = info["vehicle_depot"]
    region_code = info["region_code"]
    display_name = info.get("display_name", key.upper())

    if args.date:
        report_date = args.date
    else:
        yesterday = datetime.now() - timedelta(days=1)
        report_date = yesterday.strftime("%Y-%m-%d")

    # Generate the report
    cmd = [
        "python", os.path.join(PROJECT_DIR, "run_daily_report.py"),
        "--date", report_date,
        "--depot", display_name,
        "--vehicle-depot", vehicle_depot,
        "--region-code", region_code
    ]
    result = subprocess.run(cmd, cwd=PROJECT_DIR, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)

    if result.returncode != 0 or "REPORT GENERATION FAILED" in result.stdout:
        # Print the output for the poller to capture
        print(result.stdout)
        sys.exit(1)

    # Find the generated file
    match = re.search(r"Saved to: (reports/[^\s]+)", result.stdout)
    if not match:
        print("ERROR: Could not find 'Saved to:' in output")
        sys.exit(1)

    file_path = os.path.join(PROJECT_DIR, match.group(1))
    if not os.path.exists(file_path):
        print(f"ERROR: File {file_path} not found")
        sys.exit(1)

    # Upload to Drive
    try:
        drive_link = upload_to_drive(file_path)
        print(f"Upload successful: {drive_link}")
    except Exception as e:
        print(f"Upload failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
