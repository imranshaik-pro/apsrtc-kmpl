#!/usr/bin/env python3
"""Annual KPI v8 target expansion + exact depot-wise LUB parsing.

Target rules:
- Targets are FY attributes and are fetched from APRIL of each FY only.
- HSD KMPL INCL AC / EXCL AC
- B.D RATE
- MED CANCL.
- SPRING CONS
- tyre KPIs where an exact-depot target exists
All other KPI target cells remain blank.

LUB rule:
- POST dt=Month_Year to lub_rgn_rpt.php
- select ONLY the DEPOT-WISE LUB KMPL table
- select the exact depot row (e.g. PRODDUTUR)
- monthly = For the Month CY -> Total Lub KMPL
- upto = Upto the Month CY -> Total Lub KMPL
- never use district/zone/corporation rows and never calculate the value
"""
import sys
from calendar import monthrange
from bs4 import BeautifulSoup
import annual_kpi_runner_v7 as v7

m = v7.m
v5 = v7.v5
LAYOUT_VERSION = "8"

TARGET_KPIS = {
    "HSD KMPL INCL AC", "HSD KMPL EXCL AC",
    "B.D RATE", "MED CANCL.", "SPRING CONS",
    *m.TYRE,
}
v7.TARGET_KPIS = TARGET_KPIS


def _exact_target_from_page(s, base, path, params, display, vehicle, required, header_match):
    """Return TARGET only from the selected depot row and an explicit target header."""
    html = m.get_html(s, base, path, params)
    h, row = m.find_depot(html, display, vehicle, required)
    if not row:
        return None
    for i, header in enumerate(h or []):
        nh = m.n(header)
        if "TARGET" not in nh and "TGT" not in nh:
            continue
        if header_match(nh):
            return m.at(row, i)
    return None


def operational_targets(s, display, vehicle, region, y, month):
    out = {}
    try:
        v = _exact_target_from_page(
            s, m.core.MED_BASE, "sysbd_dpt.php",
            {"action":"", "yymm":m.token(y, month), "dist":m.district(region)},
            display, vehicle, ["BD RATE"],
            lambda h: "BD RATE" in h or ("BD" in h and "RATE" in h),
        )
        if v is not None: out["B.D RATE"] = v
    except Exception as exc:
        print(f"BD target {y:04d}-{month:02d}: {exc}")

    try:
        v = _exact_target_from_page(
            s, m.core.MEDNEW_BASE, "medcan_um_dpt.php",
            {"action":"", "fdate":m.token(y, month, "-"), "dist":m.district(region)},
            display, vehicle, ["CANC"],
            lambda h: "CANC" in h or "%" in h,
        )
        if v is not None: out["MED CANCL."] = v
    except Exception as exc:
        print(f"MED target {y:04d}-{month:02d}: {exc}")

    try:
        v = _exact_target_from_page(
            s, "http://103.44.14.20/storeap", "deptspring.php",
            {"action":"", "yymm":m.token(y, month), "dist":m.district(region)},
            display, vehicle, ["SPRING CONSUMPTION PER LAKH KMS"],
            lambda h: "SPRING" in h or "CONSUMPTION" in h,
        )
        if v is not None: out["SPRING CONS"] = v
    except Exception as exc:
        print(f"SPRING target {y:04d}-{month:02d}: {exc}")

    print(f"Operational targets {display} {y:04d}-{month:02d}: {out}")
    return out


def _pick_lub_column(headers, group_words):
    """Pick Total Lub KMPL under the requested grouped header only."""
    for i, h in enumerate(headers or []):
        nh = m.n(h)
        if "TOTAL LUB KMPL" not in nh:
            continue
        if all(word in nh for word in group_words):
            return i
    return None


