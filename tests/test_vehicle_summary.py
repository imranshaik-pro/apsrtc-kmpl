from decimal import Decimal

from src.reporting.vehicle_summary import build_vehicle_summary


def make_result(vehicle_number, kmpl):
    return {
        "vehicle_number": vehicle_number,
        "total_kms": 100,
        "hsd": 20,
        "kmpl": kmpl,
        "rounded_kmpl": (
            Decimal(str(kmpl)).quantize(Decimal("0.01"))
            if kmpl is not None
            else None
        ),
        "slab": None,
    }


def test_low_kmpl_threshold_is_inclusive():
    for_day_results = [
        make_result("BUS001", Decimal("5.00")),
        make_result("BUS002", Decimal("4.99")),
        make_result("BUS003", Decimal("5.01")),
    ]

    up_to_day_results = []

    summary = build_vehicle_summary(
        for_day_results,
        up_to_day_results,
    )

    assert summary["low_day_vehicles_count"] == 2


def test_none_kmpl_is_not_counted():
    for_day_results = [
        make_result("BUS001", None),
        make_result("BUS002", Decimal("5.00")),
    ]

    up_to_day_results = []

    summary = build_vehicle_summary(
        for_day_results,
        up_to_day_results,
    )

    assert summary["low_day_vehicles_count"] == 1


def test_for_day_and_up_to_day_are_independent():
    for_day_results = [
        make_result("BUS001", Decimal("4.80")),
        make_result("BUS002", Decimal("5.20")),
    ]

    up_to_day_results = [
        make_result("BUS001", Decimal("5.20")),
        make_result("BUS002", Decimal("4.90")),
    ]

    summary = build_vehicle_summary(
        for_day_results,
        up_to_day_results,
    )

    assert summary["low_day_vehicles_count"] == 1
    assert summary["low_month_vehicles_count"] == 1


def test_duplicate_vehicle_is_rejected():
    for_day_results = [
        make_result("BUS001", Decimal("4.80")),
        make_result("BUS001", Decimal("4.90")),
    ]

    up_to_day_results = []

    try:
        build_vehicle_summary(
            for_day_results,
            up_to_day_results,
        )
        raise AssertionError(
            "Expected ValueError for duplicate vehicle."
        )
    except ValueError as exc:
        assert "Duplicate vehicle" in str(exc)


def test_up_to_day_duplicate_vehicle_is_rejected():
    for_day_results = []

    up_to_day_results = [
        make_result("BUS001", Decimal("4.80")),
        make_result("BUS001", Decimal("4.90")),
    ]

    try:
        build_vehicle_summary(
            for_day_results,
            up_to_day_results,
        )
        raise AssertionError(
            "Expected ValueError for duplicate vehicle."
        )
    except ValueError as exc:
        assert "Duplicate vehicle" in str(exc)


def test_none_result_group_is_rejected():
    try:
        build_vehicle_summary(None, [])
        raise AssertionError(
            "Expected ValueError for None For-Day results."
        )
    except ValueError as exc:
        assert "For-Day results cannot be None" in str(exc)

    try:
        build_vehicle_summary([], None)
        raise AssertionError(
            "Expected ValueError for None Up-To-Day results."
        )
    except ValueError as exc:
        assert "Up-To-Day results cannot be None" in str(exc)


print("Vehicle summary tests passed.")
