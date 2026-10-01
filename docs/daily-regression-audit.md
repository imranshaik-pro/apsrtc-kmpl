# Daily regression audit — 1 October 2026

Baseline selected daily subset: 42 passed, 13 failed. Fixed subset plus new regression coverage: 70 passed; Python compilation passed. This is not certification of all repository tests.

Confirmed defects: report get_slab used closed ranges with gaps (5.005, 5.105, 5.205 incorrectly fell into >5.30). The pipeline classifier used float limits: Decimal 5.10 and 5.30 could enter the next slab. Both now share the existing upper-bound business rule using exact decimal limits. Classification uses unrounded calculated KMPL; half-up two-decimal presentation is unchanged. Each eligible source vehicle is counted exactly once in independent Day and Upto tables; table sums equal total counts.

Two old rounding assertions incorrectly compared Decimal output to floats. Expected values now use Decimal; production rounding unchanged. Report fixtures now supply vehicle details and assert the current list output rather than removed count strings. Invalid dates still raise ValueError; optional absent vehicle lists retain existing empty-list output. Vehicle-summary checks supply required raw operation records and inspect the current list contract. Duplicate and None input rejection is restored with explicit ValueError before summary generation; the normal pipeline already consolidates duplicate source measurements, so valid reports are unaffected.

The missing region_response.html dependency is replaced with a checked-in synthetic contract fixture copied from the existing application test. Its three Proddatur categories and source values are asserted; it is not labeled a live capture or an eleven-row production response.

No annual FY24–25/FY25–26 history, tyre feature, Drive integration, schedule or external delivery was changed. PR #5 remains separate and unmerged. These changes do not rewrite existing cached reports. Live production execution after merging is not claimed.
