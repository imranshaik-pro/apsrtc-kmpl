from copy import deepcopy
from decimal import Decimal

from src.reporting.region_formatter import format_region_kmpl_block


def build_test_data():
    return {
        "depot": "PRODDUTUR",
        "tot": {
            "target_kmpl": Decimal("5.03"),
            "day_kmpl": Decimal("4.84"),
            "up_to_day_kmpl": Decimal("4.88"),
            "last_month_kmpl": Decimal("4.88"),
            "last_year_month_kmpl": Decimal("5.09"),
        },
        "nac": {
            "target_kmpl": Decimal("5.05"),
            "day_kmpl": Decimal("4.87"),
            "up_to_day_kmpl": Decimal("4.92"),
            "last_month_kmpl": Decimal("4.91"),
            "last_year_month_kmpl": Decimal("5.11"),
        },
        "ac": {
            "target_kmpl": None,
            "day_kmpl": Decimal("3.68"),
            "up_to_day_kmpl": Decimal("3.73"),
            "last_month_kmpl": Decimal("3.79"),
            "last_year_month_kmpl": Decimal("4.11"),
        },
    }


def test_region_formatter_output_structure():
    data = build_test_data()

    output = format_region_kmpl_block(data)

    lines = output.splitlines()

    assert len(lines) == 7

    assert lines[0] == "Metric            TOT       NAC       AC"

    assert lines[1] == "────────────────────────────────────────"

    assert lines[2].startswith("Target")
    assert "5.03" in lines[2]
    assert "5.05" in lines[2]
    assert "—" in lines[2]

    assert lines[3].startswith("ఈ రోజు")
    assert "4.84" in lines[3]
    assert "4.87" in lines[3]
    assert "3.68" in lines[3]

    assert lines[4].startswith("ఈ రోజు వరకు")
    assert "4.88" in lines[4]
    assert "4.92" in lines[4]
    assert "3.73" in lines[4]

    assert lines[5].startswith("గత నెల")
    assert "4.88" in lines[5]
    assert "4.91" in lines[5]
    assert "3.79" in lines[5]

    assert lines[6].startswith("గత ఇయర్ నెల")
    assert "5.09" in lines[6]
    assert "5.11" in lines[6]
    assert "4.11" in lines[6]


def test_none_value_is_displayed_as_dash():
    data = build_test_data()

    output = format_region_kmpl_block(data)

    target_line = output.splitlines()[2]

    assert "—" in target_line


def test_category_order_is_tot_nac_ac():
    data = build_test_data()

    output = format_region_kmpl_block(data)

    header = output.splitlines()[0]

    assert header.index("TOT") < header.index("NAC")
    assert header.index("NAC") < header.index("AC")


def test_formatter_does_not_modify_input():
    data = build_test_data()
    original = deepcopy(data)

    format_region_kmpl_block(data)

    assert data == original


def test_missing_category_is_rejected():
    data = build_test_data()
    del data["ac"]

    try:
        format_region_kmpl_block(data)
        raise AssertionError("Expected ValueError for missing AC category.")
    except ValueError as exc:
        assert "missing categories" in str(exc)


def test_non_dictionary_input_is_rejected():
    try:
        format_region_kmpl_block([])
        raise AssertionError("Expected ValueError for non-dictionary input.")
    except ValueError as exc:
        assert "dictionary" in str(exc)


print("Region formatter tests passed.")
