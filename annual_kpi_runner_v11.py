#!/usr/bin/env python3
"""Annual KPI v11: v10 logic plus visible borders for the Upto column."""
import sys
import os
import annual_history as history
from datetime import datetime
from annual_visuals import dashboard_model, render_xlsx_dashboard, google_dashboard_requests, print_setup, period_label, rgb, number

REPORT_MONTH = ""

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
    return render_xlsx_dashboard(wb,DASHBOARD_TITLE,
        dashboard_model(display,fys,mat,REPORT_MONTH),display,REPORT_MONTH)


def make_xlsx_v11(display, mat, fys):
    """Approved two-sheet Annual workbook: executive dashboard + detailed APSRTC data."""
    mat=list(mat)
    while mat and not any(v not in (None, "") for v in mat[-1]): mat.pop()
    path = ORIGINAL_MAKE_XLSX(display, mat, fys)
    wb = load_workbook(path)
    ws = wb[m.SHEET_TITLE]
    ws.title = DETAIL_TITLE
    # Move merge definitions explicitly when adding presentation headers.
    for merged in list(ws.merged_cells.ranges): ws.unmerge_cells(str(merged))
    ws.insert_rows(1, 4)
    _style_detailed_xlsx(ws, display, fys)
    ws["A2"] = f"ANNUAL KPI — Through {period_label(REPORT_MONTH)}"
    ws["A3"] = f"FY {fys[0]} / {fys[1]}: full year. FY {fys[-1]}: through selected month. Blank = unavailable."
    for r in range(6,ws.max_row+1,3):
        for col in (1,2):
            ws.merge_cells(start_row=r,start_column=col,end_row=min(r+2,ws.max_row),end_column=col)
    for r in range(5,ws.max_row+1):
        for col in range(1,19):
            cell=ws.cell(r,col)
            cell.border=Border(left=Side(style="thin",color="CCD7E3"),right=Side(style="thin",color="CCD7E3"),
                               top=Side(style="medium" if (r-6)%3==0 else "thin",color="CCD7E3"),
                               bottom=Side(style="thin",color="CCD7E3"))
            cell.alignment=Alignment(horizontal="left" if col==2 else "center",vertical="center",wrap_text=True)
            if r>5:
                cell.font=Font(name="Arial",size=10,color="23364D",bold=col in (1,2,18))
        ws.row_dimensions[r].height=44 if any("MANUAL" in str(ws.cell(r,c).value) for c in range(4,19)) else 26
    from openpyxl.worksheet.pagebreak import Break
    # Six complete KPI blocks per page, including taller MANUAL rows.
    for end in range(23,ws.max_row,18): ws.row_breaks.append(Break(id=end))
    ws.column_dimensions["B"].width=27
    ws.column_dimensions["Q"].width=2
    ws.column_dimensions["Q"].hidden=True
    print_setup(ws,display,period_label(REPORT_MONTH),"1:5",18,ws.max_row)
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
    # A newly imported XLSX already uses the presentation detail-tab name.
    _prepare_live_detail_sheet(spreadsheet_id)
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
    svc=m.sheets_service().spreadsheets()
    meta=svc.get(spreadsheetId=spreadsheet_id).execute()
    dash=next((s for s in meta.get("sheets",[]) if s["properties"]["title"]==DASHBOARD_TITLE),None)
    if dash is None:
        result=svc.batchUpdate(spreadsheetId=spreadsheet_id,body={"requests":[{"addSheet":{"properties":{"title":DASHBOARD_TITLE,"gridProperties":{"rowCount":100,"columnCount":24}}}}]}).execute()
        sid=result["replies"][0]["addSheet"]["properties"]["sheetId"]
    else:
        sid=dash["properties"]["sheetId"]
    req=[{"deleteEmbeddedObject":{"objectId":chart["chartId"]}} for chart in (dash or {}).get("charts",[])]
    req+=google_dashboard_requests(sid,dashboard_model(display,fys,mat,REPORT_MONTH))
    svc.batchUpdate(spreadsheetId=spreadsheet_id,body={"requests":req}).execute()


