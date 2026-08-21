from bs4 import BeautifulSoup


def parse_number(value):
    value = value.strip()

    if not value:
        return 0.0

    return float(value)


def parse_vehicle_rows(html):
    """
    Parse the APSRTC vehicle KMPL report.

    Valid vehicle rows contain exactly 15 TD elements.

    Returns the normalized parser-level vehicle records.
    """

    soup = BeautifulSoup(html, "html.parser")

    table = soup.select_one("table.demoTable")

    if table is None:
        raise RuntimeError("table.demoTable was not found")

    vehicle_rows = []

    for row in table.find_all("tr"):
        cells = row.find_all("td")

        if len(cells) != 15:
            continue

        values = [
            cell.get_text(strip=True)
            for cell in cells
        ]

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
