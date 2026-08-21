def validate_calculation_result(result):
    """
    Validate one integrated calculation result.

    This validation layer checks data integrity and internal
    calculation invariants. It does not perform calculations
    and does not introduce new APSRTC business rules.

    Returns:
        True when the result is valid.

    Raises:
        ValueError when a validation rule fails.
    """

    required_fields = {
        "vehicle_number",
        "total_kms",
        "hsd",
        "kmpl",
        "rounded_kmpl",
        "slab",
    }

    missing_fields = required_fields - result.keys()

    if missing_fields:
        raise ValueError(
            f"Missing required fields: {sorted(missing_fields)}"
        )

    vehicle_number = result["vehicle_number"]
    total_kms = result["total_kms"]
    hsd = result["hsd"]
    kmpl = result["kmpl"]
    rounded_kmpl = result["rounded_kmpl"]
    slab = result["slab"]

    if not vehicle_number:
        raise ValueError("Vehicle number must not be empty.")

    if not isinstance(total_kms, (int, float)):
        raise ValueError("total_kms must be numeric.")

    if not isinstance(hsd, (int, float)):
        raise ValueError("hsd must be numeric.")

    if total_kms < 0:
        raise ValueError("total_kms must not be negative.")

    if hsd < 0:
        raise ValueError("hsd must not be negative.")

    if hsd == 0:
        if kmpl is not None:
            raise ValueError(
                "KMPL must be None when HSD is zero."
            )

        if rounded_kmpl is not None:
            raise ValueError(
                "rounded_kmpl must be None when KMPL is None."
            )

        if slab is not None:
            raise ValueError(
                "slab must be None when KMPL is None."
            )

    else:
        if kmpl is None:
            raise ValueError(
                "KMPL must not be None when HSD is non-zero."
            )

        if rounded_kmpl is None:
            raise ValueError(
                "rounded_kmpl must not be None when KMPL exists."
            )

        if slab is None:
            raise ValueError(
                "slab must not be None when KMPL exists."
            )

    return True