"""Vehicle Performance History sheet for Monthly reports.

Rules:
- Current selected-month MTD-598 roster defines vehicles shown.
- FY24-25 history comes from month-wise MTD-598 snapshots.
- FY25-26/FY26-27 history comes from Vehicle-wise 12 Month KMPL Trend.
- Existing history is preserved; only a new month/new vehicle is backfilled.
- SCH-III/SCH-IV annotations start Apr-2026 only.
- Duplicate/conflicting schedule data is logged, never guessed.
"""
from __future__ import annotations

from datetime import datetime
from io import StringIO
import re

import pandas as pd
from openpyxl.styles import Alignment, Border, Font, PatternFill, Side
from openpyxl.utils import get_column_letter

MTD_URL = "http://103.44.14.20/med/edeengine.php"
TREND_URL = "http://103.44.14.20/med/vkmpl12trend.php"
S3_URL = "http://103.44.14.20/med/s3cover.php"
S4_URL = "http://103.44.14.20/med/s4cover.php"
FYS = ("2024-25", "2025-26", "2026-27")
MONTHS = ("Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec", "Jan", "Feb", "Mar")
THIN = Side(style="thin")
BORDER = Border(left=THIN, right=THIN, top=THIN, bottom=THIN)


def norm_vehicle(value):
    return re.sub(r"\s+", "", str(value or "")).upper()


def _clean_columns(df):
    if isinstance(df.columns, pd.MultiIndex):
        cols = []
        for col in df.columns:
            parts = [str(x).strip() for x in col if str(x).strip() and not str(x).startswith("Unnamed")]
            cols.append(" ".join(dict.fromkeys(parts)))
        df.columns = cols
    else:
        df.columns = [str(x).strip() for x in df.columns]
    return df


def _table(html, required):
    for df in pd.read_html(StringIO(html)):
        df = _clean_columns(df)
        joined = " | ".join(map(str, df.columns)).lower()
        if all(x.lower() in joined for x in required):
            return df
    return None


def fetch_mtd(session, yyyymm, regn, depot):
    payload = {"yymm": yyyymm, "regn": regn, "depot": depot, "stype": "", "eng": "", "kms": "", "kmsl": "", "kmpl": "", "kmpll": "", "fstatus": "0", "veh": ""}
    r = session.post(MTD_URL, data=payload, timeout=30)
    r.raise_for_status()
    df = _table(r.text, ["Veh No", "HSD KMPL", "Comm Date"])
    if df is None:
        raise RuntimeError(f"MTD-598 table not found for {depot} {yyyymm}")
    result = {}
    for _, row in df.iterrows():
        def get(label):
            for c in df.columns:
                if label.lower() == str(c).strip().lower():
                    return row[c]
            return ""
        v = norm_vehicle(get("Veh No"))
        if not v or v == "NAN":
            continue
        try:
            kmpl = float(get("HSD KMPL"))
        except (TypeError, ValueError):
            kmpl = None
        result[v] = {"kmpl": kmpl, "op": str(get("Veh Type")).strip(), "engine": str(get("Eng Make")).strip(), "comm_date": str(get("Comm Date")).strip()}
    return result


def fetch_trend(session, fy, zone, regn, depot):
    fyymm = {"2025-26": "202603March_2026", "2026-27": "202703March_2027"}[fy]
    r = session.post(TREND_URL, data={"yymm": "", "fyymm": fyymm, "zone": zone, "regn": regn, "dept": depot, "submit": "SUBMIT"}, timeout=30)
    r.raise_for_status()
    df = _table(r.text, ["Vehicle No", "Product Type", "Engine Type"])
    if df is None:
        raise RuntimeError(f"12-month trend table not found for {depot} {fy}")
    result = {}
    for _, row in df.iterrows():
        def find(prefix, contains=None):
            for c in df.columns:
                s = str(c)
                if s.lower().startswith(prefix.lower()) and (contains is None or contains.lower() in s.lower()):
                    return row[c]
            return ""
        v = norm_vehicle(find("Vehicle No"))
        if not v or v == "NAN":
            continue
        months = {}
        start_year = int(fy[:4])
        for i, mon in enumerate(MONTHS):
            yy = start_year if i < 9 else start_year + 1
            label = f"{mon}-{str(yy)[2:]}"
            val = find(label, "HSD KMPL")
            try:
                months[mon] = float(val)
            except (TypeError, ValueError):
                months[mon] = None
        result[v] = {"op": str(find("Product Type")).strip(), "engine": str(find("Engine Type")).strip(), "months": months}
    return result