def _add_live_identity(spreadsheet_id,display,fys):
    sid=m.sheet_id(spreadsheet_id,m.SHEET_TITLE)
    svc=m.sheets_service().spreadsheets()
    req=[{"updateSheetProperties":{"properties":{"sheetId":sid,"gridProperties":{"frozenRowCount":0,"frozenColumnCount":0}},"fields":"gridProperties.frozenRowCount,gridProperties.frozenColumnCount"}},
         {"insertDimension":{"range":{"sheetId":sid,"dimension":"ROWS","startIndex":0,"endIndex":4},"inheritFromBefore":False}}]
    for r in range(3):
        area={"sheetId":sid,"startRowIndex":r,"endRowIndex":r+1,"startColumnIndex":0,"endColumnIndex":18}
        req.extend([{"mergeCells":{"range":area,"mergeType":"MERGE_ALL"}},
                    {"repeatCell":{"range":area,"cell":{"userEnteredFormat":{
                        "backgroundColor":rgb("12345B" if r==0 else "EAF2FA"),
                        "textFormat":{"fontFamily":"Arial","fontSize":16 if r==0 else 11,"bold":True,
                                      "foregroundColor":rgb("FFFFFF" if r==0 else "12345B")},
                        "verticalAlignment":"MIDDLE","horizontalAlignment":"CENTER"}},"fields":"userEnteredFormat"}},
                    {"updateDimensionProperties":{"range":{"sheetId":sid,"dimension":"ROWS","startIndex":r,"endIndex":r+1},
                     "properties":{"pixelSize":36 if r==0 else 28},"fields":"pixelSize"}}])
    req.append({"updateSheetProperties":{"properties":{"sheetId":sid,"gridProperties":{"frozenRowCount":5}},"fields":"gridProperties.frozenRowCount"}})
    svc.batchUpdate(spreadsheetId=spreadsheet_id,body={"requests":req}).execute()
    m.write_values(spreadsheet_id,f"'{m.SHEET_TITLE}'!A1",[
        [f"APSRTC — {display} DEPOT"],
        [f"ANNUAL KPI — Reporting through {period_label(REPORT_MONTH)}"],
        [f"FY {fys[0]} / {fys[1]}: full year. FY {fys[-1]}: selected-month YTD. Blank = unavailable."]])


def _prepare_live_detail_sheet(spreadsheet_id):
    """Make reruns idempotent and return the detailed sheet to v7's internal name."""
    svc = m.sheets_service()
    meta = svc.spreadsheets().get(spreadsheetId=spreadsheet_id).execute()
    by_title = {s["properties"]["title"]: s for s in meta.get("sheets", [])}
    detail=by_title.get(m.SHEET_TITLE) or by_title.get(DETAIL_TITLE)
    if detail:
        title=detail["properties"]["title"]; sid=detail["properties"]["sheetId"]
        top=m.read_values(spreadsheet_id,f"'{title}'!A1:B5")
        if top and str(top[0][0]).startswith("APSRTC") and len(top)>4 and top[4] and top[4][0]=="SL.No":
            svc.spreadsheets().batchUpdate(spreadsheetId=spreadsheet_id,body={"requests":[
                {"updateSheetProperties":{"properties":{"sheetId":sid,"gridProperties":{"frozenRowCount":0,"frozenColumnCount":0}},"fields":"gridProperties.frozenRowCount,gridProperties.frozenColumnCount"}},
                {"deleteDimension":{"range":{"sheetId":sid,"dimension":"ROWS","startIndex":0,"endIndex":4}}}
            ]}).execute()
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
    requests.insert(0,{"repeatCell":{"range":{"sheetId":sid,"startRowIndex":0,"endRowIndex":row_count,"startColumnIndex":0,"endColumnIndex":18},
        "cell":{"userEnteredFormat":{"textFormat":{"fontFamily":"Arial","fontSize":10,"foregroundColor":medium},"verticalAlignment":"MIDDLE","wrapStrategy":"WRAP"}},
        "fields":"userEnteredFormat.textFormat,userEnteredFormat.verticalAlignment,userEnteredFormat.wrapStrategy"}})
    for idx,row in enumerate(mat[1:],1):
        height=58 if any("MANUAL" in str(v) for v in row) else 30
        requests.append({"updateDimensionProperties":{"range":{"sheetId":sid,"dimension":"ROWS","startIndex":idx,"endIndex":idx+1},"properties":{"pixelSize":height},"fields":"pixelSize"}})
    widths = [(0, 1, 58), (1, 2, 235), (2, 3, 82), (3, 4, 76), (4, 16, 72), (16,17,20), (17,18,90)]
    requests.append({"updateDimensionProperties":{"range":{"sheetId":sid,"dimension":"COLUMNS",
        "startIndex":16,"endIndex":17},"properties":{"hiddenByUser":True},"fields":"hiddenByUser"}})
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
            # History and metadata are durable storage, not presentation tabs.
            # Hide legacy tabs as well: formatting must never delete user history.
            requests.append({"updateSheetProperties": {"properties": {"sheetId": sid, "hidden": True},
                                                        "fields": "hidden"}})
    svc.spreadsheets().batchUpdate(spreadsheetId=spreadsheet_id, body={"requests": requests}).execute()


ORIGINAL_V7_MAIN=v7.main

