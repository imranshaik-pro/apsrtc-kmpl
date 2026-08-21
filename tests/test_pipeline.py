from src.calculations.kmpl import calculate_kmpl
from src.calculations.normalization import (
    normalize_for_day_record,
    normalize_up_to_day_record,
)
from src.calculations.rounding import round_kmpl
from src.calculations.slabs import classify_kmpl
from src.calculations.consolidation import consolidate_measurements
from src.calculations.validation import validate_calculation_result


def test_kmpl_calculation():
    assert calculate_kmpl(145, 41) == 145 / 41


def test_zero_hsd():
    assert calculate_kmpl(100, 0) is None


def test_rounding():
    assert round_kmpl(4.625) == 4.63
    assert round_kmpl(5.125) == 5.13
    assert round_kmpl(4.624) == 4.62


def test_slab_boundaries():
    assert classify_kmpl(5.00) == 1
    assert classify_kmpl(5.01) == 2
    assert classify_kmpl(5.10) == 2
    assert classify_kmpl(5.11) == 3
    assert classify_kmpl(5.20) == 3
    assert classify_kmpl(5.21) == 4
    assert classify_kmpl(5.30) == 4
    assert classify_kmpl(5.31) == 5
    assert classify_kmpl(6.00) == 5


def test_duplicate_consolidation():
    records = [
        {
            "vehicle_number": "TEST001",
            "total_kms": 100,
            "hsd": 20,
        },
        {
            "vehicle_number": "TEST001",
            "total_kms": 200,
            "hsd": 50,
        },
        {
            "vehicle_number": "TEST002",
            "total_kms": 300,
            "hsd": 60,
        },
    ]

    result = consolidate_measurements(records)

    assert result == [
        {
            "vehicle_number": "TEST001",
            "total_kms": 300,
            "hsd": 70,
        },
        {
            "vehicle_number": "TEST002",
            "total_kms": 300,
            "hsd": 60,
        },
    ]


def test_zero_hsd_after_consolidation():
    records = [
        {
            "vehicle_number": "TEST002",
            "total_kms": 100,
            "hsd": 0,
        },
        {
            "vehicle_number": "TEST002",
            "total_kms": 50,
            "hsd": 0,
        },
    ]

    result = consolidate_measurements(records)

    assert result == [
        {
            "vehicle_number": "TEST002",
            "total_kms": 150,
            "hsd": 0,
        }
    ]

    assert calculate_kmpl(
        result[0]["total_kms"],
        result[0]["hsd"],
    ) is None


def test_normalization_separates_measurement_groups():
    record = {
        "vehicle_no": "04Z0070",
        "for_day_total_kms": 145.0,
        "for_day_hsd": 41.0,
        "up_to_day_total_kms": 1041.0,
        "up_to_day_hsd": 223.0,
    }

    for_day = normalize_for_day_record(record)
    up_to_day = normalize_up_to_day_record(record)

    assert for_day == {
        "vehicle_number": "04Z0070",
        "total_kms": 145.0,
        "hsd": 41.0,
    }

    assert up_to_day == {
        "vehicle_number": "04Z0070",
        "total_kms": 1041.0,
        "hsd": 223.0,
    }


def test_parser_output_can_be_normalized():
    parser_record = {
        "vehicle_no": "04Z0070",
        "for_day_total_kms": 145.0,
        "for_day_hsd": 41.0,
        "up_to_day_total_kms": 1041.0,
        "up_to_day_hsd": 223.0,
    }

    for_day = normalize_for_day_record(parser_record)
    up_to_day = normalize_up_to_day_record(parser_record)

    assert for_day["vehicle_number"] == parser_record["vehicle_no"]
    assert for_day["total_kms"] == parser_record["for_day_total_kms"]
    assert for_day["hsd"] == parser_record["for_day_hsd"]

    assert up_to_day["vehicle_number"] == parser_record["vehicle_no"]
    assert up_to_day["total_kms"] == parser_record["up_to_day_total_kms"]
    assert up_to_day["hsd"] == parser_record["up_to_day_hsd"]


