from src.auth.client import login
from src.calculations.pipeline import (
    calculate_for_day,
    calculate_up_to_day,
)
from src.parser.vehicle_parser import parse_vehicle_rows
from src.parser.region_parser import parse_region_html
from src.reporting.region_summary import build_region_reporting_data
from src.reporting.telugu_report import build_telugu_daily_report
from src.reporting.vehicle_summary import build_vehicle_summary


VEHICLE_REPORT_URL = (
    "http://103.44.14.20/med/vehkmpl.php"
)

REGION_REPORT_URL = (
    "http://103.44.14.20/med/achsd1.php"
)


def _format_vehicle_report_date(report_date):
    parts = report_date.split("-")
    if len(parts) != 3:
        raise ValueError("Report date must use YYYY-MM-DD format.")
    year, month, day = parts
    if len(year) != 4 or len(month) != 2 or len(day) != 2:
        raise ValueError("Report date must use YYYY-MM-DD format.")
    return f"{day}/{month}/{year}"


def _collect_vehicle_records(session, report_date, vehicle_depot):
    vehicle_report_date = _format_vehicle_report_date(report_date)
    response = session.post(
        VEHICLE_REPORT_URL,
        data={"fyymm": vehicle_report_date, "dept": vehicle_depot},
        timeout=30,
    )
    response.raise_for_status()
    return parse_vehicle_rows(response.text)


def _collect_region_records(session, report_date, region_code):
    response = session.get(
        REGION_REPORT_URL,
        params={"action": "", "fdate": report_date, "rreg": region_code},
        timeout=30,
    )
    response.raise_for_status()
    return parse_region_html(response.text)


def _select_depot_region_records(records, depot):
    depot_records = [rec for rec in records if rec.get("depot") == depot]
    if not depot_records:
        raise ValueError(f"No Region records found for depot {depot!r}.")
    return depot_records


def build_daily_report(session, report_date, depot, vehicle_depot, region_code):
    if session is None:
        raise ValueError("Authenticated session is required.")
    if not report_date:
        raise ValueError("Report date is required.")
    if not depot:
        raise ValueError("Depot is required.")
    if not vehicle_depot:
        raise ValueError("Vehicle depot value is required.")
    if not region_code:
        raise ValueError("Region code is required.")

    vehicle_records = _collect_vehicle_records(
        session=session,
        report_date=report_date,
        vehicle_depot=vehicle_depot,
    )

    if not vehicle_records:
        raise RuntimeError("Vehicle report returned no valid vehicle records.")

    for_day_results = calculate_for_day(vehicle_records)
    up_to_day_results = calculate_up_to_day(vehicle_records)

    vehicle_summary = build_vehicle_summary(
        for_day_results=for_day_results,
        up_to_day_results=up_to_day_results,
        raw_records=vehicle_records,  # Pass raw records to filter NAC only
    )

    region_records = _collect_region_records(
        session=session,
        report_date=report_date,
        region_code=region_code,
    )

    depot_region_records = _select_depot_region_records(
        records=region_records,
        depot=depot,
    )

    region_reporting_data = build_region_reporting_data(depot_region_records)

    return build_telugu_daily_report(
        depot=depot,
        report_date=report_date,
        region_reporting_data=region_reporting_data,
        vehicle_summary=vehicle_summary,
    )


def run_daily_report(report_date, depot, vehicle_depot, region_code):
    session = login()
    return build_daily_report(
        session=session,
        report_date=report_date,
        depot=depot,
        vehicle_depot=vehicle_depot,
        region_code=region_code,
    )
