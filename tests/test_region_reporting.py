from decimal import Decimal

from src.reporting.region_summary import build_region_reporting_data


def test_proddutur_tot_nac_ac_mapping():
    records = [
        {
            "slno": 6,
            "depot": "PRODDUTUR",
            "category": "TOT",
            "target_kmpl": Decimal("5.03"),
            "day_kmpl": Decimal("4.84"),
            "upd_kmpl": Decimal("4.88"),
            "lyud_kmpl": Decimal("5.09"),
            "lmonth_kmpl": Decimal("4.88"),
        },
        {
            "slno": 6,
            "depot": "PRODDUTUR",
            "category": "NAC",
            "target_kmpl": Decimal("5.05"),
            "day_kmpl": Decimal("4.87"),
            "upd_kmpl": Decimal("4.92"),
            "lyud_kmpl": Decimal("5.11"),
            "lmonth_kmpl": Decimal("4.91"),
        },
        {
            "slno": 6,
            "depot": "PRODDUTUR",
            "category": "AC",
            "target_kmpl": None,
            "day_kmpl": Decimal("3.68"),
            "upd_kmpl": Decimal("3.73"),
            "lyud_kmpl": Decimal("4.11"),
            "lmonth_kmpl": Decimal("3.79"),
        },
    ]

    result = build_region_reporting_data(records)

    assert result["depot"] == "PRODDUTUR"

    assert result["tot"] == {
        "target_kmpl": Decimal("5.03"),
        "day_kmpl": Decimal("4.84"),
        "up_to_day_kmpl": Decimal("4.88"),
        "last_month_kmpl": Decimal("4.88"),
        "last_year_month_kmpl": Decimal("5.09"),
    }

    assert result["nac"] == {
        "target_kmpl": Decimal("5.05"),
        "day_kmpl": Decimal("4.87"),
        "up_to_day_kmpl": Decimal("4.92"),
        "last_month_kmpl": Decimal("4.91"),
        "last_year_month_kmpl": Decimal("5.11"),
    }

    assert result["ac"] == {
        "target_kmpl": None,
        "day_kmpl": Decimal("3.68"),
        "up_to_day_kmpl": Decimal("3.73"),
        "last_month_kmpl": Decimal("3.79"),
        "last_year_month_kmpl": Decimal("4.11"),
    }


def test_tot_is_the_main_report_source():
    records = [
        {
            "slno": 6,
            "depot": "PRODDUTUR",
            "category": "TOT",
            "target_kmpl": Decimal("5.03"),
            "day_kmpl": Decimal("4.84"),
            "upd_kmpl": Decimal("4.88"),
            "lyud_kmpl": Decimal("5.09"),
            "lmonth_kmpl": Decimal("4.88"),
        },
        {
            "slno": 6,
            "depot": "PRODDUTUR",
            "category": "NAC",
            "target_kmpl": Decimal("5.05"),
            "day_kmpl": Decimal("4.87"),
            "upd_kmpl": Decimal("4.92"),
            "lyud_kmpl": Decimal("5.11"),
            "lmonth_kmpl": Decimal("4.91"),
        },
        {
            "slno": 6,
            "depot": "PRODDUTUR",
            "category": "AC",
            "target_kmpl": None,
            "day_kmpl": Decimal("3.68"),
            "upd_kmpl": Decimal("3.73"),
            "lyud_kmpl": Decimal("4.11"),
            "lmonth_kmpl": Decimal("3.79"),
        },
    ]

    result = build_region_reporting_data(records)

    assert result["tot"]["target_kmpl"] == Decimal("5.03")
    assert result["tot"]["day_kmpl"] == Decimal("4.84")
    assert result["tot"]["up_to_day_kmpl"] == Decimal("4.88")


