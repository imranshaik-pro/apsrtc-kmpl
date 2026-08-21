from src.reporting.summary import build_slab_summary


def test_single_vehicle_slab_1():
    results = [
        {
            "vehicle_number": "TEST001",
            "total_kms": 145,
            "hsd": 41,
            "kmpl": 3.5365853658536586,
            "rounded_kmpl": 3.54,
            "slab": 1,
        }
    ]

    summary = build_slab_summary(results)

    assert summary["total_eligible_vehicles"] == 1
    assert summary["slab_counts"] == {
        1: 1,
        2: 0,
        3: 0,
        4: 0,
        5: 0,
    }


def test_vehicles_distributed_across_all_slabs():
    results = [
        {
            "vehicle_number": "TEST001",
            "total_kms": 100,
            "hsd": 20,
            "kmpl": 5.0,
            "rounded_kmpl": 5.00,
            "slab": 1,
        },
        {
            "vehicle_number": "TEST002",
            "total_kms": 102,
            "hsd": 20,
            "kmpl": 5.1,
            "rounded_kmpl": 5.10,
            "slab": 2,
        },
        {
            "vehicle_number": "TEST003",
            "total_kms": 104,
            "hsd": 20,
            "kmpl": 5.2,
            "rounded_kmpl": 5.20,
            "slab": 3,
        },
        {
            "vehicle_number": "TEST004",
            "total_kms": 106,
            "hsd": 20,
            "kmpl": 5.3,
            "rounded_kmpl": 5.30,
            "slab": 4,
        },
        {
            "vehicle_number": "TEST005",
            "total_kms": 120,
            "hsd": 20,
            "kmpl": 6.0,
            "rounded_kmpl": 6.00,
            "slab": 5,
        },
    ]

    summary = build_slab_summary(results)

    assert summary["total_eligible_vehicles"] == 5
    assert summary["slab_counts"] == {
        1: 1,
        2: 1,
        3: 1,
        4: 1,
        5: 1,
    }


def test_none_slab_records_are_excluded():
    results = [
        {
            "vehicle_number": "TEST001",
            "total_kms": 100,
            "hsd": 0,
            "kmpl": None,
            "rounded_kmpl": None,
            "slab": None,
        },
        {
            "vehicle_number": "TEST002",
            "total_kms": 100,
            "hsd": 20,
            "kmpl": 5.0,
            "rounded_kmpl": 5.00,
            "slab": 1,
        },
    ]

    summary = build_slab_summary(results)

    assert summary["total_eligible_vehicles"] == 1
    assert summary["slab_counts"] == {
        1: 1,
        2: 0,
        3: 0,
        4: 0,
        5: 0,
    }


def test_invalid_slab_is_rejected():
    results = [
        {
            "vehicle_number": "TEST001",
            "total_kms": 100,
            "hsd": 20,
            "kmpl": 5.0,
            "rounded_kmpl": 5.00,
            "slab": 6,
        }
    ]

    try:
        build_slab_summary(results)
        raise AssertionError("Expected ValueError for invalid slab")
    except ValueError as error:
        assert str(error) == "Invalid slab value in reporting input: 6"


def test_original_calculation_values_are_preserved():
    results = [
        {
            "vehicle_number": "TEST001",
            "total_kms": 145,
            "hsd": 41,
            "kmpl": 3.5365853658536586,
            "rounded_kmpl": 3.54,
            "slab": 1,
        }
    ]

    summary = build_slab_summary(results)

    reported_result = summary["results"][0]

    assert reported_result["vehicle_number"] == "TEST001"
    assert reported_result["total_kms"] == 145
    assert reported_result["hsd"] == 41
    assert reported_result["kmpl"] == 3.5365853658536586
    assert reported_result["rounded_kmpl"] == 3.54
    assert reported_result["slab"] == 1


def run_tests():
    test_single_vehicle_slab_1()
    test_vehicles_distributed_across_all_slabs()
    test_none_slab_records_are_excluded()
    test_invalid_slab_is_rejected()
    test_original_calculation_values_are_preserved()

    print("Reporting tests passed.")


if __name__ == "__main__":
    run_tests()