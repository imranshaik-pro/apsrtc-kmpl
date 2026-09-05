#!/usr/bin/env python3
"""Annual KPI v4: strict Product/Engine dimensions + stale-row cleanup.

Keeps v3 source logic, but guarantees that TOTAL rows and numeric-only
pseudo-dimensions can never enter or remain in the dashboard.
"""
import re
from bs4 import BeautifulSoup
import annual_kpi_runner_v3 as m


def strict_dimension_rows(html, label, prefix):
    soup = BeautifulSoup(html, "html.parser")
    out = {}
    for table in soup.find_all("table"):
        text = m.n(table.get_text(" ", strip=True))
        if m.n(label) not in text or "FOR THE MONTH" not in text or "UP TO THE MONTH" not in text:
            continue
        for tr in table.find_all("tr"):
            cells = [c.get_text(" ", strip=True) for c in tr.find_all("td", recursive=False)]
            if len(cells) < 7:
                continue
            name = cells[1].strip()
            normalized = m.n(name)
            # APSRTC Product/Engine names may be alphabetic or alphanumeric.
            # Pure numbers are never valid names. Any TOTAL row is excluded completely.
            if not name or "TOTAL" in normalized or not re.search(r"[A-Za-z]", name):
                continue
            mv = m.num(cells[3])
            uv = m.num(cells[6])
            out[f"{prefix}: {name}"] = {"month": mv, "upto": uv}
    return out


def strict_valid_dynamic(name):
    if not (name.startswith("PRODUCT:") or name.startswith("ENGINE:")):
        return True
    raw = name.split(":", 1)[1].strip()
    normalized = m.n(raw)
    return bool(re.search(r"[A-Za-z]", raw)) and "TOTAL" not in normalized


def clean_format_sheet(spreadsheet_id, mat, fys):
    # v3 wrote a shorter matrix over the old sheet without clearing rows below it.
    # That is why rejected numeric Product/Engine labels could still remain visible.
    sid = m.sheet_id(spreadsheet_id, m.SHEET_TITLE)
    svc = m.sheets_service()
    maxr = max(1000, len(mat) + 100)
    svc.spreadsheets().batchUpdate(
        spreadsheetId=spreadsheet_id,
        body={"requests": [
            {"unmergeCells": {"range": {"sheetId": sid, "startRowIndex": 1, "endRowIndex": maxr, "startColumnIndex": 0, "endColumnIndex": 1}}},
            {"updateCells": {"range": {"sheetId": sid, "startRowIndex": 0, "endRowIndex": maxr, "startColumnIndex": 0, "endColumnIndex": 16}, "fields": "userEnteredValue"}}
        ]}
    ).execute()
    # Call v3 formatter after the old values have been cleared.
    m.format_sheet_original(spreadsheet_id, mat, fys)


# Monkey-patch v3 globals used by its main().
m.direct_dimension_rows = strict_dimension_rows
m.valid_dynamic = strict_valid_dynamic
m.format_sheet_original = m.format_sheet
m.format_sheet = clean_format_sheet

if __name__ == "__main__":
    try:
        raise SystemExit(m.main())
    except Exception as exc:
        print(f"ANNUAL_KPI_FAILURE: {exc}")
        raise