def test_tot_only_depot_is_supported():
    records = [
        {
            "slno": 2,
            "depot": "MYDUKUR",
            "category": "TOT",
            "target_kmpl": Decimal("5.22"),
            "day_kmpl": Decimal("5.23"),
            "upd_kmpl": Decimal("5.29"),
            "lyud_kmpl": Decimal("5.28"),
            "lmonth_kmpl": Decimal("5.35"),
        }
    ]

    result = build_region_reporting_data(records)

    assert result["depot"] == "MYDUKUR"

    assert result["tot"]["target_kmpl"] == Decimal("5.22")
    assert result["tot"]["day_kmpl"] == Decimal("5.23")

    assert result["nac"] == {
        "target_kmpl": None,
        "day_kmpl": None,
        "up_to_day_kmpl": None,
        "last_month_kmpl": None,
        "last_year_month_kmpl": None,
    }

    assert result["ac"] == {
        "target_kmpl": None,
        "day_kmpl": None,
        "up_to_day_kmpl": None,
        "last_month_kmpl": None,
        "last_year_month_kmpl": None,
    }


def test_missing_tot_is_rejected():
    records = [
        {
            "slno": 6,
            "depot": "PRODDUTUR",
            "category": "NAC",
            "target_kmpl": Decimal("5.05"),
            "day_kmpl": Decimal("4.87"),
            "upd_kmpl": Decimal("4.92"),
            "lyud_kmpl": Decimal("5.11"),
            "lmonth_kmpl": Decimal("4.91"),
        }
    ]

    try:
        build_region_reporting_data(records)
        raise AssertionError("Expected ValueError for missing TOT")
    except ValueError as error:
        assert str(error) == (
            "Region reporting requires a TOT record for depot PRODDUTUR."
        )


def test_duplicate_category_is_rejected():
    record = {
        "slno": 6,
        "depot": "PRODDUTUR",
        "category": "TOT",
        "target_kmpl": Decimal("5.03"),
        "day_kmpl": Decimal("4.84"),
        "upd_kmpl": Decimal("4.88"),
        "lyud_kmpl": Decimal("5.09"),
        "lmonth_kmpl": Decimal("4.88"),
    }

    try:
        build_region_reporting_data([record.copy(), record.copy()])
        raise AssertionError("Expected ValueError for duplicate TOT")
    except ValueError as error:
        assert str(error) == (
            "Duplicate Region TOT records for depot PRODDUTUR."
        )


def test_multiple_depots_are_rejected():
    records = [
        {
            "slno": 1,
            "depot": "KADAPA",
            "category": "TOT",
            "target_kmpl": Decimal("4.90"),
            "day_kmpl": Decimal("4.74"),
            "upd_kmpl": Decimal("4.69"),
            "lyud_kmpl": Decimal("4.77"),
            "lmonth_kmpl": Decimal("4.62"),
        },
        {
            "slno": 2,
            "depot": "MYDUKUR",
            "category": "TOT",
            "target_kmpl": Decimal("5.22"),
            "day_kmpl": Decimal("5.23"),
            "upd_kmpl": Decimal("5.29"),
            "lyud_kmpl": Decimal("5.28"),
            "lmonth_kmpl": Decimal("5.35"),
        },
    ]

    try:
        build_region_reporting_data(records)
        raise AssertionError("Expected ValueError for multiple depots")
    except ValueError as error:
        assert str(error) == (
            "Region reporting requires records for exactly one depot."
        )


def test_empty_input_is_rejected():
    try:
        build_region_reporting_data([])
        raise AssertionError("Expected ValueError for empty input")
    except ValueError as error:
        assert str(error) == "Region reporting input is empty."


def test_input_records_are_not_modified():
    records = [
        {
            "slno": 6,
            "depot": "PRODDUTUR",
            "category": "TOT",
            "target_kmpl": Decimal("5.03"),
            "day_kmpl": Decimal("4.84"),
            "upd_kmpl": Decimal("4.88"),
            "lyud_kmpl": Decimal("5.09"),
            "lmonth_kmpl": Decimal("4.88"),
        }
    ]

    original = [record.copy() for record in records]

    build_region_reporting_data(records)

    assert records == original


def run_tests():
    test_proddutur_tot_nac_ac_mapping()
    test_tot_is_the_main_report_source()
    test_tot_only_depot_is_supported()
    test_missing_tot_is_rejected()
    test_duplicate_category_is_rejected()
    test_multiple_depots_are_rejected()
    test_empty_input_is_rejected()
    test_input_records_are_not_modified()

    print("Region reporting tests passed.")


if __name__ == "__main__":
    run_tests()
