from datetime import datetime
from unittest.mock import patch

import pytest
import requests

import run_automated_daily as runner
from src.reporting.tyre_checks import (
    BASE, SECTION_MARKER, COMPLETE_MARKER, append_tyre_checks,
    build_tyre_checks, parse_tyre_popup, tyre_checks_due,
)
from test_application import FakeSession as DailySession
from src.reporting.application import build_daily_report


def popup(rows="", report_date="1/9/2026"):
    return f"""<h3>VEHICLES AT YSRKADAPA DISTRICT ON {report_date}</h3>
    <table><tr><th>Sno</th><th>District</th><th>Depot</th><th>Veh. No.</th>
    <th>Tyre Position</th><th>Tyre Stage</th><th>RTC No.</th><th>Tyre Make</th>
    <th>Tyre Size</th><th>R/N/TU</th><th>F Mark (Y/N)</th></tr>{rows}</table>"""


def row(number, depot, vehicle, position, rtc):
    return "<tr>" + "".join(f"<td>{v}</td>" for v in (
        number, "YSRKADAPA", depot, vehicle, position, "RC1", rtc,
        "APOLLO", "10.00R20", "R", "N",
    )) + "</tr>"


# Contract fixture using observed source headers and anonymized vehicle IDs.
RC_HTML = popup(row(1, "RAJAMPET", "BUS001", "FNS", "R25/1330") +
                row(2, "RAJAMPET", "BUS001", "FOS", "R25/093") +
                row(3, "PRODDUTUR", "9999999", "FNS", "OTHER"))
MISMATCH_HTML = popup(row(1, "RAJAMPET", "BUS002", "RNS", "M1"))


class Response:
    def __init__(self, text):
        self.text = text

    def raise_for_status(self):
        pass


class Session:
    def __init__(self, broken=None):
        self.calls = []
        self.broken = broken

    def post(self, url, data, timeout):
        self.calls.append((url, data, timeout))
        if url.endswith(self.broken or "NEVER"):
            raise requests.Timeout()
        return Response(RC_HTML if url.endswith("rcpopup.php") else
                        MISMATCH_HTML if url.endswith("samepopup.php") else "summary")


def test_even_date_makes_no_extra_requests():
    s = Session()
    assert append_tyre_checks("Original KMPL", s, "2026-09-02", "RAJAMPET", "YSRKADAPA") == ("Original KMPL", True)
    assert s.calls == []


def test_odd_date_depot_counts_and_exact_payload():
    s = Session()
    text, complete = build_tyre_checks(s, "2026-09-01", "RAJAMPET", "YSRKADAPA")
    assert complete and COMPLETE_MARKER in text
    assert "ముందు స్థానాల్లో RC టైర్లు\nవాహనాలు: 1 | టైర్ల నమోదులు: 2" in text
    assert "ఒకే రకం టైర్లు అమర్చని వాహనాలు\nవాహనాలు: 1 | టైర్ల నమోదులు: 1" in text
    assert "BUS001" in text and "BUS002" in text and "9999999" not in text
    assert "FNS" in text and "FOS" in text
    assert "వాహనం BUS001 — టైర్ పొజిషన్లు: FNS, FOS" in text
    assert "RTC No." not in text and "APOLLO" not in text
    assert s.calls == [
        (BASE + "rc_tyres_front1.php", {"fyymm": "1/9/2026"}, 30),
        (BASE + "rcpopup.php", {"dt": "1/9/2026", "regn": "YSRKADAPA", "dept": ""}, 30),
        (BASE + "samepopup.php", {"dt": "1/9/2026", "regn": "YSRKADAPA", "dept": ""}, 30),
    ]


def test_duplicate_rows_deduplicated_without_losing_positions():
    html = popup(row(1, "RAJAMPET", "V1", "FNS", "T1") * 2 + row(2, "RAJAMPET", "V1", "FOS", "T2"))
    rows, _ = parse_tyre_popup(html, "RAJAMPET", "2026-09-01")
    assert len(rows) == 2


def test_rowspan_vehicle_and_depot_preserved():
    html = "<h3>ON 1/9/2026</h3><table><tr><th>Depot</th><th>Veh. No.</th><th>Tyre Position</th></tr>" + \
        '<tr><td rowspan="2">RAJAMPET</td><td rowspan="2">V1</td><td>FNS</td></tr><tr><td>FOS</td></tr></table>'
    rows, _ = parse_tyre_popup(html, "RAJAMPET", "2026-09-01")
    assert [r["Tyre Position"] for r in rows] == ["FNS", "FOS"]
    assert all(r["Veh. No."] == "V1" for r in rows)


@pytest.mark.parametrize("html", ["<form>Login</form>", popup(report_date="2/9/2026"),
    '<h3>ON 1/9/2026</h3><table><tr><th>Depot</th><th>Veh. No.</th></tr><tr><td>RAJAMPET</td></tr></table>'])
def test_invalid_sources_are_not_zero(html):
    with pytest.raises(ValueError):
        parse_tyre_popup(html, "RAJAMPET", "2026-09-01")


def test_valid_empty_table_is_zero():
    rows, _ = parse_tyre_popup(popup(), "RAJAMPET", "2026-09-01")
    assert rows == []


