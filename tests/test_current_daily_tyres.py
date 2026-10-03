from datetime import date, datetime
from pathlib import Path
from unittest.mock import patch

import pytest

import run_automated_daily as runner
from src.reporting import tyre_checks


@pytest.mark.parametrize('today', ['2026-10-01', '2026-10-02'])
def test_current_intent_is_independent_of_yesterday_odd_even(today):
    class Clock:
        @classmethod
        def now(cls, timezone):
            return datetime.fromisoformat(today + 'T05:00:00').replace(tzinfo=timezone)
    with patch.object(runner, 'datetime', Clock):
        for selected, scheduled in [(today, False), (None, True), (None, False)]:
            assert runner.current_daily_request(selected, scheduled)
            assert runner.resolve_report_date(selected, scheduled) < date.fromisoformat(today)
        for historical in ['2026-09-29', '2026-09-30']:
            assert not runner.current_daily_request(historical, False)
            assert runner.resolve_report_date(historical, False) == date.fromisoformat(historical)
        with pytest.raises(ValueError):
            runner.resolve_report_date('2026-10-03', False)


@pytest.mark.parametrize('current', [True, False])
@pytest.mark.parametrize('depot', ['PRODDUTUR', 'RAJAMPET'])
@pytest.mark.parametrize('cached', [True, False])
def test_main_gates_tyres_for_all_depots_and_cached_delivery(tmp_path, monkeypatch, current, depot, cached):
    class Clock:
        @classmethod
        def now(cls, timezone):
            assert str(timezone) == 'Asia/Kolkata'
            return datetime(2026, 10, 1, 5, 0, tzinfo=timezone)
    monkeypatch.setattr(runner, 'datetime', Clock)
    monkeypatch.setattr(runner, 'ROOT', tmp_path)
    settings = {'daily': {'default_depot': 'proddutur', 'drive_folder_id': 'FOLDER'}}
    mapping = {depot.lower(): {'display_name': depot, 'vehicle_depot': depot, 'region_code': 'YSRKADAPA'}}
    monkeypatch.setattr(runner, 'load_json', lambda path: settings if path == runner.SETTINGS_PATH else mapping)
    monkeypatch.setattr(runner, 'find_file', lambda **kwargs: {'id': 'CACHED', 'webViewLink': 'existing'} if cached else None)
    old = 'Daily HSD\n\n' + tyre_checks.SECTION_MARKER + ' old snapshot\n'
    def download(file_id, output):
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(old)
    monkeypatch.setattr(runner, 'download_file', download)
    def generate(*args, **kwargs):
        output = tmp_path / 'reports' / f'{depot}_2026-09-30.txt'
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text('Daily HSD\n')
        return type('Result', (), {'stdout': '', 'stderr': '', 'returncode': 0})()
    monkeypatch.setattr(runner.subprocess, 'run', generate)
    tyre_calls = []
    def enrich(output, report_date, selected_depot, region):
        tyre_calls.append((report_date, selected_depot, region))
        assert 'old snapshot' not in output.read_text()
        output.write_text(output.read_text() + tyre_checks.SECTION_MARKER + ' fresh snapshot\n')
    monkeypatch.setattr(tyre_checks, 'enrich_daily_file', enrich)
    uploads = []
    monkeypatch.setattr(runner, 'upload_file', lambda output, **kwargs: uploads.append(output) or {'id': 'NEW'})
    monkeypatch.setattr(runner, 'publish_styled_report', lambda *args, **kwargs: None)
    monkeypatch.setattr(runner.sys, 'argv', ['runner', '--depot', depot, '--date', '2026-10-01' if current else '2026-09-30'])
    assert runner.main() == 0
    assert len(tyre_calls) == int(current)
    if current:
        assert tyre_calls == [('2026-09-30', depot, 'YSRKADAPA')]
    text = (tmp_path / 'reports' / f'{depot}_2026-09-30.txt').read_text()
    assert text.startswith('Daily HSD\n')
    assert ('fresh snapshot' in text) == current
    assert 'old snapshot' not in text
    assert len(uploads) == int(not cached)


def test_scheduled_mode_includes_tyres(tmp_path, monkeypatch):
    assert runner.current_daily_request('2026-09-01', True)
