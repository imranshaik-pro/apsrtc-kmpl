#!/usr/bin/env python3
"""Annual KPI v4: strict Product/Engine dimensions, exact LUB POST, SL.No, stale-row cleanup."""
import re
from bs4 import BeautifulSoup
import annual_kpi_runner_v3 as m

# Dashboard layout: SL.No before KPI.
m.HEADERS = ["SL.No", "KPI", "Year"] + m.MONTHS + ["", "Upto"]


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
            if not name or "TOTAL" in normalized or not re.search(r"[A-Za-z]", name):
                continue
            out[f"{prefix}: {name}"] = {"month": m.num(cells[3]), "upto": m.num(cells[6])}
    return out


def strict_valid_dynamic(name):
    if not (name.startswith("PRODUCT:") or name.startswith("ENGINE:")):
        return True
    raw = name.split(":", 1)[1].strip()
    return bool(re.search(r"[A-Za-z]", raw)) and "TOTAL" not in m.n(raw)


def exact_lub_html(s, y, month):
    """APSRTC lub_rgn_rpt.php authoritative request contract: POST dt=Month_Year."""
    wanted = f"{m.datetime(y, month, 1).strftime('%B')}_{y}"
    url = f"{m.core.MED_BASE}/lub_rgn_rpt.php"
    rr = s.post(url, data={"dt": wanted}, headers={"Content-Type": "application/x-www-form-urlencoded"}, timeout=45)
    rr.raise_for_status()
    if "<table" not in rr.text.lower():
        raise RuntimeError("LUB report returned no table")
    if not m.page_month(rr.text, y, month):
        raise RuntimeError(f"LUB POST dt month not verified: {wanted}")
    print(f"LUB POST verified {wanted} using field: dt")
    return rr.text


def matrix_with_serial(st):
    m.reorder(st)
    out = [m.HEADERS]
    serial = 0
    for name in st["order"]:
        serial += 1
        for j, fy in enumerate(st["fys"]):
            v = st["rows"][name][fy]
            out.append([
                serial if j == 0 else "",
                name if j == 0 else "",
                fy,
                *[v["months"].get(mon, "") for mon in m.MONTHS],
                "",
                v["upto"] if v["upto"] is not None else "",
            ])
    return out


def load_existing_shifted(values, fys):
    st = m.new_store(fys)
    current = None
    for row in values[1:] if values else []:
        if len(row) > 1 and str(row[1]).strip():
            candidate = str(row[1]).strip()
            current = candidate if strict_valid_dynamic(candidate) else None
            if current:
                m.ensure(st, current)
        if not current or len(row) < 3 or str(row[2]).strip() not in fys:
            continue
        fy = str(row[2]).strip()
        for i, mon in enumerate(m.MONTHS):
            c = 3 + i
            if c < len(row) and str(row[c]).strip() != "":
                st["rows"][current][fy]["months"][mon] = row[c]
        if len(row) > 16 and str(row[16]).strip() != "":
            st["rows"][current][fy]["upto"] = row[16]
    m.seed(st)
    return st


def make_xlsx_17(display, mat, fys):
    path = m.REPORTS / f"{display}_ANNUAL_KPI_DASHBOARD.xlsx"
    wb = m.Workbook(); ws = wb.active; ws.title = m.SHEET_TITLE
    for r in mat: ws.append(r)
    thin=m.Side(style="thin"); border=m.Border(left=thin,right=thin,top=thin,bottom=thin); fill=m.PatternFill("solid",fgColor="1F4E78"); colors=["1F4E79","008000","C00000"]
    for c in range(1,18):
        ws.cell(1,c).font=m.Font(bold=True,color="FFFFFF"); ws.cell(1,c).fill=fill; ws.cell(1,c).alignment=m.Alignment(horizontal="center")
    for r in range(2,ws.max_row+1):
        fy=str(ws.cell(r,3).value or ""); color=colors[fys.index(fy)] if fy in fys else "000000"
        for c in range(1,18):
            ws.cell(r,c).border=border; ws.cell(r,c).alignment=m.Alignment(horizontal="center",vertical="center"); ws.cell(r,c).font=m.Font(color=color)
    for r in range(2,ws.max_row+1,3):
        end=min(r+2,ws.max_row)
        ws.merge_cells(start_row=r,start_column=1,end_row=end,end_column=1)
        ws.merge_cells(start_row=r,start_column=2,end_row=end,end_column=2)
        ws.cell(r,1).font=m.Font(bold=True,color="000000"); ws.cell(r,2).font=m.Font(bold=True,color="000000")
    ws.column_dimensions[m.get_column_letter(1)].width=8; ws.column_dimensions[m.get_column_letter(2)].width=28; ws.column_dimensions[m.get_column_letter(3)].width=12
    for c in range(4,16): ws.column_dimensions[m.get_column_letter(c)].width=11
    ws.column_dimensions[m.get_column_letter(16)].width=3; ws.column_dimensions[m.get_column_letter(17)].width=12
    ws.freeze_panes="D2"; wb.save(path); return path


