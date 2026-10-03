# Current status and action plan

Reviewed on 3 October 2026. Baseline: [54dcf6b](https://github.com/imranshaik-pro/apsrtc-kmpl/commit/54dcf6bd760bbf60d728ce1aee8677b54021b177). Status words below deliberately separate runtime changes, verification and owner-deferred work.

## Completed on production

| Work | Evidence |
| --- | --- |
| Multi-depot manual dispatch, daily/monthly Hub request contract | PR #2 merged 30 September |
| APSRTC asset branding and established performance colours | PR #3 merged 30 September |
| Continuous exact-bound slab classifier; repair 13 old daily checks | PR #6 merged 2 October at 314f85d; same KMPL/rounding business rule |
| Current-request Telugu tyres with independent spare snapshot | PR #5 merged 2 October at df13f60; regular KMPL first, historical exclusion |
| Approved daily-v1.1 layout and text/HTML delivery | PR #7 merged 2 October at 54dcf6b; production tree matches a6d740c, which passed 157 local daily checks and compilation |
| Persistent annual history and selected-month views | Active v11/history implementation; available-source checks do not certify missing legacy rows |
| Monthly open/closed lifecycle and workbook Vehicle 360 | Active monthly/history/event implementation |

## Work requiring a next action

| Priority | Item / status | Concrete next action and acceptance |
| --- | --- | --- |
| 1 | Monthly/Annual owner-template B/C/F tyre and engine/product detail tabs: [PR #9](https://github.com/imranshaik-pro/apsrtc-kmpl/pull/9) ready for owner review | The supplied model, Statement C, fiscal-year formulas, both depot transitions, native Sheets recalculation, 45 focused tests, compilation and four full workbook previews passed on the implementation commit. The final presentation rerun also passed on cb0ac0d; only owner review/production merge approval remains for this feature. Review the [rules and evidence](monthly-annual-detail-tabs.md), then obtain separate production merge approval. |
| 2 | PR #4: Hub callback/native logo code remains draft in Git; recorded Apps Script version 7 already deployed | Reconcile reviewed branch with active deployed source, refresh its checks and resolve documentation overlaps before a separate approved merge. Do not paste conflicting doPost handlers. Preserve actual Hub row, authenticated callback, valid daily Drive-file and annual spreadsheet URLs, repeat-safe logos and event API. |
| 3 | Production v1.1 live acceptance | Next approved current daily Hub/scheduled run should confirm date, source values, latest HTML link, callback when applicable and Telegram formatting. Earlier live v1 delivery is verified; screenshot-correction v1.1 had local/rendered checks, not a separately sent live message at merge time. |
| 4 | Standalone Vehicle 360 lookup: not implemented | Scope separately if the owner requests it. The monthly workbook Vehicle 360 tab must not be confused with this input-channel feature. |

## Deferred or evidence-dependent

Documentation consolidation was approved and merged in [PR #8](https://github.com/imranshaik-pro/apsrtc-kmpl/pull/8) at cf07f0f. The detail-tabs review extends that documentation with new source contracts and history rules.

| Item | Decision / reopening evidence |
| --- | --- |
| Proddatur historical Engine Upto | Owner-deferred; exact source row for seven legacy labels or authoritative classification crosswalk is required. Preserve existing history and do not widen speculative parser changes to Rajampet. |
| PR #1 em-dash missing-value correction | Draft/unmerged; narrow predicate correction does not supply unmatched Engine values. Review separately before activation. |
| Unknown operation code CG | Display the unresolved code/vehicle; change mapping only with authoritative source classification. |
| Early 1 October daily vehicle-source failure | A later scheduled run succeeded without a parser change. Exact failed-response cause is unknown because raw HTML was not retained. Capture a safe failing response if it recurs before proposing a correction. |
| Current source constraints | v11 direct CLI lacks the Hub's future-month check; target attempts are once per FY; vehicle history FY tokens are fixed; provisional event population and cutoff filtering are distinct. These are documented code boundaries, not runtime changes authorised by this documentation task. |

## Closed / not current work

- Fleet-availability trend and depot-versus-APSRTC comparisons are closed/out of current scope by the owner's decision because accessible source data is unavailable. Do not keep listing them as pending features. Reopen only when source access changes and the owner directs it.
- Odd-day tyre gating is superseded by current-request gating. Do not restore it.
- Missing annual command / vehicle-number event input are old concerns: guided annual and event input code now exist. Their deployment/delivery still needs specific evidence; do not relist them as absent implementation.
- Q is a deliberately hidden annual spacer, not a data-fetch issue.
- WhatsApp remains an unimplemented future idea, outside current approved delivery work.

## Change discipline and completion criteria

For a data defect, capture selected depot/date/FY, exact source endpoint/payload and table cells, parsed fields, persistent cache and visible workbook row. Compare the source-to-workbook path before a bounded correction. Verify historical preservation and selected-month endpoint semantics.

For a presentation change, retain the approved model data and section order, run the relevant contracts, render and inspect, version an approved change, then obtain production merge approval. Telegram API acceptance, user reading, Google HTML preview support and full report correctness are different checks.

For Hub changes, verify the real originating response row and returned report URL, not only workflow success. For Apps Script, record the deployed version and existing URL/access settings separately from a Git merge. The documentation update itself does not run a report, send Telegram or deploy Apps Script.
