#!/usr/bin/env python3
"""Annual KPI v11: v10 logic plus visible borders for the Upto column."""
import sys

from openpyxl import load_workbook
from openpyxl.styles import Alignment, Font, PatternFill, Side, Border

import annual_kpi_runner_v10 as v10

m = v10.m
v7 = v10.v7
LAYOUT_VERSION = "10"

# Keep existing v7/v8/v9/v10 sheet layouts compatible.
# v11 is a formatting-only patch; retain the established v10 layout contract.
v7.LAYOUT_VERSION = "10"

ORIGINAL_FORMAT_SHEET = v7.format_sheet_v7
ORIGINAL_MAKE_XLSX = v7.make_xlsx_v7




def make_xlsx_v11(display, mat, fys):
    """Professional Annual workbook presentation without changing KPI values."""
    path = ORIGINAL_MAKE_XLSX(display, mat, fys)
    wb = load_workbook(path)
    ws = wb[m.SHEET_TITLE]
    ws.insert_rows(1, 4)
    last_col = 18
    ws.merge_cells(start_row=1,start_column=1,end_row=1,end_column=last_col)
    ws["A1"] = f"APSRTC – {display} DEPOT"
    ws["A1"].font = Font(bold=True,color="FFFFFF",size=16)
    ws["A1"].fill = PatternFill("solid",fgColor="17365D")
    ws["A1"].alignment = Alignment(horizontal="center",vertical="center")
    ws.row_dimensions[1].height = 28
    ws.merge_cells(start_row=2,start_column=1,end_row=2,end_column=last_col)
    ws["A2"] = "ANNUAL KPI PERFORMANCE DASHBOARD"
    ws["A2"].font = Font(bold=True,color="1F4E78",size=12)
    ws["A2"].alignment = Alignment(horizontal="center",vertical="center")
    ws.merge_cells(start_row=3,start_column=1,end_row=3,end_column=last_col)
    ws["A3"] = "Three Financial Year Performance | Target | Monthly Trend | Upto"
    ws["A3"].font = Font(italic=True,color="595959",size=9)
    ws["A3"].alignment = Alignment(horizontal="center",vertical="center")
    ws.freeze_panes = "E6"
    ws.sheet_view.showGridLines = False
    ws.row_dimensions[5].height = 30
    # Reassert a strong header after inserting the title band.
    for c in range(1,last_col+1):
        cell=ws.cell(5,c)
        cell.font=Font(bold=True,color="FFFFFF")
        cell.fill=PatternFill("solid",fgColor="1F4E78")
        cell.alignment=Alignment(horizontal="center",vertical="center",wrap_text=True)
    # Give every 3-FY KPI block a calm visual boundary.
    divider=Side(style="medium",color="5B9BD5")
    for start in range(6,ws.max_row+1,3):
        end=min(start+2,ws.max_row)
        for c in range(1,last_col+1):
            cell=ws.cell(end,c)
            cell.border=Border(left=cell.border.left,right=cell.border.right,top=cell.border.top,bottom=divider)
    wb.save(path)
    return path


v7.make_xlsx_v7 = make_xlsx_v11

def _apply_upto_borders(spreadsheet_id, mat):
    sid = m.sheet_id(spreadsheet_id, m.SHEET_TITLE)
    if sid is None:
        return
    border = {"style": "SOLID"}
    m.sheets_service().spreadsheets().batchUpdate(
        spreadsheetId=spreadsheet_id,
        body={
            "requests": [
                {
                    "updateBorders": {
                        "range": {
                            "sheetId": sid,
                            "startRowIndex": 0,
                            "endRowIndex": len(mat),
                            "startColumnIndex": 17,
                            "endColumnIndex": 18,
                        },
                        "top": border,
                        "bottom": border,
                        "left": border,
                        "right": border,
                        "innerHorizontal": border,
                    }
                }
            ]
        },
    ).execute()


def format_sheet_v11(spreadsheet_id, mat, fys):
    # v10 already retries transient failures for the main sheet formatting.
    ORIGINAL_FORMAT_SHEET(spreadsheet_id, mat, fys)
    # Apply a visible grid specifically to column R (Upto), including header and rows.
    attempts = 4
    for attempt in range(1, attempts + 1):
        try:
            _apply_upto_borders(spreadsheet_id, mat)
            return
        except Exception as exc:
            if attempt >= attempts or not v10._retryable_google_error(exc):
                raise
            delay = 2 ** attempt
            print(
                f"GOOGLE SHEETS UPTO BORDER RETRY {attempt}/{attempts - 1}: "
                f"{exc}; retrying in {delay}s"
            )
            v10.time.sleep(delay)


v7.format_sheet_v7 = format_sheet_v11


if __name__ == "__main__":
    try:
        sys.exit(v7.main())
    except Exception as exc:
        print(f"ANNUAL_KPI_FAILURE: {exc}")
        raise
