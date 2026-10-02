"""Optional depot tyre checks, fetched only for current daily requests.

Endpoints and payload come from the owner's captured rctyre.js. District
responses are filtered by exact depot identity; no vehicle/tyre aliases inferred.
"""

from datetime import date
import re

from bs4 import BeautifulSoup
from requests import RequestException


BASE = "http://103.44.14.20/med/"
SPARE_URL = "http://103.44.14.20/tyres/spare_tyre.php"
SPARE_TITLE = "రెండు నెలలకు పైగా ఉపయోగంలో ఉన్న స్పేర్ టైర్లు"
SECTION_MARKER = "టైర్ల వివరాలు —"
COMPLETE_MARKER = "టైర్ల వివరాల స్థితి: పూర్తయింది"
REPORTS = (
    ("ముందు స్థానాల్లో RC టైర్లు", "rcpopup.php"),
    ("ఒకే రకం టైర్లు అమర్చని వాహనాలు", "samepopup.php"),
    ("RNSO/RNSI స్థానాల్లో రిపేర్ టైర్లు అమర్చిన వాహనాలు", "repairpopup.php"),
)


def _key(value):
    return re.sub(r"[^a-z0-9]", "", value.casefold())


def format_tyre_table(rows, spare=False):
    """Present source values under one Telugu column header."""
    headers = ("వాహనం", "స్థానం", "టైర్ నం.", "రోజులు") if spare else ("వాహనం", "స్థానాలు")
    widths = [max(len(headers[column]), *(len(row[column]) for row in rows))
              for column in range(len(headers))]
    lines = [" | ".join(value.ljust(widths[column]) for column, value in enumerate(headers)).rstrip()]
    for row in rows:
        lines.append(" | ".join(value.rjust(widths[column]) if spare and column == 3
                                else value.ljust(widths[column])
                                for column, value in enumerate(row)).rstrip())
    return "\n".join(lines)


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



def spare_depot_id(html, depot):
    select = BeautifulSoup(html, "html.parser").find("select", attrs={"name": "depot_id"})
    if select is None:
        raise ValueError("Spare tyre depot selector is missing")
    matches = [option.get("value", "") for option in select.find_all("option")
               if _key(option.get_text(" ", strip=True)) == _key(depot)]
    if len(matches) != 1 or not matches[0].isdigit():
        raise ValueError("Unique spare tyre depot ID is missing")
    return matches[0]


def parse_spare_tyres(html, depot):
    """Parse a source snapshot; its Run Date is independent of daily date."""
    soup = BeautifulSoup(html, "html.parser")
    required = {"rundate", "depot", "vehiclenum", "rtctyreno", "position", "numofdaysinuse"}
    for table in soup.find_all("table"):
        headers = None
        records = []
        for tr in table.find_all("tr"):
            cells = tr.find_all(["th", "td"], recursive=False)
            if not cells:
                continue
            values = [cell.get_text(" ", strip=True) for cell in cells]
            keys = [_key(value) for value in values]
            if required.issubset(keys):
                if len(keys) != len(set(keys)):
                    raise ValueError("Duplicate spare tyre columns")
                headers = keys
                continue
            if headers is None:
                continue
            if len(values) != len(headers):
                if len(values) == 1 and re.fullmatch(r"no (?:data|records|vehicles)(?: found)?[.!]?", values[0], re.I):
                    continue
                raise ValueError("Unexpected spare tyre row shape")
            record = dict(zip(headers, values))
            record.pop("slnum", None)
            if _key(record["depot"]) != _key(depot):
                continue
            for field in ("vehiclenum", "rtctyreno", "position"):
                if not record[field]:
                    raise ValueError("Missing spare tyre identity/position")
            if not re.fullmatch(r"\d{2}-\d{2}-\d{4}", record["rundate"]):
                raise ValueError("Missing or invalid spare tyre Run Date")
            day, month, year = map(int, record["rundate"].split("-"))
            record["rundate"] = date(year, month, day).isoformat()
            if not record["numofdaysinuse"].isdigit():
                raise ValueError("Missing spare tyre days in use")
            records.append(record)
        if headers is not None:
            dates = {row["rundate"] for row in records}
            if len(dates) > 1:
                raise ValueError("Mixed spare tyre snapshot dates")
            # Source serial numbers are not tyre identity; deduplicate repeated entries.
            unique = {(row["vehiclenum"], row["rtctyreno"], row["position"]): row for row in records}
            if len(unique) < len(records):
                for row in records:
                    if unique[(row["vehiclenum"], row["rtctyreno"], row["position"])] != row:
                        raise ValueError("Conflicting duplicate spare tyre entries")
            return list(unique.values()), next(iter(dates), None)
    raise ValueError("Recognized spare tyre table is missing")


