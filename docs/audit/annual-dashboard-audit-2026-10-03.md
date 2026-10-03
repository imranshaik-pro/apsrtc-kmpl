# Annual dashboard and value audit — 3 October 2026

## Baseline and scope

Reviewed master `295e3cd8c48a51dc8c6e61b4be709da41c3b3628` through the GitHub connector and the owner-provided `PRODDUTUR_ANNUAL_KPI_2026-05_TEMPLATE.xlsx` (SHA-256 recorded by the read-only audit). Work is on `feat/annual-dashboard-v2`; no merge, dispatch, APSRTC request, Drive upload, Telegram send or Apps Script deployment is part of this change.

The first change improves the annual dashboard. It preserves the original KPI grid, B/C/F detail source snapshots, count-only FY totals, UD month-end history and selected UM semantics. Monthly and daily generation are unchanged. Proddutur's seven unavailable historical Engine Upto rows remain deferred.

## Value findings before styling

The reference workbook is older than the approved count-only tyre FY totals: `Tyre Statements!L22:N22` and `L32:N32` contain six percentage-total formulas. Current master already leaves these blank; no production calculation fix is needed. The review copy clears precisely those six formulas. All other original cell values, types and formulas, hidden caches, embedded source-sheet images and source-sheet print areas were verified unchanged.

The original `_ANNUAL_HISTORY` and `_META` are absent from the supplied reference. Its detailed KPI grid can be checked against dashboard values, but original HSD/Product/Engine/LUB/BD/Tyre-life source responses, cache endpoint provenance and km/HSD weights cannot be certified from this workbook. `_REPORT_DETAILS_HISTORY` is present and its depot identity and checksum validate.

The audit checks captured May B/C/F/UD/UM HTML against the saved detail matrices, every generated detail cell against its saved source snapshot, percentage arithmetic against captured numerators/denominators, count-only FY formulas and recalculated sums, blank FY percentage totals, dashboard/headline equality with original Detailed Data, and future-month blanks. The reference has **2,445 passing checks and six obsolete percentage-total failures**. The recalculated review copy has **2,430 passing checks and zero presentation/formula failures**. The smaller passing count reflects seven unavailable engine rows omitted only from the executive summary, not from Detailed Data.

Unresolved diagnostics are not presentation failures or proven parser defects:

| Diagnostic | Count | Meaning |
| --- | ---: | --- |
| Current-FY ratio outside complete rounded monthly range | 9 | Needs original same-scope monthly/cumulative responses and positive denominator weights. Screening tolerance is 0.01 for two-decimal source rounding. |
| Exact product names differ across separate endpoints | 5 | `prodkmpl_um.php` Upto versus `mednew/eng_prod_um.php` UM; equivalence is unproven. No substitution. |
| Statement C first-RC stage sum differs from reported total | 10 months | Source inconsistency preserved and documented, including May 13 versus S1–S9 sum 10. |
| Original historical Engine Upto unavailable | 7 | Owner-deferred; not aliased or filled. |

For example, May EXPRESS is 5.07 in the original KPI grid and 4.91 in the captured combined UM report. The strict original annual dimension adapter selects direct body-cell indexes 3 for monthly and 6 for Upto. The existing report-details fixtures cover the combined endpoint; `region-report.html` is a daily HSD fixture, not an original annual product/engine report. These fixtures cannot establish whether the original mismatch is a source quirk, parser issue or stale cache. Original endpoint HTML and the production annual history are required before any numerical correction. Do not treat the prompt's '21/81 violations' as a confirmed current defect count.

### Read-only production history reconciliation

