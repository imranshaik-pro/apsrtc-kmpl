from html.parser import HTMLParser
from html import unescape
import hashlib
import json
from pathlib import Path

from bs4 import BeautifulSoup
import pytest

from src.reporting.daily_template import (
    ASSETS, CSS, VERSION, kpi_rows, read_daily_view, render_daily_html,
    render_daily_telegram, upto_shares, write_daily_html,
)

FIXTURES = Path(__file__).parent / 'fixtures'
SAMPLE = (FIXTURES / 'proddutur-daily-2026-09-30.txt').read_text()
LINK = 'https://drive.google.com/file/d/17HG-Fp_rw7y1SnAg_CTuQCzYLVtBDb_i/view?usp=drivesdk'


def rows(table):
    return [[cell.get_text(strip=True) for cell in row.find_all(['th', 'td'])]
            for row in table.find_all('tr')]


def test_approved_model_all_tables_values_and_section_order():
    approved = json.loads((FIXTURES / 'daily-v1-approved-layout.json').read_text())
    generated = BeautifulSoup(render_daily_html(SAMPLE, 'PRODDUTUR', '2026-09-30', LINK, True), 'html.parser')
    assert [tag.get_text(strip=True) for tag in generated.select('section h2')] == approved['section_headings']
    assert [rows(table) for table in generated.select('section table')] == approved['tables']
    assert generated.select_one('meta[name="daily-template"]')['content'] == VERSION
    assert not generated.select('.review, .proof')
    assert len(generated.select('.card.good')) == len(generated.select('.card.bad')) == 1


def test_locked_styles_and_exact_embedded_fonts():
    manifest = json.loads((ASSETS / 'daily-v1.json').read_text())
    assert hashlib.sha256(CSS.read_bytes()).hexdigest() == manifest['css_sha256']
    for name, digest in manifest['font_sha256'].items():
        assert hashlib.sha256((ASSETS / name).read_bytes()).hexdigest() == digest
    html = render_daily_html(SAMPLE, 'PRODDUTUR', '2026-09-30')
    assert html.count('data:font/ttf;base64,') == 3
    assert 'SIL OPEN FONT LICENSE' in html
    assert 'fonts.googleapis.com' not in html


def test_telegram_preserves_every_vehicle_and_tyre_association():
    approved = json.loads((FIXTURES / 'daily-v1-approved-layout.json').read_text())
    messages = render_daily_telegram(SAMPLE, 'PRODDUTUR', '2026-09-30', LINK, True)
    assert len(messages) == 1
    soup = BeautifulSoup(messages[0], 'html.parser')
    grids = [[list(map(str.strip, line.split('|'))) for line in block.get_text().splitlines()]
             for block in soup.select('pre')]
    assert grids[1][1:] == approved['tables'][1][1:]
    assert grids[3:] == approved['tables'][3:]
    # The table headers occur once, rather than repeating labels on each vehicle.
    assert messages[0].count('టైర్ నం.') == 1
    assert 'వాహనం 39Z0321' not in messages[0]
    assert 'టైర్ పొజిషన్లు:' not in messages[0]
    assert 'src/reporting/' not in messages[0]
    assert '07Z0158 (CG)' in messages[0]
    assert '2026-10-01' in messages[0]


def test_derived_differences_and_count_shares_are_not_root_causes():
    view = read_daily_view(SAMPLE, 'PRODDUTUR', '2026-09-30')
    assert kpi_rows(view.metrics['TOT'])[0][3] == '+0.14'
    assert kpi_rows(view.metrics['TOT'])[1][3] == '-0.05'
    assert upto_shares(view) == [('EX', '10', '13', '76.9%'), ('IH', '7', '12', '58.3%')]
    result = '\n'.join(render_daily_telegram(SAMPLE, 'PRODDUTUR', '2026-09-30'))
    assert 'కారణ నిర్ధారణ కావు' in result
    assert 'వెంటనే తొలగించాలి' not in result
    assert 'మూల నివేదికలో టైర్ల నమోదులు: 40' in result


def test_other_depots_dates_and_untrusted_values_keep_the_layout():
    report = SAMPLE.replace('29Z2857', 'BUS<&>01')
    html = render_daily_html(report, 'RAJAMPET<&>', '2026-10-01', 'javascript:alert(1)')
    soup = BeautifulSoup(html, 'html.parser')
    assert 'RAJAMPET<&> DEPOT' in soup.select_one('.brand').get_text()
    assert '01 October 2026 | గురువారం' in soup.select_one('.period').get_text()
    assert soup.select_one('.low tbody td:nth-child(2)').get_text() == 'BUS<&>01'
    assert not soup.select('script, a[href^="javascript:"]')
    assert 'PRODDUTUR' not in soup.get_text()
    assert len(soup.select('section table')) == 6


