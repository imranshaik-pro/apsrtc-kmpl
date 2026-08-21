from copy import deepcopy


def _empty_category():
    return {
        "target_kmpl": None,
        "day_kmpl": None,
        "up_to_day_kmpl": None,
        "last_month_kmpl": None,
        "last_year_month_kmpl": None,
    }


def _map_region_record(record):
    """
    Convert one Region record into the reporting representation.

    Business mapping:
        target_kmpl -> Target
        day_kmpl -> ? ????
        upd_kmpl -> ? ???? ????
        lmonth_kmpl -> ?? ???
        lyud_kmpl -> ?? ???? ???

    Original Decimal values are preserved.
    No calculation or rounding is performed.
    """

    return {
        "target_kmpl": record["target_kmpl"],
        "day_kmpl": record["day_kmpl"],
        "up_to_day_kmpl": record["upd_kmpl"],
        "last_month_kmpl": record["lmonth_kmpl"],
        "last_year_month_kmpl": record["lyud_kmpl"],
    }


def build_region_reporting_data(records):
    """
    Build the Region reporting structure for one depot.

    TOT, NAC and AC are preserved independently.

    TOT is used for the main depot KMPL metrics.
    NAC and AC are retained for their respective details.

    The input records are not modified.

    Returns:

        {
            "depot": <depot name>,

            "tot": {
                "target_kmpl": ...,
                "day_kmpl": ...,
                "up_to_day_kmpl": ...,
                "last_month_kmpl": ...,
                "last_year_month_kmpl": ...
            },

            "nac": {
                "target_kmpl": ...,
                "day_kmpl": ...,
                "up_to_day_kmpl": ...,
                "last_month_kmpl": ...,
                "last_year_month_kmpl": ...
            },

            "ac": {
                "target_kmpl": ...,
                "day_kmpl": ...,
                "up_to_day_kmpl": ...,
                "last_month_kmpl": ...,
                "last_year_month_kmpl": ...
            }
        }

    Raises ValueError for:
        - empty input
        - missing depot
        - multiple depots
        - missing TOT
        - duplicate categories
        - invalid categories
    """

    if not records:
        raise ValueError("Region reporting input is empty.")

    depot_names = {
        record.get("depot")
        for record in records
        if record.get("depot")
    }

    if not depot_names:
        raise ValueError("Region reporting input contains no depot.")

    if len(depot_names) != 1:
        raise ValueError(
            "Region reporting requires records for exactly one depot."
        )

    depot = next(iter(depot_names))

    reporting_data = {
        "depot": depot,
        "tot": _empty_category(),
        "nac": _empty_category(),
        "ac": _empty_category(),
    }

    seen_categories = set()

    for record in records:
        category = record.get("category")

        if category not in {"TOT", "NAC", "AC"}:
            raise ValueError(
                f"Invalid Region category for reporting: {category!r}"
            )

        if category in seen_categories:
            raise ValueError(
                f"Duplicate Region {category} records for depot {depot}."
            )

        seen_categories.add(category)

        reporting_data[category.lower()] = _map_region_record(record)

    if "TOT" not in seen_categories:
        raise ValueError(
            f"Region reporting requires a TOT record for depot {depot}."
        )

    return deepcopy(reporting_data)
