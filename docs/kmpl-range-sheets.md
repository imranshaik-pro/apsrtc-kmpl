# Monthly vehicle/driver range distribution and Annual FY trend

Requested on 3 October 2026. `kmpl_ranges.py` adds one **KMPL Range Distribution** sheet to Monthly and one **FY KMPL Range Trend** sheet to Annual KPI. Both include vehicle and driver populations, the seven original source ranges, source G.Total, first-three-range count/share and highest-range share. Monthly also shows the original regional rows, highlighting the selected depot. Annual uses the same three FYs as its KPI dashboard: closed FYs show April–March; the current FY stops at the selected month. FY share charts use the monthly cells. Missing values produce chart gaps; entirely unavailable FY charts are omitted.

These are monthly classification snapshots. Adding totals across months would count the same vehicle or driver repeatedly, so there is no distinct-population FY total. No average KMPL is inferred from the range counts.

## Observed source requests

All requests reuse the existing authenticated `requests.Session`. No credentials or cookies are recorded in history or documentation.

| Source | Method and URL path | Parameters | Scope |
| --- | --- | --- | --- |
| Vehicle range table | **GET** `/med/vehlog_kmpldepot.php` | `action=` (blank), `yymm=202609`, `rreg=YSRKADAPA` | All source-listed depots in that region; select exact requested depot |
| Driver range table | **GET** `/med/drvlog_kmpldepot.php` | Same names and formats | Separate driver population |
| Vehicle drilldown link, observed only | **GET** `/med/vehlog_kmplveh.php` | `action=`, `yymm=202609`, `rreg=PRODDUTUR` or another exact depot | Per-vehicle details; not fetched by this feature |
| Driver drilldown link, observed only | Source-linked driver detail URL | Depot/month query validated if a link is present | Not fetched or used to reclassify drivers |

Base: `http://103.44.14.20`. Owner screenshots show both regional GET URLs. Owner vehicle HTML supplies the table and its drilldown links. The driver fixture is transcribed from the supplied screenshot. Blank `action` is retained explicitly. In regional requests `rreg` is a **region**; in the shown vehicle drilldown it is a **depot**. These meanings must not be interchanged.

APSRTC has several HTML report families, **not one universal POST contract**. These two pages share GET selection fields and differ in URL and population. Other existing adapters include POST `/med/vehkmpl.php` with `fyymm`/`dept`, POST `/mednew/eng_prod_um.php` with `fdate`/`reg`/`dept`/`fupto`, and GET tyre statements with `month_year`/`depot`/`tyre_size`. See [data-sources.md](data-sources.md) for the repository-wide request inventory. Similar visual tables do not authorize swapping paths, methods, date formats or depot codes.

Routing uses the existing mapped region/display depot. No historical district crosswalk is guessed. If a region restructure means a requested depot is absent from the returned month, that source is unavailable until a verified route is supplied.

## Validation and source semantics

The parser requires exactly one recognised two-level table, the exact entity/month heading, all seven range headings in order, one unique selected-depot row, non-negative integer counts and one final regional total. Each depot's seven buckets must equal its G.Total; every regional bucket and regional G.Total must equal the sum of depot rows. Present drilldown links must agree with their row's exact depot and YYYYMM. Login pages, wrong months, mismatched populations, blank/negative/fractional counts, duplicates and unreconciled totals are rejected.

Original labels are preserved, including **Below -3.00**, **5.31 - 5.60**, and **5.60 - ABV**. The last two labels overlap at 5.60; this feature does not guess a new cutoff or recompute buckets from raw logs. First-three-range share uses only the first three reported bucket counts divided by that population's source G.Total. Highest-range share uses only the seventh reported bucket. Vehicle and driver denominators remain separate. If a verified total is zero, source counts remain zero and percentage cells are blank.

The range pages select a month, without a daily cutoff parameter. An open month is visibly **provisional**, as fetched; it is not described as a snapshot through yesterday. Future source months are not fetched.

## Incremental history and integration

`_KMPL_RANGE_HISTORY` is an independent hidden, depot-bound, chunked JSON cache with schema and SHA-256 checks. Existing `_ANNUAL_HISTORY`, `_REPORT_DETAILS_HISTORY`, tyre formulas, legacy engine identities, Monthly grid and vehicle history are unchanged.

* First Annual use fetches missing months for its three displayed FYs, if sources are supported.
* Later use fills missing months, refreshes provisional history and replaces the selected month's vehicle/driver snapshots.
* Verified closed history other than the selected month is reused.
* May → July → May rebuilds only the range view. June/July remain saved but disappear from the May view; chart ranges and grids are rebuilt too.
* A failed refresh retains the **same depot/month/entity** snapshot with a stale status. A first failure leaves numeric cells blank and shows unavailable. No other month or depot supplies replacement counts.
* Checkpoint/write failures and corrupt history stop replacement. Successful source validation cannot erase saved history due to a later source failure.

Monthly attaches the new view/cache immediately before its existing branding/save/upload boundary. It reads only the existing same-depot, same-month file's range cache. Annual checkpoints the independent cache, builds the range tab alongside its existing four views, publishes typed numbers and native formulas/charts, then keeps the new range sheet visible. The shared native serializer clears/shrinks only the owned new view and removes stale charts/merges/formatting. Embedded XLSX branding uses A3:C3; native publication retains the existing serializer's text/logo limitations.

## Owner September controls and review

| Source | Proddutur buckets in source order | Proddutur G.Total | Rajampet G.Total | Region G.Total |
| --- | --- | --- | --- | --- |
| Vehicles | 0, 2, 39, 18, 9, 9, 4 | 81 | 43 | 411 |
| Drivers | 0, 3, 78, 36, 35, 16, 5 | 173 | 82 | 911 |

`tests/test_kmpl_ranges.py` verifies these owner controls, bad-source rejection, exact GET payloads, FY rollover/cutoff, missing versus zero, stale preservation, provisional refresh, checksum/depot checks, checkpoint failure, May/July/May and core/native integration. Existing detail/history/branding tests verify preserved consumers.

`verify_kmpl_ranges.py --offline` creates four isolated previews from only the real supplied September tables. Other months remain unavailable; it invents no history. Normal execution logs in and samples both source types for both depots across the three FYs plus May/July/selected month. It creates local XLSX and JSON review artifacts only: no Drive/Sheets write, Hub callback or Telegram delivery. Sampled source availability does not certify every unrequested historical month. `kmpl-ranges-review.yml` runs these checks using existing GitHub secrets and retains its artifacts for seven days.

This review establishes repository implementation and isolated source/preview evidence. Existing production workbooks gain the tab when regenerated after release; an old downloaded XLSX does not update itself. This feature does not resolve the separately documented seven Proddutur historical engine Upto labels.

Local validation on 3 October 2026: **82 affected tests passed**, including 16 new range tests and the existing 66 detail/template/history/dashboard/branding/presentation tests. Four September previews for Proddutur/Rajampet were imported and recalculated in Artifact Tool, with zero formula-error matches. Selected-depot shares matched independent source-count arithmetic; changing/restoring one source bucket proved share recalculation. All four changed views were rendered and inspected, including selected-month highlighting, source totals, logo placement, FY chart gaps and readable chart labels. Native Sheets typed-value/formula/chart requests are checked structurally; an authenticated native Sheets write/readback is not part of this read-only review.