def test_one_failed_section_keeps_other_section():
    text, complete = append_tyre_checks("KMPL preserved", Session("rcpopup.php"), "2026-09-01", "RAJAMPET", "YSRKADAPA")
    assert text.startswith("KMPL preserved") and not complete
    assert "ముందు స్థానాల్లో RC టైర్లు: వివరాలు అందుబాటులో లేవు." in text
    assert "ఒకే రకం టైర్లు అమర్చని వాహనాలు\nవాహనాలు: 1" in text
    assert COMPLETE_MARKER not in text


def test_summary_failure_stops_popup_requests():
    s = Session("rc_tyres_front1.php")
    text, complete = build_tyre_checks(s, "2026-09-01", "RAJAMPET", "YSRKADAPA")
    assert not complete and "అందుబాటులో లేవు" in text and len(s.calls) == 1


def test_existing_section_replaced_once():
    text, _ = append_tyre_checks("KMPL\n\n" + SECTION_MARKER + " old", Session(), "2026-09-01", "RAJAMPET", "YSRKADAPA")
    assert text.count(SECTION_MARKER) == 1 and " old" not in text


def test_date_resolution_before_odd_day_check():
    class Clock:
        @classmethod
        def now(cls, timezone):
            return datetime(2026, 10, 2, 5, 7, tzinfo=timezone)
    with patch.object(runner, "datetime", Clock):
        for selected, scheduled in [("2026-10-02", False), (None, True)]:
            resolved = runner.resolve_report_date(selected, scheduled)
            assert resolved.isoformat() == "2026-10-01" and tyre_checks_due(resolved.isoformat())
        assert not tyre_checks_due(runner.resolve_report_date("2026-09-30", False).isoformat())
        assert tyre_checks_due(runner.resolve_report_date("2026-09-15", False).isoformat())
        with pytest.raises(ValueError):
            runner.resolve_report_date("2026-10-03", False)


def test_odd_day_application_keeps_base_when_auxiliary_fails():
    class OddSession(DailySession):
        def post(self, url, data, timeout):
            if not url.endswith("vehkmpl.php"):
                raise requests.Timeout()
            return super().post(url, data, timeout)
    text = build_daily_report(OddSession(), "2026-08-19", "PRODDUTUR", "PDTR/PRODDUTUR", "YSRKADAPA")
    assert "DAILY HSD KMPL" in text and "4.84" in text and "టైర్ల వివరాలు అందుబాటులో లేవు" in text


@pytest.mark.parametrize("cached,expect_fetch,expect_update", [
    ("Original HSD report", True, True),
    ("Original HSD report\n" + SECTION_MARKER + "\n" + COMPLETE_MARKER, False, False),
])
def test_cached_odd_report_keeps_hsd_and_file_id(tmp_path, monkeypatch, cached, expect_fetch, expect_update):
    session = Session()
    monkeypatch.setattr(runner, "ROOT", tmp_path)
    monkeypatch.setattr(runner, "find_file", lambda **kw: {"id": "same-id", "webViewLink": "existing-link"})
    def download(file_id, destination):
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_text(cached, encoding="utf-8")
    monkeypatch.setattr(runner, "download_file", download)
    monkeypatch.setattr(runner, "login", lambda: session)
    monkeypatch.setattr(runner, "load_json", lambda path:
        {"daily": {"default_depot": "RAJAMPET", "drive_folder_id": "folder"}} if path == runner.SETTINGS_PATH else
        {"rajampet": {"display_name": "RAJAMPET", "vehicle_depot": "RJPT/RAJAMPET", "region_code": "YSRKADAPA"}})
    updates = []
    monkeypatch.setattr(runner, "update_text_file", lambda path, file_id: updates.append((path.read_text(), file_id)))
    monkeypatch.setattr("sys.argv", ["runner", "--depot", "RAJAMPET", "--date", "2026-09-01"])
    assert runner.main() == 0
    assert bool(session.calls) == expect_fetch and bool(updates) == expect_update
    if updates:
        assert updates[0][0].startswith("Original HSD report") and updates[0][1] == "same-id"


def test_existing_even_report_never_authenticates_for_tyres(tmp_path, monkeypatch):
    monkeypatch.setattr(runner, "ROOT", tmp_path)
    monkeypatch.setattr(runner, "find_file", lambda **kw: {"id": "same-id"})
    def download(file_id, destination):
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_text("HSD report", encoding="utf-8")
    monkeypatch.setattr(runner, "download_file", download)
    monkeypatch.setattr(runner, "login", lambda: pytest.fail("Even date must not fetch tyre data"))
    monkeypatch.setattr(runner, "load_json", lambda path:
        {"daily": {"default_depot": "RAJAMPET", "drive_folder_id": "folder"}} if path == runner.SETTINGS_PATH else
        {"rajampet": {"display_name": "RAJAMPET", "vehicle_depot": "RJPT/RAJAMPET", "region_code": "YSRKADAPA"}})
    monkeypatch.setattr("sys.argv", ["runner", "--depot", "RAJAMPET", "--date", "2026-09-02"])
    assert runner.main() == 0
