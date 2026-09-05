#!/usr/bin/env python3
"""Annual KPI entry point with strict tyre total-row selection.

Tyre Statement D must use only the exact `All Tyre Sizes Total` row for the
selected depot. Individual tyre-size rows are never accepted as a fallback.
"""

import sys

import annual_kpi_incremental as annual
import annual_kpi_report as core


def exact_tyre_total_row(headers, rows, display, vehicle):
    depot_idx = core.col(headers, ["DEPOT"])
    size_idx = core.col(headers, ["TYRE SIZE", "SIZE"])
    if depot_idx is None or size_idx is None:
        return None

    tyre_code = core.norm(vehicle.split("/")[0])
    for row in rows:
        if depot_idx >= len(row) or size_idx >= len(row):
            continue
        if core.norm(row[depot_idx]) != tyre_code:
            continue
        if core.norm(row[size_idx]) == "ALL TYRE SIZES TOTAL":
            return row
    return None


# fetch_tyre() resolves this function from the annual module at runtime.
annual.tyre_total_row = exact_tyre_total_row


if __name__ == "__main__":
    try:
        sys.exit(annual.main())
    except Exception as exc:
        print(f"ANNUAL_KPI_FAILURE: {exc}")
        sys.exit(1)
