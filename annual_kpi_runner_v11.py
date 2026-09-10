#!/usr/bin/env python3
"""Annual KPI v11: v10 logic plus visible borders for the Upto column."""
import sys

import annual_kpi_runner_v10 as v10

m = v10.m
v7 = v10.v7
LAYOUT_VERSION = "11"

# Keep existing v7/v8/v9/v10 sheet layouts compatible.
v7.LAYOUT_VERSION = LAYOUT_VERSION

ORIGINAL_FORMAT_SHEET = v7.format_sheet_v7


def _apply_upto_borders(spreadsheet_id, mat):
    sid = m.sheet_id(spreadsheet_id, m.SHEET_TITLE)
    if sid is None:
        return
    border = {"style": "SOLID"}
    m.sheets_service().spreadsheets().batchUpdate(
        spreadsheetId=spreadsheet_id,
        body={
            "requests": [
                {
                    "updateBorders": {
                        "range": {
                            "sheetId": sid,
                            "startRowIndex": 0,
                            "endRowIndex": len(mat),
                            "startColumnIndex": 17,
                            "endColumnIndex": 18,
                        },
                        "top": border,
                        "bottom": border,
                        "left": border,
                        "right": border,
                        "innerHorizontal": border,
                    }
                }
            ]
        },
    ).execute()


def format_sheet_v11(spreadsheet_id, mat, fys):
    # v10 already retries transient failures for the main sheet formatting.
    ORIGINAL_FORMAT_SHEET(spreadsheet_id, mat, fys)
    # Apply a visible grid specifically to column R (Upto), including header and rows.
    attempts = 4
    for attempt in range(1, attempts + 1):
        try:
            _apply_upto_borders(spreadsheet_id, mat)
            return
        except Exception as exc:
            if attempt >= attempts or not v10._retryable_google_error(exc):
                raise
            delay = 2 ** attempt
            print(
                f"GOOGLE SHEETS UPTO BORDER RETRY {attempt}/{attempts - 1}: "
                f"{exc}; retrying in {delay}s"
            )
            v10.time.sleep(delay)


v7.format_sheet_v7 = format_sheet_v11


if __name__ == "__main__":
    try:
        sys.exit(v7.main())
    except Exception as exc:
        print(f"ANNUAL_KPI_FAILURE: {exc}")
        raise
