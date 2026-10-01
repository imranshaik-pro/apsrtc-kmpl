# Annual KPI: known issues and regression pattern

Updated: 1 October 2026.

## Proddatur historical engine Upto — deferred

The observed production issue is specific to Proddatur (repository/source spelling: PRODDUTUR): historical engine rows retained in the annual workbook have missing Upto values. Rajampet (RAJAMPET) worked in the checks performed. This is an observed depot-specific pattern, not proof that every Rajampet period is unaffected.

Owner decision: retain this as a known issue and proceed with Hub integration and report presentation. Do not extend speculative fixes to other depots. Revisit if the same pattern appears elsewhere or verified source evidence becomes available.

The retained historical engine labels for which verified source Upto values remain unresolved are:

- EICHER-BS-III
- EURO-3 1512TC
- INDRA NEW
- TA-1510
- TA-BS-IV
- EICHER BS-III LATEST
- TATA BS-III NRE SPIN

These rows must not be assigned invented aliases, zeros, or another engine's values. The current evidence does not establish an old Proddatur-only parser as the cause: both depots were traced through the shared annual runner/parser path. Exact source-to-row mapping remains unresolved. Hub callback and logo repairs do not resolve this data issue.

## Annual refresh business rules to preserve

| Scenario | Required behavior |
| --- | --- |
| First run without annual depot data | Fetch the requested historical FY data and current FY months through the selected month. |
| Later run for a later month | Preserve historical FY 2024-25 and FY 2025-26 values; fill missing current FY months through the new selection; replace current Upto with the selected month's source Upto. |
| Return to an earlier month | Display current FY months only through that selection; replace Upto with that selected month's source Upto. Later cached months must not appear in the selected-period presentation. |

Regression sequences discussed and checked for available values: Proddatur April 2026 → July 2026 → May 2026; Rajampet May 2026 → July 2026 → May 2026. These checks do not close the unresolved Proddatur historical engine rows.

## Evidence required before reopening the data fix

Capture depot, selected month, FY, exact engine label, source table headers and cells, parsed value, workbook row and Upto cell. Compare equivalent source-to-workbook paths in Proddatur and an affected comparison depot before changing shared parsing or normalization. Verify historical FY values remain unchanged and selected-period display/Upto behavior still follows the rules above.

## Separate ongoing Hub work

Hub row forwarding, authenticated callback routing and annual logos over cells are tracked in PR #4. Apps Script version 6 was deployed and the Rajampet June annual logos were visually verified. Local syntax and callback authentication/row/URL/idempotency tests passed. End-to-end callback validation remains pending matching callback configuration and working signed-in access; the last verified Apps Script configuration lacked HUB_CALLBACK_TOKEN. Do not treat deployment or logo validation as proof that the Proddatur data issue is fixed.
