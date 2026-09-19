#!/usr/bin/env python3
"""Generate the Monthly KMPL workbook and upload it as a Google Sheet."""
import argparse
import json
import os
import sys
from calendar import monthrange
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

import pandas as pd
from openpyxl import load_workbook
from openpyxl.styles import Alignment, Border, Font, PatternFill, Side
from openpyxl.utils import get_column_letter

from src.auth.client import login
from src.integrations.google_drive import upload_xlsx_as_google_sheet, download_latest_prior_monthly_sheet
from src.parser.vehicle_parser import parse_vehicle_rows
from src.reporting.vehicle_history import (
    read_existing_history, build_history, write_history_sheet, fetch_schedule,
)

PROJECT_DIR = Path(__file__).resolve().parent
MAPPING_FILE = PROJECT_DIR / "depot_mapping.json"
DEFAULT_GDRIVE_FOLDER = "1O6rKH39INogYxsNI9IepEO9UJq1MMnPj"
IST = ZoneInfo("Asia/Kolkata")
ZONE_BY_REGION = {"YSRKADAPA": "ZONE-4"}
THIN = Side(style="thin", color="B7C9E2")
THIN_BORDER = Border(left=THIN, right=THIN, top=THIN, bottom=THIN)


def get_style(value):
    if value is None or pd.isna(value): return None, None
    if value <= 5.00: return PatternFill(start_color="F4CCCC", end_color="F4CCCC", fill_type="solid"), Font(color="9C0006", bold=True)
    if value <= 5.10: return PatternFill(start_color="FCE5CD", end_color="FCE5CD", fill_type="solid"), Font(color="7F6000", bold=True)
    if value <= 5.20: return PatternFill(start_color="FFF2CC", end_color="FFF2CC", fill_type="solid"), Font(color="7F6000")
    if value <= 5.30: return PatternFill(start_color="D9EAD3", end_color="D9EAD3", fill_type="solid"), Font(color="274E13")
    return PatternFill(start_color="B6D7A8", end_color="B6D7A8", fill_type="solid"), Font(color="274E13", bold=True)


def load_depot_mapping():
    with MAPPING_FILE.open("r", encoding="utf-8") as f: return json.load(f)


def get_depot_info(depot_key):
    mapping = load_depot_mapping()
    for key in [depot_key, depot_key.lower()]:
        if key in mapping:
            info = mapping[key]
            return info["vehicle_depot"], info.get("display_name", key.upper()), info.get("region_code", "")
    for info in mapping.values():
        if str(info.get("display_name", "")).upper() == depot_key.upper():
            return info["vehicle_depot"], info.get("display_name", depot_key.upper()), info.get("region_code", "")
    raise ValueError(f"Depot '{depot_key}' not found.")


def consolidate_day_records(records):
    consolidated = {}
    for rec in records:
        v = rec["vehicle_no"]
        if v not in consolidated:
            consolidated[v] = {"total_kms": rec["for_day_total_kms"], "hsd": rec["for_day_hsd"], "operation_type": rec.get("operation_type", ""), "engine_type": rec.get("engine_type", ""), "up_to_day_kmpl": rec.get("up_to_day_kmpl")}
        else:
            consolidated[v]["total_kms"] += rec["for_day_total_kms"]
            consolidated[v]["hsd"] += rec["for_day_hsd"]
            if not consolidated[v]["up_to_day_kmpl"] and rec.get("up_to_day_kmpl"): consolidated[v]["up_to_day_kmpl"] = rec.get("up_to_day_kmpl")
    for data in consolidated.values():
        hsd = data["hsd"]; data["kmpl"] = data["total_kms"] / hsd if hsd and hsd > 0 else None
    return consolidated


def fetch_daily_data(session, date_obj, vehicle_depot):
    r = session.post("http://103.44.14.20/med/vehkmpl.php", data={"fyymm": date_obj.strftime("%d/%m/%Y"), "dept": vehicle_depot}, timeout=30)
    r.raise_for_status(); records = parse_vehicle_rows(r.text)
    return consolidate_day_records(records) if records else {}


def _event_day(raw_date):
    """Return actual completion day from APSRTC schedule date, or None."""
    parsed = pd.to_datetime(str(raw_date).strip(), dayfirst=True, errors="coerce")
    return None if pd.isna(parsed) else int(parsed.day)


def fetch_monthly_schedule_markers(session, year, month, zone, region_code, depot):
    """Map vehicle -> actual day -> schedule icon for this report month.

    Ambiguous duplicate/conflicting schedule source rows are deliberately not marked
    here; Vehicle Performance keeps the detailed exception for review.
    """
    if (year, month) < (2026, 4):
        return {}
    yyyymm = f"{year}{month:02d}"
    month_label = datetime(year, month, 1).strftime("%B_%Y")
    s3 = fetch_schedule(session, 3, yyyymm, month_label, zone, region_code, depot)
    s4 = fetch_schedule(session, 4, yyyymm, month_label, zone, region_code, depot)
    markers = {}
    for vehicle in set(s3) | set(s4):
        e3, e4 = s3.get(vehicle, []), s4.get(vehicle, [])
        if len(e3) > 1 or len(e4) > 1 or (e3 and e4):
            continue
        event = ("🔧", e3[0]) if e3 else (("⚙", e4[0]) if e4 else None)
        if not event:
            continue
        day = _event_day(event[1])
        if day is not None and 1 <= day <= monthrange(year, month)[1]:
            markers.setdefault(vehicle, {})[day] = event[0]
    return markers


