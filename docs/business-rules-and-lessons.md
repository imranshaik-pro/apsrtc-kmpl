# APSRTC reporting: business rules, decisions and lessons

Last reviewed: 1 October 2026. Review branch: `fix/hub-callback-over-grid-logo`.

## Scope and evidence

This is the consolidated record of the rules recoverable from the current repository and the owner's recorded decisions through this review. It is not a claim that every historical conversation, deployment or report has been independently retested. Each status below distinguishes implemented behavior, observed validation, requirements and open work. Existing operating guides remain authoritative for their specific modules.

The original README mainly documents daily KMPL. Its blanket phase-complete labels must not be interpreted as certification that every later Hub integration, annual source row or bot feature is complete.

## Purpose and operating model

Prepare accurate depot reports that help identify poor performance and support operational decisions, while preserving source values and historical evidence. GitHub contains runners and workflows; APSRTC supplies operational source reports; Google Drive/Sheets stores outputs and annual history; Forms/Telegram are input channels, not independent calculation engines.

The owner selected one Automation Hub Form for depot and report selection: daily, monthly, annual and supported event actions. Preserve the separate scheduled Proddatur daily report around the 05:00 IST window. Do not reintroduce a Proddatur-only route into shared manual reporting.

## Core calculation rules

| Rule | Required behavior / implementation reference |
| --- | --- |
| KMPL | Total kilometres divided by HSD. Sum kilometres and fuel first; never average individual vehicle KMPL. `src/calculations/kmpl.py`, `pipeline.py`. |
| Duplicate vehicle rows | Consolidate by vehicle number before calculating daily vehicle KMPL. `src/calculations/consolidation.py`. |
| For-Day versus Upto | Independent measures and source periods. Neither is a substitute for the other. |
| Rounding | Production daily presentation uses Decimal and ROUND_HALF_UP, as recorded in README and `src/calculations/rounding.py`. Do not assume every workbook adapter has been audited against this requirement. |
| Slabs | <=5.00; >5.00–5.10; >5.10–5.20; >5.20–5.30; >5.30. Exactly 5.30 belongs to slab 4. |
| Regional categories | Preserve TOT, NAC and AC and the target/day/Upto/previous-month/previous-year-month comparison structure. |
| Product versus engine | Keep Product KMPL and Engine KMPL separate; preserve source identities. |
| Missing data | Unavailable is not zero. Preserve blanks/manual markers; do not infer values from another engine, depot or district. |

## Dates, financial years and depot identity

- Financial years run April–March. April 2026 through March 2027 is FY 2026-27.
- Annual v11 derives the three-FY reporting window from selected month; the workflow's FY input is not justification for overwriting retained history.
- Daily scheduled runs use yesterday in Asia/Kolkata. Manual today resolves to yesterday; future dates are rejected (`run_automated_daily.py`).
- User/workflow dates use YYYY-MM-DD; annual/monthly selection uses YYYY-MM. Source adapters translate to their required source date formats.
- Resolve selected depot through mappings rather than treating display names, vehicle codes and tyre booklet codes as interchangeable. PRODDUTUR/PDTR and RAJAMPET/RJPT are examples.
- Owner business context: Rajampet moved from Annamayya to YSR Kadapa effective January 2026. Tyre FY 2025-26 comparisons must respect the relevant source-period mapping. This document records the requirement; it does not certify every historical mapping.
- Selecting All Zones/All Regions was proposed for depot discovery. It is not evidence that every adapter supports a universal query.

## Annual history and selected-month behavior

Persistent snapshots live in the hidden `_ANNUAL_HISTORY` tab. Presentation is a view, not the history store (`annual_history.py`, `annual_kpi_runner_v11.py`).

| Situation | Business rule |
| --- | --- |
| First depot run | Fetch missing source groups for historical FYs and current FY months through the selection. Retain unavailable markers where source evidence is absent. |
| Later month | Reuse valid saved values; fetch missing months/groups and needed endpoint Upto. Do not refetch or overwrite all historical FY numbers merely to redraw the report. |
| Earlier month after later month | Render only months through the selected endpoint; select that month's stored/source Upto. Later cached months remain stored but must not appear in this view. |
| Closed FY | Show March/full-year Upto, separately labelled from current FY selected-month YTD. |
| Failed fetch | Preserve saved valid numbers. Never replace them with blanks, failures or manual markers. |
| Invalid/wrong-depot cache | Fail closed on schema, depot identity, chunk count or checksum failure; do not silently rebuild over saved history. |
| Legacy workbook | Migrate valid monthly cells and targets; assign current FY Upto only when its date is proven by heading/metadata. Save migration before changing visible tabs. |
| FY rollover | Preserve snapshots and display the newly derived FY window. |
| Dynamic engine rows | Keep exact identities. A versioned legacy row-set repair can refresh source evidence without merging unrelated engine names or replacing good saved values. |

