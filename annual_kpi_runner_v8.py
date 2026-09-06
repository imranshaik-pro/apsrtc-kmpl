#!/usr/bin/env python3
"""Annual KPI v8 target expansion + exact depot-wise LUB parsing.

Target rules:
- Targets are FY attributes and are fetched from APRIL of each FY only.
- HSD KMPL INCL AC / EXCL AC
- B.D RATE
- MED CANCL.
- SPRING CONS
- tyre KPIs where an exact-depot target exists
All other KPI target cells remain blank.

LUB rule:
- submit the site's own month form and verify the returned report month
- select ONLY the DEPOT-WISE LUB KMPL table
- select the exact depot row (e.g. PRODDUTUR)
- monthly = For the Month CY -> Total Lub KMPL
- upto = Upto the Month CY -> Total Lub KMPL
"""
import sys
from datetime import datetime
from urllib.parse import urljoin
from bs4 import BeautifulSoup
import annual_kpi_runner_v7 as v7

m = v7.m
v5 = v7.v5
LAYOUT_VERSION = "8"
TARGET_KPIS = {"HSD KMPL INCL AC","HSD KMPL EXCL AC","B.D RATE","MED CANCL.","SPRING CONS",*m.TYRE}
v7.TARGET_KPIS = TARGET_KPIS


def _exact_target_from_page(s,base,path,params,display,vehicle,required):
    html=m.get_html(s,base,path,params)
    h,row=m.find_depot(html,display,vehicle,required)
    if not row:
        return None
    # APSRTC operational reports use a plain explicit depot-level Target column.
    # Do not require the KPI name to be repeated in that header.
    for i,header in enumerate(h or []):
        nh=m.n(header)
        if nh == "TARGET" or nh == "TGT" or "| TARGET" in nh or "TARGET |" in nh:
            return m.at(row,i)
    return None


def operational_targets(s,display,vehicle,region,y,month):
    out={}
    specs=[
      ("B.D RATE",m.core.MED_BASE,"sysbd_dpt.php",{"action":"","yymm":m.token(y,month),"dist":m.district(region)},["BD RATE"]),
      ("MED CANCL.",m.core.MEDNEW_BASE,"medcan_um_dpt.php",{"action":"","fdate":m.token(y,month,"-"),"dist":m.district(region)},["CANC"]),
      ("SPRING CONS","http://103.44.14.20/storeap","deptspring.php",{"action":"","yymm":m.token(y,month),"dist":m.district(region)},["SPRING CONSUMPTION PER LAKH KMS"])]
    for k,base,path,params,req in specs:
        try:
            val=_exact_target_from_page(s,base,path,params,display,vehicle,req)
            if val is not None:
                out[k]=val
        except Exception as exc:
            print(f"{k} target {y:04d}-{month:02d}: {exc}")
    print(f"Operational targets {display} {y:04d}-{month:02d}: {out}")
    return out


def _page_month(html,y,month):
    text=m.n(BeautifulSoup(html,"html.parser").get_text(" ",strip=True))
    mn=datetime(y,month,1).strftime("%B").upper()
    return any(x in text for x in (f"{mn}_{y}",f"{mn}-{y}",f"{mn} {y}"))


def _depot_row_has_data(html,display,vehicle):
    wanted={m.n(display),m.n(vehicle)}
    soup=BeautifulSoup(html,"html.parser")
    for table in soup.find_all("table"):
        text=m.n(table.get_text(" ",strip=True))
        if "DEPOT" not in text or "TOTAL LUB KMPL" not in text:
            continue
        try:
            headers,rows=m.core.expanded_headers(table)
            di=m.core.col(headers,["DEPOT","DEPOT NAME"])
        except Exception:
            continue
        if di is None:
            continue
        for row in rows:
            if di < len(row) and m.n(row[di]) in wanted:
                vals=[m.at(row,i) for i,h in enumerate(headers) if "TOTAL LUB KMPL" in m.n(h)]
                return row,vals
    return None,[]


