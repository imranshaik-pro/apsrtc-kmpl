#!/usr/bin/env python3
"""Annual KPI v10: safe historical backfill + source-availability rules.

Rules enforced here:
- Never replace an already-valid monthly value with blank/MANUAL because a fetch failed.
- Historical HSD repair is month-only; do not touch historical Upto while backfilling.
- LUB is re-fetched for available months, but FY2024-25 is explicitly unavailable.
- Completed-FY Upto is written only from March; current-FY Upto only from selected month.
- Tyres FY2025-26 onward use the original web implementation captured BEFORE v6 monkey-patching.
- FY2024-25 tyre data is available only for Apr-2024; May-2024..Mar-2025 remain MANUAL.
- FY2024-25 Spring Consumption is unavailable and remains MANUAL.
- Existing v7/v8/v9/v10 layout is treated as compatible, avoiding destructive rebuilds.
"""
import sys

# Capture the real original web tyre function BEFORE importing v8/v7/v6, because v6
# monkey-patches annual_kpi_runner_v3.fetch_tyre in-place during import.
import annual_kpi_runner_v3 as v3
ORIGINAL_WEB_FETCH_TYRE = v3.fetch_tyre

import annual_kpi_runner_v8 as v8

m = v8.m
v7 = v8.v7
LAYOUT_VERSION = "10"
FY24 = "2024-25"


def _is_good(value):
    if value is None:
        return False
    text = str(value).strip()
    return bool(text) and text.upper() != m.MANUAL


def fetch_tyre_v10(s, depot, y, month, need_upto):
    if m.selected_fy(y, month) == FY24:
        # Official booklet path is retained only for Apr-2024 use below.
        return v7.v6.fetch_tyre_v6(s, depot, y, month, need_upto)
    # This is the captured original v3 web implementation, not the monkey-patched symbol.
    return ORIGINAL_WEB_FETCH_TYRE(s, depot, y, month, need_upto)


m.fetch_tyre = fetch_tyre_v10
v7.LAYOUT_VERSION = LAYOUT_VERSION


def meta_version_v10(spreadsheet_id):
    try:
        vals = m.read_values(spreadsheet_id, f"'{m.META_TITLE}'!A:B")
        d = {str(r[0]): str(r[1]) for r in vals[1:] if len(r) >= 2}
        stored = d.get("LAYOUT_VERSION", "")
        if stored in {"7", "8", "9", "10"}:
            return LAYOUT_VERSION
        return stored
    except Exception:
        return ""


v7.meta_version = meta_version_v10


def _set_month_if_fetched(st, name, fy, mon_name, value, only_if_missing=False):
    if value is None:
        return False
    m.ensure(st, name)
    existing = st["rows"][name][fy]["months"].get(mon_name)
    if only_if_missing and _is_good(existing):
        return False
    st["rows"][name][fy]["months"][mon_name] = value
    return True


def _set_upto_if_fetched(st, name, fy, value):
    if value is None:
        return False
    m.ensure(st, name)
    st["rows"][name][fy]["upto"] = value
    return True


def safe_apply(st, fy, y, month, data, need_upto, repair):
    """Merge successful values only; failures never erase valid history."""
    mon_name = m.month_name(month)
    for name, pair in (data or {}).items():
        if not m.valid_dynamic(name):
            continue
        m.ensure(st, name)
        mv = pair.get("month")
        uv = pair.get("upto")
        if mv is not None:
            st["rows"][name][fy]["months"][mon_name] = mv
        # Blank/MANUAL from a failed source is deliberately ignored.
        if need_upto and uv is not None:
            st["rows"][name][fy]["upto"] = uv


m.apply = safe_apply


def safe_hsd_month_backfill(st, s, display, vehicle, region, sy, sm):
    """Repair only missing/MANUAL HSD monthly cells; never historical Upto."""
    for fy in st["fys"]:
        for y, month in m.fy_months(fy, sy, sm):
            mon_name = m.month_name(month)
            needs = []
            for k in ("HSD KMPL INCL AC", "HSD KMPL EXCL AC"):
                cur = st["rows"].get(k, {}).get(fy, {}).get("months", {}).get(mon_name)
                if not _is_good(cur):
                    needs.append(k)
            if not needs:
                continue
            try:
                got = m.fetch_hsd(s, display, vehicle, region, y, month)
            except Exception as exc:
                print(f"HSD SAFE BACKFILL {y:04d}-{month:02d}: fetch failed, preserving existing cells: {exc}")
                continue
            for k in needs:
                val = (got.get(k) or {}).get("month")
                if _set_month_if_fetched(st, k, fy, mon_name, val, only_if_missing=True):
                    print(f"HSD SAFE BACKFILL {display} {y:04d}-{month:02d} {k}: {val}")