def test_tot_nac_ac_source_values_are_all_preserved():
    from test_application import FakeSession
    from src.reporting.application import build_daily_report
    source = build_daily_report(FakeSession(), '2026-08-18', 'PRODDUTUR', 'PDTR/PRODDUTUR', 'YSRKADAPA')
    html = BeautifulSoup(render_daily_html(source, 'PRODDUTUR', '2026-08-18'), 'html.parser')
    tables = html.select('section table.num')[:3]
    assert len(tables) == 3
    assert [rows(table)[1][1:3] for table in tables] == [['5.03', '4.84'], ['5.05', '4.87'], ['—', '3.68']]
    assert rows(tables[2])[1][-1] == '—'
    text = '\n'.join(render_daily_telegram(source, 'PRODDUTUR', '2026-08-18'))
    for value in ('5.03', '4.84', '5.05', '4.87', '3.68', '3.73', '4.11', '3.79'):
        assert value in text


@pytest.mark.parametrize('target,day', [('—','5.17'), ('5.03','—'), ('NaN','5.17')])
def test_missing_values_do_not_create_zero_or_performance_claims(target, day):
    source = f'Metric TOT NAC AC\nTarget {target} — —\nఈ రోజు {day} — —\nఈ రోజు వరకు — — —'
    text = '\n'.join(render_daily_telegram(source, 'DEPOT', '2026-10-01'))
    assert 'టార్గెట్ కంటే' not in text
    assert '+0.00' not in text
    assert target in text and day in text


def test_zero_tyres_omitted_unavailable_preserved_and_no_snapshot_invented():
    base = SAMPLE.split('టైర్ల వివరాలు —')[0]
    for render in (render_daily_html, render_daily_telegram):
        output = render(base, 'PRODDUTUR', '2026-09-30')
        text = output if isinstance(output,str) else '\n'.join(output)
        assert '🛞' not in text and 'టైర్ల నివేదిక' not in text
        unavailable = render(base+'టైర్ల వివరాలు —\nముందు స్థానాల్లో RC టైర్లు: వివరాలు అందుబాటులో లేవు.', 'PRODDUTUR', '2026-09-30')
        text = unavailable if isinstance(unavailable,str) else '\n'.join(unavailable)
        assert 'అందుబాటులో లేవు' in text
        assert 'RC ముందు టైర్లు' in text
        assert 'మూల నివేదిక తేదీ:' not in text


class BalancedHTML(HTMLParser):
    def __init__(self):
        super().__init__(); self.stack=[]
    def handle_starttag(self,tag,attrs):
        assert tag in {'b','pre'}; self.stack.append(tag)
    def handle_endtag(self,tag):
        assert self.stack.pop()==tag


def test_long_telegram_tables_keep_rows_and_headers_within_utf16_limit():
    source = 'టైర్ల వివరాలు —\nఒకే రకం టైర్లు అమర్చని వాహనాలు\nవాహనాలు: 180 | టైర్ల నమోదులు: 180\nవాహనం | స్థానాలు\n'
    source += '\n'.join(f'BUS{i:03d}<&> | FNS, FOS, RNSI, 🚌' for i in range(180))
    chunks = render_daily_telegram(source, 'DEPOT', '2026-10-01')
    assert len(chunks)>1
    for chunk in chunks:
        assert len(chunk.encode('utf-16-le'))//2<=4000
        parser=BalancedHTML();parser.feed(chunk);parser.close();assert not parser.stack
    combined=unescape('\n'.join(chunks))
    for i in range(180):
        assert combined.count(f'BUS{i:03d}<&>')==1


def test_current_and_historical_companions_do_not_overwrite_each_other(tmp_path):
    source=tmp_path/'PRODDUTUR_2026-09-30.txt'
    source.write_text(SAMPLE)
    historical=write_daily_html(source,'PRODDUTUR','2026-09-30',current=False)
    current=write_daily_html(source,'PRODDUTUR','2026-09-30',current=True)
    assert current!=historical
    assert current.name=='PRODDUTUR_2026-09-30_daily-v1_current.html'
    assert historical.name=='PRODDUTUR_2026-09-30_daily-v1.html'
    assert source.read_text()==SAMPLE


def test_real_tot_nac_ac_report_keeps_its_footer_in_one_telegram_message():
    source = (FIXTURES / 'proddutur-daily-2026-10-01.txt').read_text()
    link = 'https://drive.google.com/file/d/1qMROIj6rDS3ZfYWUJ70rERzC29VtqP9i/view?usp=drivesdk'
    messages = render_daily_telegram(source, 'PRODDUTUR', '2026-10-01', link, True)
    assert len(messages) == 1
    assert len(messages[0].encode('utf-16-le')) // 2 <= 4000
    soup = BeautifulSoup(messages[0], 'html.parser')
    tables = soup.select('pre')
    assert len(tables) == 8
    assert all(value in tables[0].get_text() for value in ('5.03', '5.37', '+0.34'))
    assert '5.43' in tables[1].get_text() and '3.44' in tables[2].get_text()
    assert '70' in tables[4].get_text()
    assert '39Z0321' in tables[-1].get_text() and '183' in tables[-1].get_text()
    assert '2026-10-02' in messages[0]
    assert link in messages[0] and messages[0].endswith('డిపో ప్రగతి • మనందరి బాధ్యత!')
