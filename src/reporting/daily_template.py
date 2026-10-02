"""Locked daily-v1 presentation, shared by the coloured report and Telegram.

Reads completed report text only. No source fetching, KMPL/slab calculations,
date resolution, or tyre eligibility belongs in this module.
"""
from __future__ import annotations

import base64
import json
from dataclasses import dataclass, field
from datetime import date
from decimal import Decimal, InvalidOperation, ROUND_HALF_UP
from functools import lru_cache
from html import escape
from pathlib import Path
import re
from urllib.parse import urlsplit

VERSION = "daily-v1.1"
# sendMessage allows 4096 characters after entity parsing. Counting the complete
# HTML in UTF-16 and keeping a 96-unit margin also bounds the parsed message.
TELEGRAM_MAX_UNITS = 4000
ROOT = Path(__file__).resolve().parents[2]
ASSETS = ROOT / "assets" / "reporting"
CSS = Path(__file__).parent / "templates" / "daily_v1.css"
WEEKDAYS = ("సోమవారం", "మంగళవారం", "బుధవారం", "గురువారం", "శుక్రవారం", "శనివారం", "ఆదివారం")
METRICS = ("Target", "ఈ రోజు", "ఈ రోజు వరకు", "గత నెల", "గత ఇయర్ నెల")
LABELS = ("ఈ రోజు", "ఈ రోజు వరకు", "గత నెల", "గత సంవత్సరం ఇదే నెల")
TYRE_TITLES = (
    "ముందు స్థానాల్లో RC టైర్లు",
    "ఒకే రకం టైర్లు అమర్చని వాహనాలు",
    "RNSO/RNSI స్థానాల్లో రిపేర్ టైర్లు అమర్చిన వాహనాలు",
    "రెండు నెలలకు పైగా ఉపయోగంలో ఉన్న స్పేర్ టైర్లు",
)
TYRE_LABELS = (
    "RC ముందు టైర్లు", "ఒకే రకం టైర్లు అమర్చని వాహనాలు",
    "రిపేర్ టైర్లు • RNSO / RNSI", "స్పేర్ టైర్లు • రెండు నెలలకు పైగా",
)


@dataclass
class TyreGroup:
    kind: int
    rows: list[tuple[str, ...]] = field(default_factory=list)
    vehicles: str = ""
    records: str = ""
    snapshot_date: str = ""
    unavailable: bool = False


@dataclass
class DailyView:
    depot: str
    report_date: str
    metrics: dict = field(default_factory=lambda: {c: {} for c in ("TOT", "NAC", "AC")})
    low: list[tuple[str, ...]] = field(default_factory=list)
    low_section: bool = False
    slab_headers: tuple[str, ...] = ()
    slabs: list[tuple[str, ...]] = field(default_factory=list)
    tyres: list[TyreGroup] = field(default_factory=list)
    tyre_note: str = ""
    unknown: list[tuple[str, str]] = field(default_factory=list)
    notes: list[str] = field(default_factory=list)


