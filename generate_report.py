#!/usr/bin/env python3
import json
import subprocess
import sys
import argparse
from datetime import datetime, timedelta

MAPPING_FILE = "depot_mapping.json"
RUN_SCRIPT = "run_daily_report.py"

def load_mapping():
    with open(MAPPING_FILE, 'r', encoding='utf-8') as f:
        return json.load(f)

def main():
    parser = argparse.ArgumentParser(description="Generate APSRTC report for any depot")
    parser.add_argument("--depot", required=True, help="Depot code or alias")
    parser.add_argument("--date", help="Report date in YYYY-MM-DD (default: yesterday)")
    args = parser.parse_args()

    mapping = load_mapping()
    key = args.depot.lower().strip()
    if key not in mapping:
        print(f"Depot '{args.depot}' not found. Available depots:")
        # Show a few for brevity
        for k, v in list(mapping.items())[:20]:
            print(f"  - {v.get('display_name', k)} (use: {k})")
        if len(mapping) > 20:
            print(f"  ... and {len(mapping)-20} more.")
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

    cmd = [
        "python", RUN_SCRIPT,
        "--date", report_date,
        "--depot", display_name,
        "--vehicle-depot", vehicle_depot,
        "--region-code", region_code
    ]

    print(f"Generating report for {display_name} on {report_date}...")
    # For Python 3.6, use stdout=None, stderr=None (or just omit capture_output)
    result = subprocess.run(cmd)
    sys.exit(result.returncode)

if __name__ == "__main__":
    main()
