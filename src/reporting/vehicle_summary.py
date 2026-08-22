"""
Vehicle summary – low KMPL list for For‑Day (top 10).
"""

from decimal import Decimal
from typing import List, Dict, Any

THRESHOLD = Decimal("5.00")


def build_vehicle_summary(
    for_day_results: List[Dict[str, Any]],
    up_to_day_results: List[Dict[str, Any]],
) -> Dict[str, Any]:
    """
    Build a list of vehicles with For‑Day KMPL <= 5.00, sorted ascending,
    taking only the top 10. Each entry includes the Up‑To‑Day KMPL as well.
    """
    # Create a map from vehicle number to Up‑To‑Day KMPL
    month_map = {}
    for rec in up_to_day_results:
        vehicle = rec["vehicle_number"]
        kmpl = rec.get("kmpl")
        if kmpl is not None:
            month_map[vehicle] = kmpl

    # Collect For‑Day vehicles with KMPL <= 5.00 (ignore None, zero)
    low_vehicles = []
    for rec in for_day_results:
        day_kmpl = rec.get("kmpl")
        if day_kmpl is None or day_kmpl == Decimal("0"):
            continue
        if day_kmpl <= THRESHOLD:
            vehicle = rec["vehicle_number"]
            month_kmpl = month_map.get(vehicle)  # may be None if not present
            low_vehicles.append({
                "vehicle": vehicle,
                "day_kmpl": day_kmpl,
                "month_kmpl": month_kmpl,
            })

    # Sort ascending by day_kmpl
    low_vehicles.sort(key=lambda x: x["day_kmpl"])

    # Take only top 10
    low_vehicles = low_vehicles[:10]

    return {
        "low_day_vehicles": low_vehicles,
    }
