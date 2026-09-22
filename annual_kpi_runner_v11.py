#!/usr/bin/env python3
"""Annual KPI v11: v10 logic plus visible borders for the Upto column."""
import sys
import os

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






DASHBOARD_TITLE = "1. KPI Dashboard"
DETAIL_TITLE = "2. Detailed Data (Our Format)"


def _coerce_dashboard_value(v):
    """Google values are strings; convert only genuine numeric text for charts/trends."""
    if isinstance(v, bool):
        return v
    if isinstance(v, (int, float)):
        return v
    text = str(v or "").strip()
    if not text or text.upper() == "MANUAL":
        return v
    try:
        return float(text.replace(",", ""))
    except ValueError:
        return v


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
    rows={}; current_kpi=""
    for row in mat[1:]:
        if len(row) >= 18:
            if str(row[1] or "").strip():
                current_kpi=str(row[1]).strip()
            fy=str(row[2] or "").strip()
            if current_kpi and fy in fys:
                rows.setdefault(current_kpi, {})[fy] = _coerce_dashboard_value(row[17])
    preferred=list(rows.keys())
    rr=8
    for name in preferred:
        if name not in rows: continue
        ws.cell(rr,1).value=name; ws.cell(rr,1).font=Font(bold=True,color="17365D")
        for j,fy in enumerate(fys,2):
            val=_coerce_dashboard_value(rows[name].get(fy,""))
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
    ws.title = DETAIL_TITLE
    ws.insert_rows(1, 4)
    _style_detailed_xlsx(ws, display, fys)
    _build_dashboard_xlsx(wb, display, fys, mat)
    if "_META" in wb.sheetnames:
        del wb["_META"]
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
        # Existing Annual sheets can contain merged KPI blocks in columns A:B.
        # Google Sheets rejects changing a freeze boundary through only part of
        # a merged range, so clear BOTH row and column freezes before v7
        # unmerges/rebuilds the matrix. v7 restores the intended A:D freeze.
        m.sheets_service().spreadsheets().batchUpdate(
            spreadsheetId=spreadsheet_id,
            body={"requests":[{"updateSheetProperties":{
                "properties":{"sheetId":sid,"gridProperties":{"frozenRowCount":0,"frozenColumnCount":0}},
                "fields":"gridProperties.frozenRowCount,gridProperties.frozenColumnCount"
            }}]}
        ).execute()
    # v7's legacy formatter tries to freeze A:D after it has merged the
    # three-FY KPI labels in A:B. Google Sheets rejects that boundary. For the
    # live sheet, suppress that legacy freeze request during the rebuild and
    # apply only the safe header-row freeze afterwards.
    svc = m.sheets_service()
    original_batch_update = svc.spreadsheets().batchUpdate
    def safe_batch_update(*args, **kwargs):
        body = kwargs.get("body") or {}
        requests = body.get("requests") or []
        for req in requests:
            usp = req.get("updateSheetProperties")
            if not usp:
                continue
            props = usp.get("properties", {})
            grid = props.get("gridProperties", {})
            if grid.get("frozenColumnCount") == 4:
                grid["frozenColumnCount"] = 0
                usp["fields"] = "gridProperties.frozenRowCount,gridProperties.frozenColumnCount"
        return original_batch_update(*args, **kwargs)
    svc.spreadsheets().batchUpdate = safe_batch_update
    try:
        ORIGINAL_FORMAT_SHEET(spreadsheet_id, mat, fys)
    finally:
        svc.spreadsheets().batchUpdate = original_batch_update
    # Keep the header visible; columns remain scrollable because the merged KPI
    # blocks make a four-column freeze invalid in Google Sheets.
    original_batch_update(
        spreadsheetId=spreadsheet_id,
        body={"requests":[{"updateSheetProperties":{
            "properties":{"sheetId":sid,"gridProperties":{"frozenRowCount":1,"frozenColumnCount":0}},
            "fields":"gridProperties.frozenRowCount,gridProperties.frozenColumnCount"
        }}]}
    ).execute()
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


