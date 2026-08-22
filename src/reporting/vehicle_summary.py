"""
Vehicle summary – low KMPL list for For‑Day (top 10, NAC only).
Unknown vehicle types are flagged for review.
"""

from decimal import Decimal
from typing import List, Dict, Any, Set

THRESHOLD = Decimal("5.00")

# Define known vehicle types (use first token of operation_type)
NAC_CODES = {"EX", "OR", "IH", "UD", "HT", "IU"}  # Non‑AC
AC_CODES = {"MB", "IB", "IR"}                     # AC – exclude


def _get_vehicle_code(op_type: str) -> str:
    """Extract the first token from operation_type."""
    return op_type.strip().split()[0] if op_type.strip() else ""


def build_vehicle_summary(
    for_day_results: List[Dict[str, Any]],
    up_to_day_results: List[Dict[str, Any]],
    raw_records: List[Dict[str, Any]],
) -> Dict[str, Any]:
    """
    Build a list of NAC vehicles with For‑Day KMPL <= 5.00, sorted ascending,
    taking only the top 10. Unknown vehicle types are flagged.
    """
    nac_vehicles = set()
    unknown_vehicles = []

    for rec in raw_records:
        op_type = rec.get("operation_type", "")
        code = _get_vehicle_code(op_type)
        vehicle_no = rec.get("vehicle_no", "")

        if code in AC_CODES:
            continue  # Explicitly exclude AC
        elif code in NAC_CODES:
            nac_vehicles.add(vehicle_no)
        else:
            # Unknown type – flag it for review
            unknown_vehicles.append(vehicle_no)

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
