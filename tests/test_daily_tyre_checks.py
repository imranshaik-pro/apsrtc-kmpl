from pathlib import Path
from datetime import datetime
from unittest.mock import patch
import re

import pytest
import requests

import run_automated_daily as runner
from src.reporting.tyre_checks import (
    SPARE_URL, SPARE_TITLE, spare_depot_id, parse_spare_tyres, build_spare_snapshot,
    BASE, SECTION_MARKER, COMPLETE_MARKER, append_tyre_checks,
    build_tyre_checks, parse_tyre_popup,
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
REPAIR_HTML = popup(row(1, "RAJAMPET", "BUS003", "RNSO", "REP1") +
                    row(2, "PRODDUTUR", "OTHER_DEPOT", "RNSI", "REP2"))


SPARE_HTML = (Path(__file__).parent / "fixtures" / "spare-tyres-proddutur.html").read_text()


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
        if url == SPARE_URL:
            return Response(SPARE_HTML)
        return Response(RC_HTML if url.endswith("rcpopup.php") else
                        MISMATCH_HTML if url.endswith("samepopup.php") else
                        REPAIR_HTML if url.endswith("repairpopup.php") else "summary")


def test_current_request_depot_counts_and_exact_payload():
    s = Session()
    text, complete = build_tyre_checks(s, "2026-09-01", "RAJAMPET", "YSRKADAPA")
    assert complete
    assert "ముందు స్థానాల్లో RC టైర్లు\nవాహనాలు: 1 | టైర్ల నమోదులు: 2" in text
    assert "ఒకే రకం టైర్లు అమర్చని వాహనాలు\nవాహనాలు: 1 | టైర్ల నమోదులు: 1" in text
    assert "BUS001" in text and "BUS002" in text and "9999999" not in text
    assert "FNS" in text and "FOS" in text
    assert re.search(r"BUS001\s*\| FNS, FOS", text)
    assert "స్థానాలు" in text and "వాహనం BUS001" not in text
    assert "RTC No." not in text and "APOLLO" not in text
    assert s.calls == [
        (BASE + "rc_tyres_front1.php", {"fyymm": "1/9/2026"}, 30),
        (BASE + "rcpopup.php", {"dt": "1/9/2026", "regn": "YSRKADAPA", "dept": ""}, 30),
        (BASE + "samepopup.php", {"dt": "1/9/2026", "regn": "YSRKADAPA", "dept": ""}, 30),
        (BASE + "fitted_repair1.php", {"fyymm": "1/9/2026"}, 30),
        (BASE + "repairpopup.php", {"dt": "1/9/2026", "regn": "YSRKADAPA", "dept": ""}, 30),
        (SPARE_URL, {"depot_id": ""}, 30),
        (SPARE_URL, {"depot_id": "115"}, 30),
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


def test_front_failure_keeps_independent_repair_and_spare():
    s = Session("rc_tyres_front1.php")
    text, complete = build_tyre_checks(s, "2026-09-01", "RAJAMPET", "YSRKADAPA")
    assert not complete and "అందుబాటులో లేవు" in text
    assert not any(url.endswith(("rcpopup.php", "samepopup.php")) for url, _, _ in s.calls)
    assert "BUS003" in text and any(url == SPARE_URL for url, _, _ in s.calls)


def test_existing_section_replaced_once():
    text, _ = append_tyre_checks("KMPL\n\n" + SECTION_MARKER + " old", Session(), "2026-09-01", "RAJAMPET", "YSRKADAPA")
    assert text.count(SECTION_MARKER) == 1 and " old" not in text


def test_zero_results_preserve_daily_exactly():
    class EmptySession(Session):
        def post(self, url, data, timeout):
            if url == SPARE_URL:
                return super().post(url, data, timeout)
            return Response(popup())
    original = "Daily HSD\n"
    assert append_tyre_checks(original, EmptySession(), "2026-09-01", "RAJAMPET", "YSRKADAPA") == (original, True)


def test_zero_mismatch_hidden_with_positive_rc():
    class OnlyRC(Session):
        def post(self, url, data, timeout):
            if url == SPARE_URL:
                return super().post(url, data, timeout)
            return Response(popup() if url.endswith(("samepopup.php", "repairpopup.php")) else RC_HTML)
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
    assert runner.run_report("RAJAMPET", {"vehicle_depot": "RJPT/RAJAMPET", "region_code": "YSRKADAPA"}, date(2026, 9, 1), include_tyres=True) == path
    assert calls == ["Completed HSD"]


def test_repair_category_depot_vehicle_position_and_count():
    text, complete = build_tyre_checks(Session(), "2026-09-01", "RAJAMPET", "YSRKADAPA")
    assert complete
    assert "RNSO/RNSI స్థానాల్లో రిపేర్ టైర్లు అమర్చిన వాహనాలు\nవాహనాలు: 1 | టైర్ల నమోదులు: 1" in text
    assert re.search(r"BUS003\s*\| RNSO", text)
    assert "OTHER_DEPOT" not in text


@pytest.mark.parametrize("endpoint", ["fitted_repair1.php", "repairpopup.php"])
def test_repair_failure_preserves_daily_and_other_categories(endpoint):
    session = Session(endpoint)
    text, complete = append_tyre_checks("Completed HSD", session, "2026-09-01", "RAJAMPET", "YSRKADAPA")
    assert not complete and text.startswith("Completed HSD")
    assert "BUS001" in text and "BUS002" in text
    assert "రిపేర్ టైర్లు అమర్చిన వాహనాలు: వివరాలు అందుబాటులో లేవు." in text
    if endpoint == "fitted_repair1.php":
        assert not any(url.endswith("repairpopup.php") for url, _, _ in session.calls)


def test_wrong_repair_date_is_unavailable_not_zero():
    class WrongDate(Session):
        def post(self, url, data, timeout):
            if url.endswith("repairpopup.php"):
                return Response(REPAIR_HTML.replace("1/9/2026", "3/9/2026"))
            return super().post(url, data, timeout)
    text, complete = build_tyre_checks(WrongDate(), "2026-09-01", "RAJAMPET", "YSRKADAPA")
    assert not complete and "BUS003" not in text and "BUS001" in text


def test_zero_repair_category_is_hidden():
    class NoRepair(Session):
        def post(self, url, data, timeout):
            if url.endswith("repairpopup.php"):
                return Response(popup())
            return super().post(url, data, timeout)
    text, complete = build_tyre_checks(NoRepair(), "2026-09-01", "RAJAMPET", "YSRKADAPA")
    assert complete and "రిపేర్ టైర్లు" not in text and "BUS001" in text


def test_owner_spare_source_nine_proddutur_records_and_ids():
    assert spare_depot_id(SPARE_HTML, "PRODDUTUR") == "114"
    assert spare_depot_id(SPARE_HTML, "RAJAMPET") == "115"
    rows, run_date = parse_spare_tyres(SPARE_HTML, "PRODDUTUR")
    assert len(rows) == 9 and run_date == "2026-10-01"
    assert rows[0]["vehiclenum"] == "39Z0321"
    assert rows[0]["position"] == "SPARE1" and rows[0]["numofdaysinuse"] == "182"
    assert parse_spare_tyres(SPARE_HTML, "RAJAMPET") == ([], None)


def test_snapshot_date_is_independent_of_historical_daily_date():
    session = Session()
    text, complete = build_tyre_checks(session, "2026-09-01", "PRODDUTUR", "YSRKADAPA")
    assert complete
    assert "మూల నివేదిక తేదీ: 2026-10-01" in text
    assert "వాహనాలు: 9 | టైర్ల నమోదులు: 9" in text
    assert "39Z0321" in text and "SPARE1" in text and "182" in text
    assert session.calls[-1] == (SPARE_URL, {"depot_id": "114"}, 30)


@pytest.mark.parametrize("html", ["<form>Login</form>", SPARE_HTML.replace("01-10-2026", "99-10-2026"),
    SPARE_HTML.replace("<th>Position</th>", "<th>Absent</th>"),
    SPARE_HTML.replace("182</td>", "unknown</td>")])
def test_invalid_spare_sources_are_not_zero(html):
    with pytest.raises(ValueError):
        parse_spare_tyres(html, "PRODDUTUR")


def test_spare_failure_keeps_other_categories_and_daily():
    text, complete = append_tyre_checks("Completed HSD", Session("spare_tyre.php"), "2026-09-01", "RAJAMPET", "YSRKADAPA")
    assert not complete and text.startswith("Completed HSD")
    assert "BUS001" in text and "BUS003" in text
    assert SPARE_TITLE + ": వివరాలు అందుబాటులో లేవు." in text


def test_unknown_spare_depot_does_not_send_unverified_id():
    session = Session()
    with pytest.raises(ValueError):
        build_spare_snapshot(session, "UNKNOWN")
    assert len(session.calls) == 1


def test_mixed_spare_run_dates_rejected():
    with pytest.raises(ValueError):
        parse_spare_tyres(SPARE_HTML.replace("01-10-2026", "02-10-2026", 1), "PRODDUTUR")


def test_spare_duplicate_rows_keep_one_tyre():
    from bs4 import BeautifulSoup
    soup = BeautifulSoup(SPARE_HTML, "html.parser")
    table = soup.find("table")
    first = table.find_all("tr")[1]
    duplicate = BeautifulSoup(str(first), "html.parser").find("tr")
    duplicate.find("td").string = "10"
    table.append(duplicate)
    rows, _ = parse_spare_tyres(str(soup), "PRODDUTUR")
    assert len(rows) == 9


def test_empty_spare_table_is_zero_and_hidden():
    from bs4 import BeautifulSoup
    soup = BeautifulSoup(SPARE_HTML, "html.parser")
    for tr in soup.find("table").find_all("tr")[1:]:
        tr.decompose()
    class EmptySpare(Session):
        def post(self, url, data, timeout):
            if url == SPARE_URL:
                return Response(str(soup))
            return super().post(url, data, timeout)
    assert build_spare_snapshot(EmptySpare(), "PRODDUTUR") == ""
