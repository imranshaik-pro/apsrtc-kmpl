# Annual KPI known issues and regression record

Reviewed on 3 October 2026. Proddatur's historical Engine Upto issue remains explicitly deferred by the owner.

## Exact unresolved scope

The observed issue is Proddatur (source/repository spelling PRODDUTUR), not a proven all-depot problem. Rajampet worked for the checks performed. Those observations do not certify every Rajampet source period.

Seven retained Engine labels lack verified historical Upto mapping:

- EICHER-BS-III
- EURO-3 1512TC
- INDRA NEW
- TA-1510
- TA-BS-IV
- EICHER BS-III LATEST
- TATA BS-III NRE SPIN

Do not copy another engine's values, invent aliases, substitute zeros or treat callback/logo repairs as a data fix.

## Current path and diagnosis boundaries

Annual-kpi.yml executes v11. Its shared import chain reaches v4.strict_dimension_rows, installed on the v3 module, for Product/Engine row parsing; both depots use this path. The suspected Proddatur-only old parser is not established. Details are in [architecture](architecture-and-flows.md).

Production history.good regards an em dash as present, so that marker can block missing-field fill. Draft [PR #1](https://github.com/imranshaik-pro/apsrtc-kmpl/pull/1) corrects the predicate, with two regression checks, but does not resolve the seven labels and is not merged.

## Retained investigation evidence

| Investigation | Finding / limit |
| --- | --- |
| [36668329677](https://github.com/imranshaik-pro/apsrtc-kmpl/actions/runs/36668329677) | Current Engine endpoint returned six current names for Proddatur June. |
| [36668724244](https://github.com/imranshaik-pro/apsrtc-kmpl/actions/runs/36668724244) | Explicit April–June engine-product report returned seven current model names and different cumulative readings; total 4.97 matched depot HSD Upto. These are not verified legacy-label aliases. |
| [36668881482](https://github.com/imranshaik-pro/apsrtc-kmpl/actions/runs/36668881482) | Official June booklet supplied coarse make/BS categories. |
| [36669098074](https://github.com/imranshaik-pro/apsrtc-kmpl/actions/runs/36669098074) | Finalised April/May/June MTD vehicle masters checked. |
| [36669235033](https://github.com/imranshaik-pro/apsrtc-kmpl/actions/runs/36669235033) | June 30 daily logs also used current Engine names. |

Findings above are retained in PR #1. Its temporary probes were removed from the reviewed diff. The production commit ledger also records earlier source diagnostics and their removal. A commit named repair or a successful workbook build is not proof that the seven Upto fields were filled.

## Selection/history regression rules

| Scenario | Required result |
| --- | --- |
| First selected-month run | Missing historical groups and current FY months through selection are fetched; supported valid source values are retained. |
| Later selection | Fill missing current months and needed endpoint Upto; preserve earlier supported historical values. |
| Return to earlier selection | Display only months through that selection and its Upto; later cached months remain stored. |
| Source failure | Preserve saved valid values; unavailable does not become zero. |
| Wrong/corrupt cache | Fail closed instead of rebuilding over saved history. |

Recorded sequences: Proddatur April 2026 → July 2026 → May 2026; Rajampet May 2026 → July 2026 → May 2026. The available-value checks do not close the missing historical Engine scope. See [history tests](../tests/test_annual_history.py).

## Reopening criteria

Capture exact depot, selected month, FY, retained Engine label, source payload, returned headers/cells, active parser output, cache snapshot and workbook Upto cell. Find the report that originally supplied the legacy identities or an authoritative classification crosswalk. Preserve all other FY values and compare the same path in a relevant depot before changing shared code.

The owner directed proceeding with other work until this evidence exists or the pattern appears elsewhere.

## Separate Hub/logo work

PR #4 remains unmerged in Git; its record reports Apps Script version 7 deployed on 1 October. [Rajampet June Hub run 36833906698, attempt 2](https://github.com/imranshaik-pro/apsrtc-kmpl/actions/runs/36833906698) validated build, callback and Telegram; row 19 and floating logos were checked. June HSD Upto was 5.24, with July onward blank in that view. None of this fills the Proddatur legacy Engine values.
