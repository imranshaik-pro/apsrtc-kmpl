"""
Telugu daily report builder – now includes top 10 low For‑Day vehicles.
Unknown vehicle types trigger an alert at the bottom.
"""

from datetime import datetime
from decimal import Decimal
from typing import Dict, Any, List

from src.reporting.region_formatter import format_region_kmpl_block

WEEKDAYS = {
    0: "సోమవారం",
    1: "మంగళవారం",
    2: "బుధవారం",
    3: "గురువారం",
    4: "శుక్రవారం",
    5: "శనివారం",
    6: "ఆదివారం",
}


def _format_vehicle_list(vehicles: List[Dict]) -> str:
    """Format low‑KMPL vehicles with header and numbered lines."""
    if not vehicles:
        return "  (లేవు)"  # None

    lines = ["  `రోజు`  | `ఈ రోజు వరకు`"]

    for idx, item in enumerate(vehicles, start=1):
        day_str = f"{item['day_kmpl']:.2f}"
        month_str = f"{item['month_kmpl']:.2f}" if item['month_kmpl'] is not None else "—"
        lines.append(f"  `{idx:2d}. {item['vehicle']}` : {day_str} | {month_str}")

    return "\n".join(lines)


def build_telugu_daily_report(
    depot: str,
    report_date: str,
    region_reporting_data: Dict[str, Any],
    vehicle_summary: Dict[str, Any],
) -> str:
    dt = datetime.strptime(report_date, "%Y-%m-%d")
    weekday = WEEKDAYS[dt.weekday()]
    date_display = dt.strftime("%d/%m/%Y")

    header = f"🌟 {depot} డిపో :: {date_display} ({weekday})"
    region_block = format_region_kmpl_block(region_reporting_data)

    low_day_vehicles = vehicle_summary.get("low_day_vehicles", [])
    vehicle_list_str = _format_vehicle_list(low_day_vehicles)

    # Unknown vehicles alert – improved message
    unknown_vehicles = vehicle_summary.get("unknown_vehicles", [])
    unknown_alert = ""
    if unknown_vehicles:
        unknown_list = ", ".join(unknown_vehicles)
        unknown_alert = (
            f"⚠️ *జాగ్రత్త:* కింది వాహనాల ఆపరేషన్ రకం (operation type) గుర్తించబడలేదు.\n"
            f"   దయచేసి 'src/reporting/vehicle_summary.py' లో NAC_CODES / AC_CODES ను సమీక్షించండి.\n"
            f"   వాహనాలు: {unknown_list}"
        )

    lines = [
        header,
        "🛢️ HSD KMPL ⛽🚌💧",
        "━━━━━━━━━━━━━━━━━━",
        region_block,
        "━━━━━━━━━━━━━━━━━━",
        f"⚠️ *తక్కువ సామర్థ్య వాహనాలు* (రోజు KMPL ≤ 5.00):",
        vehicle_list_str,
        "━━━━━━━━━━━━━━━━━━",
        "*తక్షణ చర్య!* 🛠️ టాప్ 10 తక్కువ HSD KMPL నమోదు చేసిన వాహనాలపై దృష్టి పెట్టండి.",
        "",
        unknown_alert,
        "",
        "✅ తక్కువ KMPL వాహనాల సంఖ్య తగ్గించేందుకు ప్రతి ఒక్కరం బాధ్యతగా వ్యవహరిద్దాం. డిపో అభివృద్ధి మనందరి లక్ష్యం! 💪",
    ]

    # Remove duplicate empty lines if alert is empty
    report = "\n".join(lines)
    if not unknown_alert:
        report = report.replace("\n\n\n", "\n\n")
    return report
