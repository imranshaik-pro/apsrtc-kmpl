"""Canonical Daily Vehicle Event Register schema and helpers.

The register is intentionally append-only. One real-world event is one row.
Google Form and Telegram can both feed this same schema later without changing
Monthly/Vehicle-360 consumers.
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
import re
from typing import Iterable\nimport csv\nfrom pathlib import Path

EVENT_TYPES = ("UNIT CHANGE", "BREAKDOWN", "TYRE CHANGE")

# Keep the first fields generic. Category-specific fields are optional so the
# schema can grow without invalidating historical rows.
EVENT_HEADERS = (
    "Event ID",
    "Created At",
    "Event Date",
    "Depot",
    "Vehicle No",
    "Event Type",
    "Component / Aggregate",
    "Tyre Position",
    "Tyre No",
    "Breakdown Details",
    "Remarks",
    "Entry Source",
)

def norm_vehicle(value: str) -> str:
    return re.sub(r"\s+", "", str(value or "")).upper()

def norm_event_type(value: str) -> str:
    event = re.sub(r"\s+", " ", str(value or "").strip()).upper()
    aliases = {
        "UNIT": "UNIT CHANGE",
        "AGGREGATE CHANGE": "UNIT CHANGE",
        "COMPONENT CHANGE": "UNIT CHANGE",
        "TYRE": "TYRE CHANGE",
        "TIRE CHANGE": "TYRE CHANGE",
    }
    return aliases.get(event, event)

@dataclass(frozen=True)
class VehicleEvent:
    event_id: str
    created_at: str
    event_date: str
    depot: str
    vehicle_no: str
    event_type: str
    component: str = ""
    tyre_position: str = ""
    tyre_no: str = ""
    breakdown_details: str = ""
    remarks: str = ""
    entry_source: str = ""

    def validate(self) -> None:
        if not self.event_date:
            raise ValueError("Event Date is required")
        if not self.depot:
            raise ValueError("Depot is required")
        if not self.vehicle_no:
            raise ValueError("Vehicle No is required")
        if self.event_type not in EVENT_TYPES:
            raise ValueError(f"Unsupported Event Type: {self.event_type}")
        if self.event_type == "UNIT CHANGE" and not self.component:
            raise ValueError("Component / Aggregate is required for Unit Change")

    def as_row(self) -> list[str]:
        self.validate()
        return [
            self.event_id, self.created_at, self.event_date, self.depot,
            self.vehicle_no, self.event_type, self.component,
            self.tyre_position, self.tyre_no, self.breakdown_details,
            self.remarks, self.entry_source,
        ]

def make_event_id(depot: str, event_date: str, sequence: int) -> str:
    """Human-readable audit id, e.g. PDT-20260919-004."""
    depot_code = re.sub(r"[^A-Z0-9]", "", depot.upper())[:3] or "EVT"
    dt = datetime.strptime(event_date, "%Y-%m-%d")
    return f"{depot_code}-{dt:%Y%m%d}-{sequence:03d}"

def aggregate_change_dates(events: Iterable[VehicleEvent]) -> dict[str, list[str]]:
    """Vehicle-360 helper: preserve every date for repeatedly changed aggregates."""
    out: dict[str, list[str]] = {}
    for event in sorted(events, key=lambda e: (e.event_date, e.event_id)):
        if event.event_type != "UNIT CHANGE" or not event.component:
            continue
        dates = out.setdefault(event.component.strip(), [])
        if event.event_date not in dates:
            dates.append(event.event_date)
    return out


def event_from_mapping(data: dict[str, str], sequence: int = 1, source: str = "") -> VehicleEvent:
    """Normalize a Form/Telegram/API payload into the canonical event model."""
    depot = str(data.get("Depot") or data.get("depot") or "").strip().upper()
    event_date = str(data.get("Event Date") or data.get("event_date") or "").strip()
    event_type = norm_event_type(data.get("Event Type") or data.get("event_type") or "")
    vehicle = norm_vehicle(data.get("Vehicle No") or data.get("vehicle_no") or "")
    created = str(data.get("Created At") or data.get("created_at") or datetime.now().isoformat(timespec="seconds"))
    event = VehicleEvent(
        event_id=str(data.get("Event ID") or data.get("event_id") or make_event_id(depot,event_date,sequence)),
        created_at=created,
        event_date=event_date,
        depot=depot,
        vehicle_no=vehicle,
        event_type=event_type,
        component=str(data.get("Component / Aggregate") or data.get("component") or "").strip(),
        tyre_position=str(data.get("Tyre Position") or data.get("tyre_position") or "").strip(),
        tyre_no=str(data.get("Tyre No") or data.get("tyre_no") or "").strip(),
        breakdown_details=str(data.get("Breakdown Details") or data.get("breakdown_details") or "").strip(),
        remarks=str(data.get("Remarks") or data.get("remarks") or "").strip(),
        entry_source=str(data.get("Entry Source") or data.get("entry_source") or source).strip(),
    )
    event.validate()
    return event


def append_event_csv(path: str | Path, event: VehicleEvent) -> None:
    """Append safely to a portable register used by tests/import-export workflows."""
    target=Path(path); target.parent.mkdir(parents=True,exist_ok=True)
    new=not target.exists() or target.stat().st_size==0
    with target.open("a",newline="",encoding="utf-8") as fh:
        writer=csv.writer(fh)
        if new: writer.writerow(EVENT_HEADERS)
        writer.writerow(event.as_row())
