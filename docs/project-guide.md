# APSRTC-KMPL project guide

Reviewed on 3 October 2026. Production source baseline: [54dcf6b](https://github.com/imranshaik-pro/apsrtc-kmpl/commit/54dcf6bd760bbf60d728ce1aee8677b54021b177), merged on 2 October 2026. Repository created on 21 August 2026; first commit was [e3301d6](https://github.com/imranshaik-pro/apsrtc-kmpl/commit/e3301d6046032e16dc7040786cd112b60684feb2).

## What the project does and why

The project turns authorised APSRTC operational reports into depot reports that support fuel-performance review, maintenance follow-up and historical comparison. It calculates vehicle KMPL where raw kilometres and HSD are available, preserves the depot KPIs supplied by APSRTC, and keeps reported source periods and identities visible.

The owner's operating model is one Automation Hub Form: select a depot, select Daily, Monthly, Annual KPI or a supported event action, select the relevant period, and submit. The separate scheduled Proddutur daily report remains. Manual reports use the selected depot; they are not Proddutur-only.

GitHub Actions runs the Python reporting code. APSRTC is the operational data source. Google Drive/Sheets holds outputs, permanent events and annual history. Forms and Telegram provide input and delivery; neither replaces the source calculations.

## Read the documentation

| Question | Document |
| --- | --- |
| What are our rules and decisions? | [Business rules and lessons](business-rules-and-lessons.md) |
| Where does each value come from, with which request? | [Data sources and workbook lineage](data-sources.md) |
| How do components and report sequences connect? | [Architecture and flows](architecture-and-flows.md) |
| What changed since the project began? | [Milestones and challenges](project-history.md), [complete production commit ledger](change-ledger.md) |
| What is finished, deferred, closed or awaiting approval? | [Roadmap and known issues](roadmap-and-known-issues.md) |
| How are reports operated and validated? | [Operations and validation](operations-and-validation.md) |
| What is the Proddatur Engine Upto issue? | [Annual KPI known issues](annual-kpi-known-issues.md) |
| What is the approved daily visual/delivery contract? | [Daily template v1.1](daily-template-v1.md) |
| When do tyres appear? | [Current-request tyre details](daily-tyre-checks.md) |
| How do Monthly/Annual B/F tyres and engine/product UD/UM snapshots work? | [Monthly and Annual detail tabs](monthly-annual-detail-tabs.md) |
| What were the 13 failed checks? | [Daily regression audit](daily-regression-audit.md) |
| How do events and Telegram input work? | [Vehicle event register](vehicle-event-register.md), [Telegram operations](telegram-operations.md), [Apps Script guide](telegram-google-apps-script-webhook.md) |

## Status at the audited baseline

| Area | Status and scope |
| --- | --- |
| Daily calculations, date rules, Drive cache and scheduled retries | Implemented on production; source availability can still fail a particular run. |
| Current-request tyres | Merged in [PR #5](https://github.com/imranshaik-pro/apsrtc-kmpl/pull/5). Current requests fetch tyres daily; historical requests skip them. Odd-day gating was superseded. |
| Daily slab defect and 13 earlier regression failures | Corrected in [PR #6](https://github.com/imranshaik-pro/apsrtc-kmpl/pull/6); the failures were daily checks, not annual FY24-25 tests. |
| Approved daily-v1.1 presentation | Merged in [PR #7](https://github.com/imranshaik-pro/apsrtc-kmpl/pull/7). Centred tables, common spare position once, guarded NAC deduplication. 157 local daily checks and compilation passed before merge. |
| Monthly and Vehicle 360 workbook | Implemented; current/open-month and closed-month populations follow different source rules. |
| Annual three-FY report | Implemented with persistent history and two visible tabs. Available values do not prove that every historical source row is complete. |
| Proddatur historical Engine Upto | Owner-deferred, unresolved for seven retained labels; [PR #1](https://github.com/imranshaik-pro/apsrtc-kmpl/pull/1) remains draft. |
| Hub callback / native annual logos | [PR #4](https://github.com/imranshaik-pro/apsrtc-kmpl/pull/4) remains draft and unmerged. Its record reports Apps Script version 7 deployed and Rajampet June callback/logo validation. Git merge and Apps Script deployment are separate states. |
| Standalone Vehicle 360 lookup | Not implemented in Hub/bot; Vehicle 360 in the monthly workbook exists. |
| Fleet availability / depot-versus-APSRTC comparisons | Closed/out of current scope by owner decision because accessible source data is unavailable. |
| WhatsApp delivery | Future idea, not implemented or an approved current delivery requirement. |

## How to interpret the evidence

After the audited baseline, documentation PR #8 was approved and merged at cf07f0f. [PR #9](https://github.com/imranshaik-pro/apsrtc-kmpl/pull/9) now contains the Monthly/Annual source-detail extension, its business rules and live acceptance record. That code is reviewed separately and is not yet a production release.

The [ledger](change-ledger.md) contains every one of the 295 commits reachable from the audited production baseline, including temporary diagnostics and their removal. Open PR changes are listed separately. Commit subjects describe work performed; they do not by themselves certify every value, external deployment or delivery.

The guides distinguish current code, owner requirements, recorded live validation and unresolved issues. The old README phase labels were an early daily-project plan; they were not certification of the later Hub, monthly, annual and source-completeness work. Private conversations or external changes without a retained record cannot be reconstructed from Git.

For a future change, update the relevant rule, source contract, history entry and action status in the same review. Record the selected depot/period, tested commit, test scope, source/workbook evidence, merge state and any separate Apps Script deployment.