def lock_fy24_unavailable_sources(st, s, display):
    """Apply the confirmed FY2024-25 source-availability exceptions.

    LUB: no valid FY2024-25 source data; zero pages are NOT real values.
    Spring: no FY2024-25 website data.
    Tyres: only Apr-2024 exact depot data is usable; May-2024..Mar-2025 unavailable.
    """
    if FY24 not in st["fys"]:
        return

    # LUB FY2024-25 is unavailable. Explicitly remove previously written bogus zero history.
    m.ensure(st, "TOTAL LUB KMPL")
    for mon in m.MONTHS:
        st["rows"]["TOTAL LUB KMPL"][FY24]["months"][mon] = m.MANUAL
    st["rows"]["TOTAL LUB KMPL"][FY24]["upto"] = m.MANUAL
    print(f"FY24 SOURCE RULE {display}: TOTAL LUB KMPL Apr-2024..Mar-2025 unavailable -> MANUAL")

    # Spring Consumption FY2024-25 is unavailable on the website.
    m.ensure(st, "SPRING CONS")
    for mon in m.MONTHS:
        st["rows"]["SPRING CONS"][FY24]["months"][mon] = m.MANUAL
    st["rows"]["SPRING CONS"][FY24]["upto"] = m.MANUAL
    print(f"FY24 SOURCE RULE {display}: SPRING CONS Apr-2024..Mar-2025 unavailable -> MANUAL")

    # Tyres: fetch/retain Apr-2024 only. Later FY24 months are confirmed unavailable.
    try:
        apr = fetch_tyre_v10(s, display, 2024, 4, False)
    except Exception as exc:
        print(f"FY24 TYRE APR-2024 fetch failed; preserving any existing valid April value: {exc}")
        apr = {}
    for k in m.TYRE:
        m.ensure(st, k)
        existing_apr = st["rows"][k][FY24]["months"].get("Apr")
        april_value = (apr.get(k) or {}).get("month")
        if april_value is not None:
            st["rows"][k][FY24]["months"]["Apr"] = april_value
        elif not _is_good(existing_apr):
            st["rows"][k][FY24]["months"]["Apr"] = m.MANUAL
        for mon in m.MONTHS[1:]:
            st["rows"][k][FY24]["months"][mon] = m.MANUAL
        st["rows"][k][FY24]["upto"] = m.MANUAL
    print(f"FY24 SOURCE RULE {display}: TYRES Apr-2024 retained/fetched; May-2024..Mar-2025 unavailable -> MANUAL")


def safe_lub_all_months(st, s, display, vehicle, region, sy, sm):
    """Fetch direct-source Total Lub KMPL for every month where source data exists."""
    current_fy = m.selected_fy(sy, sm)
    for fy in st["fys"]:
        if fy == FY24:
            # Confirmed unavailable; never interpret the returned all-zero page as real data.
            continue
        months = m.fy_months(fy, sy, sm)
        for y, month in months:
            mon_name = m.month_name(month)
            try:
                pair = (m.fetch_lub(s, display, vehicle, region, y, month).get("TOTAL LUB KMPL") or {})
            except Exception as exc:
                print(f"LUB SAFE BACKFILL {y:04d}-{month:02d}: fetch failed, preserving existing cells: {exc}")
                continue
            mv, uv = pair.get("month"), pair.get("upto")
            if _set_month_if_fetched(st, "TOTAL LUB KMPL", fy, mon_name, mv):
                print(f"LUB SAFE BACKFILL {display} {y:04d}-{month:02d}: month={mv}")
            # Completed FY: Upto must be March cumulative only.
            if fy != current_fy and month == 3:
                if _set_upto_if_fetched(st, "TOTAL LUB KMPL", fy, uv):
                    print(f"LUB SAFE BACKFILL {display} {fy}: March Upto={uv}")
            # Current FY: Upto represents the selected month cumulative value.
            elif fy == current_fy and y == sy and month == sm:
                if _set_upto_if_fetched(st, "TOTAL LUB KMPL", fy, uv):
                    print(f"LUB SAFE BACKFILL {display} {fy}: selected-month Upto={uv}")


def safe_tyre_web_backfill(st, s, display, sy, sm):
    """Repair FY2025-26 onward tyre history using exact All Tyre Sizes Total web rows."""
    current_fy = m.selected_fy(sy, sm)
    for fy in st["fys"]:
        if fy == FY24:
            continue
        months = m.fy_months(fy, sy, sm)
        for y, month in months:
            need_upto = (fy != current_fy and month == 3) or (fy == current_fy and y == sy and month == sm)
            try:
                got = fetch_tyre_v10(s, display, y, month, need_upto)
            except Exception as exc:
                print(f"TYRE SAFE BACKFILL {y:04d}-{month:02d}: fetch failed, preserving existing cells: {exc}")
                continue
            mon_name = m.month_name(month)
            for k in m.TYRE:
                pair = got.get(k) or {}
                mv = pair.get("month")
                if mv is not None:
                    _set_month_if_fetched(st, k, fy, mon_name, mv)
                if need_upto and pair.get("upto") is not None:
                    _set_upto_if_fetched(st, k, fy, pair.get("upto"))
            print(f"TYRE SAFE BACKFILL {display} {y:04d}-{month:02d}: successful source merge")


ORIGINAL_POPULATE_TARGETS = v7.populate_targets


def populate_targets_v10(st, s, display, vehicle, region, sy, sm):
    # Repair source history before formatting/writing the sheet.
    safe_hsd_month_backfill(st, s, display, vehicle, region, sy, sm)
    safe_lub_all_months(st, s, display, vehicle, region, sy, sm)
    safe_tyre_web_backfill(st, s, display, sy, sm)
    lock_fy24_unavailable_sources(st, s, display)
    ORIGINAL_POPULATE_TARGETS(st, s, display, vehicle, region, sy, sm)


v7.populate_targets = populate_targets_v10


if __name__ == "__main__":
    try:
        sys.exit(v7.main())
    except Exception as exc:
        print(f"ANNUAL_KPI_FAILURE: {exc}")
        raise
