# Monthly and Annual source-detail tabs

Implementation review started on 3 October 2026 from production [cf07f0f](https://github.com/imranshaik-pro/apsrtc-kmpl/commit/cf07f0ff163b1af7d88e18cf671e7f61ec5bddcc). The owner authorised these additions after supplying Statements A/B/C/F and the engine/product form. The requested tyre scope is **B and F only**, with **All Tyre Sizes Total**. This review does not resolve the separately deferred seven legacy Proddutur Engine Upto labels.

## Output and period rules

| Report | Tyre Statements tab | Engine & Product KMPL tab |
| --- | --- | --- |
| Monthly | Selected-month B and F source rows, exact mapped depot and total tyre size | Selected month's source matrix with UD and the month's last date |
| Annual | Available B/F monthly rows from April 2025 through the selected month | FY2025-26 monthly UD snapshots, current FY monthly UD snapshots through selection, and a selected-month UM matrix |

April 2025 is the Annual detail-history starting point. A standalone Monthly request fetches its selected month, including an earlier month if the source supports it; it does not backfill older FYs. Unsupported source months are reported unavailable.

For a completed month, UD covers its first through last day. UM covers 1 April of the selected FY through the selected month's last day. The authenticated engine report heading verifies both endpoints. **UM is fiscal cumulative; UD is monthly actual.** The source's product and Grand Total KMPL values are retained directly, not averaged from engine rows.

An open month uses yesterday in Asia/Kolkata and is marked provisional. No completed day on the first of the month, or a future month, cannot produce a verified month-end detail snapshot. Provisional snapshots remain refreshable until a completed-month source is captured. The existing Hub/Monthly future-month guards remain; this addition does not change the legacy annual CLI guard boundary.

The day cutoff applies to engine/product requests. B/F statements expose a month filter rather than a daily cutoff: an open-month tyre row is labelled as the current monthly source as fetched, without claiming it stops at yesterday.

## Exact source contracts

Base URL: `http://103.44.14.20`.

| Data | Method/path | Parameters |
| --- | --- | --- |
| Statement B | GET `/tyres/b_statement_final.php` | `zone=`, `region=`, `depot=PDT` or `RJP`, `month_year=MAY-2026`, `tyre_size=All Tyre Sizes Total` |
| Statement F | GET `/tyres/f_statement_final.php` | Same parameters as B; only the path changes |
| Engine/product monthly | POST `/mednew/eng_prod_um.php` | `fdate=31/5/2026`, `reg=YSRKADAPA`, `dept=PRODDUTUR` or `RAJAMPET`, `fupto=UD` |
| Engine/product selected cumulative | POST `/mednew/eng_prod_um.php` | Same mapped depot/date/region; `fupto=UM` |

`annual_kpi_runner_v3.tyre_site_info` supplies routing only. The new parser does not reuse the legacy single-dimension Engine parser. Vehicle depot codes, tyre depot codes and numeric spare IDs are distinct. The existing tyre mapper supports its recorded depots; an unmapped depot is reported unavailable instead of guessing a source code.

Tyre parsing requires one exact depot/month/size row. Source column names and order are preserved, including `Mech. Defetcs %`. Statement B has 24 captured columns; F has 18. Percentages are source percentage points: 37.50 is stored as 37.5 and displayed as 37.50, without multiplying by 100. Zero and blank remain distinct.

Engine parsing requires one recognised matrix, the exact depot and request interval, unique source engine identities and one final TOTAL. TOTAL's `colspan=2` is expanded as a label and blank engine cell so product totals cannot shift columns. Dynamic source products/engine rows remain exact identities. The new combined matrix is not a crosswalk to the old seven KPI labels.

## Durable history and May → July → May

`report_details.py` owns the hidden `_REPORT_DETAILS_HISTORY` tab, separate from `_ANNUAL_HISTORY` and monthly vehicle history. Its schema, depot identity, chunk count and SHA-256 checksum must validate before use. A corrupt/wrong-depot cache stops replacement. Checkpoint failures stop processing; they are not swallowed as source failures.

1. First May 2026 request fetches missing B/F/UD months from April 2025 through May 2026, plus May UM.
2. July request reuses the closed snapshots, fetches missing June/July B/F/UD, and refreshes July UM.
3. Returning to May refreshes May UM. June/July stay cached but disappear from the visible report.

When all requested sources exist, these steps require 43, 7 and 1 detail-source calls respectively. Missing sources and provisional snapshots may be retried. A verified closed B/F/UD snapshot is historical and is not refetched by the Annual path. Monthly requests refresh their selected month's three detail sources; failure retains that same depot/month's previous detail snapshot.

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

The change is open for review in [PR #9](https://github.com/imranshaik-pro/apsrtc-kmpl/pull/9). A production merge requires the owner's separate approval.

## Live acceptance evidence

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
