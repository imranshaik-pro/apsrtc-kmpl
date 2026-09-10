#!/usr/bin/env python3
"""Annual KPI v9 safety wrapper.

Fixes two production issues without disturbing the validated v8 LUB/target logic:
1) break the tyre recursion introduced by v6 for FY2025-26 onward;
2) treat v7/v8 sheet layouts as compatible so a version bump does not force a destructive full rebuild.
"""
import sys

import annual_kpi_runner_v3 as v3
import annual_kpi_runner_v8 as v8

m = v8.m
v7 = v8.v7
LAYOUT_VERSION = "9"


def fetch_tyre_v9(s, depot, y, month, need_upto):
    # FY2024-25 keeps the exact official-booklet parser from v6.
    if m.selected_fy(y, month) == "2024-25":
        return v7.v6.fetch_tyre_v6(s, depot, y, month, need_upto)
    # FY2025-26 onward must call the original web tyre implementation directly.
    # Calling m.fetch_tyre here would recurse because v6 replaced that symbol.
    return v3.fetch_tyre(s, depot, y, month, need_upto)


m.fetch_tyre = fetch_tyre_v9
v7.LAYOUT_VERSION = LAYOUT_VERSION


def meta_version_v9(spreadsheet_id):
    """Preserve an existing v7/v8 dashboard instead of forcing FULL REPAIR.

    Those layouts already have the Target column. Returning v9 compatibility causes
    the runner to load the existing sheet and update only the requested month/targets,
    so failed/blank source fetches cannot erase unrelated historical months.
    """
    try:
        vals = m.read_values(spreadsheet_id, f"'{m.META_TITLE}'!A:B")
        d = {str(r[0]): str(r[1]) for r in vals[1:] if len(r) >= 2}
        stored = d.get("LAYOUT_VERSION", "")
        if stored in {"7", "8", "9"}:
            return LAYOUT_VERSION
        return stored
    except Exception:
        return ""


v7.meta_version = meta_version_v9


if __name__ == "__main__":
    try:
        sys.exit(v7.main())
    except Exception as exc:
        print(f"ANNUAL_KPI_FAILURE: {exc}")
        raise
