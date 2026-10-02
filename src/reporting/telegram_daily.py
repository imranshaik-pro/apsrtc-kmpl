"""Presentation only: render completed daily text as safe Telegram HTML."""
from html import escape
import re


def _block(kind, text):
    if kind == 'table':
        return '<pre>' + escape(text) + '</pre>'
    if kind == 'heading':
        return '<b>' + escape(text) + '</b>'
    return escape(text)


def format_daily_telegram(report, depot, report_date, drive_link='', cached=False):
    """Return valid, individually bounded HTML messages; do not change KPI data."""
    blocks = [('heading', f'🚌 APSRTC • {depot}'), ('text', f'రోజువారీ నివేదిక | {report_date}')]
    lines = report.splitlines()
    i = 0
    while i < len(lines):
        line = lines[i].strip()
        i += 1
        if not line or line.startswith(('APSRTC —', 'Report date:', '🌟', '🛢️', '✅ తక్కువ KMPL', '━━━━━━━━')):
            continue
        if line.startswith('Metric'):
            blocks.append(('heading', '⛽ HSD KMPL'))
            # All reported TOT/NAC/AC values retained in a short monospaced grid.
            table = [line.replace('Metric', 'KPI', 1)]
            while i < len(lines) and not lines[i].startswith('━━━━━━━━'):
                value = lines[i].strip()
                if value and not set(value) <= {'─', '-'}:
                    table.append(value)
                i += 1
            blocks.append(('table', '\n'.join(table)))
            continue
        if line.startswith('Slab'):
            table = [line.replace('Type', 'Period').replace('Total', 'Tot')]
            while i < len(lines) and not lines[i].startswith('━━━━━━━━'):
                value = lines[i].strip()
                if value and not re.fullmatch(r'[-|]+', value):
                    table.append(value.replace('ఈరోజు వరకు', 'Upto').replace('రోజు', 'Day'))
                i += 1
            blocks.append(('text', 'Day = రోజు | Upto = ఈరోజు వరకు'))
            blocks.append(('table', '\n'.join(table)))
            continue
        if line.startswith('⚠️ *తక్కువ సామర్థ్య'):
            blocks.append(('heading', '⚠️ తక్కువ KMPL • చర్య అవసరం'))
            blocks.append(('text', 'రోజు KMPL ≤ 5.00 | రోజు / ఈరోజు వరకు'))
            continue
        if line.startswith('`రోజు`'):
            continue
        if line.startswith('*రేంజ్'):
            blocks.append(('heading', '📊 KMPL రేంజ్ • వాహనాల సంఖ్య'))
            continue
        if line.startswith('*తక్షణ చర్య!'):
            blocks.append(('text', '🛠️ తక్కువ KMPL వాహనాలపై తనిఖీకి ప్రాధాన్యం ఇవ్వండి.'))
            continue
        if line.startswith('⚠️ *జాగ్రత్త:'):
            blocks.append(('heading', 'ℹ️ వర్గీకరణ తనిఖీ'))
            blocks.append(('text', 'కింది వాహనాల సేవా రకం నిర్ధారించాలి:'))
            continue
        if 'src/reporting/' in line:
            continue
        if line.startswith('టైర్ల వివరాలు —'):
            blocks.append(('heading', '🔧 టైర్ల తనిఖీ'))
            continue
        headings = {
            'ముందు స్థానాల్లో RC టైర్లు': 'RC ముందు టైర్లు',
            'ఒకే రకం టైర్లు అమర్చని వాహనాలు': 'ఒకే రకం టైర్లు అమర్చని వాహనాలు',
            'RNSO/RNSI స్థానాల్లో రిపేర్ టైర్లు అమర్చిన వాహనాలు': 'రిపేర్ టైర్లు • RNSO / RNSI',
            'రెండు నెలలకు పైగా ఉపయోగంలో ఉన్న స్పేర్ టైర్లు': 'స్పేర్ టైర్లు • రెండు నెలలకు పైగా',
        }
        if line in headings:
            blocks.append(('heading', headings[line]))
            continue
        if line.startswith('వాహనాలు:') and i >= 2 and lines[i-2].strip() == 'ఒకే రకం టైర్లు అమర్చని వాహనాలు':
            line = line.replace('టైర్ల నమోదులు:', 'మూల నివేదికలో టైర్ల నమోదులు:')
        line = line.replace('`', '').replace('(op_type:', '(రకం:')
        blocks.append(('text', line))
    if drive_link:
        blocks.append(('heading', '📄 Google Drive'))
        if cached:
            blocks.append(('text', 'సేవ్ చేసిన KMPL నివేదిక; తాజా టైర్ల వివరాలు ఈ సందేశంలో ఉన్నాయి.'))
        else:
            blocks.append(('text', 'ఈ నివేదిక Google Driveలో సేవ్ చేయబడింది.'))
        blocks.append(('text', drive_link))
    # Each fragment owns all its HTML tags, including table continuations.
    fragments = []
    for kind, text in blocks:
        rendered = _block(kind, text)
        if len(rendered) <= 3400:
            fragments.append(rendered)
            continue
        # Conservative escaped-length bound supports large source vehicle lists.
        for raw_line in text.splitlines():
            while raw_line:
                piece, raw_line = raw_line[:450], raw_line[450:]
                fragments.append(_block(kind, piece))
    chunks, current = [], ''
    for fragment in fragments:
        gap = '\n\n' if fragment.startswith('<b>') or fragment.startswith('<pre>') else '\n'
        candidate = current + (gap if current else '') + fragment
        if len(candidate) > 3700 and current:
            chunks.append(current)
            current = fragment
        else:
            current = candidate
    if current:
        chunks.append(current)
    return chunks