def _ensure_dashboard_google_sheet(spreadsheet_id, display, fys, mat):
    """Refresh the live executive dashboard from source-grounded Annual KPI values."""
    svc=m.sheets_service()
    meta=svc.spreadsheets().get(spreadsheetId=spreadsheet_id).execute()
    sheets=meta.get("sheets",[])
    dash=next((s for s in sheets if s.get("properties",{}).get("title")==DASHBOARD_TITLE),None)
    if dash is None:
        svc.spreadsheets().batchUpdate(
            spreadsheetId=spreadsheet_id,
            body={"requests":[{"addSheet":{"properties":{"title":DASHBOARD_TITLE,"index":0,"gridProperties":{"rowCount":90,"columnCount":18}}}}]}
        ).execute()
        dash_id=m.sheet_id(spreadsheet_id,DASHBOARD_TITLE)
    else:
        dash_id=dash["properties"]["sheetId"]
        svc.spreadsheets().values().clear(spreadsheetId=spreadsheet_id,range=f"'{DASHBOARD_TITLE}'!A1:R90",body={}).execute()

    rows={}; current_kpi=""
    for row in mat[1:]:
        if len(row)>=18:
            if str(row[1]).strip(): current_kpi=str(row[1]).strip()
            fy=str(row[2]).strip()
            if current_kpi and fy in fys:
                rows.setdefault(current_kpi,{})[fy]=_coerce_dashboard_value(row[17])

    preferred=list(rows.keys())
    values=[
      ["APSRTC | ANNUAL KPI EXECUTIVE DASHBOARD"],
      [f"{display} DEPOT | THREE FINANCIAL YEAR PERFORMANCE"],
      [f"Financial Years: {' | '.join(fys)}"],
      ["Source-grounded management view | Current FY automatically follows selected reporting month"],
      [],
      ["KPI / PARAMETER",*fys,"TREND / STATUS"]
    ]
    for name in preferred:
        if name in rows:
            vals=[rows[name].get(fy,"") for fy in fys]
            numeric=[v for v in vals if isinstance(v,(int,float)) and not isinstance(v,bool)]
            trend=""
            if len(numeric)>=2:
                d=numeric[-1]-numeric[-2]
                trend=("▲ " if d>0 else "▼ " if d<0 else "● ")+f"{abs(d):.2f}"
            values.append([name,*vals,trend])
    values += [[],["SOURCE INTEGRITY"],["Missing/unavailable source values remain blank or MANUAL. No KPI value is fabricated."]]
    m.write_values(spreadsheet_id,f"'{DASHBOARD_TITLE}'!A1",values)

    last=len(values)
    req=[
      {"unmergeCells":{"range":{"sheetId":dash_id,"startRowIndex":0,"endRowIndex":90,"startColumnIndex":0,"endColumnIndex":18}}},
      {"mergeCells":{"range":{"sheetId":dash_id,"startRowIndex":0,"endRowIndex":1,"startColumnIndex":0,"endColumnIndex":18},"mergeType":"MERGE_ALL"}},
      {"mergeCells":{"range":{"sheetId":dash_id,"startRowIndex":1,"endRowIndex":2,"startColumnIndex":0,"endColumnIndex":18},"mergeType":"MERGE_ALL"}},
      {"mergeCells":{"range":{"sheetId":dash_id,"startRowIndex":2,"endRowIndex":3,"startColumnIndex":0,"endColumnIndex":18},"mergeType":"MERGE_ALL"}},
      {"mergeCells":{"range":{"sheetId":dash_id,"startRowIndex":3,"endRowIndex":4,"startColumnIndex":0,"endColumnIndex":18},"mergeType":"MERGE_ALL"}},
      {"repeatCell":{"range":{"sheetId":dash_id,"startRowIndex":0,"endRowIndex":1,"startColumnIndex":0,"endColumnIndex":18},
       "cell":{"userEnteredFormat":{"backgroundColor":{"red":0.035,"green":0.18,"blue":0.34},"textFormat":{"foregroundColor":{"red":1,"green":1,"blue":1},"bold":True,"fontSize":20},"horizontalAlignment":"CENTER","verticalAlignment":"MIDDLE"}},"fields":"userEnteredFormat"}},
      {"repeatCell":{"range":{"sheetId":dash_id,"startRowIndex":1,"endRowIndex":2,"startColumnIndex":0,"endColumnIndex":18},
       "cell":{"userEnteredFormat":{"backgroundColor":{"red":0.08,"green":0.32,"blue":0.52},"textFormat":{"foregroundColor":{"red":1,"green":1,"blue":1},"bold":True,"fontSize":13},"horizontalAlignment":"CENTER"}},"fields":"userEnteredFormat"}},
      {"repeatCell":{"range":{"sheetId":dash_id,"startRowIndex":2,"endRowIndex":4,"startColumnIndex":0,"endColumnIndex":18},
       "cell":{"userEnteredFormat":{"backgroundColor":{"red":0.92,"green":0.96,"blue":0.99},"textFormat":{"foregroundColor":{"red":0.10,"green":0.23,"blue":0.36},"bold":True},"horizontalAlignment":"CENTER"}},"fields":"userEnteredFormat"}},
      {"repeatCell":{"range":{"sheetId":dash_id,"startRowIndex":5,"endRowIndex":6,"startColumnIndex":0,"endColumnIndex":5},
       "cell":{"userEnteredFormat":{"backgroundColor":{"red":0.08,"green":0.28,"blue":0.45},"textFormat":{"foregroundColor":{"red":1,"green":1,"blue":1},"bold":True},"horizontalAlignment":"CENTER","verticalAlignment":"MIDDLE","borders":{"bottom":{"style":"SOLID_MEDIUM","color":{"red":0.95,"green":0.65,"blue":0.08}}}}},"fields":"userEnteredFormat"}},
      {"repeatCell":{"range":{"sheetId":dash_id,"startRowIndex":6,"endRowIndex":last,"startColumnIndex":0,"endColumnIndex":5},
       "cell":{"userEnteredFormat":{"borders":{"bottom":{"style":"SOLID","color":{"red":0.82,"green":0.85,"blue":0.88}}},"verticalAlignment":"MIDDLE"}},"fields":"userEnteredFormat.borders,userEnteredFormat.verticalAlignment"}},
      {"updateSheetProperties":{"properties":{"sheetId":dash_id,"gridProperties":{"frozenRowCount":6,"frozenColumnCount":0,"hideGridlines":True}},"fields":"gridProperties.frozenRowCount,gridProperties.frozenColumnCount,gridProperties.hideGridlines"}},
      {"updateDimensionProperties":{"range":{"sheetId":dash_id,"dimension":"COLUMNS","startIndex":0,"endIndex":1},"properties":{"pixelSize":245},"fields":"pixelSize"}},
      {"updateDimensionProperties":{"range":{"sheetId":dash_id,"dimension":"COLUMNS","startIndex":1,"endIndex":4},"properties":{"pixelSize":120},"fields":"pixelSize"}},
      {"updateDimensionProperties":{"range":{"sheetId":dash_id,"dimension":"COLUMNS","startIndex":4,"endIndex":5},"properties":{"pixelSize":125},"fields":"pixelSize"}},
      {"updateDimensionProperties":{"range":{"sheetId":dash_id,"dimension":"ROWS","startIndex":0,"endIndex":1},"properties":{"pixelSize":42},"fields":"pixelSize"}},
    ]
    for chart in (dash or {}).get("charts", []):
        chart_id = chart.get("chartId")
        if chart_id is not None:
            req.insert(0, {"deleteEmbeddedObject": {"objectId": chart_id}})
    fy_colors=[
      {"red":0.84,"green":0.91,"blue":0.97},
      {"red":0.86,"green":0.94,"blue":0.86},
      {"red":1.0,"green":0.94,"blue":0.75},
    ]
    for j,color in enumerate(fy_colors,start=1):
        req.append({"repeatCell":{"range":{"sheetId":dash_id,"startRowIndex":6,"endRowIndex":last,"startColumnIndex":j,"endColumnIndex":j+1},
          "cell":{"userEnteredFormat":{"backgroundColor":color,"numberFormat":{"type":"NUMBER","pattern":"0.00"},"horizontalAlignment":"CENTER","textFormat":{"bold":True}}},
          "fields":"userEnteredFormat"}})
    svc.spreadsheets().batchUpdate(spreadsheetId=spreadsheet_id,body={"requests":req}).execute()

    # Add source-grounded trend chart from the dashboard table. It intentionally
    # plots blanks as gaps and never manufactures missing values.
    chart_end=min(last,12)
    if chart_end>7:
        domain={"domain":{"sourceRange":{"sources":[{"sheetId":dash_id,"startRowIndex":6,"endRowIndex":chart_end,"startColumnIndex":0,"endColumnIndex":1}]}}}
        series=[]
        for j in range(1,4):
            series.append({"series":{"sourceRange":{"sources":[{"sheetId":dash_id,"startRowIndex":6,"endRowIndex":chart_end,"startColumnIndex":j,"endColumnIndex":j+1}]}},"targetAxis":"LEFT_AXIS"})
        basic={"chartType":"COLUMN","legendPosition":"BOTTOM_LEGEND","axis":[{"position":"BOTTOM_AXIS","title":"KPI"},{"position":"LEFT_AXIS","title":"Value"}],"domains":[domain],"series":series,"headerCount":0}
        chart={"spec":{"title":"3-FY KPI Performance Overview","basicChart":basic},"position":{"overlayPosition":{"anchorCell":{"sheetId":dash_id,"rowIndex":5,"columnIndex":6},"widthPixels":760,"heightPixels":360}}}
        svc.spreadsheets().batchUpdate(spreadsheetId=spreadsheet_id,body={"requests":[{"addChart":{"chart":chart}}]}).execute()


