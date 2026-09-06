#!/usr/bin/env python3
"""Annual KPI v7: add source-grounded Target column.

Target rules:
- HSD KMPL INCL AC / EXCL AC: exact selected-depot target from mth_acnac_dpt.php.
- Tyre KPIs: exact selected-depot target only, from tyre web tables when a target
  column exists, or from FY2024-25 booklet only when the same target table has the
  exact depot row (e.g. PDTR). Never substitute district/zone/corporation targets.
- All remaining KPI target cells stay blank.
"""
import argparse, io, os, re, sys
from calendar import monthrange
from datetime import datetime

import pdfplumber
import annual_kpi_runner_v6 as v6

m = v6.m
v5 = v6.v5
LAYOUT_VERSION = "7"
TARGET_KPIS = {"HSD KMPL INCL AC", "HSD KMPL EXCL AC", *m.TYRE}


def _target_header_index(headers, required, reject=()):
    for i, h in enumerate(headers or []):
        nh = m.n(h)
        if "TARGET" not in nh:
            continue
        if all(m.n(x) in nh for x in required) and not any(m.n(x) in nh for x in reject):
            return i
    return None


def hsd_targets(s, display, vehicle, region, y, month):
    last = monthrange(y, month)[1]
    html = m.get_html(s, m.core.MED_BASE, "mth_acnac_dpt.php", {
        "action": "", "fdate": f"{last:02d}/{month:02d}/{y}", "dist": m.district(region)
    })
    h, row = m.find_depot(html, display, vehicle, ["WITH AC KMPL", "WITHOUT AC KMPL"])
    if not row:
        return {}
    wi = _target_header_index(h, ["WITH AC KMPL"], ["WITHOUT"])
    ni = _target_header_index(h, ["WITHOUT AC KMPL"])
    out = {}
    if wi is not None:
        out["HSD KMPL INCL AC"] = m.at(row, wi)
    if ni is not None:
        out["HSD KMPL EXCL AC"] = m.at(row, ni)
    print(f"HSD targets {display} {y:04d}-{month:02d}: INCL={out.get('HSD KMPL INCL AC')} EXCL={out.get('HSD KMPL EXCL AC')}")
    return out


def _row_value_target(headers, row, aliases):
    """Return a value only from a header that explicitly contains TARGET."""
    for i, h in enumerate(headers or []):
        nh = m.n(h)
        if "TARGET" not in nh:
            continue
        for alias in aliases:
            na = m.n(alias)
            if na in nh or all(tok in nh for tok in na.split()):
                return m.at(row, i)
    return None


def tyre_targets_web(s, depot, y, month):
    """Exact selected-depot targets from tyre web row; blank if target columns absent."""
    try:
        h, row = m.tyre_page(s, "d_statement_final.php", depot, y, month)
    except Exception as exc:
        print(f"TYRE target web {y:04d}-{month:02d}: {exc}")
        return {}
    if not row:
        return {}
    raw = {
        "NEW TYRE LIFE": _row_value_target(h, row, ["NEW MILEAGE"]),
        "RC TYRE LIFE": _row_value_target(h, row, ["RC MILEAGE", "RC_MILEAGE"]),
        "AVG TYRE LIFE": _row_value_target(h, row, ["AVG TOTAL MILEAGE", "AVG_TOTAL MILEAGE"]),
        "N.T.S RATE": _row_value_target(h, row, ["NEW TYRE %", "NEW %"]),
        "Ist RC S Rate": _row_value_target(h, row, ["IST RC %"]),
        "TTL SCP Rate": _row_value_target(h, row, ["TOTAL %"]),
        "RT Factor": _row_value_target(h, row, ["RT FACTOR", "RT_FACTOR"]),
    }
    out = {}
    for k, v in raw.items():
        if v is None:
            continue
        if k in {"NEW TYRE LIFE", "RC TYRE LIFE", "AVG TYRE LIFE"}:
            v = v / 100000.0
        out[k] = v
    if out:
        print(f"TYRE web targets {depot} {y:04d}-{month:02d}: {out}")
    else:
        print(f"TYRE web targets {depot} {y:04d}-{month:02d}: no explicit depot TARGET columns")
    return out


def _nums(s):
    return [float(x) for x in re.findall(r"-?\d+(?:\.\d+)?", s or "")]


