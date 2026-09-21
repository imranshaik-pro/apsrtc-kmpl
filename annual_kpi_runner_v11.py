#!/usr/bin/env python3
"""Annual KPI v11: v10 logic plus visible borders for the Upto column."""
import sys

from openpyxl import load_workbook
from openpyxl.chart import LineChart, Reference
from openpyxl.styles import Alignment, Font, PatternFill, Side, Border
from openpyxl.utils import get_column_letter

import annual_kpi_runner_v10 as v10

m = v10.m
v7 = v10.v7
LAYOUT_VERSION = "10"

# Keep existing v7/v8/v9/v10 sheet layouts compatible.
# v11 is a formatting-only patch; retain the established v10 layout contract.
v7.LAYOUT_VERSION = "10"

ORIGINAL_FORMAT_SHEET = v7.format_sheet_v7
ORIGINAL_MAKE_XLSX = v7.make_xlsx_v7






DASHBOARD_TITLE = "KPI Dashboard"
DETAIL_TITLE = "Annual KPI"


def _good_number(v):
    return isinstance(v, (int, float)) and not isinstance(v, bool)


def _style_detailed_xlsx(ws, display, fys):
    """Apply approved visual language while preserving the existing 18-column data model."""
    last_col = 18
    ws.sheet_view.showGridLines = False
    ws.merge_cells(start_row=1, start_column=1, end_row=1, end_column=last_col)
    ws["A1"] = f"APSRTC – {display} DEPOT"
    ws["A1"].font = Font(bold=True, color="FFFFFF", size=16)
    ws["A1"].fill = PatternFill("solid", fgColor="123B69")
    ws["A1"].alignment = Alignment(horizontal="center", vertical="center")
    ws.row_dimensions[1].height = 30
    ws.merge_cells(start_row=2, start_column=1, end_row=2, end_column=last_col)
    ws["A2"] = "ANNUAL KPI – DETAILED DATA"
    ws["A2"].font = Font(bold=True, color="17365D", size=13)
    ws["A2"].alignment = Alignment(horizontal="center")
    ws.merge_cells(start_row=3, start_column=1, end_row=3, end_column=last_col)
    ws["A3"] = f"Three Financial Years: {' | '.join(fys)}  •  Monthly values preserved in APSRTC source format"
    ws["A3"].font = Font(italic=True, color="595959", size=9)
    ws["A3"].alignment = Alignment(horizontal="center")
    fy_fills = ["D9EAF7", "E2F0D9", "FFF2CC"]
    for r in range(6, ws.max_row + 1):
        fy = str(ws.cell(r, 3).value or "")
        if fy in fys:
            fill = PatternFill("solid", fgColor=fy_fills[fys.index(fy)])
            for col in range(3, last_col + 1):
                ws.cell(r, col).fill = fill
    ws.freeze_panes = "E6"
    ws.print_title_rows = "1:5"
    ws.page_setup.orientation = "landscape"
    ws.page_setup.fitToWidth = 1
    ws.page_setup.fitToHeight = 0
    ws.sheet_properties.pageSetUpPr.fitToPage = True
    ws.oddFooter.center.text = f"APSRTC | {display} DEPOT | Annual KPI Detailed Data"


