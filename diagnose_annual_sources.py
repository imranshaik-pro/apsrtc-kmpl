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
    try:
        parsed=v8.fetch_lub_depotwise(session,DISPLAY,VEHICLE,REGION,y,mo)
        print('PARSED:',parsed)
    except Exception as e:
        print('PARSED ERROR:',repr(e))
        return


def main():
    s=login()
    print_hsd(s,2024,9)
    print_hsd(s,2025,1)

    # Historical LUB values specifically requested for diagnosis, plus May-2026 screenshot comparison.
    print_lub(s,2024,9)
    print_lub(s,2025,1)
    print_lub(s,2026,5)

    print('\n=== APR-2026 TARGETS ===')
    try: print('HSD:', v8.v7.hsd_targets(s,DISPLAY,VEHICLE,REGION,2026,4))
    except Exception as e: print('HSD TARGET ERROR:',repr(e))
    try: print('OPER:', v8.operational_targets(s,DISPLAY,VEHICLE,REGION,2026,4))
    except Exception as e: print('OPER TARGET ERROR:',repr(e))

if __name__=='__main__':
    main()
