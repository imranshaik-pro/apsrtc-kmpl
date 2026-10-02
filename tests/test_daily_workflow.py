import tempfile
from pathlib import Path
import re
import subprocess
import pytest

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


@pytest.mark.parametrize('runner_log', [
    'Report date: 2026-09-01\nReport date: 01 September 2026\n',
    'Report date: 2026-09-01\nALREADY_DELIVERED: https://example.org/report\n',
])
def test_workflow_uses_runner_iso_date_for_fresh_and_cached_delivery(runner_log):
    workflow = Path(__file__).parents[1] / '.github/workflows/daily-report.yml'
    command = re.search(r'report_date=\$\(([^\n]+)\)', workflow.read_text()).group(1)
    result = subprocess.run(['bash', '-c', command.replace('/tmp/daily.log', '/dev/stdin')],
                            input=runner_log, text=True, capture_output=True, check=True)
    assert result.stdout.strip() == '2026-09-01'