def tyre_targets_pdf_2024(s, depot):
    """Use Apr-2024 booklet, but only if a TARGET table itself contains exact depot row."""
    code = v6.PDF_DEPOT_CODE.get(m.n(depot))
    if not code:
        return {}
    url = f"{m.core.MED_BASE}/trs_booklet/2024-25/apr-2024.pdf"
    rr = s.get(url, timeout=60); rr.raise_for_status()
    if not rr.content.startswith(b"%PDF"):
        return {}
    out = {}
    with pdfplumber.open(io.BytesIO(rr.content)) as pdf:
        for page_no, page in enumerate(pdf.pages, start=1):
            text = page.extract_text() or ""
            nt = m.n(text)
            if "TARGET" not in nt:
                continue
            # Safety rule: do not use district target page unless exact depot code is present there.
            line = v6._line_for_code(text, code)
            if not line:
                continue
            vals = _nums(line[len(code):])
            # Supported only when table headings prove KPI identity and row begins with target.
            if "NEW TYRE LIFE" in nt and "RC TYRE LIFE" in nt and "TOTAL TYRE LIFE" in nt and len(vals) >= 3:
                out["NEW TYRE LIFE"] = vals[0]
                out["RC TYRE LIFE"] = vals[1]
                out["AVG TYRE LIFE"] = vals[2]
            if "NEW TYRE SCRAP RATE" in nt and "1ST RC SCRAP RATE" in nt and "TOTAL SCRAP RATE" in nt and "RT FACTOR" in nt and len(vals) >= 4:
                out["N.T.S RATE"] = vals[0]
                out["Ist RC S Rate"] = vals[1]
                out["TTL SCP Rate"] = vals[2]
                out["RT Factor"] = vals[3]
            if out:
                print(f"TYRE PDF depot targets {depot}/{code} p{page_no}: {out}")
    if not out:
        print(f"TYRE PDF target 2024-25 {depot}/{code}: no exact depot TARGET row found; target cells left blank")
    return out


def ensure_target_slots(st):
    for name in st["order"]:
        for fy in st["fys"]:
            st["rows"][name][fy].setdefault("target", None)


def populate_targets(st, s, display, vehicle, region, sy, sm):
    ensure_target_slots(st)
    for fy in st["fys"]:
        start_y, _ = m.core.parse_fy(fy)
        # Target is an FY attribute. Prefer April of that FY; if current FY April is unavailable,
        # selected month is the fallback source month, still using explicit TARGET columns only.
        source_y, source_m = start_y, 4
        try:
            ht = hsd_targets(s, display, vehicle, region, source_y, source_m)
        except Exception as exc:
            print(f"HSD target {fy}: {exc}"); ht = {}
        for k, v in ht.items():
            if k in st["rows"]:
                st["rows"][k][fy]["target"] = v

        if fy == "2024-25":
            try:
                tt = tyre_targets_pdf_2024(s, display)
            except Exception as exc:
                print(f"TYRE PDF target {fy}: {exc}"); tt = {}
        else:
            try:
                tt = tyre_targets_web(s, display, source_y, source_m)
            except Exception as exc:
                print(f"TYRE web target {fy}: {exc}"); tt = {}
        for k, v in tt.items():
            if k in st["rows"]:
                st["rows"][k][fy]["target"] = v


def matrix_with_target(st):
    m.reorder(st); ensure_target_slots(st)
    headers = ["SL.No", "KPI", "Year", "Target"] + m.MONTHS + ["", "Upto"]
    out = [headers]
    serial = 0
    for name in st["order"]:
        serial += 1
        for j, fy in enumerate(st["fys"]):
            v = st["rows"][name][fy]
            target = v.get("target") if name in TARGET_KPIS else None
            out.append([
                serial if j == 0 else "",
                name if j == 0 else "",
                fy,
                target if target is not None else "",
                *[v["months"].get(mon, "") for mon in m.MONTHS],
                "",
                v["upto"] if v["upto"] is not None else "",
            ])
    return out


def load_existing_v7(values, fys):
    st = m.new_store(fys); m.seed(st); ensure_target_slots(st)
    current = None
    for row in values[1:] if values else []:
        if len(row) > 1 and str(row[1]).strip():
            cand = str(row[1]).strip()
            current = cand if v6.v5.v4.strict_valid_dynamic(cand) else None
            if current:
                m.ensure(st, current)
                for fy in fys: st["rows"][current][fy].setdefault("target", None)
        if not current or len(row) < 4 or str(row[2]).strip() not in fys:
            continue
        fy = str(row[2]).strip()
        if str(row[3]).strip() != "": st["rows"][current][fy]["target"] = row[3]
        for i, mon in enumerate(m.MONTHS):
            c = 4 + i
            if c < len(row) and str(row[c]).strip() != "": st["rows"][current][fy]["months"][mon] = row[c]
        if len(row) > 17 and str(row[17]).strip() != "": st["rows"][current][fy]["upto"] = row[17]
    return st