def read_daily_view(report, depot, report_date):
    """Preserve all displayed source values, including cached/legacy tyre rows."""
    view = DailyView(depot, report_date)
    date.fromisoformat(report_date)
    active = None
    table_kind = None
    for raw in report.splitlines():
        line = raw.strip()
        if not line:
            continue
        metric = re.fullmatch(r'(Target|ఈ రోజు|ఈ రోజు వరకు|గత నెల|గత ఇయర్ నెల)\s+(\S+)\s+(\S+)\s+(\S+)', line)
        if metric:
            for category, value in zip(("TOT", "NAC", "AC"), metric.groups()[1:]):
                view.metrics[category][metric[1]] = value
            continue
        low = re.fullmatch(r'`\s*(\d+)\. (.+?)(?: \((.*?)\))?` : (\S+) \| (\S+)', line)
        if low:
            number, vehicle, operation, day, upto = low.groups()
            view.low.append((f'{int(number):02d}', vehicle, operation or "", day, upto))
            continue
        if line.startswith('Slab') and '|' in line:
            view.slab_headers = tuple(c.strip() for c in line.split('|'))
            table_kind = 'slabs'
            continue
        if re.fullmatch(r'[-|─]+', line):
            continue
        if line.startswith('టైర్ల వివరాలు —'):
            table_kind = None
            if 'వివరాలు అందుబాటులో లేవు' in line:
                view.tyre_note = 'వివరాలు అందుబాటులో లేవు.'
            continue
        kind = next((i for i, title in enumerate(TYRE_TITLES) if line == title or line.startswith(title + ':')), None)
        if kind is not None:
            active = TyreGroup(kind, unavailable='అందుబాటులో లేవు' in line)
            view.tyres.append(active)
            table_kind = None
            continue
        if active is not None:
            count = re.fullmatch(r'వాహనాలు: (\d+) \| టైర్ల నమోదులు: (\d+)', line)
            if count:
                active.vehicles, active.records = count.groups()
                continue
            snapshot = re.match(r'మూల నివేదిక తేదీ: (\d{4}-\d{2}-\d{2})', line)
            if snapshot:
                active.snapshot_date = snapshot[1]
                continue
        if '|' in line and line.split('|', 1)[0].strip() == 'వాహనం':
            table_kind = 'tyres'
            continue
        legacy = re.fullmatch(r'వాహనం (.+?) — (.+)', line)
        if legacy:
            details = legacy[2]
            for label in ('టైర్ పొజిషన్లు: ', 'టైర్ పొజిషన్: ', 'టైర్ నం.: ', 'ఉపయోగంలో రోజులు: '):
                details = details.replace(label, '')
            row = (legacy[1], *(c.strip() for c in details.split('|')))
            if len(row) in (2, 4):
                if active is None:
                    active = TyreGroup(3 if len(row) == 4 else 1)
                    view.tyres.append(active)
                active.rows.append(row)
                continue
        if '|' in line and table_kind == 'slabs':
            row = tuple(c.strip() for c in line.split('|'))
            if len(row) == len(view.slab_headers):
                view.slabs.append(row)
                continue
        if '|' in line and table_kind == 'tyres' and active is not None:
            row = tuple(c.strip() for c in line.split('|'))
            if len(row) == (4 if active.kind == 3 else 2):
                active.rows.append(row)
                continue
        if line.startswith('వాహనాలు:'):
            found = re.findall(r'([^ ,]+) \((?:op_type:|రకం:) ?(.*?)\)', line)
            if found:
                view.unknown.extend(found)
                continue
        if line.startswith('⚠️ *తక్కువ సామర్థ్య'):
            view.low_section = True
            continue
        if line.startswith(('APSRTC —', 'Report date:', '🌟', '🛢️', '━━━━━━━━', 'Metric', '`రోజు`', '*రేంజ్', '*తక్షణ చర్య!', '⚠️ *జాగ్రత్త:', '✅ తక్కువ KMPL')) or 'src/reporting/' in line:
            continue
        if line == '(లేవు)' and view.low_section:
            continue
        view.notes.append(line)
    return view


def number(value):
    try:
        parsed = Decimal(value)
        return parsed if parsed.is_finite() else None
    except (InvalidOperation, ValueError, TypeError):
        return None


def kpi_rows(values):
    target = values.get('Target', '—')
    rows = []
    for key, label in zip(METRICS[1:], LABELS):
        actual = values.get(key, '—')
        comparable = key in METRICS[1:3] and number(target) is not None and number(actual) is not None
        difference = (number(actual) - number(target)).quantize(Decimal('.01'), rounding=ROUND_HALF_UP) if comparable else None
        rows.append((label, target if key in METRICS[1:3] else '—', actual, f'{difference:+.2f}' if difference is not None else '—'))
    return rows


def upto_shares(view):
    """A count share is an inspection cue; it cannot explain weighted KMPL."""
    low = next((row for row in view.slabs if row[0] in ('', '<=5.00', '<= 5.00') and row[1] == 'ఈరోజు వరకు'), None)
    # Continuation rows have a blank slab label; the first is the <=5.00 row.
    totals = next((view.slabs[i+1] for i, row in enumerate(view.slabs[:-1]) if row[0] == 'Total'), None)
    if not low or not totals:
        return []
    operations = view.slab_headers[2:-1]
    shares = []
    preferred = [op for op in ('EX', 'IH') if op in operations]
    for op in preferred or list(operations[:2]):
        column = operations.index(op) + 2
        a, b = low[column], totals[column]
        if a.isdigit() and b.isdigit() and int(b) > 0 and int(a) <= int(b):
            percent = (Decimal(a) * 100 / Decimal(b)).quantize(Decimal('.1'), rounding=ROUND_HALF_UP)
            shares.append((op, a, b, f'{percent}%'))
    return shares


