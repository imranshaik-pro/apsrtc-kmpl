# PR #4 reconciliation and scheduled delivery — 3 October 2026

## Scope and release boundary

Reconcile `fix/hub-callback-over-grid-logo` with production `b007426742fdf162fa74e40596931d9c5994d479`. Preserve all current master files, including the PR #9 B/C/F detail tabs, count-only FY totals, locked daily template and consolidated documentation. Apply the bounded callback/router/logo changes, callback checks, submitted-row stale-link removal and scheduler diagnostics. Do not merge master or redeploy Apps Script as part of this review.

Production Git had two `doPost` declarations: one in `automation_hub.gs` and another in `vehicle_event_trigger.gs`. The reconciled project has one entry point. Requests with a vehicle API key retain vehicle authentication/validation; requests without that key use the separately authenticated Hub callback. The callback validates integer row bounds and allowed actual Google report URLs, resolves `Automation Requests` by name, accepts daily Drive files without opening them as Sheets, and brands annual Sheets idempotently. No KPI source values change.

The earlier PR #4 record reports Apps Script version 7 deployed on 1 October. Today's fresh successful callback establishes deployed behaviour, not a byte-for-byte deployed-source comparison. Google account sign-in returned HTTP 502, so version/source inspection remains blocked. Git merge alone does not deploy Apps Script. The new submitted-row link cleanup requires a separately approved Apps Script update.

## Fresh end-to-end Hub verification

Used the owner's existing [HUB form](https://docs.google.com/forms/d/e/1FAIpQLSfmywB_UDpW8AKoZ5sEAsMraTMFK5BRVxoHO1L-y1qJSuKKRA/viewform), not a synthetic GitHub dispatch. Selected PRODDUTUR, Daily HSD KMPL Report, current date 2026-10-03.