def fetch_schedule(session, schedule_no, yyyymm, month_label, zone, regn, depot):
    url = S3_URL if schedule_no == 3 else S4_URL
    r = session.post(url, data={"yymm": f"{yyyymm}{month_label}", "zone": zone, "regn": regn, "dept": depot, "submit": "SUBMIT"}, timeout=30)
    r.raise_for_status()
    date_col = f"Date of Sch-{'III' if schedule_no == 3 else 'IV'}"
    df = _table(r.text, ["Vehicle No", date_col])
    if df is None:
        return {}
    events = {}
    for _, row in df.iterrows():
        vcol = next((c for c in df.columns if str(c).strip().lower() == "vehicle no."), None) or next((c for c in df.columns if "vehicle no" in str(c).lower()), None)
        dcol = next((c for c in df.columns if date_col.lower() in str(c).lower()), None)
        if vcol is None or dcol is None:
            continue
        v = norm_vehicle(row[vcol]); d = str(row[dcol]).strip()
        if not v or v == "NAN" or not d or d.lower() == "nan":
            continue
        events.setdefault(v, []).append(d)
    return events


def _month_pairs(fy):
    y = int(fy[:4])
    return [(MONTHS[i], f"{y if i < 9 else y+1}{i+4:02d}" if i < 9 else f"{y+1}{i-8:02d}") for i in range(12)]


def _selected_month_index(year, month):
    return month - 4 if month >= 4 else month + 8


def read_existing_history(ws):
    """Return displayed cell history keyed by vehicle/fy from a prior workbook."""
    out = {}
    if ws is None:
        return out
    headers = {str(c.value).strip(): c.column for c in ws[1] if c.value is not None}
    if "Veh No" not in headers or "FY Year" not in headers:
        return out
    last_vehicle = ""
    for r in range(2, ws.max_row + 1):
        raw_v = ws.cell(r, headers["Veh No"]).value
        if raw_v not in (None, ""):
            last_vehicle = norm_vehicle(raw_v)
        fy = str(ws.cell(r, headers["FY Year"]).value or "").strip()
        if not last_vehicle or fy not in FYS:
            continue
        out.setdefault(last_vehicle, {})[fy] = {m: ws.cell(r, headers[m]).value for m in MONTHS if m in headers}
    return out