def lub_html_v8(s,y,month,display=None,vehicle=None):
    url=f"{m.core.MED_BASE}/lub_rgn_rpt.php"
    wanted=f"{datetime(y,month,1).strftime('%B')}_{y}"
    landing=s.get(url,timeout=45)
    landing.raise_for_status()
    soup=BeautifulSoup(landing.text,"html.parser")

    # Reproduce the browser's own form submission, including named submit controls.
    candidates=[]
    for form in soup.find_all("form"):
        data={}
        found=False
        for inp in form.find_all("input"):
            name=inp.get("name")
            if name:
                data[name]=inp.get("value","")
        for sel in form.find_all("select"):
            name=sel.get("name")
            if not name:
                continue
            for opt in sel.find_all("option"):
                ov=opt.get("value","")
                ot=opt.get_text(" ",strip=True)
                if m.n(wanted) in {m.n(ov),m.n(ot)}:
                    data[name]=ov or ot
                    found=True
                    break
        if found:
            action=urljoin(url,form.get("action") or url)
            candidates.append((action,data,"site-form"))

    # Keep exact dt as a fallback because older APSRTC markup used it.
    candidates.append((url,{"dt":wanted},"dt-fallback"))

    best_zero=None
    for action,data,label in candidates:
        rr=s.post(action,data=data,timeout=45)
        rr.raise_for_status()
        if not _page_month(rr.text,y,month):
            continue
        row,vals=_depot_row_has_data(rr.text,display,vehicle) if display else (None,[])
        print(f"LUB POST verified {wanted} via {label}; fields={','.join(sorted(data))}; depot_totals={vals}")
        if not display:
            return rr.text
        if row is not None and any(v not in (None,0,0.0) for v in vals):
            return rr.text
        if row is not None:
            best_zero=rr.text
    if best_zero is not None:
        return best_zero
    raise RuntimeError(f"LUB POST month not verified: {wanted}")


def _pick_lub_column(headers,words):
    for i,h in enumerate(headers or []):
        nh=m.n(h)
        if "TOTAL LUB KMPL" in nh and all(w in nh for w in words):
            return i
    return None


def fetch_lub_depotwise(s,display,vehicle,region,y,month):
    html=lub_html_v8(s,y,month,display,vehicle)
    soup=BeautifulSoup(html,"html.parser")
    wanted={m.n(display),m.n(vehicle)}
    for table in soup.find_all("table"):
        text=m.n(table.get_text(" ",strip=True))
        if "DEPOT" not in text or "TOTAL LUB KMPL" not in text:
            continue
        headers,rows=m.core.expanded_headers(table)
        di=m.core.col(headers,["DEPOT","DEPOT NAME"])
        if di is None:
            continue
        row=next((r for r in rows if di<len(r) and m.n(r[di]) in wanted),None)
        if row is None:
            continue
        mi=_pick_lub_column(headers,["FOR","MONTH","CY"])
        ui=_pick_lub_column(headers,["UPTO","MONTH","CY"])
        totals=[i for i,h in enumerate(headers or []) if "TOTAL LUB KMPL" in m.n(h)]
        if mi is None and totals:
            mi=totals[0]
        if ui is None and len(totals)>=2:
            ui=totals[1]
        mv=m.at(row,mi)
        uv=m.at(row,ui)
        print(f"LUB depot-wise {display} {y:04d}-{month:02d}: month={mv} upto={uv}; total_cols={totals}")
        return {"TOTAL LUB KMPL":{"month":mv,"upto":uv}}
    raise RuntimeError(f"DEPOT-WISE LUB KMPL row not found for {display} {y:04d}-{month:02d}")


def populate_targets_v8(st,s,display,vehicle,region,sy,sm):
    v7.ensure_target_slots(st)
    for fy in st["fys"]:
        start_y,_=m.core.parse_fy(fy)
        y,mo=start_y,4
        try:
            ht=v7.hsd_targets(s,display,vehicle,region,y,mo)
        except Exception as exc:
            print(f"HSD target {fy}: {exc}")
            ht={}
        for k,val in ht.items():
            if k in st["rows"]:
                st["rows"][k][fy]["target"]=val
        ot=operational_targets(s,display,vehicle,region,y,mo)
        for k,val in ot.items():
            if k in st["rows"]:
                st["rows"][k][fy]["target"]=val
        try:
            tt=v7.tyre_targets_pdf_2024(s,display) if fy=="2024-25" else v7.tyre_targets_web(s,display,y,mo)
        except Exception as exc:
            print(f"TYRE target {fy}: {exc}")
            tt={}
        for k,val in tt.items():
            if k in st["rows"]:
                st["rows"][k][fy]["target"]=val

v7.populate_targets=populate_targets_v8
v7.LAYOUT_VERSION=LAYOUT_VERSION
m.lub_html=lambda s,y,month: lub_html_v8(s,y,month)
m.fetch_lub=fetch_lub_depotwise


def meta_version_v8(spreadsheet_id):
    try:
        vals=m.read_values(spreadsheet_id,f"'{m.META_TITLE}'!A:B")
        d={str(r[0]):str(r[1]) for r in vals[1:] if len(r)>=2}
        return d.get("LAYOUT_VERSION","")
    except Exception:
        return ""
v7.meta_version=meta_version_v8

if __name__=="__main__":
    try:
        sys.exit(v7.main())
    except Exception as exc:
        print(f"ANNUAL_KPI_FAILURE: {exc}")
        raise