The user's phrase “replace Upto for the selected month” means replace the displayed endpoint when switching months. Current cache logic fills missing fields and preserves existing good values; it is not a general forced-refresh mechanism for a source that later revises an already valid number. That distinction must remain explicit.

Owner regression sequences: Proddatur April 2026 → July 2026 → May 2026; Rajampet May 2026 → July 2026 → May 2026. Prior checks passed for available values; they do not resolve absent Proddatur historical engine Upto. Automated history tests also cover later-to-earlier views, failed fetch preservation, migration, cache integrity and rollover (`tests/test_annual_history.py`).

## Annual source groups and tyres

Annual groups include HSD incl./excl. AC, Product, Engine, Total Lub KMPL, breakdown rate, MED cancellation, spring consumption and tyre metrics.

Tyre source availability is evidence-dependent:
- The original concern was missing FY 2024-25 tyre web history. The v6 adapter can use exact depot rows in official TRS monthly PDF booklets where present.
- PDF depot tyre-life values are already in lakh km; do not divide them by 100,000 again.
- April monthly can equal April Upto because it is the first FY month. Later cumulative-only depot pages do not justify invented monthly figures.
- District Target/For/Upto pages must never substitute for selected-depot values.
- FY 2024-25 lubricant and spring groups are explicitly marked unavailable by the current history adapter.
- A partial fallback is not proof that every tyre cell or every depot/FY is available.

References: `annual_kpi_runner_v6.py`, `annual_kpi_runner_v10.py`, `annual_history.py`.

## Monthly and vehicle history

The monthly runner fetches daily vehicle rows, consolidates duplicates and preserves day-wise KMPL in the workbook. It carries prior history and builds Vehicle Performance/Vehicle 360 projections using verified source and event data.

Schedule III is Major Service; Schedule IV is Complete Major Service. Source completion dates determine daily-cell markers, while retaining that day's KMPL. Ambiguous duplicate/conflicting schedule rows are not assigned a guessed marker. Current marker logic starts April 2026 (`monthly_vehicle_report.py`).

Manual events are append-only: one real event = one row. Keep stable event IDs, vehicle identity, event date, depot, category-specific details and entry source. Repeated aggregate changes remain chronological. Forms and Telegram must use the same canonical schema. Source-derived schedules must not be manually duplicated just to populate history. Standalone Telegram Vehicle 360 lookup is not certified implemented by the existing guide.

See [Vehicle event register](vehicle-event-register.md), [Telegram operations](telegram-operations.md) and [Apps Script Telegram guide](telegram-google-apps-script-webhook.md).

## Presentation and decision rules

- Every visible sheet identifies depot and reporting period.
- Annual report exposes two main tabs: KPI Dashboard and Detailed Data. History/metadata remain hidden and are not deleted during formatting.
- Preserve separate HSD incl. AC and excl. AC measures and separate Product/Engine groups.
- Upto is column R in the detail layout; retain clear borders and numbers. Hide the unused Q spacer rather than presenting it as missing KPI data.
- Annual charts use same-unit monthly series through selected month. Current model includes HSD and tyre trends.
- Fuel and TOTAL LUB KMPL: higher is better. Breakdown and MED cancellation rates: lower is better.
- Annual red/green target colouring requires a numeric source target; missing values use an unavailable treatment. Do not invent thresholds.
- Monthly daily cells use the established KMPL slab colours.
- Full-year and YTD are different periods: label them clearly and avoid misleading like-for-like comparisons.
- Requested fleet-availability trends and depot-versus-APSRTC comparisons are not implemented by the current annual chart model; they require verified comparable source data.
- XLSX logos are embedded image assets. Owner requested native Google Sheets logos over cells, not an IMAGE cell formula. Rajampet June 2026 dashboard/detail floating logos were installed and visually verified.
- Use clear operational captions and legends; avoid decorative claims that imply unsupported performance.

References: `annual_visuals.py`, `annual_kpi_runner_v11.py`, `report_branding.py`, `apps-script/report_branding.gs`.

## Hub and delivery contract

1. Form submission selects depot and applicable date/month/action.
2. Apps Script validates inputs and dispatches the matching GitHub workflow, including the originating Hub row.
3. Workflow generates/updates the report and emits its actual Google URL.
4. An authenticated callback records the report link and COMPLETED status on the same request row.
5. Verify output data, period and visual rendering as well as workflow completion.

SUBMITTED means dispatch was accepted, not that report generation or delivery completed. A successful build with callback skipped is not end-to-end success. Missing callback secrets currently cause a skip message in workflows.

