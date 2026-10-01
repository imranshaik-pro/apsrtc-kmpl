"""Optional depot tyre checks, fetched only on odd resolved report dates.

Endpoints and payload come from the owner's captured rctyre.js. District
responses are filtered by exact depot identity; no vehicle/tyre aliases inferred.
"""

from datetime import date
import re

from bs4 import BeautifulSoup
from requests import RequestException


BASE = "http://103.44.14.20/med/"
SECTION_MARKER = "టైర్ల వివరాలు —"
COMPLETE_MARKER = "టైర్ల వివరాల స్థితి: పూర్తయింది"
REPORTS = (
    ("ముందు స్థానాల్లో RC టైర్లు", "rcpopup.php"),
    ("ఒకే రకం టైర్లు అమర్చని వాహనాలు", "samepopup.php"),
)


def tyre_checks_due(report_date):
    return date.fromisoformat(report_date).day % 2 == 1


def _key(value):
    return re.sub(r"[^a-z0-9]", "", value.casefold())


def parse_tyre_popup(html, depot, report_date):
    soup = BeautifulSoup(html, "html.parser")
    # Validate the report heading, not unrelated fitted-date columns in rows.
    heading = BeautifulSoup(html, "html.parser")
    for table in heading.find_all("table"):
        table.decompose()
    text = heading.get_text(" ", strip=True)
    dates = re.findall(r"\b(\d{1,2})/(\d{1,2})/(\d{4})\b", text)
    expected = date.fromisoformat(report_date)
    if not dates or any(date(int(y), int(m), int(d)) != expected for d, m, y in dates):
        raise ValueError("Tyre source date is missing or differs from report date")
    for table in soup.find_all("table"):
        headers = None
        rows = []
        spans = {}
        for tr in table.find_all("tr"):
            cells = tr.find_all(["th", "td"], recursive=False)
            if not cells:
                continue
            values = []
            column = 0

            def inherited():
                nonlocal column
                while column in spans:
                    value, remaining = spans[column]
                    values.append(value)
                    if remaining == 1:
                        del spans[column]
                    else:
                        spans[column] = (value, remaining - 1)
                    column += 1

            for cell in cells:
                inherited()
                value = cell.get_text(" ", strip=True)
                for _ in range(int(cell.get("colspan", 1))):
                    values.append(value)
                    rowspan = int(cell.get("rowspan", 1))
                    if rowspan > 1:
                        spans[column] = (value, rowspan - 1)
                    column += 1
            inherited()
            keys = [_key(v) for v in values]
            depot_columns = [i for i, k in enumerate(keys) if k == "depot"]
            vehicle_columns = [i for i, k in enumerate(keys) if k in {"vehno", "vehicleno", "vehiclenumber"}]
            if depot_columns and vehicle_columns:
                if "tyreposition" not in keys:
                    raise ValueError("Tyre position column is missing")
                headers = values
                depot_column, vehicle_column = depot_columns[0], vehicle_columns[0]
                position_column = keys.index("tyreposition")
                continue
            if headers is None:
                continue
            if len(values) != len(headers):
                # Explicit empty-result rows can span the table; other malformed
                # rows must not be quietly interpreted as zero vehicles.
                if len(set(values)) == 1 and re.search(r"no (?:data|records|vehicles)", values[0], re.I):
                    continue
                raise ValueError("Unexpected tyre table row shape")
            if _key(values[depot_column]) != _key(depot):
                continue
            if not values[vehicle_column]:
                raise ValueError("Tyre row has no vehicle number")
            if not values[position_column]:
                raise ValueError("Tyre row has no position")
            rows.append(dict(zip(headers, values)))
        if headers is not None:
            # Preserve distinct tyre positions, even on the same vehicle.
            unique = {tuple(row.items()): row for row in rows}
            return list(unique.values()), headers[vehicle_column]
    raise ValueError("Recognized depot/vehicle tyre table is missing")


def build_tyre_checks(session, report_date, depot, region_code):
    if not tyre_checks_due(report_date):
        return "", True
    dt = date.fromisoformat(report_date)
    source_date = f"{dt.day}/{dt.month}/{dt.year}"
    lines = [f"{SECTION_MARKER} {depot} | {report_date}"]
    complete = True
    try:
        response = session.post(BASE + "rc_tyres_front1.php", data={"fyymm": source_date}, timeout=30)
        response.raise_for_status()
    except RequestException:
        return "\n".join(lines + ["టైర్ల వివరాలు అందుబాటులో లేవు: మూల నివేదిక పొందలేకపోయాము."]), False
    for title, endpoint in REPORTS:
        try:
            response = session.post(BASE + endpoint, data={"dt": source_date, "regn": region_code, "dept": ""}, timeout=30)
            response.raise_for_status()
            rows, vehicle_header = parse_tyre_popup(response.text, depot, report_date)
            vehicles = list(dict.fromkeys(row[vehicle_header] for row in rows))
            lines.append(f"\n{title}\nవాహనాలు: {len(vehicles)} | టైర్ల నమోదులు: {len(rows)}")
            if not rows:
                lines.append("ఈ డిపోకు సంబంధించిన వాహనాలు లేవు.")
            for vehicle in vehicles:
                positions = list(dict.fromkeys(
                    value for row in rows if row[vehicle_header] == vehicle
                    for key, value in row.items() if _key(key) == "tyreposition"
                ))
                lines.append(f"వాహనం {vehicle} — టైర్ పొజిషన్లు: {', '.join(positions)}")
        except (RequestException, ValueError):
            complete = False
            lines.append(f"\n{title}: వివరాలు అందుబాటులో లేవు.")
    if complete:
        lines.append(COMPLETE_MARKER)
    return "\n".join(lines), complete


def append_tyre_checks(report, session, report_date, depot, region_code):
    section, complete = build_tyre_checks(session, report_date, depot, region_code)
    base = report.split(SECTION_MARKER, 1)[0].rstrip()
    return (base + "\n\n" + section if section else base), complete
