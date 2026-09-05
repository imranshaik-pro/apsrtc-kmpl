#!/usr/bin/env python3
"""Incrementally update annual KPI Google Sheets.

Rules:
- Reuse historical values already present in the Annual KPI sheet.
- Closed FYs fetch only missing KPI/source groups.
- Current FY refreshes only when the cumulative source month advances.
- Product/Engine rows remain exactly as APSRTC returns them; no merging.
- Tyre pages use depot code (e.g. KDP, PDTR, BDVL), not display name.
- Never substitute or guess a KPI value from another APSRTC column/source.
- If the correct source has no value, write MANUAL INPUT REQUIRED.
"""

from __future__ import annotations

import argparse
import os
import sys
from datetime import datetime

import annual_kpi_report as core
from src.auth.client import login
from src.integrations.google_drive import find_file, upload_xlsx_as_google_sheet
from src.integrations.google_sheets import (
    ensure_hidden_sheet,
    format_number_rows,
    read_values,
    write_values,
)

SHEET_TITLE = "Annual KPI"
META_TITLE = "_META"
MANUAL_INPUT = "MANUAL INPUT REQUIRED"
FIXED_KPIS = [
    "HSD KMPL INCL AC",
    "HSD KMPL EXCL AC",
    "TOTAL LUB KMPL",
    "B.D RATE",
    "MED CANCL.",
    "SPRING CONS",
    "AVG TYRE LIFE",
    "NEW TYRE LIFE",
    "RC TYRE LIFE",
    "N.T.S RATE",
    "Ist RC S Rate",
    "TTL SCP Rate",
    "RT Factor",
]
TYRE_KPIS = FIXED_KPIS[-7:]


def blank(value):
    return value is None or str(value).strip() == ""


def safe_value(value):
    """Return the source value, or an explicit manual-input marker.

    We intentionally do not infer, substitute, or calculate a replacement from
    another APSRTC column when the correct KPI source is blank/unavailable.
    """
    return MANUAL_INPUT if value is None else value


def tyre_total_row(headers, rows, display, vehicle):
    di = core.col(headers, ["DEPOT"])
    si = core.col(headers, ["TYRE SIZE", "SIZE"])
    tyre_code = vehicle.split("/")[0]
    wanted = {
        core.norm(tyre_code),
        core.norm(display),
        core.norm(vehicle),
        core.norm(vehicle.split("/")[-1]),
    }
    for row in rows:
        if di is None or di >= len(row) or core.norm(row[di]) not in wanted:
            continue
        if si is not None and si < len(row) and core.norm(row[si]) == core.norm("All Tyre Sizes Total"):
            return row
    return None


def fetch_tyre(session, display, vehicle, region, y, m):
    tyre_code = vehicle.split("/")[0]
    params = core.source_params(y, m, region, vehicle)
    params.update(
        {
            "month_year": datetime(y, m, 1).strftime("%b-%Y").upper(),
            "tyre_size": "All Tyre Sizes Total",
            "depot": tyre_code,
        }
    )
    html = core.request_html(session, core.TYRE_BASE, "d_statement_final.php", params)
    h, rows = core.find_table(
        html,
        ["DEPOT", "TYRE SIZE"],
        ["RT_FACTOR", "NEW MILEAGE", "AVG TOTAL MILEAGE"],
    )
    row = tyre_total_row(h, rows, display, vehicle)
    if not row:
        return {name: (None, "0.00") for name in TYRE_KPIS}
    rv = lambda aliases: core.row_value(h, row, aliases)
    return {
        "AVG TYRE LIFE": (rv(["AVG TOTAL MILEAGE", "AVERAGE TOTAL MILEAGE"]), "lakh"),
        "NEW TYRE LIFE": (rv(["NEW MILEAGE"]), "lakh"),
        "RC TYRE LIFE": (rv(["RC MILEAGE"]), "lakh"),
        "N.T.S RATE": (rv(["NEW %", "NTS", "N.T.S"]), "0.00"),
        "Ist RC S Rate": (rv(["IST RC %", "IST RC SCP %", "1ST RC %"]), "0.00"),
        "TTL SCP Rate": (rv(["TOTAL %", "TTL.SCP %", "TOTAL SCRAP %"]), "0.00"),
        "RT Factor": (rv(["RT_FACTOR", "RT FACTOR"]), "0.00"),
    }


