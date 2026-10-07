# Operations and validation

Reviewed on 3 October 2026. Start with [project guide](project-guide.md); exact source fields are in [data sources](data-sources.md).

## Entry points

| Purpose | Runner / workflow |
| --- | --- |
| Daily cloud/manual report | run_automated_daily.py; daily-report.yml |
| Direct daily core, without cloud request-resolution/cache layer | run_daily_report.py |
| Monthly native Sheet and workbook Vehicle 360 | monthly_vehicle_report.py; monthly-report.yml |
| Annual persistent history/four-tab report with the detail extension | annual_kpi_runner_v11.py; report_details.py; annual-kpi.yml |
| Annual read-only source diagnosis | diagnose_annual_sources.py; annual-kpi-diagnostic.yml |
| Event validation / register integration | record_vehicle_event.py; vehicle-event.yml; permanent Apps Script register |
| Monthly source validation | validate_monthly_vehicle_history.py; monthly-source-validation.yml |

Direct source commands can authenticate, fetch, upload or send through workflows. Execute them only for an authorised report/test. This documentation review does not execute them.

For the authorised [Monthly/Annual detail review](monthly-annual-detail-tabs.md), `report-details-review.yml` compiles the affected runners, runs focused offline contracts and uses `verify_report_details.py` for isolated live source/history/Sheets checks. It creates private review files and local workbook artifacts; production upload/delivery boundaries are excluded. Its final live acceptance is recorded separately from this guide's earlier documentation-only audit.

## Production daily schedule and storage

Actual daily workflow schedules are 05:07, 06:11, 07:17, 08:23, 09:29, 10:35 and 11:41 Asia/Kolkata. The scheduled default is PRODDUTUR; date resolves to yesterday. Workflow YAML governs execution; the older settings JSON retry array is not the actual schedule.

The same depot/date TXT filename prevents repeat source upload. Scheduled Telegram delivery is skipped when that cached report is already marked delivered; manual/Form dispatch can deliberately redeliver. A saved TXT is cache evidence, not a transactional guarantee that every preceding Telegram send completed before a crash.

Current requests refresh local tyres and their current HTML companion. Historical requests use the selected KMPL period and historical HTML companion without tyres. Source TXT and styled HTML have separate links; the styled companion points back to source TXT. HTML is self-contained; Google Drive may require downloading/opening it in a browser.

## Configuration names, never values

| Setting family | Names / location |
| --- | --- |
| APSRTC source login | APSRTC_USERNAME, APSRTC_PASSWORD; environment / Actions secrets |
| Google OAuth | GOOGLE_CLIENT_ID, GOOGLE_CLIENT_SECRET, GOOGLE_REFRESH_TOKEN; Actions secrets |
| Report destinations | DAILY_DRIVE_FOLDER_ID, MONTHLY_DRIVE_FOLDER_ID, KPI_DRIVE_FOLDER_ID / configured defaults |
| Telegram delivery | TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID |
| Hub return | HUB_CALLBACK_URL, HUB_CALLBACK_TOKEN in Actions; matching token in active Apps Script Script Properties |
| Dispatch from Apps Script/listener | Repository-scoped GitHub dispatch token as documented in the deployment guides |
| Event API | VEHICLE_EVENTS_API_URL, VEHICLE_EVENTS_API_KEY and matching Script Properties |
| Bot modes / depot menu | TELEGRAM_LISTENER_MODE, DEPOT_MASTER and appropriate Script Properties |

Hub callback and event API credentials are different. A callback token is an operator-generated shared secret, not a token automatically issued by Google Forms. Its values must match at both ends; do not commit or print them.

config/automation_settings.json contains old annual FY defaults and telegram.enabled=false while current workflow/bot code has later behaviour. Treat each setting according to the entry point that actually reads it. Do not silently change configuration during a documentation update.

## Relevant validation gates

The production [daily workflow](../.github/workflows/daily-report.yml) compiles the renderer, runner, application, tyre and Drive modules, then runs its focused daily/tyre/presentation tests before report generation.

The [annual workflow](../.github/workflows/annual-kpi.yml) compiles v3/v7/v10/v11, history and visuals and runs annual history unittest discovery before generation. Its failure handling and actual URL extraction matter as well as Python syntax.

