from datetime import datetime

from src.reporting.region_formatter import format_region_kmpl_block


TELUGU_WEEKDAYS = {
    0: "సోమవారం",
    1: "మంగళవారం",
    2: "బుధవారం",
    3: "గురువారం",
    4: "శుక్రవారం",
    5: "శనివారం",
    6: "ఆదివారం",
}


REPORT_SEPARATOR = "━━━━━━━━━━━━━━━━━━"


def _format_report_date(report_date):
    """
    Convert YYYY-MM-DD into DD/MM/YYYY and Telugu weekday.
    """

    try:
        parsed_date = datetime.strptime(
            report_date,
            "%Y-%m-%d",
        )
    except (TypeError, ValueError) as exc:
        raise ValueError(
            "Report date must use YYYY-MM-DD format."
        ) from exc

    formatted_date = parsed_date.strftime("%d/%m/%Y")
    weekday = TELUGU_WEEKDAYS[parsed_date.weekday()]

    return formatted_date, weekday


def build_telugu_daily_report(
    depot,
    report_date,
    region_reporting_data,
    vehicle_summary,
):
    """
    Build the final Telugu APSRTC daily KMPL report.

    This function is presentation-only.

    It does not:
        - calculate KMPL
        - round KMPL
        - classify slabs
        - calculate vehicle counts
        - modify reporting data
    """

    if not depot:
        raise ValueError("Depot is required.")

    if not isinstance(region_reporting_data, dict):
        raise ValueError(
            "Region reporting data must be a dictionary."
        )

    if not isinstance(vehicle_summary, dict):
        raise ValueError(
            "Vehicle summary must be a dictionary."
        )

    required_vehicle_summary_fields = {
        "low_day_vehicles_count",
        "low_month_vehicles_count",
    }

    missing_fields = (
        required_vehicle_summary_fields
        - vehicle_summary.keys()
    )

    if missing_fields:
        raise ValueError(
            "Vehicle summary is missing fields: "
            f"{sorted(missing_fields)}"
        )

    formatted_date, weekday = _format_report_date(report_date)

    region_block = format_region_kmpl_block(
        region_reporting_data
    )

    low_day_count = vehicle_summary[
        "low_day_vehicles_count"
    ]

    low_month_count = vehicle_summary[
        "low_month_vehicles_count"
    ]

    return "\n".join(
        [
            (
                f"🌟 {depot.upper()} డిపో :: "
                f"{formatted_date} ({weekday})"
            ),
            "🛢️ HSD KMPL ⛽🚌💧",
            REPORT_SEPARATOR,
            "",
            region_block,
            "",
            REPORT_SEPARATOR,
            (
                "⚠️ <👇 Below 5.00 KMPL 🚌 సంఖ్య "
                f"(ఈ రోజు) :: {low_day_count}>"
            ),
            (
                "⚠️ <👇 Below 5.00 KMPL 🚌 సంఖ్య "
                f"(ఈ రోజు వరకు) :: {low_month_count}>"
            ),
            REPORT_SEPARATOR,
            (
                "✅ తక్కువ KMPL వాహనాల సంఖ్య తగ్గించేందుకు "
                "ప్రతి ఒక్కరం బాధ్యతగా వ్యవహరిద్దాం. "
                "డిపో అభివృద్ధి మనందరి లక్ష్యం! 💪"
            ),
        ]
    )