def build_spare_snapshot(session, depot):
    response = session.post(SPARE_URL, data={"depot_id": ""}, timeout=30)
    response.raise_for_status()
    depot_id = spare_depot_id(response.text, depot)
    response = session.post(SPARE_URL, data={"depot_id": depot_id}, timeout=30)
    response.raise_for_status()
    rows, run_date = parse_spare_tyres(response.text, depot)
    if not rows:
        return ""
    vehicles = {row["vehiclenum"] for row in rows}
    lines = [SPARE_TITLE, f"మూల నివేదిక తేదీ: {run_date} (రోజువారీ నివేదిక తేదీకి స్వతంత్రంగా)",
             f"వాహనాలు: {len(vehicles)} | టైర్ల నమోదులు: {len(rows)}"]
    lines.append(format_tyre_table([
        (row["vehiclenum"], row["position"], row["rtctyreno"], row["numofdaysinuse"])
        for row in rows
    ], spare=True))
    return "\n".join(lines)

def build_tyre_checks(session, report_date, depot, region_code):
    dt = date.fromisoformat(report_date)
    source_date = f"{dt.day}/{dt.month}/{dt.year}"
    lines = [f"{SECTION_MARKER} {depot} | {report_date}"]
    complete = True
    front_available = True
    try:
        response = session.post(BASE + "rc_tyres_front1.php", data={"fyymm": source_date}, timeout=30)
        response.raise_for_status()
    except RequestException:
        front_available = False
    for title, endpoint in REPORTS:
        try:
            if endpoint != "repairpopup.php" and not front_available:
                raise ValueError("Front tyre source unavailable")
            if endpoint == "repairpopup.php":
                # This report has its own date-selection parent page.
                response = session.post(BASE + "fitted_repair1.php", data={"fyymm": source_date}, timeout=30)
                response.raise_for_status()
            response = session.post(BASE + endpoint, data={"dt": source_date, "regn": region_code, "dept": ""}, timeout=30)
            response.raise_for_status()
            rows, vehicle_header = parse_tyre_popup(response.text, depot, report_date)
            vehicles = list(dict.fromkeys(row[vehicle_header] for row in rows))
            if not rows:
                continue
            lines.append(f"\n{title}\nవాహనాలు: {len(vehicles)} | టైర్ల నమోదులు: {len(rows)}")
            table_rows = []
            for vehicle in vehicles:
                positions = list(dict.fromkeys(
                    value for row in rows if row[vehicle_header] == vehicle
                    for key, value in row.items() if _key(key) == "tyreposition"
                ))
                table_rows.append((vehicle, ', '.join(positions)))
            lines.append(format_tyre_table(table_rows))
        except (RequestException, ValueError):
            complete = False
            lines.append(f"\n{title}: వివరాలు అందుబాటులో లేవు.")
    try:
        spare = build_spare_snapshot(session, depot)
        if spare:
            lines.append("\n" + spare)
    except (RequestException, ValueError):
        complete = False
        lines.append(f"\n{SPARE_TITLE}: వివరాలు అందుబాటులో లేవు.")
    if complete and len(lines) == 1:
        return "", True
    return "\n".join(lines), complete


def append_tyre_checks(report, session, report_date, depot, region_code):
    section, complete = build_tyre_checks(session, report_date, depot, region_code)
    if not section:
        return report, complete
    base = report.split(SECTION_MARKER, 1)[0].rstrip()
    return (base + "\n\n" + section if section else base), complete


def enrich_daily_file(path, report_date, depot, region_code, session_factory=None):
    """Enrich a current daily delivery after KMPL succeeds; caller gates intent."""
    original = path.read_text(encoding="utf-8")
    try:
        if session_factory is None:
            from src.auth.client import login
            session_factory = login
        combined, complete = append_tyre_checks(original, session_factory(), report_date, depot, region_code)
    except Exception:
        combined = original.rstrip() + "\n\n" + SECTION_MARKER + " వివరాలు అందుబాటులో లేవు."
        complete = False
    if combined != original:
        # Atomic replacement leaves the complete daily file intact on write failure.
        temporary = path.with_suffix(path.suffix + ".tyres.tmp")
        try:
            temporary.write_text(combined + "\n", encoding="utf-8")
            temporary.replace(path)
        except OSError:
            temporary.unlink(missing_ok=True)
            return False
    return complete
