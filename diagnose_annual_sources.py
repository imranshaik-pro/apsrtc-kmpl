#!/usr/bin/env python3
from calendar import monthrange
from bs4 import BeautifulSoup
import time
import annual_kpi_runner_v8 as v8
from src.auth.client import login

m = v8.m
DISPLAY='PRODDUTUR'
VEHICLE='PDTR'
REGION='YSRKADAPA'


def retry_get(session, url, params, tries=5):
    last=None
    for i in range(1, tries+1):
        try:
            r=session.get(url, params=params, timeout=45)
            r.raise_for_status()
            return r.text
        except Exception as e:
            last=e
            print(f'RETRY {i}/{tries} failed: {e}')
            if i<tries: time.sleep(i*2)
    raise last


def print_hsd(session,y,mo):
    last=monthrange(y,mo)[1]
    url=f"{m.core.MED_BASE}/mth_acnac_dpt.php"
    params={"action":"","fdate":f"{last:02d}/{mo:02d}/{y}","dist":REGION}
    print(f'\n=== HSD {y:04d}-{mo:02d} ===')
    html=retry_get(session,url,params)
    h,row=m.find_depot(html,DISPLAY,VEHICLE,["WITH AC KMPL","WITHOUT AC KMPL"])
    print('HEADERS:', h)
    print('ROW:', row)
    try: print('PARSED:', m.fetch_hsd(session,DISPLAY,VEHICLE,REGION,y,mo))
    except Exception as e: print('PARSED ERROR:',repr(e))


def print_lub(session,y,mo):
    print(f'\n=== LUB {y:04d}-{mo:02d} ===')
    # Use the same confirmed POST helper as production v8.
    html=m.lub_html(session,y,mo)
    soup=BeautifulSoup(html,'html.parser')
    for ti,t in enumerate(soup.find_all('table'),start=1):
        txt=m.n(t.get_text(' ',strip=True))
        if 'LUB' not in txt: continue
        try: h,rows=m.core.expanded_headers(t)
        except Exception as e:
            print(f'TABLE {ti} HEADER ERROR:',repr(e)); continue
        hits=[]
        for row in rows:
            rt=' | '.join(str(x) for x in row)
            if 'PRODDUTUR' in m.n(rt) or 'PDTR' in m.n(rt): hits.append(row)
        print(f'TABLE {ti} HEADERS:',h)
        for r in hits: print('PRODDUTUR ROW:',r)
    try: print('PARSED:', v8.fetch_lub_depotwise(session,DISPLAY,VEHICLE,REGION,y,mo))
    except Exception as e: print('PARSED ERROR:',repr(e))


def main():
    s=login()
    print_hsd(s,2024,9)
    print_hsd(s,2025,1)
    print_lub(s,2026,5)
    print('\n=== APR-2026 TARGETS ===')
    try: print('HSD:', v8.v7.hsd_targets(s,DISPLAY,VEHICLE,REGION,2026,4))
    except Exception as e: print('HSD TARGET ERROR:',repr(e))
    try: print('OPER:', v8.operational_targets(s,DISPLAY,VEHICLE,REGION,2026,4))
    except Exception as e: print('OPER TARGET ERROR:',repr(e))

if __name__=='__main__':
    main()
