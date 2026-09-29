#!/usr/bin/env python3
from calendar import monthrange
from datetime import datetime
from urllib.parse import urljoin
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


def lub_heading(html):
    soup=BeautifulSoup(html,'html.parser')
    for tag in soup.find_all(['h1','h2','h3','b','strong']):
        txt=' '.join(tag.get_text(' ',strip=True).split())
        if 'LUB' in txt.upper() and ('MONTH' in txt.upper() or 'KMPL' in txt.upper()):
            return txt[:180]
    text=' '.join(soup.get_text(' ',strip=True).split())
    pos=text.upper().find('DEPOT-WISE LUB KMPL')
    return text[pos:pos+180] if pos>=0 else text[:180]


def proddutur_totals(html):
    row,vals=v8._depot_row_has_data(html,DISPLAY,VEHICLE)
    return vals if row is not None else []


def submit_candidate(session, method, action, data, referer, label, y, mo):
    headers={
        'Referer': referer,
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/152 Safari/537.36',
        'Content-Type': 'application/x-www-form-urlencoded',
    }
    try:
        if method == 'GET':
            rr=session.get(action,params=data,headers=headers,timeout=45)
        else:
            rr=session.post(action,data=data,headers=headers,timeout=45)
        rr.raise_for_status()
        month_ok=v8._page_month(rr.text,y,mo)
        totals=proddutur_totals(rr.text)
        print(f"TEST {label}: method={method} status={rr.status_code} month_ok={month_ok} totals={totals} heading={lub_heading(rr.text)!r}")
        return rr.text,month_ok,totals
    except Exception as e:
        print(f"TEST {label}: ERROR {e!r}")
        return '',False,[]


def inspect_lub_contract(session,y,mo):
    print(f'\n=== LUB CONTRACT TEST {y:04d}-{mo:02d} ===')
    url=f"{m.core.MED_BASE}/lub_rgn_rpt.php"
    wanted=f"{datetime(y,mo,1).strftime('%B')}_{y}"
    yymm=f"{y:04d}{mo:02d}{wanted}"
    landing=session.get(url,timeout=45)
    landing.raise_for_status()
    print('LANDING:',landing.status_code,landing.url,'heading=',repr(lub_heading(landing.text)))
    soup=BeautifulSoup(landing.text,'html.parser')
    candidates=[]

    forms=soup.find_all('form')
    print('FORM COUNT:',len(forms))
    for fi,form in enumerate(forms,1):
        method=(form.get('method') or 'GET').strip().upper()
        action=urljoin(url,form.get('action') or url)
        print(f'FORM {fi}: method={method} action={action}')

        base_data={}
        submit_fields={}
        for inp in form.find_all('input'):
            name=inp.get('name')
            if not name: continue
            typ=(inp.get('type') or 'text').lower()
            val=inp.get('value','')
            print(f'  INPUT name={name!r} type={typ!r} value={val!r}')
            if typ in {'submit','button','image'}:
                submit_fields[name]=val
            elif typ not in {'checkbox','radio'} or inp.has_attr('checked'):
                base_data[name]=val

        matched=False
        for sel in form.find_all('select'):
            name=sel.get('name')
            if not name: continue
            opts=sel.find_all('option')
            selected=next((o for o in opts if o.has_attr('selected')),None)
            default_val=(selected.get('value','') if selected else (opts[0].get('value','') if opts else ''))
            default_txt=(selected.get_text(' ',strip=True) if selected else (opts[0].get_text(' ',strip=True) if opts else ''))
            print(f'  SELECT name={name!r} options={len(opts)} default_value={default_val!r} default_text={default_txt!r}')
            chosen=None
            for opt in opts:
                ov=opt.get('value','')
                ot=opt.get_text(' ',strip=True)
                if m.n(wanted) in {m.n(ov),m.n(ot)}:
                    chosen=ov or ot
                    print(f'    MATCH wanted={wanted!r} option_value={ov!r} option_text={ot!r}')
                    break
            if chosen is not None:
                base_data[name]=chosen
                matched=True
            elif default_val or default_txt:
                base_data[name]=default_val or default_txt

        if matched:
            candidates.append((method,action,dict(base_data),f'form{fi}-base'))
            if submit_fields:
                with_submit=dict(base_data); with_submit.update(submit_fields)
                candidates.append((method,action,with_submit,f'form{fi}-with-submit'))
                for sn,sv in submit_fields.items():
                    one=dict(base_data); one[sn]=sv
                    candidates.append((method,action,one,f'form{fi}-submit-{sn}'))

    # Exact browser contract supplied from Chrome DevTools.
    candidates.extend([
        ('POST',url,{'yymm':yymm},'exact-post-yymm'),
        # Legacy guesses retained only for comparison.
        ('POST',url,{'dt':wanted},'fallback-post-dt'),
        ('GET',url,{'dt':wanted},'fallback-get-dt'),
    ])

    seen=set(); successes=[]
    for method,action,data,label in candidates:
        sig=(method,action,tuple(sorted(data.items())))
        if sig in seen: continue
        seen.add(sig)
        html,month_ok,totals=submit_candidate(session,method,action,data,url,label,y,mo)
        if month_ok and totals:
            successes.append((label,method,action,data,totals,html))

    print('SUCCESS CANDIDATES:',[(x[0],x[1],x[4]) for x in successes])
    exact=[]
    if (y,mo)==(2026,5):
        for item in successes:
            totals=item[4]
            if len(totals)>=2 and totals[0]==1993 and totals[1]==1829:
                exact.append(item)
        print('MAY-2026 EXPECTED 1993/1829 MATCHES:',[(x[0],x[1]) for x in exact])
    return exact or successes



