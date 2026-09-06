#!/usr/bin/env python3
"""Annual KPI v6.

Adds evidence-based FY2024-25 tyre booklet parsing:
- booklet depot codes (e.g. PRODDUTUR -> PDTR), not tyre-web codes
- exact depot rows only
- tyre life values are already in lakh km in the booklet: no /100000 conversion
- April monthly = April upto because April is the first FY month
- later booklet depot pages are cumulative-only; do not invent monthly values
- district Target/For/Upto pages are recognised but never substituted for depot values
"""
import io
import re
import sys

import pdfplumber
import annual_kpi_runner_v5 as v5

m = v5.m
LAYOUT_VERSION = "6"

PDF_DEPOT_CODE = {
    "BADVEL": "BDVL",
    "JAMMALAMADUGU": "JMD",
    "KADAPA": "KDP",
    "MYDUKUR": "MYDK",
    "PRODDUTUR": "PDTR",
    "PULIVENDULA": "PVL",
    "RAJAMPET": "RJPT",
}


def _nums(line):
    return [float(x) for x in re.findall(r"-?\d+(?:\.\d+)?", line)]


def _line_for_code(text, code):
    for raw in (text or "").splitlines():
        line = " ".join(raw.split())
        if re.match(rf"^{re.escape(code)}(?:\s|$)", line, flags=re.I):
            return line
    return None


def exact_tyre_pdf_fallback(s, depot, y, month):
    """Return (monthly, upto) from official FY2024-25 TRS booklet.

    The depot tyre-performance pages contain cumulative (UPTO) figures only.
    District summary pages contain Target/For/Upto, but they are district values and
    must never be used as the selected depot's monthly value.
    """
    if m.selected_fy(y, month) != "2024-25":
        return {}, {}

    code = PDF_DEPOT_CODE.get(m.n(depot))
    if not code:
        raise RuntimeError(f"No FY2024-25 booklet depot code for {depot}")

    mon = m.datetime(y, month, 1).strftime("%b").lower()
    url = f"{m.core.MED_BASE}/trs_booklet/2024-25/{mon}-{y}.pdf"
    rr = s.get(url, timeout=60)
    rr.raise_for_status()
    if not rr.content.startswith(b"%PDF"):
        raise RuntimeError("TRS booklet is not a PDF")

    upto = {}
    district_target_seen = []

    with pdfplumber.open(io.BytesIO(rr.content)) as pdf:
        for page_no, page in enumerate(pdf.pages, start=1):
            text = page.extract_text() or ""
            nt = m.n(text)

            # Depot cumulative tyre-life page. Expected row layout:
            # CODE newCY newLY var rcCY rcLY var totalCY totalLY var
            if "NEW TYRE LIFE" in nt and "RC TYRE LIFE" in nt and "TOTAL TYRE LIFE" in nt and "DEPOT" in nt:
                line = _line_for_code(text, code)
                if line:
                    vals = _nums(line[len(code):])
                    if len(vals) >= 9:
                        upto["NEW TYRE LIFE"] = vals[0]
                        upto["RC TYRE LIFE"] = vals[3]
                        upto["AVG TYRE LIFE"] = vals[6]
                        print(f"TYRE PDF life {y:04d}-{month:02d} {code} p{page_no}: NEW={vals[0]:.2f} RC={vals[3]:.2f} TOTAL={vals[6]:.2f} lakh km")

            # Depot cumulative scrap/rate page. Expected row layout:
            # CODE ntsCY ntsLY var rcCY rcLY var totalCY totalLY var rtCY rtLY var
            if "NEW TYRE SCRAP RATE" in nt and "1ST RC SCRAP RATE" in nt and "TOTAL SCRAP RATE" in nt and "RT FACTOR" in nt and "DEPOT" in nt:
                line = _line_for_code(text, code)
                if line:
                    vals = _nums(line[len(code):])
                    if len(vals) >= 12:
                        upto["N.T.S RATE"] = vals[0]
                        upto["Ist RC S Rate"] = vals[3]
                        upto["TTL SCP Rate"] = vals[6]
                        upto["RT Factor"] = vals[9]
                        print(f"TYRE PDF rates {y:04d}-{month:02d} {code} p{page_no}: NTS={vals[0]:.2f} 1RC={vals[3]:.2f} TOTAL={vals[6]:.2f} RT={vals[9]:.2f}")

            # Evidence only: district Target/For/Upto summary exists in booklet.
            # Do not substitute district figures for a depot.
            if "TARGET 24-25" in nt and "FOR" in nt and "UPTO" in nt:
                district_target_seen.append(page_no)

    if not upto:
        raise RuntimeError(f"No exact depot tyre rows found in booklet for {code}: {url}")

    monthly = dict(upto) if month == 4 else {}
    if month != 4:
        print(f"TYRE PDF {y:04d}-{month:02d}: depot pages are UPTO-only; monthly values left blank rather than using district For values")
    if district_target_seen:
        print(f"TYRE PDF {y:04d}-{month:02d}: district Target/For/Upto summary seen on pages {district_target_seen}; not used as depot data")
    print(f"TYRE PDF fallback used: {url} depot={code}")
    return monthly, upto


def fetch_tyre_v6(s, depot, y, month, need_upto):
    # FY2024-25: official booklet is authoritative because tyre web history is missing.
    if m.selected_fy(y, month) == "2024-25":
        try:
            pm, pu = exact_tyre_pdf_fallback(s, depot, y, month)
            # For April, monthly == upto. For later months, only use booklet's exact
            # depot cumulative values when Upto is actually needed; do not fabricate For.
            return {
                name: {
                    "month": pm.get(name),
                    "upto": pu.get(name) if need_upto else None,
                }
                for name in m.TYRE
            }
        except Exception as exc:
            print(f"TYRE PDF {y:04d}-{month:02d}: {exc}")
            return {name: {"month": None, "upto": None} for name in m.TYRE}

    return m.fetch_tyre(s, depot, y, month, need_upto)


# Patch v3 module used by v5 main.
m.tyre_pdf_fallback = exact_tyre_pdf_fallback
m.fetch_tyre = fetch_tyre_v6

# Force one clean repair so previous wrong/missing FY2024-25 tyre cells are rebuilt.
_orig_meta_version = v5.meta_version

def meta_version_v6(spreadsheet_id):
    try:
        vals = m.read_values(spreadsheet_id, f"'{m.META_TITLE}'!A:B")
        d = {str(r[0]): str(r[1]) for r in vals[1:] if len(r) >= 2}
        return d.get("LAYOUT_VERSION", "")
    except Exception:
        return ""

v5.LAYOUT_VERSION = LAYOUT_VERSION
v5.meta_version = meta_version_v6

if __name__ == "__main__":
    try:
        sys.exit(v5.main())
    except Exception as exc:
        print(f"ANNUAL_KPI_FAILURE: {exc}")
        raise