def fetch_lub_depotwise(s, display, vehicle, region, y, month):
    """Exact parser for the DEPOT-WISE LUB KMPL table shown on APSRTC."""
    html = m.lub_html(s, y, month)  # confirmed POST dt=Month_Year
    soup = BeautifulSoup(html, "html.parser")

    wanted = {m.n(display), m.n(vehicle)}
    for table in soup.find_all("table"):
        text = m.n(table.get_text(" ", strip=True))
        # Critical discriminator: district-wise table also has Total Lub KMPL.
        # We accept only a table whose headers include DEPOT.
        if "DEPOT" not in text or "TOTAL LUB KMPL" not in text:
            continue

        headers, rows = m.core.expanded_headers(table)
        depot_i = m.core.col(headers, ["DEPOT", "DEPOT NAME"])
        if depot_i is None:
            continue

        row = None
        for r in rows:
            if depot_i < len(r) and m.n(r[depot_i]) in wanted:
                row = r
                break
        if row is None:
            continue

        month_i = _pick_lub_column(headers, ["FOR", "MONTH", "CY"])
        upto_i = _pick_lub_column(headers, ["UPTO", "MONTH", "CY"])
        if upto_i is None:
            upto_i = _pick_lub_column(headers, ["UP TO", "MONTH", "CY"])

        # Some expanded-header implementations may normalize the group wording
        # differently. Fall back only among TOTAL LUB KMPL columns in this exact
        # DEPOT table, preserving left-to-right group order from the report:
        # For Month CY, Upto Month CY, Upto Month LY.
        total_cols = [i for i, h in enumerate(headers or []) if "TOTAL LUB KMPL" in m.n(h)]
        if month_i is None and total_cols:
            month_i = total_cols[0]
        if upto_i is None and len(total_cols) >= 2:
            upto_i = total_cols[1]

        mv = m.at(row, month_i)
        uv = m.at(row, upto_i)
        print(f"LUB depot-wise {display} {y:04d}-{month:02d}: month={mv} upto={uv}; total_cols={total_cols}")
        return {"TOTAL LUB KMPL": {"month": mv, "upto": uv}}

    raise RuntimeError(f"DEPOT-WISE LUB KMPL row not found for {display} {y:04d}-{month:02d}")


def populate_targets_v8(st, s, display, vehicle, region, sy, sm):
    v7.ensure_target_slots(st)
    for fy in st["fys"]:
        start_y, _ = m.core.parse_fy(fy)
        # Locked business rule: target comes from APRIL and remains unchanged
        # for every month of that FY.
        source_y, source_m = start_y, 4

        try:
            ht = v7.hsd_targets(s, display, vehicle, region, source_y, source_m)
        except Exception as exc:
            print(f"HSD target {fy}: {exc}"); ht = {}
        for k, val in ht.items():
            if k in st["rows"]: st["rows"][k][fy]["target"] = val

        try:
            ot = operational_targets(s, display, vehicle, region, source_y, source_m)
        except Exception as exc:
            print(f"Operational target {fy}: {exc}"); ot = {}
        for k, val in ot.items():
            if k in st["rows"]: st["rows"][k][fy]["target"] = val

        if fy == "2024-25":
            try:
                tt = v7.tyre_targets_pdf_2024(s, display)
            except Exception as exc:
                print(f"TYRE PDF target {fy}: {exc}"); tt = {}
        else:
            try:
                tt = v7.tyre_targets_web(s, display, source_y, source_m)
            except Exception as exc:
                print(f"TYRE web target {fy}: {exc}"); tt = {}
        for k, val in tt.items():
            if k in st["rows"]: st["rows"][k][fy]["target"] = val


# Patch v7 before its main runs.
v7.populate_targets = populate_targets_v8
v7.LAYOUT_VERSION = LAYOUT_VERSION
m.fetch_lub = fetch_lub_depotwise

_orig_meta = v7.meta_version_v7

def meta_version_v8(spreadsheet_id):
    try:
        vals = m.read_values(spreadsheet_id, f"'{m.META_TITLE}'!A:B")
        d = {str(r[0]): str(r[1]) for r in vals[1:] if len(r) >= 2}
        return d.get("LAYOUT_VERSION", "")
    except Exception:
        return ""

v7.meta_version_v7 = meta_version_v8

if __name__ == "__main__":
    try:
        sys.exit(v7.main())
    except Exception as exc:
        print(f"ANNUAL_KPI_FAILURE: {exc}")
        raise
