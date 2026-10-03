from html.parser import HTMLParser
from html import unescape
import pytest
from src.reporting.telegram_daily import format_daily_telegram


class CheckHTML(HTMLParser):
    def __init__(self):
        super().__init__(); self.stack = []
    def handle_starttag(self, tag, attrs):
        assert tag in {'b', 'pre'}
        self.stack.append(tag)
    def handle_endtag(self, tag):
        assert self.stack.pop() == tag


def test_preserves_values_and_removes_duplicate_headings_and_code_warning():
    report = '''APSRTC — PRODDUTUR DEPOT — DAILY HSD KMPL
Report date: 30 September 2026
🌟 PRODDUTUR డిపో :: 30/09/2026
Metric            TOT       NAC       AC
Target            5.03      —         —
ఈ రోజు            5.17      —         —
ఈ రోజు వరకు       4.98      —         —
━━━━━━━━━━━━━━━━━━
⚠️ *తక్కువ సామర్థ్య వాహనాలు* (రోజు KMPL ≤ 5.00):
  ` 1. 29Z2857 (OR)` : 4.05 | 5.94
⚠️ *జాగ్రత్త:* operation type
దయచేసి 'src/reporting/vehicle_summary.py' లో NAC_CODES / AC_CODES ను సమీక్షించండి.
వాహనాలు: 07Z0158 (op_type: CG)
టైర్ల వివరాలు — PRODDUTUR | 2026-09-30
RNSO/RNSI స్థానాల్లో రిపేర్ టైర్లు అమర్చిన వాహనాలు
వాహనాలు: 2 | టైర్ల నమోదులు: 2
వాహనం 02Z0129 — RNSO'''
    output = '\n'.join(format_daily_telegram(report, 'PRODDUTUR', '2026-09-30'))
    for value in ['5.03', '5.17', '4.98', '29Z2857', '4.05 | 5.94', '07Z0158', 'CG', '02Z0129', 'RNSO']:
        assert value in output
    assert 'src/reporting' not in output and '`' not in output
    assert output.count('PRODDUTUR') == 1
    assert '<b>' in output and '<pre>' in output


@pytest.mark.parametrize('cached', [True, False])
def test_drive_footer_describes_saved_copy_honestly(cached):
    output = '\n'.join(format_daily_telegram('Completed HSD', 'DEPOT', '2026-10-01', 'https://example.org/report', cached))
    assert 'టైర్ల' not in output
    assert 'https://example.org/report' in output


def test_cached_tyre_footer_and_compact_legacy_vehicle_entries():
    report = 'టైర్ల వివరాలు — PRODDUTUR\nవాహనం 39Z0321 — టైర్ పొజిషన్: SPARE1 | టైర్ నం.: A23/0110 | ఉపయోగంలో రోజులు: 182'
    output = '\n'.join(format_daily_telegram(report, 'PRODDUTUR', '2026-09-30', 'https://example.org/report', True))
    assert 'విడిగా చేర్చబడ్డాయి' in output
    table = output.split('<pre>')[1].split('</pre>')[0].splitlines()
    assert [[cell.strip() for cell in line.split('|')] for line in table] == [
        ['వాహనం', 'టైర్ నం.', 'రోజులు'], ['39Z0321', 'A23/0110', '182']
    ]
    assert output.count('SPARE1') == 1
    assert output.count('టైర్ నం.') == 1
    assert 'టైర్ పొజిషన్' not in output and 'ఉపయోగంలో రోజులు:' not in output


def test_current_spare_table_preserves_all_nine_source_records_in_telegram():
    from test_daily_tyre_checks import Session, SPARE_HTML
    from src.reporting.tyre_checks import build_spare_snapshot, parse_spare_tyres
    report = build_spare_snapshot(Session(), 'PRODDUTUR')
    output = '\n'.join(format_daily_telegram(report, 'PRODDUTUR', '2026-09-30'))
    table = output.split('<pre>')[1].split('</pre>')[0].splitlines()
    displayed = [[cell.strip() for cell in line.split('|')] for line in table[1:]]
    source, _ = parse_spare_tyres(SPARE_HTML, 'PRODDUTUR')
    assert {row['position'] for row in source} == {'SPARE1'}
    assert displayed == [[row[key] for key in ('vehiclenum', 'rtctyreno', 'numofdaysinuse')] for row in source]
    assert output.count('SPARE1') == 1
    assert len(displayed) == 9
    assert output.count('టైర్ నం.') == output.count('రోజులు') == 1


def test_slab_table_keeps_continuation_counts_in_their_columns():
    report = '''Slab     |Type      |EX|IH|OR|UD|Total
---------|----------|--|--|--|--|-----
<=5.00   |రోజు      | 4| 3| 9| 2|   18
         |ఈరోజు వరకు|10| 7|10| 2|   29
━━━━━━━━━━━━━━━━━━'''
    output = '\n'.join(format_daily_telegram(report, 'PRODDUTUR', '2026-09-30'))
    table = output.split('<pre>')[1].split('</pre>')[0].splitlines()
    assert [[cell.strip() for cell in row.split('|')] for row in table] == [
        ['Slab', 'Period', 'EX', 'IH', 'OR', 'UD', 'Total'],
        ['&lt;=5.00', 'Day', '4', '3', '9', '2', '18'],
        ['', 'Upto', '10', '7', '10', '2', '29'],
    ]
    visible = [unescape(row) for row in table]
    assert all([i for i, value in enumerate(row) if value == '|'] == [i for i, value in enumerate(visible[0]) if value == '|'] for row in visible)


def test_large_reports_escape_values_and_each_chunk_has_balanced_tags():
    report = 'Metric TOT NAC AC\n' + '\n'.join('V<&> "' * 30 for _ in range(80))
    chunks = format_daily_telegram(report, 'DEPOT<&>', '2026-10-01')
    assert len(chunks) > 1
    for chunk in chunks:
        assert len(chunk.encode('utf-16-le')) // 2 <= 4000
        validator = CheckHTML(); validator.feed(chunk); validator.close()
        assert validator.stack == []
    assert 'DEPOT&lt;&amp;&gt;' in chunks[0]


def test_mismatch_count_described_as_source_records():
    text = 'ఒకే రకం టైర్లు అమర్చని వాహనాలు\nవాహనాలు: 6 | టైర్ల నమోదులు: 40'
    output = '\n'.join(format_daily_telegram(text, 'PRODDUTUR', '2026-09-30'))
    assert 'మూల నివేదికలో టైర్ల నమోదులు: 40' in output
