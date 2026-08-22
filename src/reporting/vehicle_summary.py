"""
Vehicle summary – low KMPL list for For‑Day (top 10, NAC only).
Vehicle type mapping is read from vehicle_type_mapping.json.
"""

import json
import os
from decimal import Decimal
from typing import List, Dict, Any

THRESHOLD = Decimal("5.00")
MAPPING_FILE = "vehicle_type_mapping.json"

def load_type_mapping():
    """Load AC/NAC mapping from JSON file."""
    # Try to find the mapping file relative to this script
    base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    mapping_path = os.path.join(base_dir, MAPPING_FILE)
    if not os.path.exists(mapping_path):
        # fallback: try current directory
        mapping_path = os.path.join(os.getcwd(), MAPPING_FILE)
    with open(mapping_path, 'r', encoding='utf-8') as f:
        return json.load(f)

def _get_vehicle_code(op_type: str) -> str:
    """Extract the first token from operation_type."""
    return op_type.strip().split()[0] if op_type.strip() else ""

def build_vehicle_summary(
    for_day_results: List[Dict[str, Any]],
    up_to_day_results: List[Dict[str, Any]],
    raw_records: List[Dict[str, Any]],
) -> Dict[str, Any]:
    mapping = load_type_mapping()
    nac_vehicles = set()
    unknown_vehicles = []

    for rec in raw_records:
        op_type = rec.get("operation_type", "")
        code = _get_vehicle_code(op_type)
        vehicle_no = rec.get("vehicle_no", "")

        if code in mapping:
            if mapping[code] == "NAC":
                nac_vehicles.add(vehicle_no)
            # else AC – skip
        else:
            unknown_vehicles.append(vehicle_no)

    month_map = {}
    for rec in up_to_day_results:
        vehicle = rec["vehicle_number"]
        kmpl = rec.get("kmpl")
        if kmpl is not None:
            month_map[vehicle] = kmpl

    low_vehicles = []
    for rec in for_day_results:
        vehicle = rec["vehicle_number"]
        if vehicle not in nac_vehicles:
            continue

        day_kmpl = rec.get("kmpl")
        if day_kmpl is None or day_kmpl == Decimal("0"):
            continue
        if day_kmpl <= THRESHOLD:
            month_kmpl = month_map.get(vehicle)
            low_vehicles.append({
                "vehicle": vehicle,
                "day_kmpl": day_kmpl,
                "month_kmpl": month_kmpl,
            })

    low_vehicles.sort(key=lambda x: x["day_kmpl"])
    low_vehicles = low_vehicles[:10]
    unknown_vehicles = list(dict.fromkeys(unknown_vehicles))

    return {
        "low_day_vehicles": low_vehicles,
        "unknown_vehicles": unknown_vehicles,
    }