| Boundary | Observed result |
| --- | --- |
| Form response | `Automation Requests` row 21, 3 October 15:09:21 IST |
| Dispatch | [Production run 37113780135](https://github.com/imranshaik-pro/apsrtc-kmpl/actions/runs/37113780135), master `b0074267`, created 15:09:23 IST |
| Business date | Runner resolved today's selection to yesterday, 2026-10-02 |
| Report | Existing valid current-request HTML report returned; source TXT and HTML identities retained |
| Callback | `AUTOMATION_HUB_LINK_UPDATED` at 15:10:08.094 IST; callback step succeeded |
| Hub row | `COMPLETED | DAILY | PRODDUTUR | 2026-10-02` with correct HYPERLINK |
| Telegram | `TELEGRAM_DAILY_REPORT_SENT: 1 message(s)` at 15:10:08.997 IST; API acceptance, not a claim that a person read it |

Returned [Proddutur 2 October report](https://drive.google.com/file/d/1h-Dbs1EBeQ__I_PJ3qHEHz7_azOo8Lmt/view?usp=drivesdk). The exact same URL was present in runner output, callback environment, Hub formula and Telegram environment. Drive metadata confirms the file is `PRODDUTUR_2026-10-02_daily-v1.1_current.html`, MIME `text/html`, shared. This check does not create a new workbook or change its sharing.

While row 21 was still SUBMITTED, its link temporarily pointed to row 20's Rajampet file. The completed callback correctly replaced it. Reconciled `hubStatus_` now clears any inherited report-link content when marking SUBMITTED and preserves links on COMPLETED. The inheritance mechanism was not established; the correction depends only on the verified inappropriate pre-completion link.

Historical annual evidence remains [Rajampet June run 36833906698, attempt 2](https://github.com/imranshaik-pro/apsrtc-kmpl/actions/runs/36833906698). Connected Sheets read confirms row 19 is COMPLETED with its actual annual spreadsheet link; row 20 is COMPLETED with the actual Rajampet daily file link. Monthly callback URL handling is tested offline; no fresh monthly form delivery is claimed in this review.

## Why today's report arrived at 07:48 IST

The first configured cron is `7 5 * * *` with `timezone: Asia/Kolkata`, meaning **05:07 IST**, followed by staggered hourly retries through 11:41. It is not an exact 05:00 schedule. GitHub added IANA timezone support in March 2026; this timezone field is valid. Do not apply a speculative UTC conversion.

| 3 October scheduled run 37089325717 | IST |
| --- | --- |
| Run created and started | 07:48:12 |
| Actual report URL logged | 07:48:46.621 |
| Telegram API acceptance | 07:48:47.537 |

[Run evidence](https://github.com/imranshaik-pro/apsrtc-kmpl/actions/runs/37089325717): execution to Telegram took about 35.5 seconds. The roughly 2h41 gap from the first configured slot occurred before run creation, not inside report generation or Telegram. GitHub documents that scheduled triggers can be delayed or dropped under load. Existing logs do not expose the triggering `github.event.schedule`; they cannot establish whether today's first trigger was delayed or an earlier slot was skipped. No exact internal GitHub cause is claimed.

[Later retry 37100725488](https://github.com/imranshaik-pro/apsrtc-kmpl/actions/runs/37100725488) found the same report at 11:13 IST and skipped Telegram; scheduled duplicate suppression worked. Later retries also succeeded. Scheduled runs have no Hub row and intentionally skip the form callback.

The reviewed workflow now records event, cron expression, UTC/IST execution start, run ID and attempt, with the cron visible in the run name. This enables future slot-by-slot delay diagnosis without logging credentials. All cron expressions and timezone are unchanged. Changing the first expression to 05:00 would change its nominal target but would not guarantee a 05:00 delivery. A reliable time-bound dispatcher is a separate reviewed scheduling decision; no external scheduler was created.

Official references: [GitHub schedule documentation](https://docs.github.com/en/actions/reference/workflows-and-actions/events-that-trigger-workflows#schedule), [19 March 2026 timezone release](https://github.blog/changelog/2026-03-19-github-actions-late-march-2026-updates/).

## Validation

- Node: 14 depot/service dispatch contracts and FY boundaries; callback authentication, row bounds, URL allow-list and repeat-safe annual logos; single POST entry point and vehicle-key isolation; submitted-link cleanup and completed-link preservation.
- Python: 38 focused daily workflow/template/Telegram configuration tests passed. Local checkout initially lacked the three tracked font binaries; restored existing copies and verified their manifest hashes through the tests. No production font change was needed.
- Compile: `run_automated_daily.py`, `run_daily_report.py`, `src/reporting/daily_template.py` passed.
- Fresh production form run, authenticated callback, connected Hub formula and Telegram API success verified above.
- CI workflow runs the three Node checks for changes to Hub scripts/tests.

Proddutur legacy historical Engine Upto remains owner-deferred. This reconciliation does not reopen unavailable fleet/comparison sources, remap CG, change FY data or modify the approved daily report layout.

## Production completion after Google sign-in

Owner approved the production merge on 3 October. PR #4 merged as `7ef3c2bd023946460625940a6a192aecf0eb6389`; [production build 37114740481](https://github.com/imranshaik-pro/apsrtc-kmpl/actions/runs/37114740481) completed successfully.

Google sign-in was subsequently confirmed on the Apps Script dashboard. Inspected the existing APSRTC Vehicle Event Engine project: active version 7, the isolated Hub/vehicle POST router in Code.gs, and authenticated report_branding.gs. The deployed project source is maintained separately and is not claimed to be byte-for-byte identical to all Git files. Applied only the tested `hubStatus_` pending-link cleanup and its missing `hubEnsureColumn_` helper to the existing automation_hub.gs. Editor copy-back exactly matched the intended change; reversing those two insertions reconstructs the prior source. Other project files, credentials, deployment URL and execute-as/access settings were unchanged.

**Version 8 deployed successfully at 15:49 IST on 3 October**, using the same active deployment ID and endpoint. This supersedes the earlier sign-in/deployment blocker in this dated review. Version 7 is retained in project history for rollback.

Post-deployment real HUB form check:
- PRODDUTUR, current date 2026-10-03, response row **22**.
- Connected Sheets read while SUBMITTED: **Drive Report Link blank**, proving the inherited-link cleanup.
- [Production run 37116252788](https://github.com/imranshaik-pro/apsrtc-kmpl/actions/runs/37116252788), master `7ef3c2bd`, completed successfully.
- Timing diagnostic: workflow_dispatch started 15:53:25.091 IST.
- Runner resolved report date **2026-10-02**, returning the same correct current-request HTML file.
- Callback logged `AUTOMATION_HUB_LINK_UPDATED` at 15:53:57.046 IST.
- Telegram logged `TELEGRAM_DAILY_REPORT_SENT: 1 message(s)` at 15:53:57.883 IST.
- Independent connected Sheets read: row 22 COMPLETED with the correct [Proddutur HTML link](https://drive.google.com/file/d/1h-Dbs1EBeQ__I_PJ3qHEHz7_azOo8Lmt/view?usp=drivesdk).

The new schedule diagnostic is now live. [Scheduled run 37116074204](https://github.com/imranshaik-pro/apsrtc-kmpl/actions/runs/37116074204) recorded cron `35 10 * * *`, configured in Asia/Kolkata, but execution began **15:50:16.627 IST**, approximately 5h15m after that nominal slot. It found the existing report and correctly skipped Telegram. This directly identifies a late scheduled slot; the GitHub scheduler's internal reason remains unproven. The reviewed change does **not** claim to fix punctual 05:00 delivery. No alternative scheduler or schedule change was made.
