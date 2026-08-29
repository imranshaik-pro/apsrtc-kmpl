"""
Vehicle summary – low KMPL list (NAC only) and slab-wise operation type table.
"""

import os
import json
import logging
from decimal import Decimal
from typing import List, Dict, Any, Tuple

THRESHOLD = Decimal("5.00")
MAPPING_FILE = "vehicle_type_mapping.json"

# Slab definitions: (label, lower_bound_inclusive, upper_bound_inclusive)
SLABS = [
    ("<=5.00", Decimal("0"), Decimal("5.00")),
    ("5.01-5.10", Decimal("5.01"), Decimal("5.10")),
    ("5.11-5.20", Decimal("5.11"), Decimal("5.20")),
    ("5.21-5.30", Decimal("5.21"), Decimal("5.30")),
    (">5.30", Decimal("5.31"), Decimal("999999")),
]

# Set up logging for unknown codes
LOG_DIR = "logs"
os.makedirs(LOG_DIR, exist_ok=True)
unknown_logger = logging.getLogger('unknown_codes')
unknown_logger.setLevel(logging.INFO)
handler = logging.FileHandler(os.path.join(LOG_DIR, 'unknown_codes.log'))
handler.setFormatter(logging.Formatter('%(asctime)s - %(message)s'))
unknown_logger.addHandler(handler)

def load_type_mapping():
    base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    mapping_path = os.path.join(base_dir, MAPPING_FILE)
    if not os.path.exists(mapping_path):
        mapping_path = os.path.join(os.getcwd(), MAPPING_FILE)
    with open(mapping_path, 'r', encoding='utf-8') as f:
        return json.load(f)

def _get_vehicle_code(op_type: str) -> str:
    return op_type.strip().split()[0] if op_type.strip() else ""

def get_slab(kmpl: Decimal) -> str:
    for label, low, high in SLABS:
        if low <= kmpl <= high:
            return label
    return ">5.30"

def build_slab_operation_table(
    for_day_results: List[Dict[str, Any]],
    up_to_day_results: List[Dict[str, Any]],
    raw_records: List[Dict[str, Any]],
) -> Tuple[List[str], Dict[str, Dict[str, Dict[str, int]]], List[str]]:
    mapping = load_type_mapping()
    vehicle_type_map = {}
    unknown_vehicles = []

    for rec in raw_records:
        vehicle_no = rec.get("vehicle_no", "")
        op_type = rec.get("operation_type", "")
        code = _get_vehicle_code(op_type)
        if code in mapping:
            vehicle_type_map[vehicle_no] = code
        else:
            unknown_vehicles.append(vehicle_no)
            log_msg = f"Unknown code '{code}' for vehicle {vehicle_no} (op_type: '{op_type}')"
            unknown_logger.info(log_msg)

    op_types = sorted(set(vehicle_type_map.values()))
    counts = {slab[0]: {"for_day": {op: 0 for op in op_types}, "up_to_day": {op: 0 for op in op_types}} for slab in SLABS}
    counts["Total"] = {"for_day": {op: 0 for op in op_types}, "up_to_day": {op: 0 for op in op_types}}

    for rec in for_day_results:
        vehicle = rec["vehicle_number"]
        if vehicle not in vehicle_type_map:
            continue
        op_type = vehicle_type_map[vehicle]
        kmpl = rec.get("kmpl")
        if kmpl is None or kmpl == Decimal("0"):
            continue
        slab_label = get_slab(kmpl)
        counts[slab_label]["for_day"][op_type] += 1
        counts["Total"]["for_day"][op_type] += 1

    for rec in up_to_day_results:
        vehicle = rec["vehicle_number"]
        if vehicle not in vehicle_type_map:
            continue
        op_type = vehicle_type_map[vehicle]
        kmpl = rec.get("kmpl")
        if kmpl is None or kmpl == Decimal("0"):
            continue
        slab_label = get_slab(kmpl)
        counts[slab_label]["up_to_day"][op_type] += 1
        counts["Total"]["up_to_day"][op_type] += 1

    return op_types, counts, unknown_vehicles

def build_vehicle_summary(
    for_day_results: List[Dict[str, Any]],
    up_to_day_results: List[Dict[str, Any]],
    raw_records: List[Dict[str, Any]],
    depot: str = None,
    report_date: str = None,
) -> Dict[str, Any]:
    mapping = load_type_mapping()
    nac_vehicles = set()
    unknown_vehicles = []   # will store {"vehicle": ..., "op_type": raw}
    vehicle_type_map = {}

    for rec in raw_records:
        op_type = rec.get("operation_type", "")
        code = _get_vehicle_code(op_type)
        vehicle_no = rec.get("vehicle_no", "")
        vehicle_type_map[vehicle_no] = code

        if code in mapping:
            if mapping[code] == "NAC":
                nac_vehicles.add(vehicle_no)
        else:
            nac_vehicles.add(vehicle_no)  # treat as NAC
            # Store the raw operation type string
            unknown_vehicles.append({"vehicle": vehicle_no, "op_type": op_type})
            log_msg = f"Unknown code '{code}' for vehicle {vehicle_no} (op_type: '{op_type}')"
            if depot and report_date:
                log_msg += f" | Depot: {depot}, Date: {report_date}"
            unknown_logger.info(log_msg)

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
            op_type = vehicle_type_map.get(vehicle, "")
            low_vehicles.append({
                "vehicle": vehicle,
                "day_kmpl": day_kmpl,
                "month_kmpl": month_kmpl,
                "operation_type": op_type,
            })

    low_vehicles.sort(key=lambda x: x["day_kmpl"])
    low_vehicles = low_vehicles[:10]

    # Remove duplicates from unknown list
    seen = set()
    unique_unknown = []
    for item in unknown_vehicles:
        if item['vehicle'] not in seen:
            seen.add(item['vehicle'])
            unique_unknown.append(item)

    return {
        "low_day_vehicles": low_vehicles,
        "unknown_vehicles": unique_unknown,
    }