def make_xlsx_v7(display, mat, fys):
    from openpyxl import Workbook
    from openpyxl.styles import Alignment, Border, Font, PatternFill, Side
    from openpyxl.utils import get_column_letter
    path = m.REPORTS / f"{display}_ANNUAL_KPI_DASHBOARD.xlsx"
    wb=Workbook(); ws=wb.active; ws.title=m.SHEET_TITLE
    for r in mat: ws.append(r)
    thin=Side(style="thin"); border=Border(left=thin,right=thin,top=thin,bottom=thin); fill=PatternFill("solid",fgColor="1F4E78"); colors=["1F4E79","008000","C00000"]
    for c in range(1,19):
        ws.cell(1,c).font=Font(bold=True,color="FFFFFF"); ws.cell(1,c).fill=fill; ws.cell(1,c).alignment=Alignment(horizontal="center")
    for r in range(2,ws.max_row+1):
        fy=str(ws.cell(r,3).value or ""); color=colors[fys.index(fy)] if fy in fys else "000000"
        for c in range(1,19):
            ws.cell(r,c).border=border; ws.cell(r,c).alignment=Alignment(horizontal="center",vertical="center"); ws.cell(r,c).font=Font(color=color)
        block_start=r-((r-2)%3); kpi=str(ws.cell(block_start,2).value or "")
        pattern="0" if kpi=="TOTAL LUB KMPL" else "0.00"
        for c in [4]+list(range(5,17))+[18]: ws.cell(r,c).number_format=pattern
    for r in range(2,ws.max_row+1,3):
        end=min(r+2,ws.max_row)
        for c in (1,2): ws.merge_cells(start_row=r,start_column=c,end_row=end,end_column=c)
        ws.cell(r,1).font=Font(bold=True,color="000000"); ws.cell(r,2).font=Font(bold=True,color="000000")
    widths=[8,28,12,11]+[11]*12+[3,12]
    for i,w in enumerate(widths,1): ws.column_dimensions[get_column_letter(i)].width=w
    ws.freeze_panes="E2"; wb.save(path); return path


def format_sheet_v7(spreadsheet_id, mat, fys):
    sid=m.sheet_id(spreadsheet_id,m.SHEET_TITLE); svc=m.sheets_service(); maxr=max(1000,len(mat)+100)
    svc.spreadsheets().batchUpdate(spreadsheetId=spreadsheet_id,body={"requests":[
        {"unmergeCells":{"range":{"sheetId":sid,"startRowIndex":1,"endRowIndex":maxr,"startColumnIndex":0,"endColumnIndex":2}}},
        {"updateCells":{"range":{"sheetId":sid,"startRowIndex":0,"endRowIndex":maxr,"startColumnIndex":0,"endColumnIndex":18},"fields":"userEnteredValue"}}
    ]}).execute()
    m.write_values(spreadsheet_id,f"'{m.SHEET_TITLE}'!A1",mat)
    req=[]; colors=[{"red":.12,"green":.31,"blue":.48},{"red":0,"green":.5,"blue":0},{"red":.75,"green":0,"blue":0}]
    req.append({"repeatCell":{"range":{"sheetId":sid,"startRowIndex":0,"endRowIndex":1,"startColumnIndex":0,"endColumnIndex":18},"cell":{"userEnteredFormat":{"backgroundColor":{"red":.12,"green":.31,"blue":.47},"textFormat":{"bold":True,"foregroundColor":{"red":1,"green":1,"blue":1}},"horizontalAlignment":"CENTER"}},"fields":"userEnteredFormat"}})
    for r in range(1,len(mat)):
        fy=str(mat[r][2]); color=colors[fys.index(fy)]; block_start=r-((r-1)%3); kpi=str(mat[block_start][1]); pattern="0" if kpi=="TOTAL LUB KMPL" else "0.00"
        req.append({"repeatCell":{"range":{"sheetId":sid,"startRowIndex":r,"endRowIndex":r+1,"startColumnIndex":2,"endColumnIndex":18},"cell":{"userEnteredFormat":{"textFormat":{"foregroundColor":color},"horizontalAlignment":"CENTER","verticalAlignment":"MIDDLE"}},"fields":"userEnteredFormat(textFormat.foregroundColor,horizontalAlignment,verticalAlignment)"}})
        for c0,c1 in ((3,16),(17,18)):
            req.append({"repeatCell":{"range":{"sheetId":sid,"startRowIndex":r,"endRowIndex":r+1,"startColumnIndex":c0,"endColumnIndex":c1},"cell":{"userEnteredFormat":{"numberFormat":{"type":"NUMBER","pattern":pattern}}},"fields":"userEnteredFormat.numberFormat"}})
    for r in range(1,len(mat),3):
        end=min(r+3,len(mat))
        for c in (0,1):
            req.append({"mergeCells":{"range":{"sheetId":sid,"startRowIndex":r,"endRowIndex":end,"startColumnIndex":c,"endColumnIndex":c+1},"mergeType":"MERGE_ALL"}})
            req.append({"repeatCell":{"range":{"sheetId":sid,"startRowIndex":r,"endRowIndex":end,"startColumnIndex":c,"endColumnIndex":c+1},"cell":{"userEnteredFormat":{"textFormat":{"bold":True,"foregroundColor":{"red":0,"green":0,"blue":0}},"horizontalAlignment":"CENTER","verticalAlignment":"MIDDLE"}},"fields":"userEnteredFormat(textFormat,horizontalAlignment,verticalAlignment)"}})
    widths=[65,240,95,85]+[85]*12+[20,95]
    for i,w in enumerate(widths): req.append({"updateDimensionProperties":{"range":{"sheetId":sid,"dimension":"COLUMNS","startIndex":i,"endIndex":i+1},"properties":{"pixelSize":w},"fields":"pixelSize"}})
    req.append({"updateSheetProperties":{"properties":{"sheetId":sid,"gridProperties":{"frozenRowCount":1,"frozenColumnCount":4}},"fields":"gridProperties.frozenRowCount,gridProperties.frozenColumnCount"}})
    svc.spreadsheets().batchUpdate(spreadsheetId=spreadsheet_id,body={"requests":req}).execute()


