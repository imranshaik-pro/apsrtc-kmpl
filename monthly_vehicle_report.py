#!/usr/bin/env python3
"""
Monthly Vehicle HSD KMPL Report with polished formatting.
"""

import os
import sys
import json
import re
import tempfile
import subprocess
from datetime import datetime
from calendar import monthrange
from typing import Dict, List, Any, Optional, Tuple
import pandas as pd
from openpyxl import load_workbook
from openpyxl.styles import PatternFill, Font, Border, Side, Alignment
from openpyxl.utils import get_column_letter

from src.auth.client import login
from src.parser.vehicle_parser import parse_vehicle_rows

PROJECT_DIR = "/home/imran/apsrtc-kmpl"
MAPPING_FILE = os.path.join(PROJECT_DIR, "depot_mapping.json")
GDRIVE_FOLDER_MONTHLY = "1O6rKH39INogYxsNI9IepEO9UJq1MMnPj"

# --- Styling constants ---
THIN_BORDER = Border(
    left=Side(style='thin'),
    right=Side(style='thin'),
    top=Side(style='thin'),
    bottom=Side(style='thin')
)

def get_style(value):
    if value is None or pd.isna(value):
        return None, None
    if value <= 5.00:
        return PatternFill(start_color="FF0000", end_color="FF0000", fill_type="solid"), Font(color="FFFFFF", bold=True)
    elif value <= 5.10:
        return PatternFill(start_color="FFA500", end_color="FFA500", fill_type="solid"), Font(color="FFFFFF", bold=True)
    elif value <= 5.20:
        return PatternFill(start_color="FFFF00", end_color="FFFF00", fill_type="solid"), Font(color="000000")
    elif value <= 5.30:
        return PatternFill(start_color="90EE90", end_color="90EE90", fill_type="solid"), Font(color="000000")
    else:
        return PatternFill(start_color="008000", end_color="008000", fill_type="solid"), Font(color="FFFFFF", bold=True)

def load_depot_mapping():
    with open(MAPPING_FILE, 'r', encoding='utf-8') as f:
        return json.load(f)

def get_depot_info(depot_key: str):
    mapping = load_depot_mapping()
    for key in [depot_key, depot_key.lower()]:
        if key in mapping:
            info = mapping[key]
            return info["vehicle_depot"], info.get("display_name", key.upper())
    raise ValueError(f"Depot '{depot_key}' not found.")

def consolidate_day_records(records):
    consolidated = {}
    for rec in records:
        v = rec["vehicle_no"]
        if v not in consolidated:
            consolidated[v] = {
                "total_kms": rec["for_day_total_kms"],
                "hsd": rec["for_day_hsd"],
                "operation_type": rec.get("operation_type", ""),
                "engine_type": rec.get("engine_type", ""),
                "up_to_day_kmpl": rec.get("up_to_day_kmpl")
            }
        else:
            consolidated[v]["total_kms"] += rec["for_day_total_kms"]
            consolidated[v]["hsd"] += rec["for_day_hsd"]
            if consolidated[v]["up_to_day_kmpl"] is None or consolidated[v]["up_to_day_kmpl"] == 0.0:
                if rec.get("up_to_day_kmpl"):
                    consolidated[v]["up_to_day_kmpl"] = rec.get("up_to_day_kmpl")
    for v, data in consolidated.items():
        total_kms = data["total_kms"]
        hsd = data["hsd"]
        data["kmpl"] = (total_kms / hsd) if hsd and hsd > 0 else None
    return consolidated

def fetch_daily_data(session, date_obj, vehicle_depot):
    day_str = date_obj.strftime("%d/%m/%Y")
    response = session.post(
        "http://103.44.14.20/med/vehkmpl.php",
        data={"fyymm": day_str, "dept": vehicle_depot},
        timeout=30
    )
    response.raise_for_status()
    records = parse_vehicle_rows(response.text)
    return consolidate_day_records(records) if records else {}

