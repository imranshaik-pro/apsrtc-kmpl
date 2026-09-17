#!/usr/bin/env python3
"""Controlled source validation for Monthly Vehicle Performance.

This does NOT create/upload a production Monthly workbook. It authenticates to
APSRTC, calls the exact source adapters used by Vehicle Performance, and checks
known PRODDUTUR August-2026 reference points before production use.
"""
import argparse
import sys

from src.auth.client import login
from src.reporting.vehicle_history import fetch_mtd, fetch_trend, fetch_schedule


def ok(label, detail=""):
    print(f"PASS: {label}" + (f" | {detail}" if detail else ""))


def fail(label, detail=""):
    print(f"FAIL: {label}" + (f" | {detail}" if detail else ""))
    return 1


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--depot", default="PRODDUTUR")
    p.add_argument("--region", default="YSRKADAPA")
    p.add_argument("--zone", default="ZONE-4")
    p.add_argument("--month", default="202608")
    args = p.parse_args()

    if args.month != "202608":
        print("This validator currently has fixed reference assertions for 202608.")
        return 2

    session = login()
    failures = 0

    print("VALIDATING MTD-598...")
    mtd = fetch_mtd(session, args.month, args.region, args.depot)
    if not mtd:
        failures += fail("MTD-598 returned vehicles")
    else:
        ok("MTD-598 returned vehicles", f"count={len(mtd)}")
    if "02Z0027" not in mtd:
        failures += fail("MTD roster contains 02Z0027")
    else:
        got = mtd["02Z0027"].get("kmpl")
        if got == 4.82:
            ok("02Z0027 Aug-2026 MTD HSD KMPL", f"{got:.2f}")
        else:
            failures += fail("02Z0027 Aug-2026 MTD HSD KMPL", f"expected=4.82 got={got}")

    print("VALIDATING FY2026-27 TREND...")
    trend_2627 = fetch_trend(session, "2026-27", args.zone, args.region, args.depot)
    if "02Z0027" not in trend_2627:
        failures += fail("FY26-27 trend contains 02Z0027")
    else:
        vals = trend_2627["02Z0027"]["months"]
        expected = {"Apr": 4.94, "May": 4.78, "Jun": 4.96, "Jul": 4.80, "Aug": 4.82}
        bad = {m: (expected[m], vals.get(m)) for m in expected if vals.get(m) != expected[m]}
        if bad:
            failures += fail("02Z0027 FY26-27 Apr-Aug trend values", str(bad))
        else:
            ok("02Z0027 FY26-27 Apr-Aug trend values", str(expected))

    print("VALIDATING FY2025-26 TREND...")
    trend_2526 = fetch_trend(session, "2025-26", args.zone, args.region, args.depot)
    if "02Z0027" not in trend_2526:
        failures += fail("FY25-26 trend contains 02Z0027")
    else:
        vals = trend_2526["02Z0027"]["months"]
        expected = {"Apr": 5.34, "May": 5.41, "Jun": 5.15, "Jul": 5.21, "Aug": 4.91, "Sep": 4.87, "Oct": 4.83, "Nov": 4.80, "Dec": 4.95, "Jan": 4.87, "Feb": 4.91, "Mar": 4.85}
        bad = {m: (expected[m], vals.get(m)) for m in expected if vals.get(m) != expected[m]}
        if bad:
            failures += fail("02Z0027 FY25-26 trend values", str(bad))
        else:
            ok("02Z0027 FY25-26 trend values")

    print("VALIDATING AUG-2026 SCH-III/SCH-IV...")
    s3 = fetch_schedule(session, 3, "202608", "August_2026", args.zone, args.region, args.depot)
    s4 = fetch_schedule(session, 4, "202608", "August_2026", args.zone, args.region, args.depot)
    ok("SCH-III parser returned", f"vehicles={len(s3)}")
    ok("SCH-IV parser returned", f"vehicles={len(s4)}")
    got_s4 = s4.get("40Z0942", [])
    if "27-08-2026" in got_s4:
        ok("40Z0942 SCH-IV actual completion date", "27-08-2026")
    else:
        failures += fail("40Z0942 SCH-IV actual completion date", f"expected 27-08-2026 got={got_s4}")

    both = sorted(set(s3) & set(s4))
    dup3 = sorted(v for v, dates in s3.items() if len(dates) > 1)
    dup4 = sorted(v for v, dates in s4.items() if len(dates) > 1)
    print(f"INFO: both SCH-III/SCH-IV same month vehicles={both}")
    print(f"INFO: duplicate SCH-III entries={dup3}")
    print(f"INFO: duplicate SCH-IV entries={dup4}")

    if failures:
        print(f"MONTHLY_SOURCE_VALIDATION_FAILED: {failures} assertion(s)")
        return 1
    print("MONTHLY_SOURCE_VALIDATION_SUCCESS")
    return 0


if __name__ == "__main__":
    sys.exit(main())