The scheduled daily workflow is separate and defaults to Proddatur. Its current schedule is 05:07, 06:11, 07:17, 08:23, 09:29, 10:35 and 11:41 IST. GitHub schedules may be delayed. The settings JSON lists a broader retry-hours array; actual workflow schedules govern execution. Existing report filename checks and scheduled Telegram suppression avoid repeatedly uploading/delivering the same daily report; manual requests may deliberately redeliver.

Telegram long polling, scheduled checks and Apps Script webhook are alternative ingestion modes; do not run competing consumers. Command registration or /status alone is not delivery proof. Never store tokens in source or chat.

## Challenges, correction and evidence

| Challenge | What changed / lesson | Current status |
| --- | --- | --- |
| Repeated annual full rebuilds and lost selected-period context | Persistent source snapshots, migration, endpoint-based views, checksum and depot guards. | Implemented; history tests exist. |
| Proddatur historical engine Upto missing | Shared runner path investigated; exact historical labels/source mapping remain unresolved. Do not manufacture aliases or zeros. | Deferred by owner; Rajampet passed the checks performed. See known-issues document. |
| Suspected old Proddatur-only parser | Both depots traced through shared annual runners/parsers; suspicion is not a proven cause. | No speculative depot parser replacement approved. |
| Annual Python indentation failure reported during earlier work | Compile gate added before build; recorded real Rajampet Hub run passed the compile step. | Gate implemented; not evidence of universal source completeness. |
| Google Sheets merge/frozen-boundary errors | v11 clears conflicting freeze boundaries during legacy formatting and restores safe header freeze. | Implemented in current runner. |
| Weak visual identity, missing legends and confusing periods | Shared presentation model, named units/series, target-based colours, grouped KPIs and depot/period headers. | Implemented; some requested charts remain open. |
| External IMAGE formula showed #REF! | Floating native images replace formula dependency for annual Hub callback/repair. | Rajampet June live repair verified; future callbacks still need end-to-end validation. |
| Live Hub omitted hub_row despite repository code having it | Corrected all three live dispatch inputs after observing callback step skipped. | Live dispatcher corrected. |
| Repository and deployed Apps Script differed | Located actual installable trigger project; empty bound project was not production engine. | Active Vehicle Event Engine project identified and version 6 updated. |
| Conflicting doPost handlers | Route unkeyed Hub callbacks from existing vehicle handler; preserve keyed vehicle-event route. | Committed in PR #4 and deployed version 6. |
| Callback token missing | Last safe diagnostic reported token absent; matching Apps Script/GitHub settings are required. | Owner credential entry and live validation pending. |
| Daily callback URL type differs from annual | Daily returns Drive file links; initial annual callback validator accepts only spreadsheet links and opens reports as spreadsheets. | Bounded correction committed: accept Drive file links without opening them as spreadsheets; require a spreadsheet for annual branding. Tests passed; deployment/live validation pending. |
| Signed-in browser session reset; Google connection failed | Existing deployment/commits remain saved; do not confuse connection failure with lost code. | 1 October recheck: sign-in 502 / Connection refused; live final test blocked. |
| Static settings lag behind later workflow features | Record differences explicitly: old FY defaults, Telegram disabled flag and retry array do not certify current workflow behavior. | Documentation warning; no unrelated settings silently changed. |

## Evidence and change status

- [PR #2](https://github.com/imranshaik-pro/apsrtc-kmpl/pull/2) and [PR #3](https://github.com/imranshaik-pro/apsrtc-kmpl/pull/3) were previously merged.
- [PR #4](https://github.com/imranshaik-pro/apsrtc-kmpl/pull/4) contains callback/over-cell logo code and this documentation; it remains unmerged unless separately approved.
- [Rajampet June Hub run 36734569179](https://github.com/imranshaik-pro/apsrtc-kmpl/actions/runs/36734569179): report generation and Telegram succeeded; callback skipped because live dispatch lacked hub_row.
- Apps Script web-app version 6 deployed with existing URL/access settings retained; not proof that callback secrets or final end-to-end delivery are ready.
- Local JavaScript syntax, callback authentication, row bounds, URL rejection and repeat-safe logo tests passed. Additional daily Drive-link and monthly spreadsheet-link success tests, annual Drive-link rejection and malformed-link rejection also passed.
- Proddatur data issue is explicitly outside the callback/logo fix.

## Acceptance and change discipline

Before closing a report integration, verify source-to-cell values, historical preservation, selected period, workflow logs, matching Hub row COMPLETED/link, image rendering and delivery. Compile/test success alone is insufficient.

Do not merge, deploy or modify unrelated external systems without owner approval. Specific Apps Script deployment approval was given for the Hub/logo work; it is not permission to invent historical KPI data or merge another PR. Keep credentials out of commits, screenshots and chat.

Known unresolved source rows are listed in [Annual KPI known issues](annual-kpi-known-issues.md). Update this register when new evidence changes a rule, a deployment differs from repository code, or a validation result closes an open item.
