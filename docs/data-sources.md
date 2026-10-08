# Data sources and source-to-workbook lineage

Reviewed on 3 October 2026 against production [54dcf6b](https://github.com/imranshaik-pro/apsrtc-kmpl/commit/54dcf6bd760bbf60d728ce1aee8677b54021b177). These are the active repository contracts, not new live requests. APSRTC reports use an authenticated requests.Session.

## Authentication and source families

[Login](../src/auth/client.py) POSTs to http://103.44.14.20/index.php with username, password and Login=Login, follows redirects, checks HTTP status and requires PHPSESSID. Credentials come from environment settings. A session cookie alone does not certify source completeness; downstream reports still validate tables and rows.

Source bases in [annual_kpi_report.py](../annual_kpi_report.py) are /med, /mednew and /tyres at http://103.44.14.20. Spring uses /storeap. Do not move a report between these families solely because the filenames look similar.

## Depot identities

| Depot | Display identity | Vehicle dept payload | Current region | Annual tyre-web depot | FY24 PDF depot | Captured spare option |
| --- | --- | --- | --- | --- | --- | --- |
| Proddatur | PRODDUTUR | PDTR/PRODDUTUR | YSRKADAPA | PDT | PDTR | 114 |
| Rajampeta | RAJAMPET | RJPT/RAJAMPET | YSRKADAPA | RJP | RJPT | 115 |

[depot_mapping.json](../depot_mapping.json) is the shared daily/monthly/core depot map. [v3 tyre mapping](../annual_kpi_runner_v3.py), [v6 PDF mapping](../annual_kpi_runner_v6.py) and the spare page dropdown are different authorities. Spare options are discovered for the selected depot at runtime. Do not send 114 for every depot.

Rajampet moved from Annamayya to YSR Kadapa effective January 2026 in the recorded business context. Annual tyre web currently uses blank zone and region with its depot code, avoiding district-dependent history lookup. This does not make the other source adapters district-independent.

## Daily inputs

| Data | Request | Selection and validation | Consumer |
| --- | --- | --- | --- |
| Vehicle logs | POST /med/vehkmpl.php; fyymm=DD/MM/YYYY, dept=vehicle_depot | table.demoTable; exactly 15 td cells per parsed row; vehicle, operation, engine, Day and Upto kilometres/HSD/source KMPL fields | [application](../src/reporting/application.py), [vehicle parser](../src/parser/vehicle_parser.py), independent calculation pipeline |
| Depot regional KPIs | GET /med/achsd1.php; action blank, fdate=YYYY-MM-DD, rreg=region_code | Exact selected-depot rows; independent TOT/NAC/AC and five KPI fields; duplicate/missing TOT rejected | [region parser](../src/parser/region_parser.py), [region summary](../src/reporting/region_summary.py) |

Daily vehicle ratios are recalculated from consolidated raw kilometres/HSD. The regional depot KPI readings are preserved from the source. A depot TOT value need not equal an average of vehicle ratios.

If no valid vehicle rows remain, the application raises Vehicle report returned no valid vehicle records and does not fabricate a report. The early 1 October-source incident's failed HTML was not retained, so the exact upstream cause is unknown.

## Optional current-request tyre inputs

| Category | Request sequence | Contract and result |
| --- | --- | --- |
| RC front | POST /med/rc_tyres_front1.php; fyymm=D/M/YYYY, then POST /med/rcpopup.php | Popup dt=D/M/YYYY, regn=region_code, dept blank |
| Mismatched | Same front parent selection, then POST /med/samepopup.php | Same popup fields; source identifies vehicles/positions |
| Repair | POST /med/fitted_repair1.php; fyymm=D/M/YYYY, then POST /med/repairpopup.php | Same popup fields; preserves source-listed vehicle/position |
| Over-two-month spare snapshot | POST /tyres/spare_tyre.php with depot_id blank to discover dropdown, then POST verified selected-depot option | No date parameter; own Run Date, vehicle, RTC tyre number, position, numeric days |

The popup fields follow the owner's captured rctyre.js, rather than the later suggested dist_code payload. [tyre_checks.py](../src/reporting/tyre_checks.py) validates heading date, row shape and exact normalised depot. Spare validates its separate Run Date, identity, row shape and conflicting duplicates. Empty and unavailable results are distinct.

Only current intent fetches tyres, after normal KMPL. Historical selected dates make no tyre calls. Date-selectable categories use the resolved KMPL date; spare uses the current source snapshot and visibly labels its different date.

## Active annual inputs

In the table, source base is http://103.44.14.20. Year/month formats are adapter contracts, not user input formats. [v11](../annual_kpi_runner_v11.py) dispatches missing groups through shared adapters.

| Group | Endpoint / method and fields | Exact output rule |
| --- | --- | --- |
| HSD incl/excl AC | GET /med/mth_acnac_dpt.php; action blank, fdate=last day as DD/MM/YYYY, dist=mapped district | Exact depot WITH AC / WITHOUT AC For and Up To columns; independent month/Upto pairs |
| PRODUCT | POST /mednew/prodkmpl_um.php; yymm=YYYYMMMonth_YYYY, reg=mapped district, dept=display | Exact PRODUCT: source label with separate monthly/Upto |
| ENGINE | POST /mednew/engkmpl_um.php; same fields | Exact ENGINE: source label; no crosswalk to retained legacy labels without evidence |
| Total lubricant KMPL | POST /med/lub_rgn_rpt.php; yymm=YYYYMMMonth_YYYY and source referer | Verify report month; exact depot-wise Total Lub KMPL For CY / Upto CY; no reconstruction from oil quantities |
| Breakdown rate | GET /med/sysbd_dpt.php; action blank, yymm=YYYYMMMonth_YYYY, dist=mapped district | Exact depot BD RATE source pair |
| MED cancellation | GET /mednew/medcan_um_dpt.php; action blank, fdate=YYYYMMMonth-YYYY, dist=mapped district | Exact depot cancellation percentage columns |
| Spring consumption | GET /storeap/deptspring.php; action blank, yymm=YYYYMMMonth_YYYY, dist=mapped district | Exact depot SPRING CONSUMPTION PER LAKH KMS columns |
| Tyre monthly | GET /tyres/d_statement_final.php; zone and region blank, depot=tyre-web code, month_year=MON-YYYY uppercase, tyre_size=All Tyre Sizes Total | Exact depot/total-size row for supported FYs |
| Tyre cumulative | GET /tyres/e_statement_final.php; same fields | Exact selected-endpoint Upto; seven tyre metrics remain separate |
| FY24-25 tyre fallback | GET /med/trs_booklet/2024-25/mon-year.pdf; lower-case abbreviated month | PDF signature required; exact depot-code life/rate rows; supported Upto, April monthly only where cumulative equals monthly |

Monthly/Upto fields are selected by the final imported adapter. The active Product/Engine parser is v4.strict_dimension_rows, installed on the shared v3 module, with body month index 3 and Upto index 6. v3 also contains newer header helpers; their existence alone does not mean the v11 import chain uses them. Both depots share the active path. See [annual architecture](architecture-and-flows.md).

The new [Monthly/Annual detail tabs](monthly-annual-detail-tabs.md) use separate B/C/F statement endpoints and `mednew/eng_prod_um.php`. C uses `/tyres/c_statement_final.php` with the same depot/month/all-size query as B/F; its four repeated S1–S9 groups are qualified by tyre stage. Only owner-template fields are displayed, while raw verified snapshots retain all source fields. That combined matrix's verified UD month interval and UM fiscal interval are independent of the original single-dimension KPI parser described above.

The v8 lubricant contract example is yymm=202605May_2026. MED token uses its separate hyphen form; do not interchange these fields. Annual targets use April of the FY and explicit target columns in the corresponding depot source, including tyre targets only where an exact depot target exists.

## Annual row storage and visible lineage

| Stage | Location / identity | Result |
| --- | --- | --- |
| Source pair | Exact group, source row label and YYYY-MM | month and upto fields stay separate |
| Persistent history | Google Sheet hidden _ANNUAL_HISTORY; schema annual-history-1 and depot identity | months[YYYY-MM][GROUP][KPI], targets per FY, attempts and repair version |
| Selected view | history.view_store for derived three FYs | April–selection values for current FY; March endpoint for closed FYs |
| Detailed Data | A serial; B KPI; C FY; D target; E:P Apr–Mar; Q hidden spacer; R Upto | Source labels remain their own rows; formatting does not fill missing data |
| KPI Dashboard | annual_visuals.dashboard_model | Both HSD cards, tyre/breakdown cards, grouped full-FY/YTD summary and same-unit monthly charts |

For supported history, a failed source request leaves valid saved fields intact. The active FY24 LUB/SPRING unavailable rule is explicit. Exact tyre PDF Upto does not establish a missing monthly value or selected-depot target.

## Monthly / Vehicle Performance / Vehicle 360 inputs

The new [KMPL range sheets](kmpl-range-sheets.md) read **GET** `/med/vehlog_kmpldepot.php` and `/med/drvlog_kmpldepot.php` with blank `action`, `yymm=YYYYMM`, and `rreg=mapped_region`. Both reports supply regional depot counts; their selected-depot range snapshots are stored separately in `_KMPL_RANGE_HISTORY`. These methods/fields differ from the POST raw-vehicle and trend adapters below. Source bucket counts and monthly populations are not reconstructed from daily logs or added into a distinct FY population.

| Data | Contract | Consumer and coverage |
| --- | --- | --- |
| Daily monthly grid | POST /med/vehkmpl.php for each completed day | [monthly_vehicle_report.py](../monthly_vehicle_report.py); consolidates duplicate daily records, latest valid source Upto |
| Closed vehicle roster / MTD-598 | POST /med/edeengine.php; yymm=YYYYMM, regn, depot and blank filter fields, fstatus=0 | [fetch_mtd](../src/reporting/vehicle_history.py); exact vehicle, HSD KMPL, operation/engine and commission fields; never queried for current/open month |
| FY25-26 / FY26-27 vehicle trend | POST /med/vkmpl12trend.php; yymm blank, fyymm=202603March_2026 or 202703March_2027, zone, regn, dept, submit=SUBMIT | Existing/new vehicle history; FY24-25 uses monthly MTD snapshots |
| Schedule III / IV | POST /med/s3cover.php or /med/s4cover.php; yymm=YYYYMMMonth_YYYY, zone, regn, dept, submit=SUBMIT | Official service dates, daily markers and maintenance exceptions from April 2026 |
| Prior workbook | Drive export of latest earlier same-depot DEPOT_YYYY-MM native Sheet | Existing Vehicle Performance history only; future/current workbooks do not seed history |
| Permanent manual events | Secured Apps Script VEHICLE_EVENTS_API_URL with API key, returning canonical Vehicle Events rows | Vehicle 360 chronological event projection; display filtered to depot and report cutoff |

For current months, provisional candidates come from daily data and depot events, not finalized MTD-598. The current code filters displayed Vehicle 360 events to cutoff separately from candidate population construction. Vehicle-history FYs/tokens are currently fixed to 2024-25/2025-26/2026-27.

## Where outputs and callbacks go

| Output | Storage / refresh rule |
| --- | --- |
| Daily TXT | reports/DEPOT_YYYY-MM-DD.txt; same stable name in configured daily Drive folder; existing source TXT is reused, not overwritten for presentation |
| Daily HTML | DEPOT_YYYY-MM-DD_daily-v1.1.html or _daily-v1.1_current.html companion; allowed companion can refresh under stable Drive ID |
| Monthly | reports/DEPOT_YYYY-MM.xlsx and stable native Google Sheet DEPOT_YYYY-MM; rerun refreshes content under same ID |
| Annual | reports/*ANNUAL_KPI*.xlsx and stable native Google Sheet DEPOT_ANNUAL_KPI_DASHBOARD; hidden history is persistent |
| Hub return | Workflow POSTs token,row,url,status to HUB_CALLBACK_URL when hub_row is supplied and secrets exist |
| Telegram | Daily full formatted text; monthly/annual completion/failure status and actual Google report link |

[Google Drive integration](../src/integrations/google_drive.py) uses configured Google OAuth credentials. [Google Sheets integration](../src/integrations/google_sheets.py) supplies annual value/tab operations. Hub callback credentials are separate from event API credentials. None of their values belongs in documentation.


## KMPL range Month/Upto source clarification — 7 October 2026

For the Monthly/Annual KMPL range feature, preserve scope separately from URL identity.

| Entity/scope | Verified flow |
| --- | --- |
| Vehicle Month | GET `/med/vehlog_kmpldepot.php?action=&yymm=YYYYMM&rreg=REGION` |
| Vehicle Upto/Cum | GET selector `/med/vehlog_kmpl.php`, then GET `/med/vehlog_kmpldepot.php?action=&yymm=YYYYMM&rreg=REGION` |
| Driver Month | GET `/med/drvlog_kmpldepot.php?action=&yymm=YYYYMM&rreg=REGION` |
| Driver Upto/Cum | GET selector `/med/drvlog_ckmpl.php`, then GET `/med/drvlog_ckmpldepot.php?action=&yymm=YYYYMM&rreg=REGION` |

The Vehicle result filename is shared by Month and Upto. Do not infer scope from filename and do not invent a vehicle `ckmpldepot` path. `action`, `yymm` and `rreg` retain the same selection names for these flows. Store and validate the requested scope with the snapshot.

These population snapshots are non-additive across months. Annual cumulative range rows must use the cumulative source flow; they must never be reconstructed by summing monthly bucket counts.
