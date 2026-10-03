# Business rules, decisions and lessons

Reviewed on 3 October 2026 against production [54dcf6b](https://github.com/imranshaik-pro/apsrtc-kmpl/commit/54dcf6bd760bbf60d728ce1aee8677b54021b177). This is the current rule register. Earlier rules and the reasons they changed are recorded in [project history](project-history.md).

## Purpose, scope and identity

| ID | Rule | Reason / implementation |
| --- | --- | --- |
| B01 | One Hub accepts selected depot, action and period; preserve the separate scheduled Proddutur daily run. | Shared manual reporting must work for mapped depots. [Hub dispatcher](../apps-script/automation_hub.gs). |
| B02 | Use depot mapping and the source-specific depot identifier. | Display, vehicle, tyre-web, PDF and spare-selector codes differ. [Source identity table](data-sources.md). |
| B03 | Product and Engine KMPL remain separate, with exact source labels. | Similar labels do not establish the same classification. [Annual adapters](../annual_kpi_runner_v3.py). |
| B04 | Unavailable source data is not zero or another depot's value. | Preserve evidence and explicitly display unavailable/manual values. The known master em-dash predicate gap is recorded below. |
| B05 | Existing working source contracts and calculations must not change silently to satisfy a visual request. | Presentation consumes completed report data; source and calculation changes need their own evidence. |

## Daily KMPL and vehicle classification

| ID | Rule | Current code |
| --- | --- | --- |
| D01 | Vehicle KMPL = total kilometres / HSD. Consolidate duplicate vehicle measurements by summing kilometres and HSD before division. Never average individual vehicle KMPL. | [Pipeline](../src/calculations/pipeline.py), [consolidation](../src/calculations/consolidation.py). |
| D02 | Calculate For-Day and Up-To-Day independently from their respective source measurements. Zero HSD gives no calculable KMPL. | [Normalization](../src/calculations/normalization.py), [KMPL](../src/calculations/kmpl.py). |
| D03 | Daily presentation rounds to two decimals with Decimal ROUND_HALF_UP. Classify the unrounded calculated ratio. | [Rounding](../src/calculations/rounding.py), [slabs](../src/calculations/slabs.py). Raw parser/calculation inputs are floats; this is not a claim that every workbook adapter uses Decimal arithmetic. |
| D04 | Slabs use continuous upper bounds: <=5.00; >5.00–5.10; >5.10–5.20; >5.20–5.30; >5.30. Exactly 5.30 belongs to slab 4. | The displayed 5.01/5.11/5.21 labels are presentation labels, not gaps in classification. |
| D05 | Low-performance list: at most ten NAC vehicles, positive calculable Day KMPL <=5.00, sorted by Day KMPL, with each vehicle's Upto retained. | [Vehicle summary](../src/reporting/vehicle_summary.py). Unknown codes provisionally enter NAC low-list consideration and are separately reported. |
| D06 | Slab tables count each eligible mapped vehicle once in each independent Day/Upto table. | Zero/uncalculable values and unmapped operation codes do not enter these tables. Their totals are eligible classified vehicles, not a fleet-availability measure. |
| D07 | Unknown operation types remain explicit. Do not invent a classification for CG or another unknown code. | [Vehicle-type mapping](../vehicle_type_mapping.json), unknown-code log and business-readable report note. |
| D08 | Depot Target, Day, Upto, last-month and last-year-month metrics come from the selected depot's regional source rows, preserving TOT/NAC/AC independently. | [Application](../src/reporting/application.py), [region summary](../src/reporting/region_summary.py). They are not averages of the displayed low-vehicle list. |

## Dates and current-request tyre eligibility

All date decisions use Asia/Kolkata. Daily input uses YYYY-MM-DD; monthly/annual input uses YYYY-MM. Adapters translate these to each source contract.

| Input intent | KMPL period | Tyres |
| --- | --- | --- |
| Scheduled daily run | Yesterday IST | Fetch after KMPL succeeds, every day. |
| Manual daily date omitted | Yesterday IST | Fetch after KMPL succeeds, every day. |
| Manual daily date equals today | Yesterday IST | Fetch after KMPL succeeds, every day. |
| Manual daily date earlier than today | Exactly the selected date | Skip all tyre requests and remove any old tyre section from the local delivery view. |
| Future date/month | Rejected by the operational entry points | No report should be claimed. |

The owner first requested an odd resolved-report-day rule, then explicitly replaced it with current-request gating. Preserve the original intent before resolving today's date to yesterday. Both odd and even current requests now fetch tyres. A manually selected yesterday is historical and skips tyres, even though today's default request resolves KMPL to that same day.

Monthly current-month reporting stops at yesterday; on the first day of a month it has no completed current-month day. The annual Hub rejects future months; direct v11 CLI expects a valid selected month but does not independently compare it with today. Do not describe a workflow input form as a complete future-period guard.

## Optional tyre categories

References: [tyre module](../src/reporting/tyre_checks.py) and [tyre operating record](daily-tyre-checks.md).

1. Generate regular KMPL first. Enrich afterwards; an optional tyre-source failure must leave completed KMPL usable.
2. Include RC front tyres, source-identified mismatched tyres, repair tyres and the source's over-two-month spare snapshot.
3. Date-selectable categories use the resolved KMPL date. Match exact normalised depot rows, validate heading date, vehicle and positions, and deduplicate identical source rows.
4. Count distinct vehicles and source tyre records separately. A mismatched report listing all positions is not proof that each listed position is independently faulty.
5. Hide validated zero categories. If every category is validated empty, show no tyre section. Failure or malformed data is unavailable, never a zero result.
6. Successful categories survive another category's failure. Login/write failures produce an unavailable note or preserve the original complete file.
7. Spare source supports depot_id, not historical date selection. Resolve its live dropdown for the selected depot; PRODDUTUR=114 and RAJAMPET=115 are captured examples, not universal constants.
8. Keep the spare source's own Run Date visible. Retain its over-two-month selection; do not impose a guessed 60/90-day replacement rule.
9. Daily-v1.1 shows one recognised common spare position once above the table. Mixed or unknown positions keep the position column. Original source rows retain every position, tyre number and days value.

## Annual history and financial years

FY runs April–March. Annual v11 derives the three-FY window from selected month. April 2026–March 2027 is FY2026-27. A supplied FY argument does not justify replacing preserved history.

| ID | Situation | Rule / actual behaviour |
| --- | --- | --- |
| A01 | First depot run | Build the historical FYs and current FY months through selection by fetching missing source groups. Keep unsupported cells unavailable. |
| A02 | Later selected month | Reuse saved good values; fetch missing monthly groups and needed endpoint Upto. Do not refetch every FY just to redraw. |
| A03 | Earlier selection after a later selection | Show only months through the selected endpoint and its stored/source Upto. Later months stay cached, hidden from this view. |
| A04 | Valid saved numeric data | Preserve it during missing-value backfill and failed fetches. Switching selection replaces the displayed Upto endpoint; it is not a forced refresh of an already valid source value. |
| A05 | Completed FY | Display March/full-FY Upto. Current FY uses selected-month YTD; label the different coverage. |
| A06 | Cache safety | Hidden _ANNUAL_HISTORY stores schema/depot identity, length/chunks and checksum. Wrong depot, corrupt or unreadable history fails closed; no silent destructive rebuild. |
| A07 | Legacy migration | Preserve monthly values/targets; date current-FY Upto only when heading/metadata proves its endpoint. Save migrated history before source requests or visible formatting. |
| A08 | Source exceptions | FY2024-25 LUB and SPRING are explicitly unavailable in the active history path; those designated fields become MANUAL INPUT REQUIRED. This exception is separate from preserving supported historical numbers. |
| A09 | Engine row-set repair | Older caches without engine-rowset-v1 may refresh Engine evidence once, add exact source identities and fill missing fields; never merge different engine models or replace good saved values. |
| A10 | Targets | FY attributes sourced from April, exact depot and explicit target column. HSD, BD, MED, SPRING and tyres where supported; targets for unsupported rows stay blank. Attempts are recorded once per FY, so a failed target attempt is not automatically retried on every redraw. |
| A11 | Proddatur missing legacy Engine Upto | Owner-deferred. Exact row/source mapping remains unresolved; no alias, copied value or guessed zero is authorised. |

The requested regression sequences are Proddutur April 2026 → July 2026 → May 2026 and Rajampet May 2026 → July 2026 → May 2026. Those reported checks for available values do not close the seven missing Proddutur legacy Engine Upto rows. Automated selection tests are in [test_annual_history.py](../tests/test_annual_history.py).

Current master history.good rejects None, blank and MANUAL strings, but considers an em dash present. Draft PR #1 fixes this predicate; it is not merged and does not provide values for unmatched engine labels. See [known issues](annual-kpi-known-issues.md).

## Annual tyre sources, units and targets

- FY2024-25 missing web history is not a blanket ban on verified official PDF data. The active v11 history path calls the exact-depot v6 booklet fallback; April monthly can equal April Upto, later cumulative-only depot pages do not justify invented monthly numbers.
- Web tyre-life numbers are converted from km to lakh km by /100000. Booklet life numbers are already lakh km and are not divided again. Rate units stay as supplied.
- Require the exact depot and All Tyre Sizes Total row. District, zone and corporation targets or For values cannot substitute for depot figures.
- Rajampet's January 2026 district change is recorded business context. Current annual tyre-web requests use blank zone/region and the verified depot code; PDF and spare IDs remain separate.
- v10's legacy all-month wrapper contains older April-only FY24 tyre restrictions. v11 deliberately uses history.update and the captured targets-only function instead of that blanket wrapper. [Architecture](architecture-and-flows.md) names the active path.

## Monthly, maintenance and manual events

| Rule | Behaviour |
| --- | --- |
| Monthly KMPL | Fetch daily vehicle rows for completed days; consolidate each vehicle's daily records, preserve daily KMPL, latest valid Upto and source operation/engine identity. |
| Closed month | Official selected-month MTD-598 is authoritative for the current vehicle population and commission information. |
| Current/open month | Skip MTD-598. Use provisional daily operational vehicles plus depot event candidates; label the population and operational cutoff. |
| Historical vehicle data | Import the latest earlier same-depot monthly workbook; existing vehicles reuse history, new vehicles need backfill. Current vehicle history is the fixed FY24-25/FY25-26/FY26-27 layout, separate from dynamic annual FY selection. |
| Schedule III/IV | Major Service / Complete Major Service. Fetch official dates; show markers without replacing that day's KMPL. Conflicting or repeated schedule records enter maintenance exceptions instead of a guessed marker. |
| Manual event register | One real event = one append-only row with stable ID, date, depot, normalised vehicle and category-specific details. Do not overwrite prior aggregate changes. |
| Event channels | Form/Hub and Telegram normalise into the canonical register. Source schedules normally come from APSRTC, although the Python schema also accepts Schedule III/IV. |
| Vehicle 360 | Workbook projection combines roster/KMPL, maintenance and chronological manual events; standalone Hub/bot lookup remains unavailable. |
| Event cutoff | Vehicle 360 event display is filtered to selected depot and completed report cutoff. Current provisional population construction separately considers all depot event candidates; it should not be described as a universally cutoff-filtered roster. |

## Visuals, decisions and delivery

Every visible report identifies depot and period. Annual KPI Dashboard and Detailed Data retain the original KPI model. The [detail-tabs extension](monthly-annual-detail-tabs.md) adds Tyre Statements and Engine & Product KMPL, making four visible tabs. _ANNUAL_HISTORY, _REPORT_DETAILS_HISTORY, _TYRE_INPUTS, _META and preserved legacy tabs remain hidden rather than deleted. Q is a hidden original KPI spacer; R is original detail Upto.

The owner's Monthly/Annual tyre model shows B mechanical defects with F Stone% and Worn Smooth%, B premature failures separately, and C's four S1–S9/Total stage groups. Monthly displays its selected month; Annual separates FY25–26 and FY26–27 through the selection, with count-only FY Total rows; percentage totals remain blank while monthly source percentages remain visible. B and F receipts are different populations. Preserve reported stage totals, visibly flag a code-sum discrepancy, and never fabricate a missing source count. May → July → May removes June/July from views and derived input ranges while preserving their cached snapshots.

Fuel and TOTAL LUB KMPL: higher is better. BD and MED cancellation rates: lower is better. Annual red/green grading for these KPIs requires a numeric source target; missing values receive unavailable treatment. Monthly cells use existing KMPL slab colours. Do not invent targets or infer the depot fuel-weighted average's cause from vehicle count shares.

Daily-v1.1 retains the approved order: depot/date; KPI target/actual/difference; low vehicles; slabs; positive tyres; classification/inspection priorities; Drive link/caption. Centred tables and reduced repeated labels do not remove source associations. Exact layout and font/style contracts live in [daily template](daily-template-v1.md).

Hide redundant NAC only with a positive mapped NAC-only source vehicle total, no unknown codes, all five Total/NAC KPI values matching, valid positive Day/Upto and absent/zero AC KPIs. Differing targets/history, AC data/types or uncertainty keep separate sections. Real Proddutur 1 October has AC data, so retains TOT/NAC/AC.

Telegram receives escaped bold/monospaced text with balanced supported HTML and bounded chunks. Its fonts/colours follow the client theme. Drive holds the source TXT and coloured self-contained HTML; PNG/PDF images are review-only, not generated/sent by the daily workflow.

XLSX uses embedded APSRTC assets. Native annual Google Sheet images over cells, including the requested A3:C3 sizing preference, belong to the separately recorded Hub branding deployment/PR #4. Do not claim that merging Python presentation code updates a live Apps Script project or makes IMAGE formulas reliable.

## Approval and closed scope

Repository change, PR merge, workflow execution, source-value verification, Apps Script deployment, callback writeback and Telegram API acceptance are distinct outcomes. SUBMITTED means dispatch accepted; it does not mean COMPLETED. A skipped callback is not a validated Hub return path. API acceptance does not establish that a person read the message.

Proddatur historical Engine Upto remains deferred by the owner. Fleet availability and depot-versus-APSRTC comparisons are closed/out of scope because accessible sources are absent, not pending features. Reopen only with source evidence and owner direction. WhatsApp is an unimplemented future idea.

Keep secrets in GitHub Actions secrets or Apps Script Script Properties. Record setting names and deployment versions, never token/password values. Preserve owner's separate merge/deployment approval boundaries.
