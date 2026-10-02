# Daily regression audit — 1 October 2026

## Current release status — reviewed 3 October 2026

The original audit below describes its initial test snapshot. PR #6 was merged on 2 October at 314f85d04156d0b7a48af8dcb7580cc77c4fbdf4, followed by the separate tyre PR #5. The later daily-v1.1 PR #7 merged at 54dcf6b after 157 relevant local daily checks and compilation passed. The original 13 failures are repaired; they were daily tests, not annual FY24-25 history checks. See [release history](project-history.md) and [current action plan](roadmap-and-known-issues.md).

## Original defect and regression findings

Baseline selected daily subset: 42 passed, 13 failed. Fixed subset plus new regression coverage: 70 passed; Python compilation passed. This is not certification of all repository tests.

Confirmed defects: report get_slab used closed ranges with gaps (5.005, 5.105, 5.205 incorrectly fell into >5.30). The pipeline classifier used float limits: Decimal 5.10 and 5.30 could enter the next slab. Both now share the existing upper-bound business rule using exact decimal limits. Classification uses unrounded calculated KMPL; half-up two-decimal presentation is unchanged. Each eligible source vehicle is counted exactly once in independent Day and Upto tables; table sums equal total counts.

Two old rounding assertions incorrectly compared Decimal output to floats. Expected values now use Decimal; production rounding unchanged. Report fixtures now supply vehicle details and assert the current list output rather than removed count strings. Invalid dates still raise ValueError; optional absent vehicle lists retain existing empty-list output. Vehicle-summary checks supply required raw operation records and inspect the current list contract. Duplicate and None input rejection is restored with explicit ValueError before summary generation; the normal pipeline already consolidates duplicate source measurements, so valid reports are unaffected.

The missing region_response.html dependency is replaced with a checked-in synthetic contract fixture copied from the existing application test. Its three Proddatur categories and source values are asserted; it is not labeled a live capture or an eleven-row production response.

No annual FY24–25/FY25–26 history, tyre feature, Drive integration, schedule or external delivery was changed. At this original audit stage PR #5 was separate and unmerged; its subsequent approved merge is recorded above. These changes do not rewrite existing cached reports. This original audit did not claim a live production execution; later release/source evidence is recorded separately in the project history.

