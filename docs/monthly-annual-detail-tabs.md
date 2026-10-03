# Monthly and Annual source-detail tabs

Implementation review started on 3 October 2026 from production [cf07f0f](https://github.com/imranshaik-pro/apsrtc-kmpl/commit/cf07f0ff163b1af7d88e18cf671e7f61ec5bddcc). The owner subsequently supplied `template.ods` and the full Statement C HTML, and authorised the B/C/F template correction. Tyre scope is **B, C and F**, with **All Tyre Sizes Total**; Statement A is excluded. This review does not resolve the separately deferred seven legacy Proddutur Engine Upto labels.

## Output and period rules

| Report | Tyre Statements tab | Engine & Product KMPL tab |
| --- | --- | --- |
| Monthly | Selected-month B mechanical defects plus F Stone/Worn Smooth %, separate B premature failures, grouped C scrap tyres | Selected month's source matrix with UD and the month's last date |
| Annual | Same template with month rows from April 2025 through selection and separate FY totals | FY2025-26 monthly UD snapshots, current FY monthly UD snapshots through selection, and a selected-month UM matrix |

April 2025 is the Annual detail-history starting point. A standalone Monthly request fetches its selected month, including an earlier month if the source supports it; it does not backfill older FYs. Unsupported source months are reported unavailable.

For a completed month, UD covers its first through last day. UM covers 1 April of the selected FY through the selected month's last day. The authenticated engine report heading verifies both endpoints. **UM is fiscal cumulative; UD is monthly actual.** The source's product and Grand Total KMPL values are retained directly, not averaged from engine rows.

An open month uses yesterday in Asia/Kolkata and is marked provisional. No completed day on the first of the month, or a future month, cannot produce a verified month-end detail snapshot. Provisional snapshots remain refreshable until a completed-month source is captured. The existing Hub/Monthly future-month guards remain; this addition does not change the legacy annual CLI guard boundary.

The day cutoff applies to engine/product requests. B/C/F statements expose a month filter rather than a daily cutoff: an open-month tyre row is labelled as the current monthly source as fetched, without claiming it stops at yesterday.

## Owner template and calculations

`report_tyre_template.py` projects the owner-supplied layout. Mechanical defects use MA/MM/CBW/KPP/BB/OI/UI/HBP (the reversed MA/MM sample is corrected), total defects and defect %. Only F's Stone % and Worn Smooth % are appended to the right. Premature failures have their own S1/S2/S3/S6/S8/S9 table. C retains four horizontal grouped stages, each with S1–S9 and a source Total. Region/zone/depot codes are retained for source validation/history but omitted from visible data columns. The identity heading retains depot and report period. No template annotation or sample engine value is a production data input.

Annual FY Total rows sum **counts only**, using guarded `SUM` over April–March for FY25–26 and April through the selected month for FY26–27. The three percentage cells in each FY Total row remain blank: no sums, averages or cumulative percentage formulas. Individual monthly source percentages remain unchanged, converted from percentage points to fractions and displayed with `0.00%`. Missing counts remain unavailable rather than becoming zero. `_TYRE_INPUTS` retains hidden supporting source counts; `_REPORT_DETAILS_HISTORY` is the authoritative checksummed history.

The sample's L17 `K17/P17` ratio was in the defect-count column and counted only Hub Bearing Play. It is replaced by a count SUM; monthly percentage belongs in the next column; the FY Total percentage remains blank under the owner's final instruction. C's sample `Tota` is corrected to `Total`. C reported totals are summed vertically without replacing them with sums of S-code categories: Proddutur May 2026 first-RC source total is 13 but S1–S9 sum to 10. The discrepancy is explicitly displayed and the source total retained.

Native Sheets receives real `formulaValue` cells and percentage formats, with the hidden numeric input tab published first. Review readback compares entered formulas and independently checks calculated FY results; changing and restoring a monthly defect count in a disposable review sheet verifies the FY count SUM recalculates while percentage totals remain blank.

## Exact source contracts

Base URL: `http://103.44.14.20`.

| Data | Method/path | Parameters |
| --- | --- | --- |
| Statement B | GET `/tyres/b_statement_final.php` | `zone=`, `region=`, `depot=PDT` or `RJP`, `month_year=MAY-2026`, `tyre_size=All Tyre Sizes Total` |
| Statement C | GET `/tyres/c_statement_final.php` | Same depot/month/total-size parameters; dedicated two-level grouped-header parser |
| Statement F | GET `/tyres/f_statement_final.php` | Same parameters as B; only the path changes |
| Engine/product monthly | POST `/mednew/eng_prod_um.php` | `fdate=31/5/2026`, `reg=YSRKADAPA`, `dept=PRODDUTUR` or `RAJAMPET`, `fupto=UD` |
| Engine/product selected cumulative | POST `/mednew/eng_prod_um.php` | Same mapped depot/date/region; `fupto=UM` |

`annual_kpi_runner_v3.tyre_site_info` supplies routing only. The new parser does not reuse the legacy single-dimension Engine parser. Vehicle depot codes, tyre depot codes and numeric spare IDs are distinct. The existing tyre mapper supports its recorded depots; an unmapped depot is reported unavailable instead of guessing a source code.

Tyre parsing requires one exact depot/month/size row. Raw source headings/order are preserved, including `Mech. Defetcs %`. B has 24 captured columns; C has 47 (seven identities plus four groups of ten); F has 18. C's repeated S1–S9 headings are qualified by stage before caching, preventing duplicate-header rejection or stage collisions. Raw percentages remain percentage points, while visible percentage cells use fractional values and percentage formats. Zero and blank remain distinct.

Engine parsing requires one recognised matrix, the exact depot and request interval, unique source engine identities and one final TOTAL. TOTAL's `colspan=2` is expanded as a label and blank engine cell so product totals cannot shift columns. Dynamic source products/engine rows remain exact identities. The new combined matrix is not a crosswalk to the old seven KPI labels.

## Durable history and May → July → May

`report_details.py` owns the hidden `_REPORT_DETAILS_HISTORY` tab, separate from `_ANNUAL_HISTORY` and monthly vehicle history. Its schema, depot identity, chunk count and SHA-256 checksum must validate before use. A corrupt/wrong-depot cache stops replacement. Checkpoint failures stop processing; they are not swallowed as source failures.

1. First May 2026 request fetches missing B/C/F/UD months from April 2025 through May 2026, plus May UM.
2. July request reuses the closed snapshots, fetches missing June/July B/C/F/UD, and refreshes July UM.
3. Returning to May refreshes May UM. June/July stay cached but disappear from the visible report.

When all requested sources exist, a new cache requires 57, 9 and 1 detail-source calls respectively. Existing schema-1 B/F/UD histories remain compatible: only missing C snapshots are backfilled, without refetching closed B/F/UD. Missing sources and provisional snapshots may be retried. A verified closed B/C/F/UD snapshot is historical and is not refetched by the Annual path. Monthly requests refresh their selected month's four detail sources; failure retains that same depot/month's previous detail snapshot.

UM refresh replaces the entire matrix, including its row and column identities. It never carries a departed July engine/product into May. Failed refresh retains the saved matrix with a visible stale-source note; a first-time failure shows unavailable instead of fabricated zero. Rendering rebuilds only the two owned views, removes stale visible rows/columns/merges/styles and keeps all historical snapshots.

## Integration and presentation

| Entry point | Behaviour |
| --- | --- |
| `monthly_vehicle_report.main` | Existing daily grid, roster, schedule/history and Vehicle 360 logic runs first; attach the two detail tabs and new hidden cache before the existing XLSX upload |
| `annual_kpi_runner_v11.main_v11` | Existing KPI cache/source logic remains; checkpoint the separate detail cache, render the two detail tabs, publish them on the same annual file |
| Annual finalizer | Four visible tabs: Dashboard, Detailed Data, Tyre Statements, Engine & Product KMPL; durable caches and legacy sheets remain hidden, not deleted |

The new views use centred depot/period headings, source tables, wrapped blue column headers, source totals, bounded print areas and exact current view dimensions. Engine KMPL uses the existing 5.00/5.10/5.20/5.30 performance bands. Tyre counts are not graded as fuel performance. XLSX embeds the APSRTC asset across A3:C3, once per new tab.

Native Sheets publication verifies typed values and dimensions through the API. Sheets v4 does not create a floating logo: these two native views use an APSRTC text wordmark in the reserved span. The existing over-grid logo/Apps Script work in PR #4 remains a separate deployment; this feature does not claim or perform that deployment.

## Verification and production approval

`tests/test_report_details.py` uses captured source tables for both depots and tests source endpoints/identity, colspans, zeros/blanks, immutable history, checksum/corruption, checkpoint failure, complete UM replacement and Google/XLSX layout cleanup. Existing annual-history and report-branding tests cover their preserved integration contracts.

The review workflow is restricted to the feature branch on push, with manual dispatch available. `verify_report_details.py` performs authenticated source reads, May/July/May history checks, private new-tab Google Sheets checks and full workbook previews. Existing annual KPI data is read from its cache for preview; it is not repaired. The monthly upload boundary is intercepted for preview. No production file is a write destination, and no Hub callback, Telegram message or Apps Script deployment occurs.

The owner approved [PR #9](https://github.com/imranshaik-pro/apsrtc-kmpl/pull/9) for production on 3 October 2026, subject to the final count-only FY Total correction and verification.

## Initial B/F acceptance evidence (before owner template extension)

Code commit [6afcdc3](https://github.com/imranshaik-pro/apsrtc-kmpl/commit/6afcdc368d05dfddcaf51a9836451cf4a3f9f494) passed [run 37090754311](https://github.com/imranshaik-pro/apsrtc-kmpl/actions/runs/37090754311): relevant compilation, 24 detail tests, 12 Annual history tests and 3 presentation tests. Full May 2026 Monthly/Annual workbooks were generated for both depots. Both Monthly builds fetched days 1–31, with 86 Proddutur and 47 Rajampet official roster vehicles in their existing history views.

| Depot | May UD / UM | July UD / UM | Return to May UD / UM | Source calls per step | Engine-view rows July → May | Engine-view columns July → May |
| --- | --- | --- | --- | --- | --- | --- |
| PRODDUTUR | 4.94 / 4.98 | 4.89 / 4.94 | 4.94 / 4.98 | 43 → 7 → 1 | 216 → 189 | 11 → 11 |
| RAJAMPET | 5.20 / 5.23 | 5.20 / 5.22 | 5.20 / 5.23 | 43 → 7 → 1 | 206 → 182 | 11 → 8 |

All 14 initial B/F/UD monthly snapshots from April 2025 through May 2026 and both June/July additions were available. FY2025-26 snapshot checksums stayed unchanged across each sequence. Proddutur retains 11 sheet columns because an earlier visible historical matrix uses them; its selected May matrix has exactly its 10 source columns. Rajampet's selected May matrix has 7 columns; its Annual historical matrices require 8. Returning to May removes every July 2026 block, while June/July remain in hidden history.

The native writer passed API readback of every generated value, merge count, resized grid and hidden checksum cache through all three selections. Review files are separate, owner-only Sheets (`shared=false` confirmed by Drive metadata): [Proddutur](https://docs.google.com/spreadsheets/d/1S75kRgbXNZ9VRXYDXAkdMG7ZTqSYp9VVXvZxR-QTpOA/edit?usp=drivesdk) and [Rajampet](https://docs.google.com/spreadsheets/d/1L6WSHC1UPIp343BrP44j7qn4u-kFnwZOzHGPK6ZVymY/edit?usp=drivesdk). They contain the new Annual detail views, not a claim of production Hub delivery.

The [run artifact](https://github.com/imranshaik-pro/apsrtc-kmpl/actions/runs/37090754311/artifacts/11261559297) contains four full May workbooks, all six transition workbooks, history snapshots and the validation summary. The new views were imported, recalculated, inspected and rendered with Artifact Tool; error scans found no spreadsheet errors. Embedded logos, centred headings, preserved source headers, readable numeric formats and the smaller May layouts were visually inspected. Google Sheets readback is native data/layout verification; it does not create a floating logo.

Two repeated previews encountered `RemoteDisconnected` in the existing vehicle fetch while the audit harness reused its source-audit HTTP session. The harness was corrected to preserve Monthly's normal fresh login. The following two complete code validations passed. The server-side cause of the closed connection is not established; no production retry/parser change was made for it.

A repository-wide compile probe found a SyntaxError in the unchanged legacy `generate_report.py` at line 101. Compiling the original production bytes reproduced it. That inactive alternative entry point is outside this feature; the active Monthly/Annual runners and affected dependencies compile.

## Initial owner B/C/F template acceptance — 3 October 2026 (before final count-only instruction)

The owner supplied `template.ods`, Statement C screenshots and complete source HTML. The correction follows its visible mechanical/premature/scrap layout, omits depot/region/zone and supporting raw receipt fields from the views, and retains F's Stone% and Worn Smooth% beside the mechanical defect percentage. MA/MM labels, the truncated C Total heading and the sample's incorrect mechanical total formula are corrected.

[Code review run 37098714266](https://github.com/imranshaik-pro/apsrtc-kmpl/actions/runs/37098714266) passed on [8e5e821](https://github.com/imranshaik-pro/apsrtc-kmpl/commit/8e5e8216f337609f53b4530412fa893328c22b2a): relevant compilation, **45 focused checks** (24 detail/history, 6 owner-template/C, 12 original annual history, 3 branding), authenticated source reads, isolated native Sheets formula/value/merge/grid/cache checks and four complete May workbook builds. The recorded live source errors were empty; the offline timeout message is an intentional failure-preservation test.

| Depot | May → July → May source calls | Tyre view rows | Engine view rows | Selected UD / UM totals |
| --- | --- | --- | --- | --- |
| Proddutur | 57 → 9 → 1 | 101 → 107 → 101 | 189 → 216 → 189 | May 4.94 / 4.98; July 4.89 / 4.94; May 4.94 / 4.98 |
| Rajampet | 57 → 9 → 1 | 98 → 106 → 98 | 182 → 206 → 182 | May 5.20 / 5.23; July 5.20 / 5.22; May 5.20 / 5.23 |

FY25–26 B/C/F/UD snapshot checksums were unchanged within both sequences. All six Annual fiscal-year total blocks were checked against independent source sums in native Sheets. A selected-May B receipt count was temporarily doubled in each isolated review sheet; its weighted fiscal-year percentage recalculated correctly, then returned to its original value after restoration. No production workbook was used as a write destination.

The four full workbooks' original Monthly KMPL/Vehicle Performance/Vehicle 360 or Annual Dashboard/Detailed Data cell values and merges match the prior accepted core previews. The two hidden detail tabs retain checksummed history and matching formula inputs. Recalculated preview scans found no formula errors. Proddutur May RC1's source total **13** remains **13**, with its S1–S9 sum **10** visibly flagged. XLSX logos remain in A3:C3; floating native logos remain outside this change.

A final presentation-only correction right-aligns calculated total cells and replaces the Monthly FY-total subtitle with a monthly-source subtitle. The final [run 37099010277](https://github.com/imranshaik-pro/apsrtc-kmpl/actions/runs/37099010277) passed on [cb0ac0d](https://github.com/imranshaik-pro/apsrtc-kmpl/commit/cb0ac0d9f77a238fc60220ce8b2d188f3bc722a9), repeating all 45 checks, live depot sequences, native formula/reactivity checks and four full workbook builds. Its final artifact is `11265711889`, generated directly by the reviewed code. Original core values and merges were checked again against the earlier accepted previews; the revised view renders and recalculated formula scans passed. This records the earlier review stage. The owner subsequently approved production with count-only FY Total rows; that instruction supersedes the earlier weighted FY percentage display.

## Final owner instruction: FY count totals only

On 3 October 2026 the owner approved production and requested FY Total rows for counts only. Full FY25–26 uses April–March; current FY26–27 ends at the selected month. Defect%, Stone% and Worn Smooth% cells in every FY Total row are blank. Individual monthly percentages, source snapshots and all other report logic remain intact. The verification driver checks every FY count total against source sums, confirms percentage totals are blank, and changes/restores one defect count to prove native SUM recalculation.
