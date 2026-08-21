from src.calculations.consolidation import consolidate_measurements
from src.calculations.kmpl import calculate_kmpl
from src.calculations.normalization import (
    normalize_for_day_record,
    normalize_up_to_day_record,
)
from src.calculations.rounding import round_kmpl
from src.calculations.slabs import classify_kmpl


def calculate_measurement_group(records, normalizer):
    """
    Normalize, consolidate, calculate KMPL, classify slab,
    and prepare presentation values for one measurement group.
    """

    normalized = [
        normalizer(record)
        for record in records
    ]

    consolidated = consolidate_measurements(normalized)

    results = []

    for record in consolidated:
        kmpl = calculate_kmpl(
            record["total_kms"],
            record["hsd"],
        )

        results.append({
            "vehicle_number": record["vehicle_number"],
            "total_kms": record["total_kms"],
            "hsd": record["hsd"],
            "kmpl": kmpl,
            "rounded_kmpl": round_kmpl(kmpl) if kmpl is not None else None,
            "slab": classify_kmpl(kmpl),
        })

    return results


def calculate_for_day(records):
    """
    Process the For-Day measurement group.
    """

    return calculate_measurement_group(
        records,
        normalize_for_day_record,
    )


def calculate_up_to_day(records):
    """
    Process the Up-To-Day measurement group.
    """

    return calculate_measurement_group(
        records,
        normalize_up_to_day_record,
    )
