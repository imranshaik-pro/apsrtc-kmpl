from html.parser import HTMLParser
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
    assert ('తాజా టైర్ల వివరాలు ఈ సందేశంలో ఉన్నాయి' in output) == cached
    assert 'https://example.org/report' in output


def test_large_reports_escape_values_and_each_chunk_has_balanced_tags():
    report = 'Metric TOT NAC AC\n' + '\n'.join('V<&> "' * 30 for _ in range(80))
    chunks = format_daily_telegram(report, 'DEPOT<&>', '2026-10-01')
    assert len(chunks) > 1
    for chunk in chunks:
        assert len(chunk) <= 3700
        validator = CheckHTML(); validator.feed(chunk); validator.close()
        assert validator.stack == []
    assert 'DEPOT&lt;&amp;&gt;' in chunks[0]


def test_mismatch_count_described_as_source_records():
    text = 'ఒకే రకం టైర్లు అమర్చని వాహనాలు\nవాహనాలు: 6 | టైర్ల నమోదులు: 40'
    output = '\n'.join(format_daily_telegram(text, 'PRODDUTUR', '2026-09-30'))
    assert 'మూల నివేదికలో టైర్ల నమోదులు: 40' in output
