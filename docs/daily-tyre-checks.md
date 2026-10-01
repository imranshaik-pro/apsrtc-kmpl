# Daily depot tyre checks on odd report dates

Owner-approved scope, 1 October 2026: add RC front tyres and mismatched tyres,
including depot summaries and vehicle numbers. Repair tyres are excluded.

## Date and fetch rules

- Scheduled requests and manual today use yesterday in Asia/Kolkata, as before.
- Earlier manual dates use exactly the selected date; future dates are rejected.
- Apply `resolved_report_date.day % 2 == 1` after date resolution.
- An even report date performs no tyre requests and adds no tyre section. The
  standard daily HSD report still runs normally.
- This is odd calendar dates, not an every-48-hour schedule. A month's 31st and
  the next month's 1st both qualify.

## Source contract

The owner's captured rctyre.js establishes these two POST endpoints:

| Step | URL path | Payload |
| --- | --- | --- |
| Date submission | `/med/rc_tyres_front1.php` | `fyymm=D/M/YYYY` |
| RC front details | `/med/rcpopup.php` | `dt=D/M/YYYY`, `regn=<mapped district>`, `dept=''` |
| Mismatched details | `/med/samepopup.php` | same popup payload |

Reuse the daily authenticated session. The blank depot parameter returns a
district list: filter rows by the selected depot's exact normalized name. Do
not infer tyre aliases or transfer another depot's rows. Preserve vehicle
numbers and tyre identifiers as text. Group by unique vehicle, retain distinct
positions. Display only Telugu category summaries, unique vehicle counts, tyre-record counts, vehicle numbers and tyre positions. Do not add RTC numbers, make, size or other detailed columns to the daily text. Mismatched vehicles come
from the source report; do not invent a new mismatch rule based only on make.

Validate the source heading date and recognized Depot/Vehicle columns. A valid
empty result means zero matching depot vehicles. HTTP, date or table validation
failure means unavailable, never zero. One unavailable extra section does not
block the HSD report or the other valid extra section.

## Cached reports and delivery

Completed tyre sections are reused. On odd dates, an existing daily file that
lacks complete checks can be enriched without recalculating its HSD content.
Update the same Drive file ID/link; do not create a duplicate. An incomplete
retry must not replace an already collected partial section with another
failed attempt. Scheduled retries keep existing Telegram resend suppression.
Google upload/update failures still fail delivery; auxiliary source failure
does not masquerade as successful tyre data.

Implementation: `src/reporting/tyre_checks.py`, `src/reporting/application.py`,
`run_automated_daily.py`, `src/integrations/google_drive.py`.

## Validation and deployment status

- Compile passed for changed Python modules.
- Focused pytest checks: 20 passed, including odd/even requests, selected-date
  resolution, depot isolation, duplicate/rowspan handling, invalid and empty
  tables, source failure isolation and cached file ID/HSD preservation.
- Live source check for RAJAMPET / 2026-09-01: RC-front endpoint returned one
  vehicle, 26Z0286, with two records (FNS and FOS); mismatched endpoint returned
  zero matching Rajampet vehicles. Both source-to-summary checks passed.
- Existing daily regression subset: 42 passed / 13 failed on both unchanged
  master and the proposed branch. Existing failures include stale report/count
  assertions, missing raw_records in vehicle-summary tests, rounding assertions
  and a region_response.html fixture absent from the repository. These are not
  claimed fixed by this bounded addition.
- This change is reviewable and unmerged. The source-level check is not a live
  Hub, Drive-update or Telegram-delivery certification of the new feature.
