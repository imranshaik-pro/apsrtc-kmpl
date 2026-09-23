"""Persistent source snapshots; presentation is a view, never the history store."""
import copy
import hashlib
import json
import re
from datetime import datetime

CACHE_TITLE = '_ANNUAL_HISTORY'
SCHEMA = 'annual-history-1'
MANUAL = 'MANUAL INPUT REQUIRED'
MONTHS = ['Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec','Jan','Feb','Mar']
GROUPS = {
    'HSD': ['HSD KMPL INCL AC','HSD KMPL EXCL AC'],
    'PRODUCT': [], 'ENGINE': [], 'LUB': ['TOTAL LUB KMPL'],
    'BD': ['B.D RATE'], 'MED': ['MED CANCL.'], 'SPRING': ['SPRING CONS'],
    'TYRE': ['AVG TYRE LIFE','NEW TYRE LIFE','RC TYRE LIFE','N.T.S RATE','Ist RC S Rate','TTL SCP Rate','RT Factor'],
}

def fy_of(period):
    y, month = map(int, period.split('-'))
    start = y if month >= 4 else y-1
    return f'{start}-{str(start+1)[-2:]}'

def periods(fy):
    y = int(fy[:4])
    return [f'{y}-{mo:02}' for mo in range(4,13)]+[f'{y+1}-{mo:02}' for mo in range(1,4)]

def good(value):
    return value is not None and str(value).strip() not in ('', MANUAL, 'MANUAL')

def new_cache(depot):
    return dict(schema=SCHEMA, depot=depot, months={}, targets={}, target_attempts=[], legacy=[])

def encode(cache):
    raw = json.dumps(cache, ensure_ascii=True, separators=(',',':'), allow_nan=False)
    chunks = [raw[i:i+30000] for i in range(0,len(raw),30000)]
    return [[SCHEMA,cache['depot'],len(chunks),hashlib.sha256(raw.encode()).hexdigest()]]+[[c] for c in chunks]

def decode(rows, depot):
    if not rows or len(rows[0])<4 or rows[0][:2] != [SCHEMA,depot]:
        raise ValueError('History cache missing, incompatible or belongs to another depot; refusing rebuild')
    count=int(rows[0][2]); raw=''.join(row[0] for row in rows[1:count+1])
    if len(rows)<count+1 or hashlib.sha256(raw.encode()).hexdigest()!=rows[0][3]:
        raise ValueError('History cache incomplete; refusing to overwrite saved history')
    cache=json.loads(raw)
    if cache.get('schema')!=SCHEMA or cache.get('depot')!=depot:
        raise ValueError('History identity mismatch')
    return cache

def group_for(name):
    for group,names in GROUPS.items():
        if name in names or (group in ('PRODUCT','ENGINE') and name.startswith(group+':')):
            return group
    return None

def snapshot(cache, period, group):
    return cache['months'].setdefault(period,{}).setdefault(group,{})

def migrate(cache, values, selected=''):
    """Import all FY/month cells, even when legacy metadata was deleted."""
    header=next((i for i,r in enumerate(values) if len(r)>3 and r[:4]==['SL.No','KPI','Year','Target']),None)
    if header is None: raise ValueError('Existing detail header not recognised; history left untouched')
    cache['legacy']=copy.deepcopy(values)
    name=None
    for raw in values[header+1:]:
        row=list(raw)+['']*18
        if row[1]: name=str(row[1])
        fy=str(row[2]); group=group_for(name or '')
        if not group or not re.fullmatch(r'\d{4}-\d{2}',fy): continue
        if good(row[3]): cache['targets'].setdefault(fy,{})[name]=row[3]
        for period,value in zip(periods(fy),row[4:16]):
            if good(value): snapshot(cache,period,group).setdefault(name,{})['month']=value
        # Closed years always use March. Current-FY cumulative needs a proven date.
        endpoint=periods(fy)[-1]
        if selected and fy==fy_of(selected): endpoint=selected
        elif not selected or endpoint>selected: endpoint=None
        if endpoint and good(row[17]):
            snapshot(cache,endpoint,group).setdefault(name,{})['upto']=row[17]
    # Retain the existing target table, including deliberately blank targets.
    cache['target_attempts']=sorted({str(r[2]) for r in values[header+1:] if len(r)>2 and re.fullmatch(r'\d{4}-\d{2}',str(r[2]))})

def known_unavailable(period, group):
    return fy_of(period)=='2024-25' and (group in ('LUB','SPRING') or (group=='TYRE' and period!='2024-04'))

def complete(data, group, field):
    names=GROUPS[group] or list(data)
    return bool(names) and all(good(data.get(name,{}).get(field)) for name in names)

def update(cache, fys, selected, fetch, checkpoint=lambda:None):
    """Fetch only missing groups; never replace saved numbers with failed fetches."""
    calls=0
    for fy in fys:
        wanted=[p for p in periods(fy) if p<=selected]
        for period in wanted:
            need_upto=period==wanted[-1]
            for group,names in GROUPS.items():
                data=snapshot(cache,period,group)
                if known_unavailable(period,group):
                    for name in names: data[name]={'month':MANUAL,'upto':MANUAL}
                    continue
                missing_month=not complete(data,group,'month')
                missing_upto=need_upto and not complete(data,group,'upto')
                if not (missing_month or missing_upto): continue
                calls+=1
                print(f'HISTORY FETCH {period} {group}: missing source values')
                try: fetched=fetch(group,period)
                except Exception as exc:
                    print(f'HISTORY SOURCE FAILED {period} {group}: preserving saved values: {exc}')
                    continue
                for name,pair in (fetched or {}).items():
                    if group_for(name)!=group: continue
                    old=data.setdefault(name,{})
                    for field in ('month','upto'):
                        if not good(old.get(field)) and good(pair.get(field)): old[field]=pair[field]
            checkpoint()
    print(f'HISTORY SOURCE GROUP REQUESTS: {calls}')
    return calls

def view_store(cache, fys, selected, m):
    st=m.new_store(fys); m.seed(st)
    for fy in fys:
        wanted=[p for p in periods(fy) if p<=selected]
        for period in wanted:
            for group,data in cache['months'].get(period,{}).items():
                for name,pair in data.items():
                    if not m.valid_dynamic(name): continue
                    m.ensure(st,name)
                    st['rows'][name][fy]['months'][MONTHS[(int(period[-2:])-4)%12]]=pair.get('month','')
                    if period==wanted[-1]: st['rows'][name][fy]['upto']=pair.get('upto')
        for name,value in cache['targets'].get(fy,{}).items():
            m.ensure(st,name); st['rows'][name][fy]['target']=value
    return st

def period_from_heading(values):
    for row in values[:4]:
        for cell in row:
            match=re.search(r'(?:through|Through)\s+([A-Za-z]+ \d{4})',str(cell))
            if match:
                return datetime.strptime(match[1],'%B %Y').strftime('%Y-%m')
    return ''
