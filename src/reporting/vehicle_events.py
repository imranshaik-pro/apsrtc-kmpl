"""Canonical APSRTC Daily Vehicle Event Register schema and helpers.

The Google Form response sheet is the append-only source register.  This module
normalizes the same fields for GitHub validation and Vehicle 360 consumers.
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
import csv
import json
import os
from pathlib import Path
import re
from urllib.parse import urlencode
from urllib.request import urlopen
from typing import Iterable

EVENT_TYPES = ("UNIT CHANGE", "BREAKDOWN", "TYRE CHANGE", "SCHEDULE III", "SCHEDULE IV")
TYRE_POSITIONS = ("FOS", "FNS", "ROSO", "ROSI", "RNSO", "RNSI", "SPARE")

EVENT_HEADERS = (
    "Event ID", "Created At", "Event Date", "Depot", "Vehicle No", "Event Type",
    "Components", "Spring Positions", "Tyre History", "Breakdown Location",
    "KM Cancelled", "Breakdown Details", "Remarks", "Entry Source",
)

def norm_vehicle(value: str) -> str:
    """Canonical APSRTC vehicle number: uppercase, no spaces, no leading AP."""
    vehicle = re.sub(r"\s+", "", str(value or "")).upper()
    return vehicle[2:] if vehicle.startswith("AP") else vehicle

def norm_event_type(value: str) -> str:
    event = re.sub(r"\s+", " ", str(value or "").strip()).upper()
    aliases = {
        "UNIT": "UNIT CHANGE", "AGGREGATE CHANGE": "UNIT CHANGE",
        "COMPONENT CHANGE": "UNIT CHANGE", "BREAK DOWN": "BREAKDOWN",
        "TYRE": "TYRE CHANGE", "TYRES": "TYRE CHANGE",
        "TYRES CHANGE": "TYRE CHANGE", "TIRE CHANGE": "TYRE CHANGE",
        "SCHEDULE 3": "SCHEDULE III", "SCHEDULE 4": "SCHEDULE IV",
    }
    return aliases.get(event, event)

def norm_event_date(value: str) -> str:
    """Canonical event date as YYYY-MM-DD; accepts Google display formats too."""
    text = str(value or "").strip()
    if not text:
        return ""
    for fmt in ("%Y-%m-%d", "%m/%d/%Y", "%d/%m/%Y", "%m/%d/%y", "%d/%m/%y"):
        try:
            return datetime.strptime(text, fmt).strftime("%Y-%m-%d")
        except ValueError:
            pass
    raise ValueError(f"Unsupported Event Date format: {text}")

def _first(data: dict[str, str], *keys: str) -> str:
    for key in keys:
        value = data.get(key)
        if value not in (None, ""):
            return str(value).strip()
    return ""

@dataclass(frozen=True)
class VehicleEvent:
    event_id: str
    created_at: str
    event_date: str
    depot: str
    vehicle_no: str
    event_type: str
    components: str = ""
    spring_positions: str = ""
    tyre_history: str = ""
    breakdown_location: str = ""
    kms_cancelled: str = ""
    breakdown_details: str = ""
    remarks: str = ""
    entry_source: str = ""

    @property
    def component(self) -> str:
        return self.components

    @property
    def tyre_position(self) -> str:
        return ""

    @property
    def tyre_no(self) -> str:
        return self.tyre_history

    def validate(self) -> None:
        if not self.event_date:
            raise ValueError("Event Date is required")
        datetime.strptime(self.event_date, "%Y-%m-%d")
        if not self.depot:
            raise ValueError("Depot is required")
        if not self.vehicle_no:
            raise ValueError("Vehicle No is required")
        if self.event_type not in EVENT_TYPES:
            raise ValueError(f"Unsupported Event Type: {self.event_type}")
        if self.event_type == "UNIT CHANGE" and not self.components:
            raise ValueError("Components are required for Unit Change")

    def as_row(self) -> list[str]:
        self.validate()
        return [
            self.event_id, self.created_at, self.event_date, self.depot,
            self.vehicle_no, self.event_type, self.components,
            self.spring_positions, self.tyre_history, self.breakdown_location,
            self.kms_cancelled, self.breakdown_details, self.remarks,
            self.entry_source,
        ]

def make_event_id(depot: str, event_date: str, sequence: int) -> str:
    depot_codes = {"PRODDUTUR": "PDT", "KADAPA": "KDP", "BADVEL": "BDV"}
    depot_name = str(depot or "").strip().upper()
    depot_code = depot_codes.get(depot_name) or re.sub(r"[^A-Z0-9]", "", depot_name)[:3] or "EVT"
    dt = datetime.strptime(event_date, "%Y-%m-%d")
    return f"{depot_code}-{dt:%Y%m%d}-R{sequence:04d}"

def _split_pipe(value: str) -> list[str]:
    return [part.strip() for part in str(value or "").split("|") if part.strip()]

def aggregate_change_dates(events: Iterable[VehicleEvent]) -> dict[str, list[str]]:
    out: dict[str, list[str]] = {}
    for event in sorted(events, key=lambda e: (e.event_date, e.event_id)):
        if event.event_type != "UNIT CHANGE":
            continue
        for component in _split_pipe(event.components):
            dates = out.setdefault(component, [])
            if event.event_date not in dates:
                dates.append(event.event_date)
    return out

def event_from_mapping(data: dict[str, str], sequence: int = 1, source: str = "") -> VehicleEvent:
    depot = _first(data, "Depot", "depot").upper()
    event_date = norm_event_date(_first(data, "Normalized Event Date", "Event Date", "event_date"))
    event_type = norm_event_type(_first(data, "Normalized Event Type", "Event Type", "event_type"))
    vehicle = norm_vehicle(_first(data, "Normalized Vehicle No", "Vehicle No", "vehicle_no"))
    created = _first(data, "Created At", "created_at") or datetime.now().isoformat(timespec="seconds")

    components = _first(data, "Components", "components", "Component / Aggregate", "component")
    spring_positions = _first(data, "Spring Positions", "spring_positions")
    tyre_history = _first(data, "Tyre History", "tyre_history")
    if not tyre_history:
        pos = _first(data, "Tyre Position", "tyre_position")
        no = _first(data, "Tyre No", "tyre_no")
        tyre_history = ": ".join(x for x in (pos, no) if x)
    breakdown_location = _first(data, "Breakdown Location", "Break Down Location", "breakdown_location")
    kms_cancelled = _first(data, "KM Cancelled", "KMs Canceled", "kms_cancelled")

    event = VehicleEvent(
        event_id=_first(data, "Event ID", "event_id") or make_event_id(depot, event_date, sequence),
        created_at=created,
        event_date=event_date,
        depot=depot,
        vehicle_no=vehicle,
        event_type=event_type,
        components=components,
        spring_positions=spring_positions,
        tyre_history=tyre_history,
        breakdown_location=breakdown_location,
        kms_cancelled=kms_cancelled,
        breakdown_details=_first(data, "Breakdown Details", "Break Down Details", "breakdown_details"),
        remarks=_first(data, "Event Remarks", "Remarks", "remarks"),
        entry_source=_first(data, "Entry Source", "entry_source") or source,
    )
    event.validate()
    return event

def append_event_csv(path: str | Path, event: VehicleEvent) -> None:
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    new = not target.exists() or target.stat().st_size == 0
    with target.open("a", newline="", encoding="utf-8") as fh:
        writer = csv.writer(fh)
        if new:
            writer.writerow(EVENT_HEADERS)
        writer.writerow(event.as_row())

def fetch_vehicle_events_api() -> list[VehicleEvent]:
    """Read the permanent Google Sheet event register through its secured Apps Script API."""
    base_url = os.getenv("VEHICLE_EVENTS_API_URL", "").strip()
    api_key = os.getenv("VEHICLE_EVENTS_API_KEY", "").strip()
    if not base_url or not api_key:
        raise RuntimeError("VEHICLE_EVENTS_API_URL / VEHICLE_EVENTS_API_KEY are not configured")

    url = base_url + ("&" if "?" in base_url else "?") + urlencode({"key": api_key})
    with urlopen(url, timeout=30) as response:
        payload = json.loads(response.read().decode("utf-8"))
    if not payload.get("ok"):
        raise RuntimeError("Vehicle Events API failed: " + str(payload.get("error", "unknown error")))

    events = []
    for i, row in enumerate(payload.get("events", []), 1):
        events.append(event_from_mapping(row, sequence=i, source="GOOGLE_FORM"))
    return events

def read_event_csv(path: str | Path) -> list[VehicleEvent]:
    target = Path(path)
    if not target.exists():
        return []
    with target.open(newline="", encoding="utf-8-sig") as fh:
        return [event_from_mapping(row, sequence=i, source="EVENT_REGISTER_CSV")
                for i, row in enumerate(csv.DictReader(fh), 1)]