def _nac_duplicates_total(view):
    """Omit NAC only when classified source vehicles and every KPI agree.

    A blank AC KPI is not evidence of an AC-free depot. The source slab
    headings cover classified raw vehicle types, including zero-KMPL vehicles.
    Unknown types, any AC type/value, or a different target/history retain NAC.
    """
    if view.unknown or not view.slab_headers or not view.slabs:
        return False
    try:
        mapping = json.loads((ROOT / 'vehicle_type_mapping.json').read_text())
    except (OSError, ValueError):
        return False
    operations = view.slab_headers[2:-1]
    if not operations or any(mapping.get(op) != 'NAC' for op in operations):
        return False
    if not any(row[0] == 'Total' and number(row[-1]) is not None and number(row[-1]) > 0
               for row in view.slabs):
        return False
    if any(number(value) is not None and number(value) != 0
           for value in view.metrics['AC'].values()):
        return False
    total, nac = view.metrics['TOT'], view.metrics['NAC']
    for key in METRICS:
        if key not in total or key not in nac:
            return False
        a, b = number(total[key]), number(nac[key])
        if a is not None and b is not None:
            if a != b:
                return False
        elif total[key] not in ('—', '-') or nac[key] not in ('—', '-'):
            return False
    return all(number(total[key]) is not None and number(total[key]) > 0
               for key in METRICS[1:3])


def _metric_sections(view):
    redundant = _nac_duplicates_total(view)
    return [(category, values) for category, values in view.metrics.items()
            if values and not (redundant and category in ('NAC', 'AC'))
            and (category == 'TOT' or any(number(v) is not None for v in values.values()))]


def _grid(headers, rows, center=False):
    values = [tuple(map(str, headers)), *(tuple(map(str, row)) for row in rows)]
    widths = [max(len(row[column]) for row in values) for column in range(len(headers))]
    return '\n'.join(' | '.join(cell.center(widths[column]) if center else cell.ljust(widths[column])
                               for column, cell in enumerate(row)) for row in values)


def _table(headers, rows, classes=''):
    return '<table class="' + classes + '"><thead><tr>' + ''.join('<th>' + escape(str(c)) + '</th>' for c in headers) + '</tr></thead><tbody>' + ''.join('<tr>' + ''.join('<td>' + escape(str(c)) + '</td>' for c in row) + '</tr>' for row in rows) + '</tbody></table>'


def _tyre_heading(group):
    count = group.vehicles or str(len({row[0] for row in group.rows}))
    return TYRE_LABELS[group.kind] + (' • ' + count + (' వాహనాలు' if group.kind in (2, 3) else '') if group.rows else '')


def _tyre_table(group):
    """Keep a uniform spare position once; retain differing/unknown positions."""
    if group.kind != 3:
        return ('వాహనం', 'స్థానాలు'), group.rows, ''
    positions = {row[1] for row in group.rows}
    if len(positions) == 1 and re.fullmatch(r'SPARE[1-9]\d*', next(iter(positions))):
        return ('వాహనం', 'టైర్ నం.', 'రోజులు'), [(r[0], r[2], r[3]) for r in group.rows], next(iter(positions))
    return ('వాహనం', 'స్థానం', 'టైర్ నం.', 'రోజులు'), group.rows, ''


def _actions(view):
    actions = []
    if view.low:
        row = view.low[0]
        actions.append(f'{row[1]}: రూట్, ఇంధన నమోదు, వాహన స్థితి పరిశీలించండి.')
    shares = upto_shares(view)
    if shares and any(int(row[1]) > 0 for row in shares):
        actions.append(' / '.join(row[0] for row in shares if int(row[1]) > 0) + ' Upto తక్కువ KMPL వాహనాలను సమీక్షించండి.')
    if any(group.rows for group in view.tyres):
        actions.append('టైర్ల అమరిక, రిపేర్ స్థితి, స్పేర్ వినియోగాన్ని తనిఖీ చేయండి.')
    return actions


@lru_cache(maxsize=1)
def _style():
    faces = []
    for family, weight, name in (('Noto Sans Telugu', 400, 'NotoSansTelugu-400.ttf'), ('Noto Sans Telugu', 700, 'NotoSansTelugu-700.ttf'), ('Noto Emoji', 400, 'NotoEmoji.ttf')):
        encoded = base64.b64encode((ASSETS / name).read_bytes()).decode('ascii')
        faces.append(f"@font-face{{font-family:'{family}';font-weight:{weight};src:url(data:font/ttf;base64,{encoded}) format('truetype')}}")
    return ''.join(faces) + CSS.read_text(encoding='utf-8')


