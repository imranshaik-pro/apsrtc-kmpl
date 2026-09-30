"""Read-only exact legacy engine names from the existing daily adapter."""
from src.auth.client import login
from src.parser.vehicle_parser import parse_vehicle_rows
import json
s=login()
r=s.post('http://103.44.14.20/med/vehkmpl.php',data={'fyymm':'30/06/2026','dept':'PDTR/PRODDUTUR'},timeout=30)
r.raise_for_status()
rows=parse_vehicle_rows(r.text)
print('LEGACY_DAILY_ENGINE_NAMES',sorted({x['engine_type'] for x in rows}))
print('LEGACY_DAILY_COUNT',len(rows))
print('LEGACY_DAILY_SAMPLE',json.dumps(rows[:3]))
