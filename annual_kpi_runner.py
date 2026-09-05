#!/usr/bin/env python3
"""Annual KPI entry point with strict source handling.

Rules enforced here:
- The month selected in the Google Form is the cumulative source month used for
  the selected financial year.
- Tyre Statement D uses only the exact `All Tyre Sizes Total` row.
- Tyre depot codes come from the tyre website mapping, not the vehicle prefix.
- MED cancellation, breakdown and spring use their verified APSRTC source paths.
- If a known KPI source is unavailable, do not guess a substitute value.
"""

from datetime import datetime
import sys

import annual_kpi_incremental as annual
import annual_kpi_report as core

STOREAP_BASE = "http://103.44.14.20/storeap"

# Tyre Statement D codes for YSR Kadapa district. These differ from several
# general vehicle-depot prefixes, so they must be explicit.
TYRE_SITE = {
    "BADVEL": {"code": "BDV", "zone": "KADAPA(KDP ZONE)", "region": "DPTO YSR KADAPA"},
    "JAMMALAMADUGU": {"code": "JMD", "zone": "KADAPA(KDP ZONE)", "region": "DPTO YSR KADAPA"},
    "KADAPA": {"code": "KDP", "zone": "KADAPA(KDP ZONE)", "region": "DPTO YSR KADAPA"},
    "MYDUKUR": {"code": "MYD", "zone": "KADAPA(KDP ZONE)", "region": "DPTO YSR KADAPA"},
    "PRODDUTUR": {"code": "PDT", "zone": "KADAPA(KDP ZONE)", "region": "DPTO YSR KADAPA"},
    "PULIVENDULA": {"code": "PVD", "zone": "KADAPA(KDP ZONE)", "region": "DPTO YSR KADAPA"},
    "RAJAMPET": {"code": "RJP", "zone": "KADAPA(KDP ZONE)", "region": "DPTO YSR KADAPA"},
}


def tyre_site_info(display):
    return TYRE_SITE.get(core.norm(display))


def exact_tyre_total_row(headers, rows, display, vehicle):
    depot_idx = core.col(headers, ["DEPOT"])
    size_idx = core.col(headers, ["TYRE SIZE", "SIZE"])
    info = tyre_site_info(display)
    if depot_idx is None or size_idx is None or not info:
        return None

    tyre_code = core.norm(info["code"])
    for row in rows:
        if depot_idx >= len(row) or size_idx >= len(row):
            continue
        if core.norm(row[depot_idx]) != tyre_code:
            continue
        if core.norm(row[size_idx]) == "ALL TYRE SIZES TOTAL":
            return row
    return None


def strict_fetch_tyre(session, display, vehicle, region, y, m):
    info = tyre_site_info(display)
    if not info:
        print(f"TYRE MANUAL INPUT REQUIRED: no verified tyre-site mapping for {display}")
        return {name: (None, "0.00") for name in annual.TYRE_KPIS}

    params = core.source_params(y, m, region, vehicle)
    params.update(
        {
            "month_year": datetime(y, m, 1).strftime("%b-%Y").upper(),
            "tyre_size": "All Tyre Sizes Total",
            "depot": info["code"],
            "zone": info["zone"],
            "region": info["region"],
        }
    )

    try:
        html = core.request_html(session, core.TYRE_BASE, "d_statement_final.php", params)
        headers, rows = core.find_table(
            html,
            ["DEPOT", "TYRE SIZE"],
            ["RT_FACTOR", "NEW MILEAGE", "AVG TOTAL MILEAGE"],
        )
        row = exact_tyre_total_row(headers, rows, display, vehicle)
    except Exception as exc:
        print(f"TYRE MANUAL INPUT REQUIRED: {exc}")
        row = None
        headers = []

    if not row:
        return {name: (None, "0.00") for name in annual.TYRE_KPIS}

    rv = lambda aliases: core.row_value(headers, row, aliases)
    return {
        "AVG TYRE LIFE": (rv(["AVG TOTAL MILEAGE", "AVERAGE TOTAL MILEAGE"]), "lakh"),
        "NEW TYRE LIFE": (rv(["NEW MILEAGE"]), "lakh"),
        "RC TYRE LIFE": (rv(["RC MILEAGE"]), "lakh"),
        "N.T.S RATE": (rv(["NEW %", "NTS", "N.T.S"]), "0.00"),
        "Ist RC S Rate": (rv(["IST RC %", "IST RC SCP %", "1ST RC %"]), "0.00"),
        "TTL SCP Rate": (rv(["TOTAL %", "TTL.SCP %", "TOTAL SCRAP %"]), "0.00"),
        "RT Factor": (rv(["RT_FACTOR", "RT FACTOR"]), "0.00"),
    }


