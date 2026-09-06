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
- POST dt=Month_Year to lub_rgn_rpt.php
- select ONLY the DEPOT-WISE LUB KMPL table
- select the exact depot row (e.g. PRODDUTUR)
- monthly = For the Month CY -> Total Lub KMPL
- upto = Upto the Month CY -> Total Lub KMPL
"""
import sys
from bs4 import BeautifulSoup
import annual_kpi_runner_v7 as v7

m = v7.m
v5 = v7.v5
LAYOUT_VERSION = "8"
TARGET_KPIS = {"HSD KMPL INCL AC","HSD KMPL EXCL AC","B.D RATE","MED CANCL.","SPRING CONS",*m.TYRE}
v7.TARGET_KPIS = TARGET_KPIS

def _exact_target_from_page(s,base,path,params,display,vehicle,required,header_match):
    html=m.get_html(s,base,path,params); h,row=m.find_depot(html,display,vehicle,required)
    if not row: return None
    for i,header in enumerate(h or []):
        nh=m.n(header)
        if ("TARGET" in nh or "TGT" in nh) and header_match(nh): return m.at(row,i)
    return None

def operational_targets(s,display,vehicle,region,y,month):
    out={}
    specs=[
      ("B.D RATE",m.core.MED_BASE,"sysbd_dpt.php",{"action":"","yymm":m.token(y,month),"dist":m.district(region)},["BD RATE"],lambda h:"BD RATE" in h or ("BD" in h and "RATE" in h)),
      ("MED CANCL.",m.core.MEDNEW_BASE,"medcan_um_dpt.php",{"action":"","fdate":m.token(y,month,"-"),"dist":m.district(region)},["CANC"],lambda h:"CANC" in h or "%" in h),
      ("SPRING CONS","http://103.44.14.20/storeap","deptspring.php",{"action":"","yymm":m.token(y,month),"dist":m.district(region)},["SPRING CONSUMPTION PER LAKH KMS"],lambda h:"SPRING" in h or "CONSUMPTION" in h)]
    for k,base,path,params,req,match in specs:
        try:
            val=_exact_target_from_page(s,base,path,params,display,vehicle,req,match)
            if val is not None: out[k]=val
        except Exception as exc: print(f"{k} target {y:04d}-{month:02d}: {exc}")
    print(f"Operational targets {display} {y:04d}-{month:02d}: {out}"); return out

def _pick_lub_column(headers,words):
    for i,h in enumerate(headers or []):
        nh=m.n(h)
        if "TOTAL LUB KMPL" in nh and all(w in nh for w in words): return i
    return None

def fetch_lub_depotwise(s,display,vehicle,region,y,month):
    html=m.lub_html(s,y,month); soup=BeautifulSoup(html,"html.parser"); wanted={m.n(display),m.n(vehicle)}
    for table in soup.find_all("table"):
        text=m.n(table.get_text(" ",strip=True))
        if "DEPOT" not in text or "TOTAL LUB KMPL" not in text: continue
        headers,rows=m.core.expanded_headers(table); di=m.core.col(headers,["DEPOT","DEPOT NAME"])
        if di is None: continue
        row=next((r for r in rows if di<len(r) and m.n(r[di]) in wanted),None)
        if row is None: continue
        mi=_pick_lub_column(headers,["FOR","MONTH","CY"]); ui=_pick_lub_column(headers,["UPTO","MONTH","CY"])
        totals=[i for i,h in enumerate(headers or []) if "TOTAL LUB KMPL" in m.n(h)]
        if mi is None and totals: mi=totals[0]
        if ui is None and len(totals)>=2: ui=totals[1]
        mv=m.at(row,mi); uv=m.at(row,ui)
        print(f"LUB depot-wise {display} {y:04d}-{month:02d}: month={mv} upto={uv}; total_cols={totals}")
        return {"TOTAL LUB KMPL":{"month":mv,"upto":uv}}
    raise RuntimeError(f"DEPOT-WISE LUB KMPL row not found for {display} {y:04d}-{month:02d}")

def populate_targets_v8(st,s,display,vehicle,region,sy,sm):
    v7.ensure_target_slots(st)
    for fy in st["fys"]:
        start_y,_=m.core.parse_fy(fy); y,mo=start_y,4
        try: ht=v7.hsd_targets(s,display,vehicle,region,y,mo)
        except Exception as exc: print(f"HSD target {fy}: {exc}"); ht={}
        for k,val in ht.items():
            if k in st["rows"]: st["rows"][k][fy]["target"]=val
        ot=operational_targets(s,display,vehicle,region,y,mo)
        for k,val in ot.items():
            if k in st["rows"]: st["rows"][k][fy]["target"]=val
        try: tt=v7.tyre_targets_pdf_2024(s,display) if fy=="2024-25" else v7.tyre_targets_web(s,display,y,mo)
        except Exception as exc: print(f"TYRE target {fy}: {exc}"); tt={}
        for k,val in tt.items():
            if k in st["rows"]: st["rows"][k][fy]["target"]=val

v7.populate_targets=populate_targets_v8
v7.LAYOUT_VERSION=LAYOUT_VERSION
m.fetch_lub=fetch_lub_depotwise

# v7 exposes meta_version (not meta_version_v7). Patch the actual hook.
def meta_version_v8(spreadsheet_id):
    try:
        vals=m.read_values(spreadsheet_id,f"'{m.META_TITLE}'!A:B"); d={str(r[0]):str(r[1]) for r in vals[1:] if len(r)>=2}; return d.get("LAYOUT_VERSION","")
    except Exception: return ""
v7.meta_version=meta_version_v8

if __name__=="__main__":
    try: sys.exit(v7.main())
    except Exception as exc: print(f"ANNUAL_KPI_FAILURE: {exc}"); raise