def apply_formatting(workbook):
    ws = workbook["Monthly KMPL"]
    # Professional report identity: title band + reporting context above the data.
    ws.insert_rows(1, 4)
    last_col = ws.max_column
    last_letter = get_column_letter(last_col)
    ws.merge_cells(f"A1:{last_letter}1")
    ws["A1"] = "APSRTC – PRODDUTUR DEPOT"
    ws["A1"].font = Font(bold=True, color="FFFFFF", size=16)
    ws["A1"].fill = PatternFill("solid", fgColor="17365D")
    ws["A1"].alignment = Alignment(horizontal="center", vertical="center")
    ws.row_dimensions[1].height = 28
    ws.merge_cells(f"A2:{last_letter}2")
    ws["A2"] = "MONTHLY VEHICLE KMPL PERFORMANCE"
    ws["A2"].font = Font(bold=True, color="1F4E78", size=12)
    ws["A2"].alignment = Alignment(horizontal="center", vertical="center")
    ws.merge_cells(f"A3:{last_letter}3")
    ws["A3"] = "Daily HSD KMPL | Up-To-Day performance | Schedule-III 🔧 | Schedule-IV ⚙"
    ws["A3"].font = Font(italic=True, color="595959", size=9)
    ws["A3"].alignment = Alignment(horizontal="center", vertical="center")
    ws.freeze_panes = "E6"
    ws.auto_filter.ref = f"A5:{last_letter}{ws.max_row}"
    ws.sheet_view.showGridLines = False
    ws.row_dimensions[5].height = 30

    for r in range(6, ws.max_row + 1):
        if r % 2 == 0:
            for c in range(1, 5):
                ws.cell(r, c).fill = PatternFill("solid", fgColor="F7F9FC")
        for c in range(1, last_col + 1):
            cell = ws.cell(r, c)
            cell.border = THIN_BORDER
            cell.alignment = Alignment(horizontal="center" if c != 3 and c != 4 else "left", vertical="center")
        for c in range(5, last_col + 1):
            cell = ws.cell(r, c)
            if cell.value in (None, ""): continue
            # Maintenance cells are strings such as "4.52 🔧" and retain their KMPL.
            if isinstance(cell.value, str) and ("🔧" in cell.value or "⚙" in cell.value):
                if "🔧" in cell.value:
                    cell.fill = PatternFill("solid", fgColor="FFF2CC"); cell.font = Font(bold=True, color="7F6000")
                else:
                    cell.fill = PatternFill("solid", fgColor="D9EAF7"); cell.font = Font(bold=True, color="1F4E78")
                continue
            try: numeric_value = float(str(cell.value).replace(",", "").strip())
            except (TypeError, ValueError): continue
            cell.value = round(numeric_value, 2); cell.number_format = "0.00"
            fill, font = get_style(numeric_value)
            if fill: cell.fill = fill
            if font: cell.font = font

    for cell in ws[5]:
        cell.font = Font(bold=True, color="FFFFFF", size=10)
        cell.fill = PatternFill("solid", fgColor="1F4E78")
        cell.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)
        cell.border = THIN_BORDER

    for r in range(1, ws.max_row + 1):
        cell = ws.cell(r, last_col)
        if r == 5:
            cell.fill = PatternFill("solid", fgColor="17365D")
            cell.font = Font(bold=True, color="FFFFFF")
        cell.border = Border(left=Side(style="medium", color="5B9BD5"), right=THIN, top=THIN, bottom=THIN)

    widths = {1: 7, 2: 14, 3: 20, 4: 18}
    for c in range(1, last_col + 1):
        ws.column_dimensions[get_column_letter(c)].width = widths.get(c, 9 if c < last_col else 20)


