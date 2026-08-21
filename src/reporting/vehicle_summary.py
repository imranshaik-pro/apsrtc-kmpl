from decimal import Decimal


LOW_KMPL_THRESHOLD = Decimal("5.00")


def _count_low_kmpl_vehicles(results):
    """
    Count unique vehicles whose calculated KMPL is <= 5.00.

    This function uses the already-calculated raw KMPL value.
    It does not calculate, round, or classify KMPL.
    """

    vehicle_numbers = set()

    for result in results:
        vehicle_number = result["vehicle_number"]
        kmpl = result["kmpl"]

        if vehicle_number in vehicle_numbers:
            raise ValueError(
                f"Duplicate vehicle in reporting input: {vehicle_number}"
            )

        vehicle_numbers.add(vehicle_number)

        if kmpl is None:
            continue

    return sum(
        1
        for result in results
        if result["kmpl"] is not None
        and result["kmpl"] <= LOW_KMPL_THRESHOLD
    )


def build_vehicle_summary(for_day_results, up_to_day_results):
    """
    Build the vehicle reporting summary.

    For-Day:
        Low Day Vehicles Count
        = unique vehicles with For-Day KMPL <= 5.00

    Up-To-Day:
        Low Month Vehicles Count
        = unique vehicles with Up-To-Day KMPL <= 5.00

    The two measurement groups are processed independently.
    """

    if for_day_results is None:
        raise ValueError("For-Day results cannot be None.")

    if up_to_day_results is None:
        raise ValueError("Up-To-Day results cannot be None.")

    return {
        "low_day_vehicles_count": _count_low_kmpl_vehicles(
            for_day_results
        ),
        "low_month_vehicles_count": _count_low_kmpl_vehicles(
            up_to_day_results
        ),
    }