def _prepare_live_detail_sheet(spreadsheet_id):
    """Make reruns idempotent and return the detailed sheet to v7's internal name."""
    svc = m.sheets_service()
    meta = svc.spreadsheets().get(spreadsheetId=spreadsheet_id).execute()
    by_title = {s["properties"]["title"]: s for s in meta.get("sheets", [])}
    if m.SHEET_TITLE not in by_title and DETAIL_TITLE in by_title:
        sid = by_title[DETAIL_TITLE]["properties"]["sheetId"]
        svc.spreadsheets().batchUpdate(
            spreadsheetId=spreadsheet_id,
            body={"requests": [{"updateSheetProperties": {
                "properties": {"sheetId": sid, "title": m.SHEET_TITLE},
                "fields": "title"
            }}]}
        ).execute()


def _style_live_detail(spreadsheet_id, mat):
    """Professional table styling with a bordered three-row block for every KPI."""
    svc = m.sheets_service().spreadsheets()
    sid = m.sheet_id(spreadsheet_id, m.SHEET_TITLE)
    if sid is None:
        return
    row_count = max(len(mat), 2)
    light = {"red": 0.78, "green": 0.82, "blue": 0.86}
    medium = {"red": 0.12, "green": 0.27, "blue": 0.42}
    thin = {"style": "SOLID", "color": light}
    outer = {"style": "SOLID_MEDIUM", "color": medium}
    requests = [
        {"updateSheetProperties": {"properties": {"sheetId": sid, "gridProperties": {
            "frozenRowCount": 1, "frozenColumnCount": 0, "hideGridlines": True
        }}, "fields": "gridProperties.frozenRowCount,gridProperties.frozenColumnCount,gridProperties.hideGridlines"}},
        {"repeatCell": {"range": {"sheetId": sid, "startRowIndex": 0, "endRowIndex": 1,
                                   "startColumnIndex": 0, "endColumnIndex": 18},
            "cell": {"userEnteredFormat": {"backgroundColor": {"red": 0.04, "green": 0.20, "blue": 0.38},
                "textFormat": {"foregroundColor": {"red": 1, "green": 1, "blue": 1}, "bold": True, "fontSize": 11},
                "horizontalAlignment": "CENTER", "verticalAlignment": "MIDDLE", "wrapStrategy": "WRAP"}},
            "fields": "userEnteredFormat"}},
        {"updateBorders": {"range": {"sheetId": sid, "startRowIndex": 0, "endRowIndex": row_count,
                                      "startColumnIndex": 0, "endColumnIndex": 18},
            "top": thin, "bottom": thin, "left": thin, "right": thin,
            "innerHorizontal": thin, "innerVertical": thin}},
        {"updateDimensionProperties": {"range": {"sheetId": sid, "dimension": "ROWS",
                                                   "startIndex": 0, "endIndex": 1},
            "properties": {"pixelSize": 42}, "fields": "pixelSize"}},
    ]
    widths = [(0, 1, 58), (1, 2, 235), (2, 3, 82), (3, 4, 76), (4, 18, 72)]
    for start, end, size in widths:
        requests.append({"updateDimensionProperties": {"range": {"sheetId": sid, "dimension": "COLUMNS",
            "startIndex": start, "endIndex": end}, "properties": {"pixelSize": size}, "fields": "pixelSize"}})
    fills = {
        "HSD": {"red": 0.86, "green": 0.93, "blue": 0.98},
        "PRODUCT": {"red": 0.88, "green": 0.95, "blue": 0.86},
        "ENGINE": {"red": 1.00, "green": 0.92, "blue": 0.78},
        "TYRE": {"red": 0.92, "green": 0.87, "blue": 0.97},
        "OTHER": {"red": 0.93, "green": 0.94, "blue": 0.95},
    }
    current = ""
    block_start = None
    for idx, row in enumerate(mat[1:], start=1):
        label = str(row[1] if len(row) > 1 else "").strip()
        if label:
            current = label.upper()
            block_start = idx
        if block_start is not None and (idx == row_count - 1 or
                (idx + 1 < len(mat) and str(mat[idx + 1][1] if len(mat[idx + 1]) > 1 else "").strip())):
            kind = "HSD" if "HSD" in current else "PRODUCT" if "PRODUCT" in current else "ENGINE" if "ENGINE" in current else "TYRE" if "TYRE" in current else "OTHER"
            requests.extend([
                {"repeatCell": {"range": {"sheetId": sid, "startRowIndex": block_start,
                    "endRowIndex": idx + 1, "startColumnIndex": 0, "endColumnIndex": 2},
                    "cell": {"userEnteredFormat": {"backgroundColor": fills[kind],
                        "textFormat": {"bold": True, "foregroundColor": medium},
                        "verticalAlignment": "MIDDLE", "wrapStrategy": "WRAP"}},
                    "fields": "userEnteredFormat"}},
                {"updateBorders": {"range": {"sheetId": sid, "startRowIndex": block_start,
                    "endRowIndex": idx + 1, "startColumnIndex": 0, "endColumnIndex": 18},
                    "top": outer, "bottom": outer, "left": outer, "right": outer}}
            ])
    svc.batchUpdate(spreadsheetId=spreadsheet_id, body={"requests": requests}).execute()


