import argparse
from pathlib import Path
import sys

from src.auth.client import login
from src.reporting.application import build_daily_report


DEFAULT_REPORTS_DIR = Path("reports")


def parse_arguments():
    parser = argparse.ArgumentParser(
        description="Generate the APSRTC daily HSD KMPL Telugu report."
    )

    parser.add_argument(
        "--date",
        required=True,
        help="Report date in YYYY-MM-DD format.",
    )

    parser.add_argument(
        "--depot",
        required=True,
        help="APSRTC depot name used in the Region report.",
    )

    parser.add_argument(
        "--vehicle-depot",
        required=True,
        help="APSRTC vehicle-report depot value.",
    )

    parser.add_argument(
        "--region-code",
        required=True,
        help="APSRTC Region report code.",
    )

    parser.add_argument(
        "--output-dir",
        default=str(DEFAULT_REPORTS_DIR),
        help="Directory where the generated report will be saved.",
    )

    return parser.parse_args()


def validate_report_date(report_date):
    parts = report_date.split("-")

    if len(parts) != 3:
        raise ValueError(
            "Report date must use YYYY-MM-DD format."
        )

    year, month, day = parts

    if (
        len(year) != 4
        or len(month) != 2
        or len(day) != 2
        or not all(part.isdigit() for part in parts)
    ):
        raise ValueError(
            "Report date must use YYYY-MM-DD format."
        )


def build_output_path(output_dir, report_date, depot):
    safe_depot = depot.replace("/", "_").replace("\\", "_")
    return Path(output_dir) / f"{safe_depot}_{report_date}.txt"


def main():
    args = parse_arguments()

    validate_report_date(args.date)

    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    output_path = build_output_path(
        output_dir=output_dir,
        report_date=args.date,
        depot=args.depot,
    )

    print("APSRTC KMPL Daily Report")
    print("========================")
    print(f"Report date : {args.date}")
    print(f"Depot       : {args.depot}")
    print("Authenticating...")

    session = login()

    print("Authentication successful.")
    print("Collecting Vehicle and Region data...")

    report = build_daily_report(
        session=session,
        report_date=args.date,
        depot=args.depot,
        vehicle_depot=args.vehicle_depot,
        region_code=args.region_code,
    )

    output_path.write_text(
        report + "\n",
        encoding="utf-8",
    )

    print("")
    print(report)

    print("")
    print("========================")
    print("REPORT GENERATED SUCCESSFULLY")
    print(f"Saved to: {output_path}")
    print("========================")


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        print("")
        print("REPORT GENERATION FAILED")
        print(f"Reason: {exc}")
        sys.exit(1)