def test_integrated_calculation_pipeline():
    from src.calculations.pipeline import (
        calculate_for_day,
        calculate_up_to_day,
    )

    records = [
        {
            "vehicle_no": "04Z0070",
            "for_day_total_kms": 145.0,
            "for_day_hsd": 41.0,
            "up_to_day_total_kms": 1041.0,
            "up_to_day_hsd": 223.0,
        }
    ]

    for_day = calculate_for_day(records)
    up_to_day = calculate_up_to_day(records)

    assert len(for_day) == 1
    assert len(up_to_day) == 1

    assert for_day[0]["vehicle_number"] == "04Z0070"
    assert for_day[0]["kmpl"] == 145.0 / 41.0
    assert for_day[0]["rounded_kmpl"] == 3.54
    assert for_day[0]["slab"] == 1

    assert up_to_day[0]["vehicle_number"] == "04Z0070"
    assert up_to_day[0]["kmpl"] == 1041.0 / 223.0
    assert up_to_day[0]["rounded_kmpl"] == 4.67
    assert up_to_day[0]["slab"] == 1


def test_validation_accepts_valid_result():
    result = {
        "vehicle_number": "TEST001",
        "total_kms": 100,
        "hsd": 20,
        "kmpl": 5.0,
        "rounded_kmpl": 5.0,
        "slab": 1,
    }

    assert validate_calculation_result(result) is True


def test_validation_accepts_zero_hsd_result():
    result = {
        "vehicle_number": "TEST002",
        "total_kms": 150,
        "hsd": 0,
        "kmpl": None,
        "rounded_kmpl": None,
        "slab": None,
    }

    assert validate_calculation_result(result) is True


def test_validation_rejects_negative_kms():
    result = {
        "vehicle_number": "TEST003",
        "total_kms": -100,
        "hsd": 20,
        "kmpl": -5.0,
        "rounded_kmpl": -5.0,
        "slab": 1,
    }

    try:
        validate_calculation_result(result)
        assert False, "Expected ValueError"
    except ValueError:
        pass


def test_validation_rejects_negative_hsd():
    result = {
        "vehicle_number": "TEST004",
        "total_kms": 100,
        "hsd": -20,
        "kmpl": -5.0,
        "rounded_kmpl": -5.0,
        "slab": 1,
    }

    try:
        validate_calculation_result(result)
        assert False, "Expected ValueError"
    except ValueError:
        pass


def test_validation_rejects_kmpl_when_hsd_is_zero():
    result = {
        "vehicle_number": "TEST005",
        "total_kms": 100,
        "hsd": 0,
        "kmpl": 5.0,
        "rounded_kmpl": 5.0,
        "slab": 1,
    }

    try:
        validate_calculation_result(result)
        assert False, "Expected ValueError"
    except ValueError:
        pass


def test_validation_rejects_missing_kmpl_when_hsd_exists():
    result = {
        "vehicle_number": "TEST006",
        "total_kms": 100,
        "hsd": 20,
        "kmpl": None,
        "rounded_kmpl": None,
        "slab": None,
    }

    try:
        validate_calculation_result(result)
        assert False, "Expected ValueError"
    except ValueError:
        pass


def test_validation_rejects_incorrect_kmpl():
    result = {
        "vehicle_number": "TEST007",
        "total_kms": 100,
        "hsd": 20,
        "kmpl": 4.0,
        "rounded_kmpl": 4.0,
        "slab": 1,
    }

    try:
        validate_calculation_result(result)
        assert False, "Expected ValueError"
    except ValueError:
        pass


def test_validation_rejects_invalid_slab():
    result = {
        "vehicle_number": "TEST008",
        "total_kms": 100,
        "hsd": 20,
        "kmpl": 5.0,
        "rounded_kmpl": 5.0,
        "slab": 6,
    }

    try:
        validate_calculation_result(result)
        assert False, "Expected ValueError"
    except ValueError:
        pass