def clean_format_sheet_17(spreadsheet_id, mat, fys):
    sid=m.sheet_id(spreadsheet_id,m.SHEET_TITLE); svc=m.sheets_service(); maxr=max(1000,len(mat)+100)
    svc.spreadsheets().batchUpdate(spreadsheetId=spreadsheet_id,body={"requests":[
        {"unmergeCells":{"range":{"sheetId":sid,"startRowIndex":1,"endRowIndex":maxr,"startColumnIndex":0,"endColumnIndex":2}}},
        {"updateCells":{"range":{"sheetId":sid,"startRowIndex":0,"endRowIndex":maxr,"startColumnIndex":0,"endColumnIndex":17},"fields":"userEnteredValue"}}
    ]}).execute()
    m.write_values(spreadsheet_id,f"'{m.SHEET_TITLE}'!A1",mat)
    req=[]; colors=[{"red":.12,"green":.31,"blue":.48},{"red":0,"green":.5,"blue":0},{"red":.75,"green":0,"blue":0}]
    req.append({"repeatCell":{"range":{"sheetId":sid,"startRowIndex":0,"endRowIndex":1,"startColumnIndex":0,"endColumnIndex":17},"cell":{"userEnteredFormat":{"backgroundColor":{"red":.12,"green":.31,"blue":.47},"textFormat":{"bold":True,"foregroundColor":{"red":1,"green":1,"blue":1}},"horizontalAlignment":"CENTER"}},"fields":"userEnteredFormat"}})
    for r in range(1,len(mat)):
        fy=str(mat[r][2]); color=colors[fys.index(fy)]
        req.append({"repeatCell":{"range":{"sheetId":sid,"startRowIndex":r,"endRowIndex":r+1,"startColumnIndex":2,"endColumnIndex":17},"cell":{"userEnteredFormat":{"textFormat":{"foregroundColor":color},"horizontalAlignment":"CENTER","verticalAlignment":"MIDDLE"}},"fields":"userEnteredFormat(textFormat.foregroundColor,horizontalAlignment,verticalAlignment)"}})
    for r in range(1,len(mat),3):
        end=min(r+3,len(mat))
        for c in (0,1):
            req.append({"mergeCells":{"range":{"sheetId":sid,"startRowIndex":r,"endRowIndex":end,"startColumnIndex":c,"endColumnIndex":c+1},"mergeType":"MERGE_ALL"}})
            req.append({"repeatCell":{"range":{"sheetId":sid,"startRowIndex":r,"endRowIndex":end,"startColumnIndex":c,"endColumnIndex":c+1},"cell":{"userEnteredFormat":{"textFormat":{"bold":True,"foregroundColor":{"red":0,"green":0,"blue":0}},"horizontalAlignment":"CENTER","verticalAlignment":"MIDDLE"}},"fields":"userEnteredFormat(textFormat,horizontalAlignment,verticalAlignment)"}})
    widths=[65,240,95]+[85]*12+[20,95]
    for i,w in enumerate(widths): req.append({"updateDimensionProperties":{"range":{"sheetId":sid,"dimension":"COLUMNS","startIndex":i,"endIndex":i+1},"properties":{"pixelSize":w},"fields":"pixelSize"}})
    req.append({"updateSheetProperties":{"properties":{"sheetId":sid,"gridProperties":{"frozenRowCount":1,"frozenColumnCount":3}},"fields":"gridProperties.frozenRowCount,gridProperties.frozenColumnCount"}})
    svc.spreadsheets().batchUpdate(spreadsheetId=spreadsheet_id,body={"requests":req}).execute()


m.direct_dimension_rows = strict_dimension_rows
m.valid_dynamic = strict_valid_dynamic
m.lub_html = exact_lub_html
m.matrix = matrix_with_serial
m.load_existing = load_existing_shifted
m.make_xlsx = make_xlsx_17
m.format_sheet = clean_format_sheet_17

if __name__ == "__main__":
    try:
        raise SystemExit(m.main())
    except Exception as exc:
        print(f"ANNUAL_KPI_FAILURE: {exc}")
        raise
