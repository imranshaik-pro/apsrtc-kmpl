"""
Telugu daily report builder – includes top 10 low KMPL list AND slab-wise table.
"""

from datetime import datetime
from decimal import Decimal
from typing import Dict, Any, List, Tuple

from src.reporting.region_formatter import format_region_kmpl_block
from src.reporting.vehicle_summary import build_slab_operation_table, SLABS

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
    if not vehicles:
        return "  (లేవు)"
    lines = ["  `రోజు`  | `ఈ రోజు వరకు`"]
    for idx, item in enumerate(vehicles, start=1):
        day_str = f"{item['day_kmpl']:.2f}"
        month_str = f"{item['month_kmpl']:.2f}" if item['month_kmpl'] is not None else "—"
        op_type = item.get('operation_type', '')
        vehicle_display = f"{item['vehicle']} ({op_type})" if op_type else item['vehicle']
        lines.append(f"  `{idx:2d}. {vehicle_display}` : {day_str} | {month_str}")
    return "\n".join(lines)


def _format_slab_table(op_types: List[str], counts: Dict) -> str:
    """
    Render the slab vs operation type table with merged rows and separators.
    """
    if not op_types:
        return "  (ఎటువంటి వాహనాలు లేవు)"

    # Column widths
    col_widths = {
        "Slab": max(len("Slab"), max(len(s) for s in counts.keys() if s != "Total")),
        "Type": max(len("Type"), len("రోజు"), len("ఈరోజు వరకు")),
    }
    for op in op_types:
        col_widths[op] = max(len(op), 2)
    col_widths["Total"] = max(len("Total"), 2)

    def sep_line():
        return "|".join([
            "-" * col_widths["Slab"],
            "-" * col_widths["Type"],
            *["-" * col_widths[op] for op in op_types],
            "-" * col_widths["Total"]
        ])

    def row_string(slab, type_val, values, compute_total=True):
        row = [
            slab.ljust(col_widths["Slab"]),
            type_val.ljust(col_widths["Type"]),
            *[str(values.get(op, 0)).rjust(col_widths[op]) for op in op_types]
        ]
        if compute_total:
            total = sum(values.get(op, 0) for op in op_types)
            row.append(str(total).rjust(col_widths["Total"]))
        else:
            # For header row, we already have the column names in values
            row.append("Total".rjust(col_widths["Total"]))
        return "|".join(row)

    lines = []

    # Header row – do NOT compute total (use strings)
    header_values = {op: op for op in op_types}
    lines.append(row_string("Slab", "Type", header_values, compute_total=False))
    lines.append(sep_line())

    # Slab rows
    for slab_label, _, _ in SLABS:
        slab_data = counts.get(slab_label)
        if not slab_data:
            continue
        lines.append(row_string(slab_label, "రోజు", slab_data["for_day"]))
        lines.append(row_string("", "ఈరోజు వరకు", slab_data["up_to_day"]))
        lines.append(sep_line())

    # Total row
    total_data = counts.get("Total")
    if total_data:
        lines.append(row_string("Total", "రోజు", total_data["for_day"]))
        lines.append(row_string("", "ఈరోజు వరకు", total_data["up_to_day"]))

    return "\n".join(lines)


def build_telugu_daily_report(
    depot: str,
    report_date: str,
    region_reporting_data: Dict[str, Any],
    vehicle_summary: Dict[str, Any],
    raw_records: List[Dict[str, Any]] = None,
    for_day_results: List[Dict[str, Any]] = None,
    up_to_day_results: List[Dict[str, Any]] = None,
) -> str:
    dt = datetime.strptime(report_date, "%Y-%m-%d")
    weekday = WEEKDAYS[dt.weekday()]
    date_display = dt.strftime("%d/%m/%Y")

    header = f"🌟 {depot} డిపో :: {date_display} ({weekday})"
    region_block = format_region_kmpl_block(region_reporting_data)

    low_day_vehicles = vehicle_summary.get("low_day_vehicles", [])
    vehicle_list_str = _format_vehicle_list(low_day_vehicles)

    # Build the slab table if raw records are provided
    slab_table_str = ""
    if raw_records is not None and for_day_results is not None and up_to_day_results is not None:
        op_types, slab_counts, unknown_in_slab = build_slab_operation_table(
            for_day_results, up_to_day_results, raw_records
        )
        existing_unknown = vehicle_summary.get("unknown_vehicles", [])
        all_unknown = list(dict.fromkeys(existing_unknown + unknown_in_slab))
        vehicle_summary["unknown_vehicles"] = all_unknown
        if op_types:
            slab_table_str = "*రేంజ్ వారీగా వాహనాల వివరాలు*\n" + _format_slab_table(op_types, slab_counts)
        else:
            slab_table_str = "*రేంజ్ వారీగా వాహనాల వివరాలు*\n  (ఎటువంటి వాహనాలు లేవు)"

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
        slab_table_str,
        "━━━━━━━━━━━━━━━━━━",
        "*తక్షణ చర్య!* 🛠️ టాప్ 10 తక్కువ HSD KMPL నమోదు చేసిన వాహనాలపై దృష్టి పెట్టండి.",
        "",
        unknown_alert,
        "",
        "✅ తక్కువ KMPL వాహనాల సంఖ్య తగ్గించేందుకు ప్రతి ఒక్కరం బాధ్యతగా వ్యవహరిద్దాం. డిపో అభివృద్ధి మనందరి లక్ష్యం! 💪",
    ]

    report = "\n".join(lines)
    if not unknown_alert:
        report = report.replace("\n\n\n", "\n\n")
    return report
