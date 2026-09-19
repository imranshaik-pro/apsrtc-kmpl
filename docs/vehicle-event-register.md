# Daily Vehicle Event Register

This register is the canonical manual-event source for Vehicle 360 history.

## Principle

One real event = one row. Never overwrite an earlier event to record a later
change. Repeated aggregate changes therefore remain auditable and Vehicle 360
can display all change dates in the same aggregate cell.

## Initial event categories

- UNIT CHANGE
- BREAKDOWN
- TYRE CHANGE

Schedule-III / Schedule-IV are not manually duplicated here because the Monthly
automation already retrieves them from the APSRTC source after the applicable
month is available.

## Canonical columns

| Column | Purpose |
|---|---|
| Event ID | Stable audit/dedup key |
| Created At | Entry timestamp |
| Event Date | Actual event date |
| Depot | Depot identity |
| Vehicle No | Vehicle identity / join key |
| Event Type | Unit Change, Breakdown or Tyre Change |
| Component / Aggregate | Major component for Unit Change; optional otherwise |
| Tyre Position | Tyre-specific detail when available |
| Tyre No | Tyre-specific detail when available |
| Breakdown Details | Breakdown-specific detail |
| Remarks | Free operational note |
| Entry Source | FORM / BOT / other future source |

The optional category-specific fields deliberately stay blank when not relevant.

## Vehicle 360 projection

Vehicle 360 will consume this append-only register together with the verified
APSRTC sources:

- KMPL + current roster + commission information: APSRTC source
- Schedule-III / Schedule-IV: APSRTC source
- Unit/Aggregate changes: Event Register
- Breakdowns: Event Register
- Tyre changes: Event Register

For major aggregates, repeated changes are rendered in one component cell as a
chronological list of dates. Tyres remain chronological transactions because
their change frequency is much higher.

## Input channels

Google Form and Telegram are front ends only. Both must validate and write the
same canonical schema. The Monthly/Vehicle-360 logic must never depend on which
front end created the event.

The Telegram listener/webhook and live Google Sheet connection are intentionally
separate deployment steps; no bot or Google credential belongs in this file or
in source control.
