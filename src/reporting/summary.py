def build_slab_summary(results):
    """
    Build a structured slab summary from validated calculation results.

    This function does not recalculate KMPL, rounding, or slab classification.
    It only summarizes the already-calculated results.
    """

    slab_counts = {
        1: 0,
        2: 0,
        3: 0,
        4: 0,
        5: 0,
    }

    eligible_results = []

    for result in results:
        slab = result["slab"]

        if slab is None:
            continue

        if slab not in slab_counts:
            raise ValueError(
                f"Invalid slab value in reporting input: {slab}"
            )

        slab_counts[slab] += 1
        eligible_results.append(result)

    return {
        "total_eligible_vehicles": len(eligible_results),
        "slab_counts": slab_counts,
        "results": eligible_results,
    }