def month_token(y, m, separator):
    month_name = datetime(y, m, 1).strftime("%B")
    return f"{y}{m:02d}{month_name}{separator}{y}"


def district_code(region):
    return core.norm(region).replace(" ", "")


def second_matching_column(headers, text):
    wanted = core.norm(text)
    matches = [i for i, h in enumerate(headers) if wanted in core.norm(h)]
    if len(matches) >= 2:
        return matches[1]
    return matches[0] if matches else None


def third_matching_column(headers, text):
    wanted = core.norm(text)
    matches = [i for i, h in enumerate(headers) if wanted in core.norm(h)]
    if len(matches) >= 3:
        return matches[2]
    return matches[-1] if matches else None


def verified_fetch_med(session, display, vehicle, region, y, m):
    params = {
        "action": "",
        "fdate": month_token(y, m, "-"),
        "dist": district_code(region),
    }
    try:
        html = core.request_html(session, core.MEDNEW_BASE, "medcan_um_dpt.php", params)
        headers, rows = core.find_table(html, ["DEPOT", "% OF CANC"], ["UP TO THE MONTH", "TOTAL CY"])
        row = core.depot_row(headers, rows, display, vehicle)
        if not row:
            return None
        idx = second_matching_column(headers, "% OF CANC")
        return core.number(row[idx]) if idx is not None and idx < len(row) else None
    except Exception as exc:
        print(f"MED CANCL. MANUAL INPUT REQUIRED: {exc}")
        return None


def verified_fetch_breakdown(session, display, vehicle, region, y, m):
    params = {
        "action": "",
        "yymm": month_token(y, m, "_"),
        "dist": district_code(region),
    }
    try:
        html = core.request_html(session, core.MED_BASE, "sysbd_dpt.php", params)
        headers, rows = core.find_table(html, ["DEPOT", "BD RATE"], ["TOTAL BDS"])
        row = core.depot_row(headers, rows, display, vehicle)
        if not row:
            return None
        idx = second_matching_column(headers, "BD RATE")
        return core.number(row[idx]) if idx is not None and idx < len(row) else None
    except Exception as exc:
        print(f"B.D RATE MANUAL INPUT REQUIRED: {exc}")
        return None


def verified_fetch_spring(session, display, vehicle, region, y, m):
    params = {
        "action": "",
        "yymm": month_token(y, m, "_"),
        "dist": district_code(region),
    }
    try:
        html = core.request_html(session, STOREAP_BASE, "deptspring.php", params)
        headers, rows = core.find_table(
            html,
            ["DEPOT", "SPRING CONSUMPTION PER LAKH KMS"],
            ["VARIANCE OVER TARGET"],
        )
        row = core.depot_row(headers, rows, display, vehicle)
        if not row:
            return None
        # This source presents the direct per-lakh-km KPI repeatedly for the
        # month / cumulative CY / comparison period. Annual uses cumulative CY.
        idx = second_matching_column(headers, "SPRING CONSUMPTION PER LAKH KMS")
        return core.number(row[idx]) if idx is not None and idx < len(row) else None
    except Exception as exc:
        print(f"SPRING CONS MANUAL INPUT REQUIRED: {exc}")
        return None


def install_selected_month_override():
    """Consume --selected-month and make it the effective month for its FY."""
    if "--selected-month" not in sys.argv:
        return
    idx = sys.argv.index("--selected-month")
    if idx + 1 >= len(sys.argv):
        raise ValueError("--selected-month requires YYYY-MM")
    raw = sys.argv[idx + 1].strip()
    del sys.argv[idx : idx + 2]

    try:
        y, m = map(int, raw.split("-"))
        datetime(y, m, 1)
    except Exception as exc:
        raise ValueError(f"Invalid selected month: {raw}; expected YYYY-MM") from exc

    start_year = y if m >= 4 else y - 1
    selected_fy = f"{start_year}-{str(start_year + 1)[-2:]}"
    original = core.effective_month_for_fy

    def effective_month_for_fy(fy):
        if fy == selected_fy:
            return y, m
        return original(fy)

    core.effective_month_for_fy = effective_month_for_fy
    print(f"Selected month override active: {raw} -> FY {selected_fy}")


annual.tyre_total_row = exact_tyre_total_row
annual.fetch_tyre = strict_fetch_tyre
core.fetch_tyre = strict_fetch_tyre
core.fetch_med = verified_fetch_med
core.fetch_breakdown = verified_fetch_breakdown
core.fetch_spring = verified_fetch_spring
install_selected_month_override()


if __name__ == "__main__":
    try:
        sys.exit(annual.main())
    except Exception as exc:
        print(f"ANNUAL_KPI_FAILURE: {exc}")
        sys.exit(1)
