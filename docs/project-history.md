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