def _source_note(view, cached):
    base = 'ఇప్పటికే సేవ్ చేసిన KMPL నివేదిక.' if cached else 'మూల KMPL నివేదిక Google Driveలో సేవ్ చేయబడింది.'
    return base + (' టైర్ల వివరాలు ఈ నివేదికలో విడిగా చేర్చబడ్డాయి.' if view.tyres or view.tyre_note else '')


def render_daily_html(report, depot, report_date, drive_link='', cached=False):
    view = read_daily_view(report, depot, report_date)
    dt = date.fromisoformat(report_date)
    has_tyres = bool(view.tyres or view.tyre_note)
    page = '<!doctype html><html lang="te"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><meta name="daily-template" content="'+VERSION+'"><title>APSRTC '+escape(depot)+' '+report_date+'</title><style>'+_style()+'</style></head><body><main>'
    page += '<header class="hero"><div class="brand">🚌 APSRTC • '+escape(depot)+' DEPOT</div><div>DAILY HSD KMPL'+(' &amp; టైర్ల నివేదిక' if has_tyres else '')+'</div><div class="period">'+dt.strftime('%d %B %Y')+' | '+WEEKDAYS[dt.weekday()]+'</div></header>'
    for category, values in _metric_sections(view):
        rows = kpi_rows(values)
        page += '<section class="section"><h2>⛽ HSD KMPL • పనితీరు ముఖ్యాంశాలు'+(' • '+category if category != 'TOT' else '')+'</h2><div class="cards">'
        for row in rows[:2]:
            diff = number(row[3])
            state = ' good' if diff is not None and diff >= 0 else ' bad' if diff is not None else ''
            arrow = ' ▲' if diff is not None and diff > 0 else ' ▼' if diff is not None and diff < 0 else ''
            page += '<div class="card'+state+'"><div>'+row[0]+'</div><div class="value">'+escape(row[2])+'</div><div class="small">Target '+escape(row[1])+' | '+escape(row[3])+arrow+'</div></div>'
        page += '</div>'+_table(('వివరాలు','Target','వాస్తవం','తేడా'),rows,'num')
        if category == 'TOT' and _nac_duplicates_total(view):
            page += '<p class="small">TOT / NAC విలువలు ఒకేలా ఉన్నాయి; మొత్తం పనితీరు ఒకసారి చూపబడింది.</p>'
        if category == 'TOT' and all(number(value) is None for c in ('NAC','AC') for value in view.metrics[c].values()):
            page += '<p class="small">TOT values shown. NAC / AC మూల విలువలు అందుబాటులో లేవు.</p>'
        page += '</section>'
    if view.low or view.low_section:
        page += '<section class="section"><h2>⚠️ తక్కువ KMPL వాహనాలు • Top 10 ≤ 5.00</h2>'
        page += _table(('#','వాహనం','రకం','ఈ రోజు','ఈ రోజు వరకు'),view.low,'low') if view.low else '<p>తక్కువ KMPL వాహనాలు నమోదు కాలేదు.</p>'
        if view.low:
            row = view.low[0]
            page += '<p class="small">అత్యల్ప రోజు KMPL: '+escape(row[1])+' ('+escape(row[3])+'). సంబంధిత రూట్, ఇంధన నమోదు, వాహన స్థితి పరిశీలించండి.</p>'
        page += '</section>'
    if view.slabs:
        rows = [(row[0], 'ఈ రోజు' if row[1]=='రోజు' else 'ఈ రోజు వరకు', *row[2:]) for row in view.slabs]
        page += '<section class="section"><h2>📊 KMPL రేంజ్ • వాహనాల సంఖ్య</h2>'+_table(('పరిధి','వ్యవధి',*view.slab_headers[2:-1],'మొత్తం'),rows,'num')
        shares = upto_shares(view)
        if shares:
            page += '<div class="note">ఈ రోజు వరకు ≤ 5.00: '+', '.join(f'{op} {a}/{b} ({percent})' for op,a,b,percent in shares)+'.<br>ఇవి తక్కువ KMPL వాహనాల వాటాలు. డిపో సగటు తగ్గడానికి కారణాన్ని ఈ సంఖ్యలతో మాత్రమే నిర్ధారించలేము.</div>'
        page += '</section>'
    if has_tyres:
        page += '<section class="section"><h2>🛞 టైర్ల తనిఖీ</h2>'
        if view.tyre_note:
            page += '<p>'+escape(view.tyre_note)+'</p>'
        for group in view.tyres:
            page += '<h3>'+_tyre_heading(group)+'</h3>'
            if group.unavailable:
                page += '<p>వివరాలు అందుబాటులో లేవు.</p>'
            if group.records:
                page += '<p class="small">మూల నివేదికలో టైర్ల నమోదులు: '+group.records+'</p>' if group.kind in (0,1) else ''
            if group.snapshot_date:
                page += '<p class="small">మూల నివేదిక తేదీ: '+group.snapshot_date+' (రోజువారీ KMPL తేదీకి స్వతంత్ర స్నాప్‌షాట్)</p>'
            if group.rows:
                headers, display_rows, position = _tyre_table(group)
                if position:
                    page += '<p class="small common-position">అన్ని నమోదుల స్థానం: '+escape(position)+'</p>'
                page += _table(headers,display_rows,'tyres')
        page += '</section>'
    actions = _actions(view)
    if view.unknown or actions:
        page += '<section class="section">'
        if view.unknown:
            page += '<h2>ℹ️ సేవా వర్గీకరణ తనిఖీ</h2>' + ''.join('<p>'+escape(vehicle)+' ('+escape(operation)+') • సేవా రకాన్ని నిర్ధారించండి.</p>' for vehicle,operation in view.unknown)
        if actions:
            page += '<h3>🛠️ తనిఖీ ప్రాధాన్యతలు</h3><ul class="actions">'+''.join('<li>'+escape(value)+'</li>' for value in actions)+'</ul>'
        page += '</section>'
    if view.notes:
        page += '<section class="section">'+''.join('<p>'+escape(value)+'</p>' for value in view.notes)+'</section>'
    if drive_link:
        parsed = urlsplit(drive_link)
        page += '<section class="section"><h2>📁 Google Drive</h2><p class="small">'+_source_note(view,cached)+'</p>'
        page += '<a href="'+escape(drive_link,quote=True)+'">పూర్తి KMPL నివేదికను తెరవండి</a>' if parsed.scheme=='https' and parsed.netloc else escape(drive_link)
        page += '</section>'
    page += '<div class="end">డిపో ప్రగతి • మనందరి బాధ్యత!</div></main></body></html>'
    # Keep the embedded fonts' redistribution notice available in the document.
    licenses = '\n'.join((ASSETS/name).read_text(encoding='utf-8') for name in ('OFL-NotoSansTelugu.txt','OFL-NotoEmoji.txt'))
    return page + '\n<!-- Embedded fonts: '+licenses.replace('--','- -')+' -->\n'