def fetch_group(session, group, display, vehicle, region, y, m):
    if group == "HSD_INCL":
        return [("HSD KMPL INCL AC", core.fetch_hsd_incl(session, display, vehicle, region, y, m), "0.00")]
    if group == "HSD_EXCL":
        return [("HSD KMPL EXCL AC", core.fetch_hsd_excl(session, display, vehicle, region, y, m), "0.00")]
    if group == "PRODUCT":
        return core.fetch_direct_dimension(session, "prodkmpl_um.php", "PRODUCT", "PRODUCT", vehicle, region, y, m)
    if group == "ENGINE":
        return core.fetch_direct_dimension(session, "engkmpl_um.php", "ENGINE TYPE", "ENGINE", vehicle, region, y, m)
    if group == "LUB":
        return [("TOTAL LUB KMPL", core.fetch_lub(session, display, vehicle, region, y, m), "0")]
    if group == "BD":
        return [("B.D RATE", core.fetch_breakdown(session, display, vehicle, region, y, m), "0.00")]
    if group == "MED":
        return [("MED CANCL.", core.fetch_med(session, display, vehicle, region, y, m), "0.00")]
    if group == "SPRING":
        return [("SPRING CONS", core.fetch_spring(session, display, vehicle, region, y, m), "0.00")]
    if group == "TYRE":
        rows = []
        for name, (value, fmt) in fetch_tyre(session, display, vehicle, region, y, m).items():
            if fmt == "lakh" and value is not None:
                value, fmt = value / 100000.0, "0.00"
            rows.append((name, value, fmt))
        return rows
    raise ValueError(group)


def parse_existing(values, years):
    header_idx = next((i for i, row in enumerate(values) if row and core.norm(row[0]) == "KPI"), None)
    if header_idx is None:
        return None
    header = values[header_idx]
    year_cols = {fy: header.index(fy) if fy in header else None for fy in years}
    rows = {}
    for idx in range(header_idx + 1, len(values)):
        row = values[idx]
        if row and str(row[0]).strip():
            rows[str(row[0]).strip()] = idx
    return header_idx, year_cols, rows


def ensure_size(matrix, rows, cols):
    while len(matrix) < rows:
        matrix.append([])
    for row in matrix:
        while len(row) < cols:
            row.append("")


def metadata_map(spreadsheet_id):
    ensure_hidden_sheet(spreadsheet_id, META_TITLE)
    values = read_values(spreadsheet_id, f"'{META_TITLE}'!A:B")
    result = {}
    for row in values[1:] if values else []:
        if len(row) >= 2 and row[0]:
            result[str(row[0]).strip()] = str(row[1]).strip()
    return result


def write_metadata(spreadsheet_id, mapping):
    values = [["FY", "SOURCE_MONTH"]] + [[fy, mapping[fy]] for fy in sorted(mapping)]
    write_values(spreadsheet_id, f"'{META_TITLE}'!A1", values)


def source_groups_needed(matrix, parsed, fy, current_refresh):
    header_idx, year_cols, rows = parsed
    col = year_cols.get(fy)
    if col is None:
        return ["HSD_INCL", "HSD_EXCL", "PRODUCT", "ENGINE", "LUB", "BD", "MED", "SPRING", "TYRE"]
    if current_refresh:
        return ["HSD_INCL", "HSD_EXCL", "PRODUCT", "ENGINE", "LUB", "BD", "MED", "SPRING", "TYRE"]

    def missing_row(name):
        r = rows.get(name)
        return r is None or col >= len(matrix[r]) or blank(matrix[r][col])

    groups = []
    if missing_row("HSD KMPL INCL AC"): groups.append("HSD_INCL")
    if missing_row("HSD KMPL EXCL AC"): groups.append("HSD_EXCL")
    product_names = [n for n in rows if n.startswith("PRODUCT:")]
    engine_names = [n for n in rows if n.startswith("ENGINE:")]
    if not product_names or any(missing_row(n) for n in product_names): groups.append("PRODUCT")
    if not engine_names or any(missing_row(n) for n in engine_names): groups.append("ENGINE")
    if missing_row("TOTAL LUB KMPL"): groups.append("LUB")
    if missing_row("B.D RATE"): groups.append("BD")
    if missing_row("MED CANCL."): groups.append("MED")
    if missing_row("SPRING CONS"): groups.append("SPRING")
    if any(missing_row(n) for n in TYRE_KPIS): groups.append("TYRE")
    return groups


