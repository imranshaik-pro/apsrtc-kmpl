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
    assert complete
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




def test_zero_results_preserve_daily_exactly():
    class EmptySession(Session):
        def post(self, url, data, timeout):
            return Response(popup())
    original = "Daily HSD\n"
    assert append_tyre_checks(original, EmptySession(), "2026-09-01", "RAJAMPET", "YSRKADAPA") == (original, True)


def test_zero_mismatch_hidden_with_positive_rc():
    class OnlyRC(Session):
        def post(self, url, data, timeout):
            return Response(popup() if url.endswith("samepopup.php") else RC_HTML)
    text, complete = build_tyre_checks(OnlyRC(), "2026-09-01", "RAJAMPET", "YSRKADAPA")
    assert complete and "BUS001" in text
    assert "ఒకే రకం టైర్లు అమర్చని వాహనాలు" not in text


def test_auxiliary_login_failure_preserves_daily(tmp_path):
    from src.reporting.tyre_checks import enrich_daily_file
    path = tmp_path / "daily.txt"
    path.write_text("Completed HSD\n")
    def fail():
        raise RuntimeError("Unavailable")
    assert not enrich_daily_file(path, "2026-09-01", "RAJAMPET", "YSRKADAPA", fail)
    assert path.read_text().startswith("Completed HSD\n")


def test_even_enrichment_skips_auth(tmp_path):
    from src.reporting.tyre_checks import enrich_daily_file
    path = tmp_path / "daily.txt"
    path.write_text("HSD\n")
    assert enrich_daily_file(path, "2026-09-02", "RAJAMPET", "YSRKADAPA", lambda: pytest.fail("no login"))
    assert path.read_text() == "HSD\n"


def test_daily_finishes_before_tyres(tmp_path, monkeypatch):
    from datetime import date
    from src.reporting import tyre_checks
    monkeypatch.setattr(runner, "ROOT", tmp_path)
    path = tmp_path / "reports" / "RAJAMPET_2026-09-01.txt"
    def generate(*args, **kwargs):
        path.parent.mkdir()
        path.write_text("Completed HSD")
        return type("Result", (), {"stdout": "", "stderr": "", "returncode": 0})()
    monkeypatch.setattr(runner.subprocess, "run", generate)
    calls = []
    monkeypatch.setattr(tyre_checks, "enrich_daily_file", lambda output, *args: calls.append(output.read_text()))
    assert runner.run_report("RAJAMPET", {"vehicle_depot": "RJPT/RAJAMPET", "region_code": "YSRKADAPA"}, date(2026, 9, 1)) == path
    assert calls == ["Completed HSD"]