def _length(text):
    return len(text.encode('utf-16-le')) // 2


def _telegram_chunks(blocks):
    fragments = []
    def wrap(kind, text):
        return '<pre>'+escape(text)+'</pre>' if kind=='table' else '<b>'+escape(text)+'</b>' if kind=='heading' else escape(text)
    for kind, text in blocks:
        rendered = wrap(kind,text)
        if _length(rendered)<=3400:
            fragments.append(rendered)
            continue
        # Repeating the header on table continuations keeps every row interpretable.
        lines = text.splitlines()
        header = lines[0] if kind=='table' else ''
        buffer = header if header else ''
        for line in lines[1:] if header else lines:
            pieces = [line[i:i+450] for i in range(0,len(line),450)] or ['']
            for piece in pieces:
                candidate = buffer+('\n' if buffer else '')+piece
                if _length(wrap(kind,candidate))>3400 and buffer:
                    fragments.append(wrap(kind,buffer))
                    buffer = header+('\n' if header else '')+piece
                else:
                    buffer = candidate
        if buffer:
            fragments.append(wrap(kind,buffer))
    chunks, current = [], ''
    for fragment in fragments:
        gap = '\n\n' if fragment.startswith(('<b>','<pre>')) else '\n'
        candidate = current+(gap if current else '')+fragment
        if _length(candidate)>TELEGRAM_MAX_UNITS and current:
            chunks.append(current)
            current=fragment
        else:
            current=candidate
    if current:
        chunks.append(current)
    return chunks


