# Project history, challenges and decisions

Reviewed on 3 October 2026. The complete [change ledger](change-ledger.md) records 295 production-reachable commits from 21 August through the 2 October 2026 merge. This narrative explains the important changes and superseded decisions; it is not a substitute for the ledger.

## Development milestones

| Period | Work / resulting behaviour | Evidence |
| --- | --- | --- |
| 21 August | Initial daily KMPL project: source authentication, vehicle/regional reporting, calculations and Telugu output | [First commit e3301d6](https://github.com/imranshaik-pro/apsrtc-kmpl/commit/e3301d6046032e16dc7040786cd112b60684feb2) |
| 22–24 August | Flexible depot mapping; top-ten NAC low-Day list with Upto; unknown operation alerts; slab operation tables; monthly dual-sheet reporting | Commits in the ledger; raw operation codes retained |
| 29–30 August | Docker/GitHub image publishing, verified website depot options, Drive upload/link fixes and Jan–Mar inclusion | Packaging/local wrappers are separate from later Actions orchestration |
| 5 September | Idempotent cloud daily runner, scheduled retries, native Sheets upload, daily/monthly Form triggers and annual workflow | Stable report names and actual Google URLs |
| 5–6 September | Annual month/FY selection; history layout; strict dimension identities; exact depot tyre totals; verified lubricant POST; PDF fallback, units and target columns | v3–v8 adapter evolution; unsupported depot values never replaced with district readings |
| 10 September | Safe backfill wrappers, tyre recursion correction, FY24 source exceptions, transient Sheets retries and v11 Upto borders | Earlier wrapper rules must be interpreted through the later active v11 path |
| 14 September | Application home and privacy documentation | Existing docs index/privacy retained |
| 17–19 September | Incremental vehicle history, schedule markers, Vehicle 360 projection and manual event schema; daily Telegram content and duplicate-retry suppression | FY24 MTD history and later trend sources; source schedules separate from manual transactions |
| 20 September | IST retry schedule, secured permanent event API, consistent vehicle joins and structured event history | Proddutur daily schedule remains independent of manual Hub requests |
| 21 September | Central depot master, guided Telegram input, one Hub Form, event input, open/closed monthly lifecycle and stable report refresh | Current/open month skips MTD-598; closed month uses official roster |
| 21–22 September | Two visible annual tabs, source/period identity, Google freeze/merge repairs, callback links and selected-month parsing | Prevented ISO first-of-month timezone rollback and invalid frozen boundaries |
| 22–23 September | Rajampet historical tyre route investigation; depot-only blank zone/region querying; annual presentation and event/annual menu improvements | Tyre codes remain distinct from vehicle/PDF/spare identities |
| 23–29 September | Persistent annual snapshots, selected endpoint views, migration/checksum guards; Telegram listener and Apps Script modes; one-line and guided request fixes | [History preservation 2676eb0](https://github.com/imranshaik-pro/apsrtc-kmpl/commit/2676eb009632149585ef7ddc91768ab5373e88e3) |
| 27–29 September | Legacy Engine row-set work, display-marker investigation and source probes; Product/Engine header changes; temporary probes removed | Missing Proddutur legacy Upto remained unresolved; repair-named commits do not establish successful numeric repair |
| 30 September | Monthly/daily Hub dispatch fixes and report branding/colour changes | PR #2 and PR #3 merged |
| 1 October | Recorded Apps Script version-7 callback/native-logo deployment and Rajampet June Hub return; owner deferred Proddutur legacy Engine Upto | PR #4 records deployment/live evidence but remains unmerged in Git |
| 1–2 October | Optional tyre work expanded from RC/mismatch to repair/spare; owner replaced odd-day gating with current-request gating; revised Telugu columns | PR #5; mandatory daily KMPL stays first |
| 2 October, 03:06–03:11 UTC | Exact-bound slab fix and 13 regression-contract repairs merged, followed by current-request tyre release and release record | PR #6 at 314f85d, PR #5 at df13f60, record db2303a |
| 2 October, 09:39–11:01 UTC | Approved daily model implemented; footer-only Telegram split corrected; v1.1 centred tables, common SPARE1 and guarded NAC omission; merge authorised | PR #7 at 54dcf6b; tested a6d740c; 157 local daily checks plus compilation |
| 3 October IST documentation release | Consolidated current rules, source contracts, diagrams, history/ledger and action register; corrected stale status/guide claims | PR #8 merged at cf07f0f on 2 October 19:41 UTC; no runtime/deployment changes |
| 3 October detail-tabs review | B/F total-size tyre rows and combined engine/product monthly UD plus selected UM; separate historical cache and professional new views | [PR #9](https://github.com/imranshaik-pro/apsrtc-kmpl/pull/9); both depots May → July → May passed with 43 → 7 → 1 calls, 39 focused checks and full workbook previews; not merged |

| 3 October owner-template extension | Add Statement C, project the supplied B/C/F layout, correct labels and FY formulas, keep receipt inputs hidden and source discrepancies explicit | PR #9 review branch; 45 focused checks and both depot live/native/formula validations passed on 8e5e821 and final cb0ac0d; still unmerged |

| 3 October final owner approval | FY Total counts cover April–March or April through the selected current-FY month; no totals for percentage columns | Production approved for PR #9 after final verification; release commit is recorded in PR merge metadata |

Commit dates above use recorded UTC where specified. Operational date decisions use Asia/Kolkata.

## Challenges and how they were handled

| Challenge | Correction or decision | What remains true |
| --- | --- | --- |
| Repeated full annual fetches / changing selected endpoint | Persistent per-period snapshots, guarded migration and endpoint-specific views | A redraw must not replace valid historical values; source failures remain visible |
| Proddutur Engine labels lacked June Upto mapping | Compared current Engine endpoint, explicit engine-product report, booklet, MTD and daily logs | Seven retained legacy identities still lack exact source mapping; owner deferred |
| Suspected Proddutur-only parser | Traced both depots through shared imported runner functions | Suspicion is not a proven depot-specific cause; active override is documented |
| Annual indentation/syntax failures | Compile gate before annual build; later recorded live annual run passed | Compile success does not establish every source cell |
| Lubricant data from wrong contract/table | Verified yymm POST and selected-depot Total Lub columns | Higher lubricant KMPL is favourable; never reconstruct from unsupported oil totals |
| Tyre web unavailable for older FY | Exact official booklet depot fallback with correct units | Cumulative-only pages cannot establish monthly depot readings after April |
| Rajampet district change / differing depot codes | Recorded source identities and used depot-only tyre-web discovery | Vehicle, PDF, web and spare codes remain separate |
| Frozen-boundary/merged-cell Sheet errors | Clear incompatible legacy freezes/merges before applying safe layout | Preserve hidden history and metadata instead of deleting them |
| IMAGE logo showed #REF! | PR #4 used repeat-safe floating native annual logos | External Apps Script deployment is distinct from Git merge |
| Hub omitted hub_row / callback credentials incomplete | Forwarded originating row; configured matching callback endpoint/token; verified Rajampet row 19 | SUBMITTED or a skipped callback is not end-to-end completion |
| Conflicting Apps Script doPost handlers | PR #4 routes Hub callback from the existing keyed vehicle handler | Do not combine master handlers blindly |
| 13 old daily regression failures | Repaired two actual slab defects and stale fixtures/expectations; explicit duplicate/None rejection | They were daily checks, not FY24-25 annual history tests; subset scope stays explicit |
| Optional tyre failures threatened normal daily delivery | Generate KMPL first; independent category errors become unavailable notes | Zero categories omitted; unavailable is not zero |
| Odd/even rule no longer fit requested spare snapshot | Owner explicitly selected current-request gating for all depots | Historical dates skip tyres; current requests fetch every day |
| Redundant labels / weak daily visual hierarchy | Shared approved model, one column heading, centred tables, common spare position once | Preserve all source row associations and dates |
| Redundant NAC for genuinely NAC-only depots | Strict positive source/matching-five-KPI guard | AC/unknown/differing historical values keep separate sections |
| Telegram report exceeded one complete sample message | Bounded balanced chunks and compact complete footer; actual sample regression fixture | Larger reports may still split without losing rows |
| Early 1 October vehicle data yielded no valid records | Later scheduled retry generated the report without a parser change | Failed HTML was not retained; exact cause not proven |
| Fleet-availability/depot-versus-APSRTC visual proposals lacked sources | Owner closed these from current scope | Reconsider only with new accessible evidence and owner direction |
| Old settings/README phase claims lagged implementation | Current guides pin active entry points and statuses | Configuration defaults/old labels are not deployment certification |

## Live evidence and its limits

| Evidence | What was observed |
| --- | --- |
| [Rajampet June Hub 36833906698, attempt 2](https://github.com/imranshaik-pro/apsrtc-kmpl/actions/runs/36833906698) | PR #4 records compile/build, authenticated return, Telegram acceptance, row-19 link and both floating logos. HSD June Upto 5.24 and July onward blank in that view. |
| [Current-request tyres 36900410412](https://github.com/imranshaik-pro/apsrtc-kmpl/actions/runs/36900410412) | Cached Proddutur September 30 KMPL enriched for current request; separate October 1 spare snapshot; Telegram API accepted. Callback skipped without a supplied Hub row. |
| [Historical delivery 36955341963](https://github.com/imranshaik-pro/apsrtc-kmpl/actions/runs/36955341963) | Historical cached report delivered without tyres; callback skipped without Hub row. |
| [Production retry 36972310230](https://github.com/imranshaik-pro/apsrtc-kmpl/actions/runs/36972310230) | Subsequent 1 October source generation succeeded; later scheduled retries reused the cached report. |
| [Daily model 36991267862](https://github.com/imranshaik-pro/apsrtc-kmpl/actions/runs/36991267862) | Live v1 HTML/text accepted, initially in two chunks; downloaded source/render outputs matched. |
| [Complete v1 delivery 36992184866](https://github.com/imranshaik-pro/apsrtc-kmpl/actions/runs/36992184866) | Tested c84f00a; compilation and 75 workflow checks; one accepted complete Telegram message, 3,878 UTF-16 units. |
| v1.1 review/merge | 157 local daily checks and compilation; real source-based HTML rendered, all tables retained; production merge tree matched tested a6d740c. No separate live v1.1 message was sent during screenshot correction. |
| [Detail tabs 37090754311](https://github.com/imranshaik-pro/apsrtc-kmpl/actions/runs/37090754311) | Both depots passed authenticated source transitions, immutable FY25-26 checks, native new-tab readback and full May Monthly/Annual previews. Private review files only; no production file writes, Hub callbacks or Telegram delivery. |

Live run references are retained records, not reruns performed for this documentation review. Telegram API acceptance does not prove recipient reading. Local test data, earlier source capture, cached KMPL and newly fetched source data must remain identified separately.


## 7 October 2026 — KMPL range Month/Upto release and review lesson

PR #12 merged at `150555a55748090084d1eaa8da4a03adf0afa276`, adding source-backed Vehicle/Driver Month and Upto range reporting to Monthly and Annual KPI views. PR #14 followed with direct-unittest coverage hardening; master after that follow-up was `92c3486add5ca87bff8cf1e31bd99946ffa52714`, whose Docker build completed successfully.

Owner verification established that Vehicle Upto uses selector `vehlog_kmpl.php` and result `vehlog_kmpldepot.php`; Driver Upto uses `drvlog_ckmpl.php` and `drvlog_ckmpldepot.php`. This corrected an earlier unsafe filename inference. The project rule is now explicit: never invent an endpoint from naming symmetry.

During post-merge review, work briefly continued against PR #12's old feature branch before the merged master state was re-read. The corrective process is now documented: current master/PR/recent-commit state must be checked before modifying an existing feature branch.

The range tests passed in the diagnostic workflow. A separate `report_details` HistoryAndViewTests group failed while its SourceContractTests passed. `report_details.py` itself is unchanged from the pre-PR-12 baseline, so the failure is tracked as an independent validation issue pending exact clean-master reproduction; no speculative production patch was made.


## 2026-10-12 — PRODDUTUR August range-source incident

- Symptom: August 2026 KMPL Range Distribution rendered blank Month/Upto populations although the main monthly vehicle report had valid operational data.
- Regional aggregate endpoints `vehlog_kmpldepot.php` and `drvlog_kmpldepot.php` repeatedly returned HTTP 200 and correct headers but only the two header rows for July, August and September in live diagnostics.
- Earlier workflow “success” was reclassified: the job completed, but its source-review log also showed empty aggregate tables. Workflow success was not evidence of populated source data.
- Retrying the aggregate and replaying the parent month selector did not restore rows; those hypotheses were disproved.
- Stable depot drill-down sources were found: `vehlog_kmplveh.php` and `drvlog_kmpldrv.php`.
- Vehicle detail parsing initially appeared inconsistent because a diagnostic used `recursive=False` and dropped a nested linked vehicle cell, shifting columns. Correct DOM indexing fixed that diagnostic error.
- September vehicle detail, filtered to positive operated KM, exactly reproduced the previously verified aggregate: [0,2,39,18,9,9,4] = 81. This is the evidence gate for the vehicle Month fallback.
- August vehicle detail currently produces 83 operated vehicles. Zero-operated-KM records are excluded, consistent with the verified September aggregate behavior.
- Driver detail is record-level: repeated driver identities can occur, and distinct drivers can also have identical KM/HSD/KMPL metrics. Therefore metric deduplication and blind driver-ID deduplication are both unsafe. Month fallback counts valid source rows.
- Upto/Cumulative remains separate. Driver Upto uses a different eight-band classification and must not be coerced into the seven Month bands. Vehicle Upto is not claimed repaired by the Month fallback.
- Principle retained: missing source data is never converted to zero and no range population is fabricated.


## 2026-10-12 — Cumulative range repair

- Identified actual vehicle cumulative selector `vehlog_ckmpl.php` and aggregate `vehlog_ckmpldepot.php`; previous configuration incorrectly reused monthly vehicle sources.
- Driver cumulative aggregate `drvlog_ckmpldepot.php` was correctly identified but rejected because the parser required the monthly heading and seven monthly bands.
- APSRTC cumulative classifications are distinct: vehicle has seven cumulative bands (Below 2, 2.01–3, 3.01–4, 4.01–5, 5.01–5.30, 5.31–6, Above 6); driver has eight cumulative bands with 5.01–5.10 and 5.11–5.30 split.
- Regional cumulative aggregate pages intermittently return only header rows. Depot cumulative drilldowns `vehlog_ckmplveh.php` and `drvlog_ckmpldrv.php` expose record-level KMPL. Driver cumulative source contained 193 rows for August PRODDUTUR; the workbook independently verified this source population.
- Repeated source identities are retained as source records rather than deduplicated without an APSRTC rule. Month and Upto are rendered in separate tables with exact source headings, not silently combined.
- No cumulative count is constructed by summing monthly counts.


## 2026-10-12 — PRODDUTUR August KMPL range repair: request-to-result record

### Owner request
The requested outcome was not merely to make the report command succeed. For PRODDUTUR August 2026, the generated workbook had to contain real APSRTC-backed **Vehicle Month, Driver Month, Vehicle Upto/Cumulative and Driver Upto/Cumulative range populations**. Blank populations, invented zeroes, monthly values relabelled as Upto, or cumulative values reconstructed by summing monthly populations were explicitly unacceptable. The investigation also had to establish why PRODDUTUR was blank by comparing the working and failing source paths rather than hiding the problem with a cosmetic workaround.

### What was wrong
The report could complete while the Range Distribution cells remained blank. APSRTC regional range endpoints intermittently returned HTTP 200, the expected heading and column headers, but no depot data rows. Therefore HTTP success and workflow success were insufficient evidence that a usable range table had been received.

There were also two deterministic cumulative-contract defects in our code. Vehicle Upto was configured against the monthly vehicle endpoint instead of the cumulative source. Driver Upto used the correct cumulative family, but our parser still required the monthly heading and seven monthly buckets; the real Driver Upto source has eight cumulative buckets. The renderer also assumed Month and Upto shared one bucket schema, which could mislabel cumulative values even if retrieval succeeded.

### Root cause and evidence
1. **Intermittent APSRTC aggregate response:** the regional Month and cumulative pages can return header-only tables. Replaying selectors and simple retries did not reliably restore rows.
2. **Wrong Vehicle Upto source mapping:** the actual cumulative selector/result pair is `vehlog_ckmpl.php` / `vehlog_ckmpldepot.php`, not the monthly `vehlog_kmpl.php` / `vehlog_kmpldepot.php` pair.
3. **Different cumulative schemas:** Vehicle Upto has seven cumulative bands; Driver Upto has eight and splits 5.01–5.10 from 5.11–5.30. These are not the Month bands.
4. **Stable depot-level evidence exists:** when aggregate tables are header-only, APSRTC depot drilldowns expose record-level KMPL: Month via `vehlog_kmplveh.php` / `drvlog_kmpldrv.php`; cumulative via `vehlog_ckmplveh.php` / `drvlog_ckmpldrv.php`.
5. **Vehicle/driver records cannot be blindly deduplicated:** source identities may repeat and equal metrics can legitimately belong to different records. The fallback therefore preserves valid source rows instead of inventing a deduplication rule.

### Implemented fix
- Corrected Vehicle Upto to the genuine cumulative endpoint family.
- Added scope/entity-specific source contracts instead of forcing cumulative responses through the Month parser.
- Added the exact Vehicle and Driver cumulative bucket definitions.
- Added bounded retry handling for transient APSRTC disconnects and removed an unnecessary cumulative selector request that created another failure point.
- Added verified depot-detail fallback counting when an aggregate page is header-only. The fallback bins the source KMPL records into the exact source-defined Month or cumulative ranges.
- Kept fail-closed behavior: if neither verified aggregate nor verified detail data is available, the workbook reports the source as unavailable rather than substituting zero.
- Changed the workbook presentation so Month and Upto/Cumulative are separate source-defined tables. Cumulative populations are never shown under Month labels and are never calculated by adding monthly populations.

### Delivered result and verification
The final live August PRODDUTUR regeneration passed the workbook-level gate with four independent source populations:

| Distribution | Verified G.Total |
| --- | ---: |
| Vehicle Month | 83 |
| Driver Month | 167 |
| Vehicle Upto/Cumulative | 84 |
| Driver Upto/Cumulative | 193 |

The same run passed all 20 focused parser/source tests and asserted that both Vehicle and Driver cumulative-specific bands physically exist in the generated workbook. Verification run: https://github.com/imranshaik-pro/apsrtc-kmpl/actions/runs/38258969198. The repair was merged through PR #17 as squash commit `6464fe1268e9542880353ac4e3679c2c67e64846`.

### Delivery status
The validated workbook from the repair run was uploaded as a **GitHub Actions artifact** named `proddutur-aug-range-repair`. The repair verification workflow does **not** contain a Google Drive upload step. Therefore this incident record does not claim that the newly validated August workbook was uploaded to the production Drive folder. Code merge, CI artifact publication, and production/Drive workbook publication are separate states and must continue to be reported separately.

### Regression rules retained
- A green command/workflow is not sufficient; workbook cells must be asserted.
- HTTP 200 is not sufficient; expected source rows and source identity must be verified.
- Month and Upto/Cumulative are independent source contracts.
- Do not infer endpoints from filename symmetry without live source evidence.
- Do not convert missing source data to zero.
- Do not sum monthly populations to manufacture Upto/Cumulative.
- Do not deduplicate source records without a verified APSRTC identity rule.


## 2026-10-12 — Production Drive publication verified

The repaired PRODDUTUR August 2026 report was executed from `master` using the production Google OAuth secrets and the configured monthly Drive folder. The target Google Sheet already existed, so the uploader refreshed that stable file ID rather than creating a duplicate.

- Production workflow run: `38261409452` — success.
- Google Sheet ID: `1-qZi_7jX3Z6fC5xmUzROD7u7GCxP3dAe2GDj7_Sl3nw`.
- The workflow exported the published Google Sheet back from Drive as XLSX and reopened the `KMPL Range Distribution` sheet; this was a read-back verification, not only a local pre-upload assertion.
- Published read-back G.Totals: Vehicle Month **83**, Driver Month **167**, Vehicle Upto **84**, Driver Upto **193**.
- Range source tests: **20 passed** before publication.
- The publication run logged all four APSRTC depot-detail fallback populations before upload: 83 / 167 / 84 / 193.
- Delivery state for this incident is therefore: **implemented → tested → workbook verified → merged → documented → production Drive refreshed → published Drive copy read back and verified**.

The one-purpose publication workflow `.github/workflows/publish-proddutur-aug-repair.yml` was introduced to make this release independently auditable. It publishes only PRODDUTUR August 2026 and fails if the Drive-exported workbook does not contain exactly the four approved totals.


## 2026-10-13 — Annual KPI propagation repair and PRODDUTUR August acceptance

### Request
After the Monthly PRODDUTUR August 2026 KMPL range repair was published and read back successfully, the next requirement was to prove that the corrected range source also reaches the **Annual KPI**. The acceptance case was PRODDUTUR, selected month August 2026, FY 2026-27. Success required a real Annual run and Drive read-back; inheritance from Monthly was not to be assumed.

### What the Annual verification exposed
The Annual path is independent of the Monthly Google Sheet for much of its history. It maintains durable Annual history and a separate KMPL range-history cache, so the Monthly fix only provides corrected shared source logic; Annual still needed its own end-to-end validation.

Three Annual-specific defects were found during that validation:

1. **Eager range-source login:** v11 instantiated the APSRTC range adapter even when cached Annual history required no range fetch. This violated the checkpoint/cache contract and broke the no-refetch regression test. The adapter is now initialized lazily only when a range period genuinely needs source retrieval.
2. **Missing engine-source disclosure regression:** the management dashboard intentionally excludes dynamic engine rows from the core KPI summary, but a refactor also removed the completeness warning when engine source rows were unavailable. The warning was restored without promoting dynamic engine rows into the management KPI table.
3. **Invalid Google Sheets chart payload:** the Annual Google renderer sent `pointSize` inside `basicChart.series`. The Google Sheets API does not accept that field at that location and rejected the final `batchUpdate` with HTTP 400. The unsupported field was removed while preserving the line-series data, target axis and colors.

### Verification
Acceptance workflow run `38291670551` completed successfully after the fixes.

Regression suites before the live run:
- Annual history: **12/12 passed**.
- Annual dashboard: **10/10 passed**.
- KMPL range source/parser: **20/20 passed**.

The live PRODDUTUR August source retrieval again produced:
- Vehicle Month: **83** records.
- Driver Month: **167** records.
- Vehicle Upto/Cumulative: **84** records.
- Driver Upto/Cumulative: **193** records.

The Annual dashboard was successfully updated in Google Drive as `PRODDUTUR_ANNUAL_KPI_DASHBOARD`, file ID `1usBGLbct9X5xjCqWt_mHLpBR4UvWqLVJY2nYg8zIi7k`. The verification then read the **published Drive sheet** through the Sheets API, not a local workbook.

Published `FY KMPL Range Trend` August 2026 rows were verified as:
- Vehicle Month: buckets `0, 2, 48, 19, 8, 5, 1`, G.Total **83**, source status `Verified source`.
- Driver Month: buckets `0, 4, 105, 35, 13, 8, 2`, G.Total **167**, source status `Verified source`.
- Cumulative rows are deliberately labelled `Upto/Cum Aug-26` with `See cumulative source bands — not comparable` instead of forcing the cumulative populations into monthly bucket columns. The source retrieval itself verified Vehicle Upto **84** and Driver Upto **193**.

### Delivery state
For the Annual KPI acceptance case the state is now: **shared Monthly source fixed → Annual regressions discovered → Annual code fixed → all regression suites passed → PRODDUTUR Aug-2026 Annual run succeeded → production Annual Google Sheet updated → published Annual range trend read back and verified → incident documented**.

### Engineering rule retained
A Monthly source repair must never be assumed to propagate to Annual merely because code is shared. Annual has its own cache/history/rendering/publication contracts and requires an independent acceptance run. Google Sheets formatting requests are also part of production correctness: a workbook can contain valid data and still fail delivery if the API rendering payload is invalid.