def _build_dashboard_xlsx(wb, display, fys, mat):
    """Create a separate executive dashboard; never invent KPI values."""
    if DASHBOARD_TITLE in wb.sheetnames:
        del wb[DASHBOARD_TITLE]
    ws = wb.create_sheet(DASHBOARD_TITLE, 0)
    ws.sheet_view.showGridLines = False
    for col, width in {"A":5,"B":28,"C":12,"D":12,"E":12,"F":12,"G":12,"H":12,"I":12,"J":12,"K":12,"L":12,"M":12,"N":12,"O":12}.items():
        ws.column_dimensions[col].width = width
    ws.merge_cells("A1:O2"); ws["A1"] = "APSRTC  |  ANNUAL KPI DASHBOARD"
    ws["A1"].font=Font(bold=True,color="FFFFFF",size=20); ws["A1"].fill=PatternFill("solid",fgColor="123B69"); ws["A1"].alignment=Alignment(horizontal="center",vertical="center")
    ws.merge_cells("A3:O3"); ws["A3"]=f"{display} DEPOT  •  3 FINANCIAL YEAR PERFORMANCE"
    ws["A3"].font=Font(bold=True,color="17365D",size=13); ws["A3"].alignment=Alignment(horizontal="center")
    ws.merge_cells("A4:O4"); ws["A4"]=f"Financial Years Covered: {' | '.join(fys)}"
    ws["A4"].font=Font(bold=True,color="008000",size=10); ws["A4"].alignment=Alignment(horizontal="center")
    # Executive summary uses only existing Upto values from the report matrix.
    headers=["KPI / Parameter"] + fys
    for j,v in enumerate(headers,1):
        cell=ws.cell(7,j); cell.value=v; cell.font=Font(bold=True,color="FFFFFF"); cell.fill=PatternFill("solid",fgColor="1F4E78"); cell.alignment=Alignment(horizontal="center")
    rows={}
    for row in mat[1:]:
        if len(row) >= 18:
            rows.setdefault(str(row[1]), {})[str(row[2])] = row[17]
    preferred=["HSD KMPL INCL AC","HSD KMPL EXCL AC","TOTAL LUB KMPL","B.D RATE","AVG TYRE LIFE","NEW TYRE LIFE","RC TYRE LIFE","N.T.S RATE","Ist RC S Rate","TTL SCP Rate","RT Factor"]
    rr=8
    for name in preferred:
        if name not in rows: continue
        ws.cell(rr,1).value=name; ws.cell(rr,1).font=Font(bold=True,color="17365D")
        for j,fy in enumerate(fys,2):
            val=rows[name].get(fy,"")
            ws.cell(rr,j).value=val
            ws.cell(rr,j).number_format="0.00"
            ws.cell(rr,j).alignment=Alignment(horizontal="center")
            ws.cell(rr,j).fill=PatternFill("solid",fgColor=["D9EAF7","E2F0D9","FFF2CC"][j-2])
        rr+=1
    ws.merge_cells(start_row=6,start_column=6,end_row=6,end_column=15); ws.cell(6,6).value="3-FY TREND VIEW"
    ws.cell(6,6).font=Font(bold=True,color="FFFFFF"); ws.cell(6,6).fill=PatternFill("solid",fgColor="009E60"); ws.cell(6,6).alignment=Alignment(horizontal="center")
    # Chart only source-grounded Upto values; blanks/MANUAL remain gaps.
    chart_rows=[]
    for name in ("HSD KMPL INCL AC","HSD KMPL EXCL AC","B.D RATE"):
        if name in rows and any(_good_number(rows[name].get(fy)) for fy in fys):
            chart_rows.append(name)
    if chart_rows:
        start=8
        for i,name in enumerate(chart_rows,start):
            ws.cell(i,6).value=name
            for j,fy in enumerate(fys,7): ws.cell(i,j).value=rows[name].get(fy,"")
        for j,fy in enumerate(fys,7): ws.cell(7,j).value=fy
        chart=LineChart(); chart.title="Selected KPI Upto Trend"; chart.style=10; chart.height=7; chart.width=16
        data=Reference(ws,min_col=7,max_col=9,min_row=7,max_row=7+len(chart_rows))
        cats=Reference(ws,min_col=6,min_row=8,max_row=7+len(chart_rows))
        chart.add_data(data,titles_from_data=True); chart.set_categories(cats); ws.add_chart(chart,"F12")
    note_row=max(rr+2,25)
    ws.merge_cells(start_row=note_row,start_column=1,end_row=note_row,end_column=15)
    ws.cell(note_row,1).value="Dashboard values are derived only from the Annual KPI source matrix. Missing/unavailable source values remain blank or MANUAL; no KPI value is fabricated."
    ws.cell(note_row,1).font=Font(italic=True,color="595959",size=9); ws.cell(note_row,1).alignment=Alignment(wrap_text=True)
    ws.freeze_panes="A7"; ws.print_title_rows="1:6"; ws.page_setup.orientation="landscape"; ws.page_setup.fitToWidth=1; ws.page_setup.fitToHeight=1; ws.sheet_properties.pageSetUpPr.fitToPage=True
    return ws


def make_xlsx_v11(display, mat, fys):
    """Approved two-sheet Annual workbook: executive dashboard + detailed APSRTC data."""
    path = ORIGINAL_MAKE_XLSX(display, mat, fys)
    wb = load_workbook(path)
    ws = wb[m.SHEET_TITLE]
    ws.insert_rows(1, 4)
    _style_detailed_xlsx(ws, display, fys)
    _build_dashboard_xlsx(wb, display, fys, mat)
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
    # Google Sheets rejects a merge that crosses a frozen-row boundary. The v7
    # formatter merges each 3-FY KPI block starting at row 2, so clear frozen
    # rows before formatting; v7 will then restore its intended freeze state.
    sid = m.sheet_id(spreadsheet_id, m.SHEET_TITLE)
    if sid is not None:
        m.sheets_service().spreadsheets().batchUpdate(
            spreadsheetId=spreadsheet_id,
            body={"requests":[{"updateSheetProperties":{
                "properties":{"sheetId":sid,"gridProperties":{"frozenRowCount":0}},
                "fields":"gridProperties.frozenRowCount"
            }}]}
        ).execute()
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