def _finalize_live_workbook(spreadsheet_id):
    """Expose exactly the two approved sheets and remove stale legacy tabs."""
    svc = m.sheets_service()
    meta = svc.spreadsheets().get(spreadsheetId=spreadsheet_id).execute()
    sheets = meta.get("sheets", [])
    detail = next((s for s in sheets if s["properties"]["title"] == m.SHEET_TITLE), None)
    dash = next((s for s in sheets if s["properties"]["title"] == DASHBOARD_TITLE), None)
    if detail is None or dash is None:
        raise RuntimeError("Dashboard/detail sheet finalization failed")
    requests = [
        {"updateSheetProperties": {"properties": {"sheetId": dash["properties"]["sheetId"], "index": 0},
                                    "fields": "index"}},
        {"updateSheetProperties": {"properties": {"sheetId": detail["properties"]["sheetId"],
                                                    "title": DETAIL_TITLE, "index": 1},
                                    "fields": "title,index"}},
    ]
    keep = {dash["properties"]["sheetId"], detail["properties"]["sheetId"]}
    for sheet in sheets:
        sid = sheet["properties"]["sheetId"]
        if sid not in keep:
            requests.append({"deleteSheet": {"sheetId": sid}})
    svc.spreadsheets().batchUpdate(spreadsheetId=spreadsheet_id, body={"requests": requests}).execute()


