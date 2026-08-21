from decimal import Decimal

from src.reporting.telugu_report import build_telugu_daily_report


def build_region_data():
    return {
        "depot": "PRODDUTUR",
        "tot": {
            "target_kmpl": Decimal("5.03"),
            "day_kmpl": Decimal("4.84"),
            "up_to_day_kmpl": Decimal("4.88"),
            "last_month_kmpl": Decimal("4.88"),
            "last_year_month_kmpl": Decimal("5.09"),
        },
        "nac": {
            "target_kmpl": Decimal("5.05"),
            "day_kmpl": Decimal("4.87"),
            "up_to_day_kmpl": Decimal("4.92"),
            "last_month_kmpl": Decimal("4.91"),
            "last_year_month_kmpl": Decimal("5.11"),
        },
        "ac": {
            "target_kmpl": None,
            "day_kmpl": Decimal("3.68"),
            "up_to_day_kmpl": Decimal("3.73"),
            "last_month_kmpl": Decimal("3.79"),
            "last_year_month_kmpl": Decimal("4.11"),
        },
    }


def build_vehicle_data():
    return {
        "low_day_vehicles_count": 12,
        "low_month_vehicles_count": 9,
    }


def test_report_date_and_weekday():
    report = build_telugu_daily_report(
        "PRODDUTUR",
        "2026-08-18",
        build_region_data(),
        build_vehicle_data(),
    )

    assert "PRODDUTUR డిపో :: 18/08/2026 (మంగళవారం)" in report


def test_report_contains_aligned_region_block():
    report = build_telugu_daily_report(
        "PRODDUTUR",
        "2026-08-18",
        build_region_data(),
        build_vehicle_data(),
    )

    assert "Metric            TOT       NAC       AC" in report
    assert "Target            5.03      5.05      —" in report
    assert "ఈ రోజు            4.84      4.87      3.68" in report
    assert "ఈ రోజు వరకు       4.88      4.92      3.73" in report
    assert "గత నెల            4.88      4.91      3.79" in report
    assert "గత ఇయర్ నెల       5.09      5.11      4.11" in report


def test_report_contains_vehicle_counts():
    report = build_telugu_daily_report(
        "PRODDUTUR",
        "2026-08-18",
        build_region_data(),
        build_vehicle_data(),
    )

    assert "(ఈ రోజు) :: 12>" in report
    assert "(ఈ రోజు వరకు) :: 9>" in report


def test_report_contains_required_header_and_closing_message():
    report = build_telugu_daily_report(
        "PRODDUTUR",
        "2026-08-18",
        build_region_data(),
        build_vehicle_data(),
    )

    assert "🛢️ HSD KMPL ⛽🚌💧" in report

    assert (
        "తక్కువ KMPL వాహనాల సంఖ్య తగ్గించేందుకు "
        "ప్రతి ఒక్కరం బాధ్యతగా వ్యవహరిద్దాం. "
        "డిపో అభివృద్ధి మనందరి లక్ష్యం! 💪"
    ) in report


def test_invalid_date_is_rejected():
    try:
        build_telugu_daily_report(
            "PRODDUTUR",
            "18-08-2026",
            build_region_data(),
            build_vehicle_data(),
        )
        raise AssertionError(
            "Expected ValueError for invalid date."
        )
    except ValueError as exc:
        assert "YYYY-MM-DD" in str(exc)


def test_missing_vehicle_summary_field_is_rejected():
    vehicle_data = {
        "low_day_vehicles_count": 12,
    }

    try:
        build_telugu_daily_report(
            "PRODDUTUR",
            "2026-08-18",
            build_region_data(),
            vehicle_data,
        )
        raise AssertionError(
            "Expected ValueError for missing vehicle summary field."
        )
    except ValueError as exc:
        assert "missing fields" in str(exc)


print("Telugu report tests passed.")