def apply_formatting(wb):
    ws = wb.active

    # Round all numeric values to 2 decimals
    for row in ws.iter_rows(min_row=2, max_row=ws.max_row, min_col=5, max_col=ws.max_column):
        for cell in row:
            if cell.value is not None and isinstance(cell.value, (int, float)):
                cell.value = round(cell.value, 2)

    # Apply conditional colors
    for row in ws.iter_rows(min_row=2, max_row=ws.max_row, min_col=5, max_col=ws.max_column):
        for cell in row:
            if cell.value is None:
                continue
            try:
                val = float(cell.value)
            except (ValueError, TypeError):
                continue
            fill, font = get_style(val)
            if fill:
                cell.fill = fill
            if font:
                cell.font = font
            cell.border = THIN_BORDER

    # Header styling
    for cell in ws[1]:
        cell.font = Font(bold=True, color="FFFFFF")
        cell.fill = PatternFill(start_color="4472C4", end_color="4472C4", fill_type="solid")
        cell.alignment = Alignment(horizontal='center', vertical='center')
        cell.border = THIN_BORDER

    # Auto-fit column widths
    for col in ws.columns:
        max_length = 0
        col_letter = get_column_letter(col[0].column)
        for cell in col:
            try:
                if cell.value:
                    max_length = max(max_length, len(str(cell.value)))
            except:
                pass
        adjusted_width = max_length + 2
        ws.column_dimensions[col_letter].width = min(adjusted_width, 30)

def extract_drive_link(output: str) -> Optional[str]:
    patterns = [
        r'ViewUrl:\s*(https://drive\.google\.com/file/d/[^\s]+)',
        r'ViewUrl: (https://drive\.google\.com/file/d/[^\s]+)',
        r'https://drive\.google\.com/file/d/[^\s]+',
    ]
    for pat in patterns:
        m = re.search(pat, output)
        if m:
            return m.group(0) if 'http' in m.group(0) else m.group(1)
    return None

def main():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--depot", required=True)
    parser.add_argument("--month", required=True)
    args = parser.parse_args()

    try:
        year, month = map(int, args.month.split("-"))
        start_date = datetime(year, month, 1)
        _, days_in_month = monthrange(year, month)
    except ValueError:
        print("❌ Invalid month format. Use YYYY-MM.")
        sys.exit(1)

    today = datetime.now()
    last_day = days_in_month
    if start_date.year == today.year and start_date.month == today.month:
        last_day = today.day - 1
        if last_day < 1:
            print("❌ No data yet this month.")
            sys.exit(1)

    vehicle_depot, display_name = get_depot_info(args.depot)
    print(f"📅 Monthly report for {display_name} ({args.month})")
    print(f"📊 Fetching days 1 to {last_day}...")

    session = login()
    vehicle_data = {}

    for day_num in range(1, last_day + 1):
        date_obj = datetime(year, month, day_num)
        print(f"  Fetching {date_obj.strftime('%d/%m/%Y')}...")
        day_records = fetch_daily_data(session, date_obj, vehicle_depot)
        for v, data in day_records.items():
            if v not in vehicle_data:
                vehicle_data[v] = {
                    "op_type": data.get("operation_type", ""),
                    "engine": data.get("engine_type", ""),
                    "days": {},
                    "up_to_day_latest": None
                }
            vehicle_data[v]["days"][day_num] = data.get("kmpl")
            if data.get("up_to_day_kmpl") is not None:
                vehicle_data[v]["up_to_day_latest"] = data.get("up_to_day_kmpl")

    if not vehicle_data:
        print("❌ No vehicle data found.")
        sys.exit(1)

    rows = []
    for idx, (v, data) in enumerate(vehicle_data.items(), 1):
        row = {"SL No": idx, "Vehicle No": v, "Op Type": data["op_type"], "Engine Type": data["engine"]}
        for d in range(1, last_day + 1):
            val = data["days"].get(d)
            row[str(d)] = val if val is not None else ""
        row["Up-To-Day (Month End)"] = data["up_to_day_latest"] if data["up_to_day_latest"] is not None else ""
        rows.append(row)

    df = pd.DataFrame(rows)

    with tempfile.NamedTemporaryFile(suffix=".xlsx", delete=False) as tmp:
        tmp_path = tmp.name

    with pd.ExcelWriter(tmp_path, engine='openpyxl') as writer:
        df.to_excel(writer, sheet_name="Monthly KMPL", index=False)

    print("🎨 Applying formatting...")
    wb = load_workbook(tmp_path)
    apply_formatting(wb)
    wb.save(tmp_path)

    print("⬆️ Uploading to Google Drive...")
    cmd = ["gdrive", "files", "upload", "--parent", GDRIVE_FOLDER_MONTHLY, tmp_path]
    result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)

    if result.returncode != 0:
        print(f"❌ Upload failed: {result.stderr}")
        sys.exit(1)

    print(result.stdout)  # show output for debugging

    link = extract_drive_link(result.stdout)
    if link:
        print(f"✅ Upload successful!\n🔗 {link}")
    else:
        print(f"✅ Upload successful!\n📁 Folder: https://drive.google.com/drive/folders/{GDRIVE_FOLDER_MONTHLY}")

    os.unlink(tmp_path)

if __name__ == "__main__":
    main()
