# Optional daily tyre details

Generate the regular daily report first using the unchanged application and
calculations. Only after its output file exists, the automated runner calls the
separate tyre module. Upload and existing Telegram delivery use that combined
file; no separate tyre message is introduced.

Scheduled requests and manual today resolve to yesterday in Asia/Kolkata.
Earlier selected dates remain unchanged. Check the resolved date: odd dates
fetch RC front tyres, mismatched tyres and fitted repair tyres in RNSO/RNSI
positions; even dates make no tyre requests.

POST rc_tyres_front1.php with fyymm=D/M/YYYY, then rcpopup.php and
samepopup.php with dt=D/M/YYYY, regn=mapped district, dept blank. For repair
 tyres, POST fitted_repair1.php with fyymm=D/M/YYYY before repairpopup.php with
 the same dt/regn/blank-dept payload. Filter the
district response by exact normalized depot identity; validate heading date,
vehicle and tyre-position columns. Never interpret unavailable data as zero.

Display Telugu category counts, vehicle numbers and tyre positions only.
Omit each category with zero rows. When all categories are zero, preserve the daily text
exactly with no tyre heading or completion marker. A valid positive RC-front
result still displays when mismatched tyres are zero. Source/authentication
failure adds a short unavailable note while preserving the completed daily
content. Replace the local combined file atomically.

Existing cached Drive reports keep the original reuse behavior. This change
does not refresh previously uploaded reports or modify the Drive integration.

Validation: 26 focused tests passed and changed Python modules compiled.
Coverage includes zero/positive category combinations, odd/even dates, source
validation, source failures, depot isolation and daily-before-tyres ordering.
The 13 prior daily regression failures are corrected separately in draft PR #6.
This draft remains unmerged; live evidence below predates the repair addition.

## Live verification — 1 October 2026

Draft run 36886050944 at commit a7f59c65506bf9244ae43b16ab9a689d853ea0e6
passed compile and 21 focused checks, generated RAJAMPET 2026-09-01, uploaded
Drive file 1T6oM9vt2opr_RAQg4lJGeU_5IhpXl-k4 and received Telegram API success
for one combined message. The saved file was read through Drive: HSD day/Upto
5.14; RC-front vehicle 26Z0286, positions FNS/FOS, one vehicle/two records;
zero mismatched category omitted.

A real Hub form request for the same depot/date created register row 20.
Hub-triggered master run 36886550663 reused that combined file, completed the
callback and received Telegram success for one message. Row 20 status is
COMPLETED | DAILY | RAJAMPET | 2026-09-01, linking the same Drive file.
This proves draft generation and production Hub cached delivery separately;
Hub still dispatches master and fresh tyre enrichment is not active there.
PR remains unmerged. Telegram API acceptance is verified, not a recipient read.

Observed existing workflow limitation: fresh-generation logs contain multiple
Report date lines; tail-based extraction takes the formatted display date,
while cached runs retain ISO date. No date calculation was changed for this.

## Fitted repair addition — 1 October 2026

The owner supplied fitted_repair1.php POST fyymm=30/09/2026 and the existing
rctyre.js repairTyre function POSTs repairpopup.php with dt/regn/dept. The
screenshot confirms district/depot/vehicle/tyre-position columns. Reuse the
validated popup parser and Telugu counts/vehicle-position rendering. Wrong
heading dates, failures and other depots cannot become matching vehicle data.
The new repair category has compile and fixture test coverage, not a live
source/delivery validation. Regular daily calculations and delivery are unchanged.

## Spare tyres over two months — source verification pending

Owner supplied POST /tyres/spare_tyre.php with depot_id=115. Screenshot shows
Run Date, Depot, Vehicle Num, Vehicle type, RTC Tyre No and Make; this is a
separate report from fitted repair tyres. No selected-date parameter was supplied.
Do not label a current snapshot as the selected historical day's data. Verify the
depot dropdown option for 115, full response HTML (including remaining columns),
and whether historical Run Dates are supported before enabling this category.
Source inspection returned 502 Bad Gateway; no spare category fetch is enabled.
The favicon request is unrelated to report data.
