import sys

sys.path.insert(0, "src")

from auth.client import login
from bs4 import BeautifulSoup

from calculations.kmpl import calculate_kmpl


REPORT_URL = "http://103.44.14.20/med/vehkmpl.php"

REPORT_DATE = "18/08/2026"
DEPOT = "PDTR/PRODDUTUR"


def parse_number(value):
    value = value.strip()

    if not value:
        return 0.0

    return float(value)


def parse_vehicle_rows(html):
    soup = BeautifulSoup(html, "html.parser")

    table = soup.select_one("table.demoTable")

    if table is None:
        raise RuntimeError("table.demoTable was not found")

    vehicle_rows = []

    for row in table.find_all("tr"):
        cells = row.find_all("td")

        if len(cells) != 15:
            continue

        values = [cell.get_text(strip=True) for cell in cells]

        record = {
            "sl_no": int(values[0]),
            "log_sheet_no": values[1],
            "vehicle_no": values[2],
            "operation_type": values[3],
            "engine_type": values[4],

            "for_day_rev_kms": parse_number(values[5]),
            "for_day_non_rev_kms": parse_number(values[6]),
            "for_day_total_kms": parse_number(values[7]),
            "for_day_hsd": parse_number(values[8]),
            "for_day_kmpl": parse_number(values[9]),

            "up_to_day_rev_kms": parse_number(values[10]),
            "up_to_day_non_rev_kms": parse_number(values[11]),
            "up_to_day_total_kms": parse_number(values[12]),
            "up_to_day_hsd": parse_number(values[13]),
            "up_to_day_kmpl": parse_number(values[14]),
        }

        vehicle_rows.append(record)

    return vehicle_rows


def main():
    session = login()

    response = session.post(
        REPORT_URL,
        data={
            "fyymm": REPORT_DATE,
            "dept": DEPOT,
        },
        timeout=30,
    )

    print("Report HTTP status:", response.status_code)
    print("Final URL:", response.url)

    records = parse_vehicle_rows(response.text)

    print("Parsed vehicle rows:", len(records))

    discrepancies = []

    for record in records:
        calculated = calculate_kmpl(
            record["for_day_total_kms"],
            record["for_day_hsd"],
        )

        displayed = record["for_day_kmpl"]

        if calculated is None:
            continue

        calculated_rounded = round(calculated, 2)

        if calculated_rounded != displayed:
            discrepancies.append(
                {
                    "vehicle_no": record["vehicle_no"],
                    "total_kms": record["for_day_total_kms"],
                    "hsd": record["for_day_hsd"],
                    "displayed": displayed,
                    "calculated": calculated,
                    "calculated_rounded": calculated_rounded,
                }
            )

    print("For-Day KMPL discrepancies:", len(discrepancies))

    if discrepancies:
        print("\nDiscrepancies:\n")

        for item in discrepancies:
            print(
                f"Vehicle={item['vehicle_no']}, "
                f"TotalKms={item['total_kms']}, "
                f"HSD={item['hsd']}, "
                f"APSRTC={item['displayed']}, "
                f"Calculated={item['calculated']}, "
                f"Rounded={item['calculated_rounded']}"
            )
    else:
        print("For-Day KMPL reconciliation: PASSED")


if __name__ == "__main__":
    main()