def update_existing_sheet(spreadsheet_id, years, display, vehicle, region):
    matrix = read_values(spreadsheet_id, f"'{SHEET_TITLE}'!A:Z")
    parsed = parse_existing(matrix, years)
    if parsed is None:
        raise RuntimeError("Existing Annual KPI sheet does not contain a KPI header row.")

    header_idx, year_cols, rows = parsed
    metadata = metadata_map(spreadsheet_id)
    session = None

    for fy in years:
        y, m = core.effective_month_for_fy(fy)
        source_month = f"{y:04d}-{m:02d}"
        is_current = fy == core.current_fy()
        current_refresh = is_current and metadata.get(fy) != source_month
        groups = source_groups_needed(matrix, parsed, fy, current_refresh)
        if not groups:
            print(f"FY {fy}: historical data complete; no APSRTC fetch required")
            metadata.setdefault(fy, source_month)
            continue

        if session is None:
            session = login()
        print(f"FY {fy}: fetching only missing/stale groups: {', '.join(groups)}")
        fetched = []
        for group in groups:
            fetched.extend(fetch_group(session, group, display, vehicle, region, y, m))

        col = year_cols.get(fy)
        if col is None:
            col = len(matrix[header_idx])
            ensure_size(matrix, len(matrix), col + 1)
            matrix[header_idx][col] = fy
            year_cols[fy] = col

        manual_required = []
        for name, value, fmt in fetched:
            if name not in rows:
                new_row = len(matrix)
                ensure_size(matrix, new_row + 1, max(len(matrix[header_idx]), col + 1))
                matrix[new_row][0] = name
                rows[name] = new_row
            r = rows[name]
            ensure_size(matrix, r + 1, col + 1)
            if current_refresh or blank(matrix[r][col]):
                matrix[r][col] = safe_value(value)
                if value is None:
                    manual_required.append(name)

        if manual_required:
            print(
                f"FY {fy}: MANUAL INPUT REQUIRED for: " + ", ".join(sorted(set(manual_required)))
            )
        metadata[fy] = source_month

    width = max((len(row) for row in matrix), default=1)
    ensure_size(matrix, len(matrix), width)
    write_values(spreadsheet_id, f"'{SHEET_TITLE}'!A1", matrix)
    write_metadata(spreadsheet_id, metadata)

    row_formats = {}
    for name, r in rows.items():
        row_formats[r + 1] = "0" if name == "TOTAL LUB KMPL" else "0.00"
    format_number_rows(
        spreadsheet_id,
        SHEET_TITLE,
        row_formats,
        start_col=2,
        end_col=max(2, width),
    )


def create_new_sheet(folder_id, sheet_name, display, vehicle, region, years):
    session = login()
    core.fetch_tyre = fetch_tyre
    fy_rows = {fy: core.collect_fy(session, display, vehicle, region, fy) for fy in years}

    # Never leave an unavailable fixed KPI looking like a valid zero/blank.
    # Explicitly mark it for manual input instead of substituting another value.
    for fy, rows in fy_rows.items():
        fixed_seen = {name for name, _, _ in rows if name in FIXED_KPIS}
        converted = []
        for name, value, fmt in rows:
            converted.append((name, safe_value(value) if name in FIXED_KPIS else value, fmt))
        for name in FIXED_KPIS:
            if name not in fixed_seen:
                converted.append((name, MANUAL_INPUT, "0" if name == "TOTAL LUB KMPL" else "0.00"))
        fy_rows[fy] = converted

    reports = core.PROJECT_DIR / "reports"
    reports.mkdir(exist_ok=True)
    year_tag = "_".join(fy.replace("-", "_") for fy in years)
    xlsx_path = reports / f"{display}_ANNUAL_KPI_{year_tag}.xlsx"
    core.build_workbook(display, years, fy_rows).save(xlsx_path)
    uploaded = upload_xlsx_as_google_sheet(xlsx_path, folder_id, sheet_name)
    metadata = {fy: "%04d-%02d" % core.effective_month_for_fy(fy) for fy in years}
    ensure_hidden_sheet(uploaded["id"], META_TITLE)
    write_metadata(uploaded["id"], metadata)
    return uploaded


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--depot", required=True)
    parser.add_argument("--years", default="2023-24,2024-25,2025-26")
    args = parser.parse_args()

    years = list(dict.fromkeys(x.strip() for x in args.years.split(",") if x.strip()))
    for fy in years:
        core.parse_fy(fy)
        core.effective_month_for_fy(fy)

    vehicle, display, region = core.depot_info(args.depot)
    folder_id = os.getenv("KPI_DRIVE_FOLDER_ID", core.DEFAULT_DRIVE_FOLDER)
    year_tag = "_".join(fy.replace("-", "_") for fy in years)
    sheet_name = f"{display}_ANNUAL_KPI_{year_tag}"
    existing = find_file(folder_id, sheet_name)

    if existing:
        print(f"Existing annual KPI sheet found: {existing.get('webViewLink')}")
        update_existing_sheet(existing["id"], years, display, vehicle, region)
        print(f"ANNUAL_KPI_INCREMENTAL_SUCCESS: {existing.get('webViewLink')}")
        print(f"GOOGLE_SHEET_ID: {existing['id']}")
        return 0

    uploaded = create_new_sheet(folder_id, sheet_name, display, vehicle, region, years)
    print(f"ANNUAL_KPI_SUCCESS: {uploaded.get('webViewLink')}")
    print(f"GOOGLE_SHEET_ID: {uploaded.get('id')}")
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception as exc:
        print(f"ANNUAL_KPI_FAILURE: {exc}")
        sys.exit(1)