def meta_version(spreadsheet_id):
    try:
        vals=m.read_values(spreadsheet_id,f"'{m.META_TITLE}'!A:B"); d={str(r[0]):str(r[1]) for r in vals[1:] if len(r)>=2}; return d.get("LAYOUT_VERSION","")
    except Exception: return ""


def main():
    p=argparse.ArgumentParser(); p.add_argument("--depot",required=True); p.add_argument("--selected-month",required=True); p.add_argument("--years",default=""); a=p.parse_args()
    sy,sm=map(int,a.selected_month.split("-")); datetime(sy,sm,1)
    fys=m.fy_triplet(sy,sm); vehicle,display,region=m.core.depot_info(a.depot); folder=os.getenv("KPI_DRIVE_FOLDER_ID",m.core.DEFAULT_DRIVE_FOLDER); name=f"{display}_ANNUAL_KPI_DASHBOARD"; existing=m.find_file(folder,name)
    repair=(not existing) or meta_version(existing["id"])!=LAYOUT_VERSION
    st=m.new_store(fys); m.seed(st) if repair else None
    if not repair:
        st=load_existing_v7(m.read_values(existing["id"],f"'{m.SHEET_TITLE}'!A:R"),fys)
    s=m.login()
    if repair:
        print(f"FULL REPAIR/BUILD {display}: {', '.join(fys)}")
        for fy in fys:
            months=m.fy_months(fy,sy,sm)
            for i,(y,mon) in enumerate(months):
                need=i==len(months)-1; print(f"FETCH {fy} {y:04d}-{mon:02d}{' + Upto' if need else ''}")
                m.apply(st,fy,y,mon,m.fetch_month(s,display,vehicle,region,y,mon,need),need,True)
    else:
        fy=m.selected_fy(sy,sm); print(f"INCREMENTAL {display} {a.selected_month}")
        m.apply(st,fy,sy,sm,m.fetch_month(s,display,vehicle,region,sy,sm,True),True,False)
    populate_targets(st,s,display,vehicle,region,sy,sm)
    mat=matrix_with_target(st); xlsx=make_xlsx_v7(display,mat,fys)
    if not existing:
        up=m.upload_xlsx_as_google_sheet(xlsx,folder,name); sid=up["id"]; link=up.get("webViewLink","")
    else:
        sid=existing["id"]; link=existing.get("webViewLink","")
    format_sheet_v7(sid,mat,fys); m.ensure_hidden_sheet(sid,m.META_TITLE)
    m.write_values(sid,f"'{m.META_TITLE}'!A1",[["KEY","VALUE"],["DEPOT",display],["FYS",','.join(fys)],["LAST_SELECTED_MONTH",a.selected_month],["LAYOUT_VERSION",LAYOUT_VERSION]])
    print(f"ANNUAL_KPI_DASHBOARD_SUCCESS: {link}"); print(f"GOOGLE_SHEET_ID: {sid}"); return 0

if __name__=="__main__":
    try: sys.exit(main())
    except Exception as exc: print(f"ANNUAL_KPI_FAILURE: {exc}"); raise