The most recent pre-merge local daily evidence was 157 passing checks across application, pipeline, region, reporting, slab, vehicle-summary, tyre, workflow and template suites, plus compilation. It is not a full-repository test certification. The 13 earlier daily failures were corrected in PR #6 and are described in [regression audit](daily-regression-audit.md).

For a future relevant daily code change, the established broader daily command is:

```bash
APSRTC_USERNAME=fixture APSRTC_PASSWORD=fixture python -m pytest -q tests/test_application.py tests/test_pipeline.py tests/test_region_formatter.py tests/test_region_parser.py tests/test_region_reporting.py tests/test_reporting.py tests/test_slab_regression.py tests/test_vehicle_summary.py tests/test_telugu_report.py tests/test_daily_tyre_checks.py tests/test_current_daily_tyres.py tests/test_daily_workflow.py tests/test_telegram_daily_visual.py tests/test_daily_template.py tests/test_daily_template_delivery.py
```

Fixture credentials only satisfy imports for offline tests; they are not source credentials. Use test scopes appropriate to the change. A documentation-only update needs link/path/ledger/status validation and a Markdown-only diff, not another live report or speculative source patch.

## Report acceptance

| Layer | Required evidence |
| --- | --- |
| Input | Correct depot, request intent and selected/derived period |
| Source | Exact report/payload, heading date, depot row, units, requested field; safe response evidence if defective |
| Calculation | Consolidated kilometres/HSD, independent Day/Upto, continuous slab boundaries and count conservation |
| Annual history | Correct cache identity/checksum; preserved historical values; requested endpoint Upto; later cached months absent from earlier view |
| Tyres | Correct eligibility, independent categories, zero versus unavailable, exact vehicle/position associations and separate spare date |
| Visual output | Rendered actual source-based layout, no lost rows, readable headings/units and approved template contracts |
| Google storage | Actual file/Sheet URL and stable identity; supported refresh behaviour |
| Hub | Originating response row contains authenticated completion/link; a skipped callback is incomplete Hub evidence |
| Telegram | API acceptance of correctly escaped complete content/chunks; reading is not inferred |
| Release | Reviewed/tested head matches merged tree; separate deployed Apps Script version recorded where applicable |

## Failure handling and rollback

For an empty/changed source, retain safe raw response and exact non-secret payload before changing parsing. HTTP 200 alone does not establish a valid report. Check source availability, active parser and selected depot/date separately.

For an annual cache read/checksum/depot failure, stop; do not erase history. Missing source-group requests preserve supported good fields. Known FY24 unavailable exceptions and em-dash limitations are documented explicitly.

For callback problems, distinguish missing hub_row, missing/mismatched credentials, rejected URL/row, handler collision and deployed-source divergence. PR #4 records the existing bounded correction; Git merge alone does not redeploy it.

For a production rollback, review a revert of the specific release commit/PR under owner approval, retain generated historical evidence and verify the restored entry point. Do not force-push master or delete historical Sheets. This guide authorises no rollback/deployment by itself.


## Repository-state gate before any new fix

Before editing code for an existing PR or reported defect:

1. Read current `master` SHA and recent master commits.
2. Read the PR state, merge state and current head SHA.
3. Compare the feature branch against current master.
4. If the PR is already merged or a newer follow-up PR contains the work, stop editing the old branch and validate master instead.
5. Record separately: code merged, CI/test evidence, Docker/deployment evidence, live source evidence, workbook evidence and external delivery evidence. None implies all the others.

This gate is mandatory after the PR #12 review on 7 October 2026, where the feature merged while additional checks were still being performed on its feature branch.

## KMPL range validation gate

For a Month/Upto range change, run compilation and `tests/test_kmpl_ranges.py` first. Validate all four logical source flows (Vehicle Month/Upto and Driver Month/Upto), exact `action/yymm/rreg` selection, separate snapshot scope, combined Monthly table, Annual final cumulative row, selected-month refresh, May→July→May visible cutoff, stale preservation and the rule that cumulative is never a monthly sum.

Then run preserved-consumer suites separately. If an unrelated suite fails, identify the exact failing class/test before changing production code. On 7 October, the range suite passed and `test_report_details.py` source-contract tests passed, while its HistoryAndViewTests group failed. Because `report_details.py` is unchanged from pre-PR-12 baseline, that result is tracked independently pending exact reproduction. It is not a reason to roll back the merged range feature.

The review workflow should keep test families in separately named steps where practical so GitHub exposes which contract failed rather than reporting one opaque bundled validation failure.
