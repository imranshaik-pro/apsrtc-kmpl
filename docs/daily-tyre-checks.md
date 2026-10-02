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

55 focused checks pass locally, with compile checks for runner, tyre module,
Telegram formatter and tests. Coverage includes current versus historical intent, yesterday
resolution on both odd/even dates, both depots, fresh/cached delivery, exact
payloads, source date and depot filtering, supplied spare records, empty
results, duplicates and isolated failures. Workflow includes this test gate.
The 13 earlier daily regression failures are fixed separately in draft PR #6.
Current-only cached delivery and live repair/spare
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

The workflow now selects the runner's ISO Report date rather than the last
human-readable header. Fresh run 36886050944 logged both 2026-09-01 and
01 September 2026; the old tail extraction selected the latter. The bounded
correction matches only YYYY-MM-DD, with fresh/cached log regression checks.
It does not change the selected-date or yesterday-resolution business rule.

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
merge, recipient-read proof or new Hub callback test. This run did not exercise historical exclusion; later live evidence is below.


## Telegram presentation and delivery validation — 2 October 2026

Completed daily text is rendered by src/reporting/telegram_daily.py only at
Telegram delivery. The formatter uses escaped native HTML, one depot/date
heading, bold business sections, aligned slab columns and monospaced KPI
values. Repeated tyre position/number labels are removed without deleting
their values. The mismatch count is explicitly labeled source tyre records,
not a count of independently diagnosed faulty positions. Technical code-path
instructions are replaced with a business-readable classification note while
preserving the vehicle and operation code. Cached-link wording does not claim
that Drive contains the newly enriched local delivery copy. Every large-message
fragment closes its HTML tags before splitting.

Draft run https://github.com/imranshaik-pro/apsrtc-kmpl/actions/runs/36955341963
(#135), job 110676964768, tested commit 011afa89ec44eb0ade46094d7e15d358d3879162
with PRODDUTUR selected 2026-09-30. Compile and 52 focused checks passed in
GitHub Python 3.11. The cached KMPL was reused; the downloaded artifact
11205817667 contains no tyre section. Telegram accepted one HTML message
at 02:23:03 UTC. Hub callback was skipped because no Hub row was supplied.
This is historical cached delivery proof, not a fresh current-day generation
or a new Hub callback test. The subsequent ISO-date extraction correction
adds two checks: all 54 focused checks pass locally.

Current-request run 36954635807 (#134), tested earlier presentation commit
f48df2475194aa7ba337e07a536c48e6dc0c1105 with selected 2026-10-02. Compile
and 50 checks passed, but the source-to-KMPL generation step failed for the
resolved 2026-10-01 date: Vehicle report returned no valid vehicle records.
No report-formatting/delivery step ran. This does not establish whether the
source was empty or its response changed; no speculative parser patch was
applied. A fresh current request still needs source verification.

The complete offline presentation sample uses verified KMPL from 30 September
and the tyre capture from 1 October, including the independently dated spare
source. It fits in one Telegram message (2,906 HTML characters with its Drive
footer), and the rendered Telugu/table layout was inspected. It is explicitly
labeled a preview using earlier verified source values, not a new tyre fetch.
Telegram applies its own theme; preview-card colors are not Telegram styling.

PR #5 at 8f27808e6ecde107dac248553e999ccf996cfb9d and PR #6 at
20d74ae16e1080c925d7996cd931b46f4228fdfa were overlaid in an isolated local
daily validation snapshot. All 120 available daily checks passed, including
slab boundaries, independent Day/Upto conservation, the repaired baseline
contracts, current/historical tyre behavior and Telegram formatting/date
extraction. This is combined local verification, not a full-repository test
claim or a production merge. Normal daily calculations remain outside the
presentation formatter. The owner requested template review before merging;
the owner subsequently approved the production merge recorded below.


## Tyre column presentation — 2 October 2026

All populated tyre categories now use Telugu column headings once. RC-front,
mismatch and repair tables have vehicle/positions columns. Spare tables have
vehicle/position/tyre number/days columns. Vehicle-row prefixes and repeated
position, tyre-number and days-in-use labels are omitted. Counts, depot filters,
source dates, record ordering, tyre-fetch gating and normal KMPL remain unchanged.
The plain report and Telegram delivery share the same table presentation;
earlier saved line entries are converted locally for delivery without rewriting
Drive files. All 17 earlier Proddatur entries retain their exact vehicle/value
associations, including all nine spare source records. The updated complete
preview uses the earlier verified source capture and fits in one message
(2,797 HTML characters including the Drive footer). Compilation and all 55
focused checks pass locally. No new live delivery is claimed for this display
revision, and the owner subsequently approved the production merge recorded below.


## Production release — 2 October 2026

The owner approved the daily production merge after reviewing the column-based
template. PR #6 was squash-merged first at
314f85d04156d0b7a48af8dcb7580cc77c4fbdf4; PR #5 followed at
df13f60458e56af52845b3222eb9159ee09dae7b. The exact approved PR heads were
20d74ae16e1080c925d7996cd931b46f4228fdfa and
a9d0c3988cf0412a0584fec75abe8c61b1effc61 respectively.

Before merging, their latest combined daily snapshot passed 121 checks and
Python compilation. After merging, all 20 reviewed changed-file blobs matched
those approved PR versions on master. Production container build and push
succeeded in https://github.com/imranshaik-pro/apsrtc-kmpl/actions/runs/36958783715
for df13f60458e56af52845b3222eb9159ee09dae7b. This documentation-only release
record does not alter that verified application code.

The Hub dispatcher and daily form trigger select master for daily-report.yml;
subsequent Hub submissions therefore select the merged daily code. No Apps
Script redeployment was performed for this GitHub release. Current/today
requests still resolve KMPL to yesterday and then fetch tyres; historical
requests still skip tyres. Scheduled retry/delivery behavior is unchanged.

This merge verification did not submit a new Hub row or claim a successful
fresh current-day report. The 1 October vehicle-source failure documented
above still needs source verification. Proddatur historical engine Upto remains
deferred; PR #1 and the separate Hub/logo/documentation PR #4 were not merged.

## Locked daily presentation

See [Approved daily template v1](daily-template-v1.md) for the shared coloured report and Telegram layout, source-preservation checks and owner-approved visual contract. This changes presentation, while keeping the current-request/historical-date tyre rules above.