def main_v11():
    """Reuse persistent history and render the selected month into two visible tabs."""
    args=sys.argv[1:]
    def _arg(name, default=""):
        try: return args[args.index(name)+1]
        except (ValueError,IndexError): return default
    global REPORT_MONTH
    depot=_arg("--depot"); selected=_arg("--selected-month")
    REPORT_MONTH=selected
    datetime.strptime(selected,'%Y-%m')
    sy,sm=map(int,selected.split('-'))
    fys=m.fy_triplet(sy,sm)
    vehicle,display,region=m.core.depot_info(depot)
    folder=os.getenv('KPI_DRIVE_FOLDER_ID',m.core.DEFAULT_DRIVE_FOLDER)
    name=f'{display}_ANNUAL_KPI_DASHBOARD'
    existing=m.find_file(folder,name)
    cache=history.new_cache(display)
    if existing:
        sid=existing['id']
        meta=m.sheets_service().spreadsheets().get(spreadsheetId=sid).execute()
        titles={s['properties']['title'] for s in meta.get('sheets',[])}
        if history.CACHE_TITLE in titles:
            # Read errors or invalid caches fail closed. Never fall back to a rebuild.
            cache=history.decode(m.read_values(sid,f"'{history.CACHE_TITLE}'!A:D"),display)
        else:
            title=DETAIL_TITLE if DETAIL_TITLE in titles else m.SHEET_TITLE
            values=m.read_values(sid,f"'{title}'!A:R")
            previous=history.period_from_heading(values)
            if not previous and m.META_TITLE in titles:
                pairs=m.read_values(sid,f"'{m.META_TITLE}'!A:B")
                previous=dict(r[:2] for r in pairs if len(r)>=2).get('LAST_SELECTED_MONTH','')
            history.migrate(cache,values,previous)
            print('HISTORY MIGRATED: existing monthly values retained without a full rebuild')
    else:
        empty=m.new_store(fys); m.seed(empty)
        xlsx=make_xlsx_v11(display,v7.matrix_with_target(empty),fys)
        existing=m.upload_xlsx_as_google_sheet(xlsx,folder,name)
        sid=existing['id']
    last_saved=None
    def save_cache():
        nonlocal last_saved
        rows=history.encode(cache)
        if rows==last_saved: return
        hid=m.ensure_hidden_sheet(sid,history.CACHE_TITLE)
        m.sheets_service().spreadsheets().batchUpdate(spreadsheetId=sid,body={'requests':[
            {'updateSheetProperties':{'properties':{'sheetId':hid,'hidden':True,
                'gridProperties':{'rowCount':max(1000,len(rows)+10),'columnCount':4}},
                'fields':'hidden,gridProperties.rowCount,gridProperties.columnCount'}}]}).execute()
        # One atomic values update, with a length and checksum. Stale trailing chunks are ignored.
        m.write_values(sid,f"'{history.CACHE_TITLE}'!A1",rows)
        last_saved=rows
    # Persist migrated history BEFORE changing the visible report or contacting APSRTC.
    save_cache()
    session=None
    def get_session():
        nonlocal session
        if session is None: session=m.login()
        return session
    def fetch(group,period):
        y,mo=map(int,period.split('-')); s=get_session()
        if group=='PRODUCT': return m.fetch_dimension(s,'prodkmpl_um.php','PRODUCT','PRODUCT',display,region,y,mo)
        if group=='ENGINE': return m.fetch_dimension(s,'engkmpl_um.php','ENGINE TYPE','ENGINE',display,region,y,mo)
        if group=='TYRE': return v10.fetch_tyre_v10(s,display,y,mo,True)
        funcs={'HSD':m.fetch_hsd,'LUB':m.fetch_lub,'BD':m.fetch_bd,'MED':m.fetch_med,'SPRING':m.fetch_spring}
        return funcs[group](s,display,vehicle,region,y,mo)
    history.update(cache,fys,selected,fetch,save_cache)
    for fy in fys:
        if fy in cache['target_attempts']: continue
        target_store=m.new_store([fy]); m.seed(target_store)
        # Targets only, once per FY. Do not invoke v10's all-month backfill wrapper.
        v10.ORIGINAL_POPULATE_TARGETS(target_store,get_session(),display,vehicle,region,sy,sm)
        cache['targets'][fy]={k:v[fy]['target'] for k,v in target_store['rows'].items() if history.good(v[fy].get('target'))}
        cache['target_attempts'].append(fy)
        save_cache()
    st=history.view_store(cache,fys,selected,m)
    mat=v7.matrix_with_target(st)
    make_xlsx_v11(display,mat,fys)
    format_sheet_v11(sid,mat,fys)
    _style_live_detail(sid,mat)
    _ensure_dashboard_google_sheet(sid,display,fys,mat)
    _add_live_identity(sid,display,fys)
    m.ensure_hidden_sheet(sid,m.META_TITLE)
    m.write_values(sid,f"'{m.META_TITLE}'!A1",[['KEY','VALUE'],['DEPOT',display],
        ['LAST_SELECTED_MONTH',selected],['LAYOUT_VERSION',LAYOUT_VERSION],['HISTORY_SCHEMA',history.SCHEMA]])
    _finalize_live_workbook(sid)
    print(f'ANNUAL_KPI_DASHBOARD_SUCCESS: https://docs.google.com/spreadsheets/d/{sid}/edit')
    print(f'GOOGLE_SHEET_ID: {sid}')
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main_v11())
    except Exception as exc:
        print(f"ANNUAL_KPI_FAILURE: {exc}")
        raise