ORIGINAL_V7_MAIN=v7.main

def main_v11():
    """Build and publish an idempotent professional two-sheet Annual workbook."""
    args=sys.argv[1:]
    def _arg(name, default=""):
        try: return args[args.index(name)+1]
        except (ValueError,IndexError): return default
    depot=_arg("--depot"); selected=_arg("--selected-month")
    existing = None
    display = ""
    fys = []
    if depot and selected:
        sy,sm=map(int,selected.split("-"))
        fys=m.fy_triplet(sy,sm)
        vehicle,display,region=m.core.depot_info(depot)
        folder=os.getenv("KPI_DRIVE_FOLDER_ID",m.core.DEFAULT_DRIVE_FOLDER)
        existing=m.find_file(folder,f"{display}_ANNUAL_KPI_DASHBOARD")
        if existing:
            _prepare_live_detail_sheet(existing["id"])
    rc=ORIGINAL_V7_MAIN()
    if depot and selected:
        folder=os.getenv("KPI_DRIVE_FOLDER_ID",m.core.DEFAULT_DRIVE_FOLDER)
        existing=m.find_file(folder,f"{display}_ANNUAL_KPI_DASHBOARD")
        if existing:
            live=m.read_values(existing["id"],f"'{m.SHEET_TITLE}'!A:R")
            _style_live_detail(existing["id"],live)
            _ensure_dashboard_google_sheet(existing["id"],display,fys,live)
            _finalize_live_workbook(existing["id"])
    return rc


if __name__ == "__main__":
    try:
        sys.exit(main_v11())
    except Exception as exc:
        print(f"ANNUAL_KPI_FAILURE: {exc}")
        raise