def build_history(session, selected_year, selected_month, zone, regn, depot, existing=None):
    selected_yyyymm = f"{selected_year}{selected_month:02d}"
    roster = fetch_mtd(session, selected_yyyymm, regn, depot)
    existing = existing or {}
    values = {v: {fy: dict(existing.get(v, {}).get(fy, {})) for fy in FYS} for v in roster}
    new_vehicles = {v for v in roster if v not in existing}

    # FY24-25: expensive month-wise MTD fetch is initialization/new-vehicle only.
    need_full_init = not existing
    targets_2425 = set(roster) if need_full_init else new_vehicles
    if targets_2425:
        for mon, ym in _month_pairs("2024-25"):
            snap = fetch_mtd(session, ym, regn, depot)
            for v in targets_2425:
                if v in snap:
                    values[v]["2024-25"][mon] = snap[v]["kmpl"]

    # Trend sources: initialize all, or backfill newly appearing vehicles.
    for fy in ("2025-26", "2026-27"):
        targets = set(roster) if need_full_init else new_vehicles
        # Current selected FY month must always be refreshed/added for all current vehicles.
        if fy == "2026-27" and (selected_year, selected_month) >= (2026, 4):
            targets |= set(roster)
        if not targets:
            continue
        trend = fetch_trend(session, fy, zone, regn, depot)
        for v in targets:
            if v not in trend:
                continue
            for mon, val in trend[v]["months"].items():
                # Never copy future 0.00 placeholders from current FY trend.
                if fy == "2026-27":
                    mi = MONTHS.index(mon)
                    if (selected_year, selected_month) < (2027, 4) and mi > _selected_month_index(selected_year, selected_month):
                        continue
                if need_full_init or v in new_vehicles or mon == MONTHS[_selected_month_index(selected_year, selected_month)]:
                    values[v][fy][mon] = val
            if not roster[v]["op"] and trend[v]["op"]:
                roster[v]["op"] = trend[v]["op"]
            if not roster[v]["engine"] and trend[v]["engine"]:
                roster[v]["engine"] = trend[v]["engine"]

    remarks = []
    # Maintenance is strictly FY26-27 onward. On first build/new vehicle, fill Apr->selected;
    # on incremental normal run, only selected month is fetched.
    if (selected_year, selected_month) >= (2026, 4):
        end_idx = min(_selected_month_index(selected_year, selected_month), 11)
        indices = range(0, end_idx + 1) if need_full_init or new_vehicles else [end_idx]
        for i in indices:
            mon = MONTHS[i]
            yy = 2026 if i < 9 else 2027
            mm = i + 4 if i < 9 else i - 8
            ym = f"{yy}{mm:02d}"
            month_label = datetime(yy, mm, 1).strftime("%B_%Y")
            s3 = fetch_schedule(session, 3, ym, month_label, zone, regn, depot)
            s4 = fetch_schedule(session, 4, ym, month_label, zone, regn, depot)
            targets = set(roster) if need_full_init else (new_vehicles | (set(roster) if i == end_idx else set()))
            for v in targets:
                e3, e4 = s3.get(v, []), s4.get(v, [])
                abnormal = len(e3) > 1 or len(e4) > 1 or (e3 and e4)
                if abnormal:
                    details = []
                    if e3: details.append("SCH-III=" + ", ".join(e3))
                    if e4: details.append("SCH-IV=" + ", ".join(e4))
                    remarks.append((f"{mon}-{str(yy)[2:]}", v, "; ".join(details)))
                    continue
                event = (3, e3[0]) if e3 else ((4, e4[0]) if e4 else None)
                if event:
                    try: day = int(event[1].split("-")[0])
                    except Exception: day = event[1]
                    base = values[v]["2026-27"].get(mon)
                    base_text = "" if base in (None, "") else (f"{base:.2f}" if isinstance(base, (int, float)) else str(base).split(" ")[0])
                    icon = "🔧" if event[0] == 3 else "⚙"
                    values[v]["2026-27"][mon] = f"{base_text} {icon} {day}".strip()
    return roster, values, remarks


def write_history_sheet(wb, roster, values, remarks):
    if "Vehicle Performance" in wb.sheetnames:
        del wb["Vehicle Performance"]
    ws = wb.create_sheet("Vehicle Performance")
    headers = ["S.NO", "Veh No", "OP Type", "Eng Type", "FY Year", *MONTHS]
    ws.append(headers)
    header_fill = PatternFill("solid", fgColor="4472C4")
    for c in ws[1]:
        c.font = Font(bold=True, color="FFFFFF"); c.fill = header_fill; c.alignment = Alignment(horizontal="center", vertical="center"); c.border = BORDER
    row = 2
    for idx, v in enumerate(sorted(roster), 1):
        start = row
        for fy in FYS:
            vals = [values.get(v, {}).get(fy, {}).get(m, "") for m in MONTHS]
            ws.append([idx, v, roster[v].get("op", ""), roster[v].get("engine", ""), fy, *vals])
            for c in ws[row]:
                c.border = BORDER; c.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)
            row += 1
        end = row - 1
        for col in range(1, 5):
            ws.merge_cells(start_row=start, start_column=col, end_row=end, end_column=col)
            ws.cell(start, col).alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)
    ws.freeze_panes = "F2"
    widths = [7, 14, 20, 18, 10] + [12] * 12
    for i, width in enumerate(widths, 1): ws.column_dimensions[get_column_letter(i)].width = width
    row += 1
    ws.cell(row, 1, "Legend / Data Remarks").font = Font(bold=True)
    row += 1; ws.cell(row, 1, "🔧 = Schedule-III completed | ⚙ = Schedule-IV completed | number = completion day")
    ws.merge_cells(start_row=row, start_column=1, end_row=row, end_column=17)
    if remarks:
        row += 2; ws.cell(row, 1, "DATA EXCEPTIONS").font = Font(bold=True)
        row += 1; ws.append(["Month", "Vehicle", "Source maintenance entries - review required"])
        for month, vehicle, detail in remarks:
            ws.append([month, vehicle, detail])
    return ws
