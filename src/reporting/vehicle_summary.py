"""
Vehicle summary – low KMPL list for For‑Day (top 10, NAC only).
Unknown vehicle types are treated as NAC and logged for review.
"""

import os
import json
import logging
from decimal import Decimal
from typing import List, Dict, Any, Set
from datetime import datetime

THRESHOLD = Decimal("5.00")
MAPPING_FILE = "vehicle_type_mapping.json"

# Set up logging for unknown codes
LOG_DIR = "logs"
os.makedirs(LOG_DIR, exist_ok=True)
unknown_logger = logging.getLogger('unknown_codes')
unknown_logger.setLevel(logging.INFO)
handler = logging.FileHandler(os.path.join(LOG_DIR, 'unknown_codes.log'))
handler.setFormatter(logging.Formatter('%(asctime)s - %(message)s'))
unknown_logger.addHandler(handler)

def load_type_mapping():
    """Load AC/NAC mapping from JSON file."""
    base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    mapping_path = os.path.join(base_dir, MAPPING_FILE)
    if not os.path.exists(mapping_path):
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
    depot: str = None,
    report_date: str = None,
) -> Dict[str, Any]:
    """
    Build a list of NAC vehicles with For‑Day KMPL <= 5.00, sorted ascending,
    taking only the top 10. Unknown vehicle types are treated as NAC and logged.
    """
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
            # Treat unknown as NAC
            nac_vehicles.add(vehicle_no)
            unknown_vehicles.append(vehicle_no)
            # Log the unknown code
            log_msg = f"Unknown code '{code}' for vehicle {vehicle_no} (op_type: '{op_type}')"
            if depot and report_date:
                log_msg += f" | Depot: {depot}, Date: {report_date}"
            unknown_logger.info(log_msg)

    # Create a map from vehicle number to Up‑To‑Day KMPL
    month_map = {}
    for rec in up_to_day_results:
        vehicle = rec["vehicle_number"]
        kmpl = rec.get("kmpl")
        if kmpl is not None:
            month_map[vehicle] = kmpl

    # Collect For‑Day NAC vehicles with KMPL <= 5.00 (ignore None, zero)
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

    # Sort ascending by day_kmpl
    low_vehicles.sort(key=lambda x: x["day_kmpl"])

    # Take only top 10
    low_vehicles = low_vehicles[:10]

    # Remove duplicates from unknown list
    unknown_vehicles = list(dict.fromkeys(unknown_vehicles))

    return {
        "low_day_vehicles": low_vehicles,
        "unknown_vehicles": unknown_vehicles,
    }
