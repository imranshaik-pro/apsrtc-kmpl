import tempfile
from pathlib import Path

import run_daily_report


def test_validate_report_date():
    run_daily_report.validate_report_date("2026-08-18")


def test_invalid_report_date():
    try:
        run_daily_report.validate_report_date("18/08/2026")
    except ValueError:
        return

    raise AssertionError(
        "Invalid report date should raise ValueError."
    )


def test_build_output_path():
    path = run_daily_report.build_output_path(
        output_dir=Path("reports"),
        report_date="2026-08-18",
        depot="PRODDUTUR",
    )

    assert path == Path(
        "reports/PRODDUTUR_2026-08-18.txt"
    )


def test_build_output_path_with_slash():
    path = run_daily_report.build_output_path(
        output_dir=Path("reports"),
        report_date="2026-08-18",
        depot="TEST/DEPOT",
    )

    assert path == Path(
        "reports/TEST_DEPOT_2026-08-18.txt"
    )


print("Production daily workflow tests passed.")