def main():
    parser = argparse.ArgumentParser(); parser.add_argument("--depot", required=True); parser.add_argument("--month", required=True, help="YYYY-MM"); args = parser.parse_args()
    try:
        year, month = map(int, args.month.split("-")); _, days_in_month = monthrange(year, month)
    except ValueError:
        print("INVALID_MONTH: Use YYYY-MM"); return 2
    now_ist = datetime.now(IST); selected_month = (year, month); current_month = (now_ist.year, now_ist.month)
    if selected_month > current_month:
        print("INVALID_MONTH: Can't retrieve future-month data."); return 2
    last_day = days_in_month
    if selected_month == current_month:
        last_day = now_ist.day - 1
        if last_day < 1: print("NO_DATA: No completed day exists yet this month."); return 1

    vehicle_depot, display_name, region_code = get_depot_info(args.depot)
    print(f"Monthly report: {display_name} {args.month}; days 1-{last_day}")
    session = login(); vehicle_data = {}
    for day_num in range(1, last_day + 1):
        date_obj = datetime(year, month, day_num); print(f"Fetching {date_obj.strftime('%d/%m/%Y')}...")
        for vehicle_no, data in fetch_daily_data(session, date_obj, vehicle_depot).items():
            if vehicle_no not in vehicle_data:
                vehicle_data[vehicle_no] = {"op_type": data.get("operation_type", ""), "engine": data.get("engine_type", ""), "days": {}, "up_to_day_latest": None}
            vehicle_data[vehicle_no]["days"][day_num] = data.get("kmpl")
            if data.get("up_to_day_kmpl") is not None: vehicle_data[vehicle_no]["up_to_day_latest"] = data.get("up_to_day_kmpl")
    if not vehicle_data: print("NO_DATA: No vehicle data found."); return 1

    # Schedule III = Major Service; Schedule IV = Complete Major Service.
    # Put only the icon in the applicable daily cell, while retaining that day's KMPL.
    zone = ZONE_BY_REGION.get(region_code, "")
    schedule_markers = fetch_monthly_schedule_markers(session, year, month, zone, region_code, display_name)
    marked_cells = 0
    for vehicle_no, by_day in schedule_markers.items():
        if vehicle_no not in vehicle_data:
            continue
        for day_num, icon in by_day.items():
            kmpl = vehicle_data[vehicle_no]["days"].get(day_num)
            if kmpl is None:
                vehicle_data[vehicle_no]["days"][day_num] = icon
            else:
                vehicle_data[vehicle_no]["days"][day_num] = f"{kmpl:.2f} {icon}"
            marked_cells += 1
    print(f"MONTHLY_SCHEDULE_MARKERS: {marked_cells} daily cells annotated")

    ordered = sorted(vehicle_data.items(), key=lambda item: (item[1]["up_to_day_latest"] is None, item[1]["up_to_day_latest"] if item[1]["up_to_day_latest"] is not None else float("inf"), item[0]))
    rows = []
    for idx, (vehicle_no, data) in enumerate(ordered, 1):
        row = {"SL No": idx, "Vehicle No": vehicle_no, "Op Type": data["op_type"], "Engine Type": data["engine"]}
        for day_num in range(1, days_in_month + 1): row[str(day_num)] = data["days"].get(day_num) if data["days"].get(day_num) is not None else ""
        row["Up-To-Day (Month End)"] = data["up_to_day_latest"] if data["up_to_day_latest"] is not None else ""; rows.append(row)

    reports_dir = PROJECT_DIR / "reports"; reports_dir.mkdir(exist_ok=True)
    xlsx_path = reports_dir / f"{display_name}_{args.month}.xlsx"
    folder_id = os.getenv("MONTHLY_DRIVE_FOLDER_ID", DEFAULT_GDRIVE_FOLDER)
    prior_path = reports_dir / f"_prior_{display_name}.xlsx"; existing_history = {}
    try:
        prior = download_latest_prior_monthly_sheet(folder_id, display_name, args.month, prior_path)
        if prior:
            prior_wb = load_workbook(prior_path, data_only=False)
            if "Vehicle Performance" in prior_wb.sheetnames:
                existing_history = read_existing_history(prior_wb["Vehicle Performance"])
                print(f"INCREMENTAL_HISTORY_FROM: {prior.get('name')}")
    except Exception as exc:
        print(f"HISTORY_CACHE_FALLBACK: {exc}")
        existing_history = {}

    pd.DataFrame(rows).to_excel(xlsx_path, sheet_name="Monthly KMPL", index=False, engine="openpyxl")
    workbook = load_workbook(xlsx_path); apply_formatting(workbook)
    if selected_month >= (2026, 4):
        print(f"Building Vehicle Performance history: region={region_code}, zone={zone or '[blank]'}")
        roster, history, remarks = build_history(session, year, month, zone, region_code, display_name, existing_history)
        write_history_sheet(workbook, roster, history, remarks)
        print(f"VEHICLE_HISTORY: {len(roster)} current vehicles; {len(remarks)} maintenance exceptions")

    workbook.save(xlsx_path)
    target_sheet_name = f"{display_name}_{args.month}"
    uploaded = upload_xlsx_as_google_sheet(xlsx_path, folder_id=folder_id, sheet_name=target_sheet_name)
    print(("ALREADY_DELIVERED: " if uploaded.get("already_existed") else "MONTHLY_AUTOMATION_SUCCESS: ") + str(uploaded.get("webViewLink")))
    print(f"GOOGLE_SHEET_ID: {uploaded.get('id')}"); return 0


if __name__ == "__main__": sys.exit(main())
