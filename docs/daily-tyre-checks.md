# Optional current-daily tyre details

## Business rule — updated 1 October 2026

The owner replaced odd-day gating with current-request gating. Apply to every
depot: scheduled daily runs, an omitted date, or a manual selected date equal
to today in Asia/Kolkata fetch tyres on every day. Manual dates earlier than
today make no tyre requests, whether odd or even. Future dates are rejected.
Keep original request intent before resolving today's KMPL date to yesterday.
The KMPL date-resolution rule and regular calculations are unchanged.

Generate regular KMPL first. Only then enrich its local delivery file. Cached
current requests refresh tyres in the downloaded local delivery copy; cached
historical requests remove any previously saved tyre section from that local
copy. Existing saved Drive files are not rewritten. Consequently, a cached
report's Drive link may still show earlier saved contents while Telegram uses
the refreshed local copy. Newly generated reports upload the combined file.

## Date-selected tyre sources

RC front: POST rc_tyres_front1.php with fyymm=D/M/YYYY, then rcpopup.php.
Mismatched tyres: samepopup.php. Repair tyres: POST fitted_repair1.php with
fyymm=D/M/YYYY before repairpopup.php. Popup payload is dt=D/M/YYYY,
regn=mapped district, dept blank, as confirmed in the owner's rctyre.js.
Use the resolved KMPL report date for these date-selectable reports.
The later supplied suggested dist_code payload does not replace that captured
JavaScript contract without an actual contradictory request capture.

Filter district rows by exact normalized depot; validate the report heading
date, vehicle and position columns. Render Telugu category counts, vehicle
numbers and tyre positions. Each zero category is hidden. Failures are
reported as unavailable, never as zero. Each successful independent category
survives another source's failure; completed KMPL remains available.

## Spare tyres over two months

The owner's source confirms PRODDUTUR=114, RAJAMPET=115; the form supports
depot_id only. POST /tyres/spare_tyre.php with blank depot_id to read the
dropdown, resolve the selected depot exactly, then POST its verified option
value. Do not hardcode one depot's ID for all depots.

Validate table columns, depot, vehicle/tyre/position, numeric days and one
valid Run Date. The supplied Proddatur snapshot contains nine records dated
2026-10-01, preserved in tests/fixtures/spare-tyres-proddutur.html.
Render counts, vehicle, spare position, tyre number and days in use in Telugu.
Always display its own source Run Date explicitly independent of the KMPL
date. The source's over-two-month selection is retained; no assumed fixed
sixty-day threshold is applied. No historical spare snapshots are fetched
for historical daily requests.

## Verification

45 focused checks pass locally, with compile checks for runner, tyre module
and tests. Coverage includes current versus historical intent, yesterday
resolution on both odd/even dates, both depots, fresh/cached delivery, exact
payloads, source date and depot filtering, supplied spare records, empty
results, duplicates and isolated failures. Workflow includes this test gate.
The 13 earlier daily regression failures are fixed separately in draft PR #6.
This draft remains unmerged. Current-only cached delivery and live repair/spare
fetching are verified in run 36900410412 below. Fresh KMPL generation plus these
new categories, and a new Hub callback with this revision, remain unverified.

## Earlier live evidence — prior RC/mismatch implementation

Draft run 36886050944 at a7f59c65506bf9244ae43b16ab9a689d853ea0e6
generated RAJAMPET 2026-09-01, uploaded Drive file
1T6oM9vt2opr_RAQg4lJGeU_5IhpXl-k4 and received Telegram API success
for one combined message. Saved HSD day/Upto 5.14; RC-front vehicle
26Z0286 FNS/FOS, one vehicle/two records; zero mismatch omitted.

Hub form row 20 triggered master run 36886550663, reused that combined file,
completed the callback and received Telegram API success. This proves that
earlier draft generation and production cached delivery separately. It does
not validate the subsequent repair/spare additions or current-only rule.
Fresh enrichment is not active on master until merge; recipient reading is
not verified. Direct source browser inspection previously returned 502.

Existing workflow limitation: fresh generation emits multiple Report date
lines and tail-based extraction can select a formatted display date. This
change does not alter that extraction or delivery scheduling.

## Current-request live validation — 1 October 2026

Draft run 36900410412 (#133), job 110497868552, tested commit
e8bd937cf33a99c9c89d23a2cc5c86e55ec4b1a8 with PRODDUTUR and selected
2026-10-01. It resolved KMPL to 2026-09-30, reused the existing saved KMPL
file and performed live tyre fetches on the local delivery copy. Compile and
45 focused checks passed in GitHub Python 3.11. The run succeeded; Telegram
API accepted one combined message at 17:35:23 UTC. Hub callback was skipped
because this manual draft test did not supply a Hub response row.

Artifact 11181398003 was downloaded and read. It contains mismatch counts
6 vehicles/40 records; repair counts 2 vehicles/2 records, 02Z0129 RNSO and
39Z0842 RNSI; spare counts 9 vehicles/9 records with source date 2026-10-01.
The RC-front category is omitted after validated zero rows. No unavailable
source notes appear. All nine spare vehicle/position/tyre-number/days values
match the supplied source fixture. Both repair vehicle positions match the
owner's supplied modal data, with the MYDUKUR vehicle excluded.

The saved Drive file 17HG-Fp_rw7y1SnAg_CTuQCzYLVtBDb_i was not overwritten;
its existing link can retain the old contents. Telegram used the local enriched
artifact. This is draft cached-KMPL enrichment/delivery proof, not a production
merge, recipient-read proof or new Hub callback test. Historical exclusion
remains covered by the focused tests rather than an additional live send.