def print_engine(session,y,mo):
    print(f'\n=== ENGINE {y:04d}-{mo:02d} ===')
    url=f"{m.core.MEDNEW_BASE}/engkmpl_um.php"
    data={"yymm":m.token(y,mo),"reg":REGION,"dept":DISPLAY}
    rr=session.post(url,data=data,timeout=45)
    rr.raise_for_status()
    soup=BeautifulSoup(rr.text,'html.parser')
    print('ENGINE HTTP:',rr.status_code,'bytes=',len(rr.text),'url=',rr.url)
    tables=0
    for table in soup.find_all('table'):
        text=' '.join(table.get_text(' ',strip=True).split())
        if 'ENGINE TYPE' not in text.upper() and 'FOR THE MONTH' not in text.upper():
            continue
        tables += 1
        print('ENGINE TABLE',tables,'header_indexes=',m._dimension_indexes(table))
        for tr in table.find_all('tr'):
            cells=m._expanded_dimension_cells(tr)
            if len(cells) >= 2 and any(k in cells[1].upper() for k in ('EICHER','EURO-3','INDRA','TA-1510','TA-BS-IV','TATA BS-III NRE')):
                print('ENGINE ROW:',cells)
    try:
        parsed=m.direct_dimension_rows(rr.text,'ENGINE TYPE','ENGINE')
        print('ENGINE PARSED:',parsed)
    except Exception as e:
        print('ENGINE PARSE ERROR:',repr(e))


def print_engine_candidates(session,y,mo):
    print(f'\n=== ENGINE CANDIDATE ENDPOINTS {y:04d}-{mo:02d} ===')
    candidates=['engkmpl.php','engkmpl_dpt.php','engkmpl_rpt.php','enginekmpl_um.php','enginekmpl.php']
    print('DEPOT IDENTIFIER CHECK:')
    for dept in ('PRODDUTUR','PDTR','PDT','PRODDATUR'):
        try:
            dr=session.post(f"{m.core.MEDNEW_BASE}/engkmpl_um.php",data={"yymm":m.token(y,mo),"reg":REGION,"dept":dept},timeout=30)
            dt=' '.join(BeautifulSoup(dr.text,'html.parser').get_text(' ',strip=True).split()).upper()
            legacy=[n for n in ('EICHER-BS-III','EURO-3','INDRA NEW','TA-1510','TA-BS-IV','EICHER BS-III LATEST','TATA BS-III NRE SPIN') if n in dt]
            print('DEPOT',dept,'status=',dr.status_code,'bytes=',len(dr.text),'legacy_names=',legacy)
        except Exception as e:
            print('DEPOT',dept,'ERROR=',repr(e))
    print('REGION VARIANT CHECK:')
    for reg in ('YSRKADAPA','KADAPA','ANNAMAYYA',''):
        try:
            vr=session.post(f"{m.core.MEDNEW_BASE}/engkmpl_um.php",data={"yymm":m.token(y,mo),"reg":reg,"dept":DISPLAY},timeout=30)
            vt=' '.join(BeautifulSoup(vr.text,'html.parser').get_text(' ',strip=True).split()).upper()
            legacy=[n for n in ('EICHER-BS-III','EURO-3','INDRA NEW','TA-1510','TA-BS-IV','EICHER BS-III LATEST','TATA BS-III NRE SPIN') if n in vt]
            print('REGION',reg or '<blank>','status=',vr.status_code,'bytes=',len(vr.text),'legacy_names=',legacy)
        except Exception as e:
            print('REGION',reg or '<blank>','ERROR=',repr(e))
    data={"yymm":m.token(y,mo),"reg":REGION,"dept":DISPLAY}
    for path in candidates:
        try:
            rr=session.post(f"{m.core.MEDNEW_BASE}/{path}",data=data,timeout=30)
            text=' '.join(BeautifulSoup(rr.text,'html.parser').get_text(' ',strip=True).split())
            names=[n for n in ('EICHER-BS-III','EURO-3','INDRA NEW','TA-1510','TA-BS-IV','EICHER BS-III LATEST','TATA BS-III NRE SPIN') if n in text.upper()]
            print('CANDIDATE',path,'status=',rr.status_code,'bytes=',len(rr.text),'tables=',len(BeautifulSoup(rr.text,'html.parser').find_all('table')),'legacy_names=',names,'heading=',text[:120])
        except Exception as e:
            print('CANDIDATE',path,'ERROR=',repr(e))

def main():
    s=login()
    print_hsd(s,2024,9)
    print_hsd(s,2025,1)
    print_engine(s,2026,7)
    print_engine_candidates(s,2026,7)

    # Known browser benchmark: PRODDUTUR May-2026 must be Monthly=1993, Upto=1829.
    matches=inspect_lub_contract(s,2026,5)
    if not matches:
        print('LUB CONTRACT RESULT: NO VERIFIED CANDIDATE')
    else:
        print('LUB CONTRACT RESULT: VERIFIED CANDIDATE FOUND')

    print('\n=== APR-2026 TARGETS ===')
    try: print('HSD:', v8.v7.hsd_targets(s,DISPLAY,VEHICLE,REGION,2026,4))
    except Exception as e: print('HSD TARGET ERROR:',repr(e))
    try: print('OPER:', v8.operational_targets(s,DISPLAY,VEHICLE,REGION,2026,4))
    except Exception as e: print('OPER TARGET ERROR:',repr(e))

if __name__=='__main__':
    main()
