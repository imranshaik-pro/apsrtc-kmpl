# APSRTC-KMPL

Depot reporting automation for daily HSD KMPL, monthly vehicle performance, annual KPI history and Vehicle 360 workbook projections. APSRTC supplies operational sources; GitHub Actions executes reports; Google Drive/Sheets stores reports and history; the Automation Hub and Telegram provide request/delivery channels.

## Project documentation

Start with the [complete project guide](docs/project-guide.md), reviewed on 3 October 2026 against production commit 54dcf6b. It covers the project from its first commit on 21 August 2026 through the latest approved daily-template release.

| Topic | Record |
| --- | --- |
| Business logic and decisions | [Rules and lessons](docs/business-rules-and-lessons.md) |
| Where values are fetched and stored | [Sources, payloads and workbook lineage](docs/data-sources.md) |
| Architecture and execution sequences | [Architecture and flows](docs/architecture-and-flows.md) |
| Changes, challenges and solutions | [Project history](docs/project-history.md), [all 295 production commits](docs/change-ledger.md) |
| Completed, pending, deferred and closed work | [Action plan and known issues](docs/roadmap-and-known-issues.md) |
| Running, validating and handling failures | [Operations and validation](docs/operations-and-validation.md) |
| Proddatur historical Engine Upto | [Exact unresolved scope](docs/annual-kpi-known-issues.md) |

The early Phase A–G list described the initial daily project; it was not certification of all later features or every historical source value. The linked status register replaces blanket complete claims.

## Current production behaviour

- Manual Hub reports use the selected mapped depot. Scheduled daily reporting defaults to Proddutur and uses yesterday in Asia/Kolkata.
- Vehicle KMPL sums kilometres and HSD before division; Day and Upto are independent. Daily display uses Decimal half-up rounding and continuous five-slab bounds.
- Current daily requests fetch optional Telugu tyre details after normal KMPL. Historical dates skip tyres. The previous odd-day rule was superseded.
- PR #6 corrected the daily slab defect and 13 earlier daily regression failures; PR #5 added current-request tyres. Both are merged.
- PR #7 merged the approved daily-v1.1 model: centred tables, common SPARE1 shown once and strict NAC redundancy filtering. Telegram receives formatted text; Drive receives source TXT plus coloured HTML. PNG/PDF are review-only.
- Annual v11 stores source snapshots in hidden history and renders the selected-month endpoint into two visible tabs, preserving supported historical values.
- Monthly reporting distinguishes provisional open-month population from official closed-month MTD-598 and includes Vehicle Performance/Vehicle 360 when applicable.

Proddatur's seven retained historical Engine Upto identities remain unresolved and owner-deferred. PR #1 and Hub/native-logo PR #4 remain draft/unmerged; PR #4 separately records a deployed Apps Script version. Standalone Vehicle 360 lookup is not implemented. Fleet availability and depot-versus-APSRTC comparisons are closed/out of current scope because sources are unavailable. WhatsApp is an unimplemented future idea.

## Local environment

Use the repository requirements in a virtual environment. GitHub workflows currently select Python 3.11. Do not commit real APSRTC, Google, Telegram, GitHub or callback credentials.

Create a local .env from [.env.example](.env.example), with APSRTC_USERNAME and APSRTC_PASSWORD configured locally. Additional cloud setting names are listed in the operating guide; their values belong in Actions secrets or Apps Script Script Properties.

The direct daily core command is:

```bash
python run_daily_report.py --date 2026-09-30 --depot PRODDUTUR --vehicle-depot "PDTR/PRODDUTUR" --region-code YSRKADAPA
```

On Windows use .venv/Scripts/python.exe in place of python. This direct core is different from the cloud runner's request/date-resolution, cache, optional tyre and HTML behaviour. A source command authenticates and fetches real data; run it for an authorised request.

Reports are written under reports/ as UTF-8 text or XLSX. Generated reports, .env, caches and logs are ignored by Git. Cloud runner/workflow commands and relevant validation gates are in [operations](docs/operations-and-validation.md).

## Focused guides

- [Approved daily-v1.1 visual and delivery contract](docs/daily-template-v1.md)
- [Current daily tyre source/date rules and live evidence](docs/daily-tyre-checks.md)
- [Daily regression defect and test audit](docs/daily-regression-audit.md)
- [Permanent vehicle event register](docs/vehicle-event-register.md)
- [Telegram listener and command operations](docs/telegram-operations.md)
- [Telegram Apps Script deployment](docs/telegram-google-apps-script-webhook.md)
- [Application home](docs/index.md) and [privacy](docs/privacy.md)

Source contracts, identities, calculation/rounding/slab rules, selected-period semantics and the approved report design must not change silently. Keep rule/source/history/status documentation with each bounded review. Git merge, Apps Script deployment, report generation, Hub return and Telegram API acceptance are separate outcomes.

