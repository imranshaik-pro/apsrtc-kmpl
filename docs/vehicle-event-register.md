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

## Canonical columns — reviewed 3 October 2026

The current Python EVENT_HEADERS contract in [vehicle_events.py](../src/reporting/vehicle_events.py) is:

| Column | Purpose |
| --- | --- |
| Event ID | Stable audit/dedup key |
| Created At | Entry timestamp |
| Event Date | Actual event date |
| Depot | Depot identity |
| Vehicle No | Normalised vehicle join key |
| Event Type | Category |
| Components | Unit/aggregate change details |
| Spring Positions | Category-specific positions |
| Tyre History | Position/number history details |
| Breakdown Location | Breakdown location |
| KM Cancelled | Source event cancellation detail |
| Breakdown Details | Breakdown-specific detail |
| Remarks | Operational note |
| Entry Source | FORM / BOT / AUTOMATION_HUB or other input source |

Legacy Component / Aggregate and separate Tyre Position / Tyre No inputs are accepted as aliases during normalisation. Irrelevant fields remain blank. The schema accepts Schedule III/IV too, while the owner's normal operating rule is to retrieve schedules from APSRTC rather than duplicate them manually.

Vehicle identity is uppercased, spaces removed and an initial AP prefix stripped for joins. Events remain append-only; Vehicle 360 display filters the selected depot and report cutoff. The current open-month candidate roster considers depot events separately from display filtering; see [business rules](business-rules-and-lessons.md).

## Vehicle 360 projection

The monthly workbook Vehicle 360 projection consumes this append-only register together with the verified
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


Standalone Vehicle 360 Hub/bot lookup remains unimplemented; it is separate from the existing monthly workbook projection. See [architecture](architecture-and-flows.md) and [action plan](roadmap-and-known-issues.md).
