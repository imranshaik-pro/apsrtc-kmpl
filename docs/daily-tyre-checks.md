# Optional daily tyre details

Generate the regular daily report first using the unchanged application and
calculations. Only after its output file exists, the automated runner calls the
separate tyre module. Upload and existing Telegram delivery use that combined
file; no separate tyre message is introduced.

Scheduled requests and manual today resolve to yesterday in Asia/Kolkata.
Earlier selected dates remain unchanged. Check the resolved date: odd dates
fetch RC front tyres, mismatched tyres and fitted repair tyres in RNSO/RNSI
positions, plus a separately dated spare-tyre snapshot; even dates make no tyre requests.

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

Validation: 37 focused tests passed and changed Python modules compiled.
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

## Spare tyres over two months — implemented 1 October 2026

The owner's uploaded source HTML confirms PRODDUTUR=114 and RAJAMPET=115.
The supplied form has only depot_id; no date selector. The nine Proddatur
records have Run Date 01-10-2026, with vehicle, tyre number, position and days
in use. Preserve the supplied source as tests/fixtures/spare-tyres-proddutur.html.

On an odd resolved daily date, POST /tyres/spare_tyre.php with blank depot_id
to obtain the source dropdown. Resolve the exact normalized selected depot,
then POST its verified option value. Do not hardcode a depot ID globally.
Filter returned rows by exact depot and validate the required table columns,
vehicle/tyre/position, numeric days and a single valid Run Date. Empty valid
tables are omitted; unavailable or malformed reports receive an unavailable
note, rather than being counted as zero. Deduplicate repeated tyre identity
(vehicle, tyre number, position); reject conflicting duplicates.

Render Telugu counts and each vehicle/position/tyre number/days-in-use.
Always label the source Run Date separately, explicitly independent of the
daily report date. This is the source's available snapshot, including when
requested alongside a historical daily report; it is not historical spare
data. No invented date parameter or historical reconstruction is used.
The source defines the over-two-month selection; do not replace it with an
assumed fixed sixty-day threshold.

An RC parent-page failure now leaves independent fitted-repair and spare
requests available. Failure in the spare source preserves the completed HSD
report and other successful tyre sections. Odd/even gating and regular HSD
calculations, upload and delivery remain unchanged.

37 focused checks and Python compile pass locally. The exact supplied nine
records, both verified IDs, snapshot date labeling, malformed/mixed dates,
empty results, duplicate rows and failure isolation are covered. Live spare
fetch/Hub/Telegram validation remains unverified: direct source browser
inspection returned 502. Existing cached Drive reports still reuse their
saved contents. This change is committed to the draft PR, not production.