On 3 October the connected Drive metadata and bounded range reads identified the production `PRODDUTUR_ANNUAL_KPI_DASHBOARD` ([spreadsheet](https://docs.google.com/spreadsheets/d/1usBGLbct9X5xjCqWt_mHLpBR4UvWqLVJY2nYg8zIi7k/edit)), last modified 30 September. `_META` confirms depot PRODDUTUR, selected May 2026 and layout version 10. Its `_ANNUAL_HISTORY` has 29 saved months; depot identity, both complete JSON chunks and SHA-256 checksum validate. There are 817 exact numeric/text agreements between the displayed detail grid and saved history, plus eight correctly displayed missing-value dashes for absent cache values. All overlapping monthly and Upto values in the owner-provided reference match the production detail grid. This confirms the EXPRESS 5.07 discrepancy is present in saved production history, rather than introduced by the visual prototype. It does not prove which original endpoint value is correct. The cache retains later months while the May view hides them, and its legacy engine repair marker is empty. No refresh, repair-marker mutation or live spreadsheet edit was performed; the deferred engine issue remains deferred.

## Bounded visual changes

- Four equal-width cards with source target, Decimal ROUND_HALF_UP difference, plain-text status and selected FY period.
- Breakdown and MED values use four decimals in unchanged APSRTC source units. TOTAL LUB stays KMPL with two decimals; higher remains better.
- Source targets alone determine performance status. No prior-full-FY/YTD grading or averaging of monthly ratios.
- Target and difference columns, restored source-target shading, short black-and-white-readable MET/BELOW statuses.
- Exact unavailable engine labels remain in Detailed Data. The dashboard summarises their count.
- Two same-unit charts through the selected month, HSD source-target series, named model anchors, aligned layout, A3 print area, preserved logo and honest missing-value notes.
- XLSX target lines are dashed; native Sheets target series are explicitly labelled but retain basic chart line styling. This renderer distinction is documented rather than claiming exact pixel parity.

The review workbook includes an offline Data Quality sheet listing unresolved diagnostics. The reusable `annual_value_audit.py` is an offline CLI, not a newly deployed runtime delivery gate. Adding a live quality tab/callback summary requires an independently reviewed integration after source discrepancies are resolved. Sparklines, prior-year same-period comparisons and a product variance chart are not part of this first change.

The preview was authored from the shared model and exported with the spreadsheet runtime. Source ZIP parts were retained to protect existing caches, formula types, print setup and images; only the owned dashboard, new review diagnostics and six obsolete percentage totals changed. LibreOffice printing was inspected; the dashboard is one A3 page. The original detail pages remain, and the quality appendix increases the full print to 19 pages. This is not a claim of a complete B/C/F page redesign or pixel-identical Excel and Sheets rendering.

## Lifecycle and validation

All **62 focused tests** pass: annual history 12, report details 24, tyre template 6, presentation 7, branding 3, dashboard/value screen 10. Annual runners v3/v7/v10/v11, annual history/visuals/value audit, report details and tyre template compile. The annual workflow now includes the new dashboard and existing branding tests. No production source test or live Sheets update was run. Ruff is unavailable in this environment; no lint pass is claimed.

A May → July → May check using the reference's actual saved detail cache and captured selected-UM fixtures showed 15 → 17 → 15 engine detail blocks and cumulative Grand Total 4.98 → 4.94 → 4.98. Only selected UM was requested because all closed B/C/F/UD months were already cached. All saved closed B/C/F/UD snapshots remained identical. Separate tests cover fetching only missing June/July groups and returning to May without erasing later history. This verifies cache/view mechanics; it does not resolve the original historical engine source issue.

Run the read-only verification against a source workbook and a disposable recalculated copy:

```bash
python annual_value_audit.py SOURCE.xlsx --depot PRODDUTUR --month 2026-05 --calculated-workbook RECALCULATED.xlsx --output audit.json
```

Zero failed checks means the implemented preservation/formula checks passed; it does not mean unresolved source diagnostics or missing provenance are cleared. Review those and approve the visual preview before any production merge. Production history has now been read and reconciled. Next data action: capture the exact original May product/engine endpoint responses; compare endpoint scope and headers with the confirmed production cache without relabelling engines. Monthly visual adaptation follows only after this annual design is approved.

Rollback the PR changes as one unit. Source contracts, caches, parser versions and Hub routing remain unchanged by this branch.

## Owner-supplied source verification and approval

After the initial audit, the owner supplied original Proddutur May 2026 Product and Engine response HTML. Extracting the actual `v4.strict_dimension_rows` function and the application's normalization/number functions from their source, then executing them against the supplied tables, reproduced all five Product and six Engine monthly CY/Upto CY pairs. All six Engine pairs also match the reference workbook. Blank LY cells in TATA - Others retain their positions and do not shift CY selection. No parser patch or numerical substitution is justified for these responses.

| Product | May CY | Upto CY |
| --- | ---: | ---: |
| EXPRESS | 4.87 | 5.07 |
| INDRA | 3.72 | 4.02 |
| PALLEVELUGU | 5.10 | 5.37 |
| SUP-LUX | 4.91 | 5.09 |
| ULTRA-DELUX | 4.99 | 5.18 |

| Engine | May CY | Upto CY |
| --- | ---: | ---: |
| AL BS-III Indra | 3.72 | 4.02 |
| AL BSVI | 4.89 | 5.07 |
| Eicher BS-III | 5.04 | 5.37 |
| TATA - Others | 4.91 | 5.52 |
| TATA BS-III | 5.09 | 5.14 |
| TATA BS-IV | 4.94 | 5.10 |

The 14 Product/Engine diagnostics now have confirmed source-value provenance for the supplied May responses. Nine monthly-range inconsistencies and five cross-endpoint differences remain source-definition questions, not proven extraction failures. This evidence does not certify denominator weights, all historical periods or equivalence between original single-dimension and combined UM reports. The ten Statement C source-arithmetic discrepancies remain retained exceptions. Audit screening counts stay 24 review and seven unverified; evidence does not erase the observations. The seven deferred legacy engine labels are absent under their exact names in this May response, so no crosswalk or alias is inferred.

On 3 October 2026 at 21:40 IST, the owner approved the annual visual change for production and requested continuing improvement toward 10/10. The production merge scope remains annual dashboard visuals and the offline audit; it does not include a new populated-Upto refresh policy, live quality-tab integration, report dispatch or Apps Script deployment.

### Follow-up visual acceptance plan

1. Apply the approved visual language to monthly and B/C/F/Engine detail sheets: readable multirow headers, consistent widths, alignment and repeated print headings.
2. Verify dynamic Product/Engine categories, long names, sparse values and changing row counts across both depots and May → July → May. Retain history while removing stale visible cells and excess print pages.
3. Add concise endpoint/period source notes and clearly distinguish source-confirmed exceptions from failed extraction checks.
4. Compare Excel, native Sheets and PDF outputs for clipping, logo proportions, chart labels and print pagination; obtain owner acceptance of representative outputs.
5. Validate values before and after each visual change. No averaging ratios, percentage FY totals or fabricated missing values. A 10/10 goal is a review target, not a claimed current result.