def render_daily_telegram(report, depot, report_date, drive_link='', cached=False):
    view = read_daily_view(report,depot,report_date)
    dt = date.fromisoformat(report_date)
    blocks = [('heading',f'🚌 APSRTC • {depot} DEPOT'),('text','📊 DAILY HSD KMPL'+(' & టైర్ల నివేదిక' if view.tyres or view.tyre_note else '')),('text',f'🗓️ {dt:%d %B %Y} | {WEEKDAYS[dt.weekday()]}')]
    for category,values in _metric_sections(view):
        rows=kpi_rows(values)
        blocks += [('heading','⛽ HSD KMPL • పనితీరు ముఖ్యాంశాలు'+(' • '+category if category!='TOT' else '')),('table',_grid(('Metric','Target','Actual','Diff'),rows))]
        if category == 'TOT' and _nac_duplicates_total(view):
            blocks.append(('text','TOT / NAC విలువలు ఒకేలా ఉన్నాయి; మొత్తం పనితీరు ఒకసారి చూపబడింది.'))
        for row in rows[:2]:
            diff=number(row[3])
            if diff is not None:
                icon='✅' if diff>=0 else '⚠️'
                status='టార్గెట్ కంటే మెరుగు' if diff>0 else 'టార్గెట్ కంటే తక్కువ' if diff<0 else 'టార్గెట్‌తో సమానం'
                blocks.append(('text',f'{icon} {row[0]}: {status} ({row[3]})'))
    if view.low or view.low_section:
        blocks += [('heading','⚠️ తక్కువ KMPL వాహనాలు • Top 10 ≤ 5.00'),('text','Day = ఈ రోజు | Upto = ఈ రోజు వరకు')]
        blocks.append(('table',_grid(('#','Vehicle','Type','Day','Upto'),view.low,center=True)) if view.low else ('text','తక్కువ KMPL వాహనాలు నమోదు కాలేదు.'))
    if view.slabs:
        blocks += [('heading','📊 KMPL రేంజ్ • వాహనాల సంఖ్య'),('table',_grid(('Slab','Period',*view.slab_headers[2:-1],'Total'),[(row[0],'Day' if row[1]=='రోజు' else 'Upto',*row[2:]) for row in view.slabs]))]
        shares=upto_shares(view)
        if shares:
            blocks.append(('text','Upto ≤ 5.00: '+' | '.join(f'{op} {a}/{b} ({percent})' for op,a,b,percent in shares)+'\nతక్కువ KMPL వాహనాల వాటా; ఇవి కారణ నిర్ధారణ కావు.'))
    if view.tyres or view.tyre_note:
        blocks.append(('heading','🛞 టైర్ల తనిఖీ'))
        if view.tyre_note:
            blocks.append(('text',view.tyre_note))
        for group in view.tyres:
            blocks.append(('heading',_tyre_heading(group)))
            if group.unavailable:
                blocks.append(('text','వివరాలు అందుబాటులో లేవు.'))
            if group.records:
                blocks.append(('text','మూల నివేదికలో టైర్ల నమోదులు: '+group.records)) if group.kind in (0,1) else None
            if group.snapshot_date:
                blocks.append(('text','మూల నివేదిక తేదీ: '+group.snapshot_date+' (ప్రత్యేక స్నాప్‌షాట్)'))
            if group.rows:
                headers, display_rows, position = _tyre_table(group)
                if position:
                    blocks.append(('text','అన్ని నమోదుల స్థానం: '+position))
                blocks.append(('table',_grid(headers,display_rows,center=True)))
    if view.unknown:
        blocks += [('heading','ℹ️ సేవా వర్గీకరణ తనిఖీ'),('text','\n'.join(f'{vehicle} ({operation}) • సేవా రకాన్ని నిర్ధారించండి.' for vehicle,operation in view.unknown))]
    actions=_actions(view)
    if actions:
        if view.low:
            actions[0]=actions[0].replace(view.low[0][1]+':',view.low[0][1]+' ('+view.low[0][3]+'):')
        blocks += [('heading','🛠️ తనిఖీ ప్రాధాన్యతలు'),('text','\n'.join('• '+value for value in actions))]
    blocks += [('text',note) for note in view.notes]
    if drive_link:
        blocks += [('heading','📁 Google Drive'),('text',_source_note(view,cached)),('text',drive_link)]
    blocks.append(('text','డిపో ప్రగతి • మనందరి బాధ్యత!'))
    return _telegram_chunks(blocks)


def write_daily_html(source_path, depot, report_date, source_link='', cached=False, current=False):
    source = Path(source_path)
    target = source.with_name(source.stem+'_'+VERSION+('_current' if current else '')+'.html')
    rendered = render_daily_html(source.read_text(encoding='utf-8'),depot,report_date,source_link,cached)
    target.write_text(rendered,encoding='utf-8')
    return target
