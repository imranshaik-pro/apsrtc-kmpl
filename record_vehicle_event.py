#!/usr/bin/env python3
"""Validate/normalize one Daily Vehicle Event before persistence."""
import argparse, json
from src.reporting.vehicle_events import event_from_mapping, append_event_csv

p=argparse.ArgumentParser()
p.add_argument("--payload",required=True,help="JSON object from Form/Telegram/webhook")
p.add_argument("--source",default="GITHUB")
p.add_argument("--output",default="reports/vehicle_event_register.csv")
a=p.parse_args()
data=json.loads(a.payload)
event=event_from_mapping(data,source=a.source)
append_event_csv(a.output,event)
print("VEHICLE_EVENT_ACCEPTED")
print("EVENT_ID:",event.event_id)
print("VEHICLE:",event.vehicle_no)
print("EVENT_TYPE:",event.event_type)
print("EVENT_DATE:",event.event_date)
