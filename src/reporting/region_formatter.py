from decimal import Decimal


METRIC_LABELS = (
    ("Target", "target_kmpl"),
    ("ఈ రోజు", "day_kmpl"),
    ("ఈ రోజు వరకు", "up_to_day_kmpl"),
    ("గత నెల", "last_month_kmpl"),
    ("గత ఇయర్ నెల", "last_year_month_kmpl"),
)

CATEGORY_HEADERS = ("TOT", "NAC", "AC")

METRIC_COLUMN_WIDTH = 18
VALUE_COLUMN_WIDTH = 10


def _format_value(value):
    """
    Format one Region KMPL value for presentation.

    Existing Decimal values are preserved.
    None is displayed as an em dash.
    No calculation or rounding is performed.
    """
    if value is None:
        return "—"

    if isinstance(value, Decimal):
        return format(value, "f")

    return str(value)


def _pad_right(value, width):
    """
    Right-pad a value to the requested column width.
    """
    return value + (" " * max(0, width - len(value)))


def _build_separator(total_width):
    """
    Build the horizontal separator for the aligned table.
    """
    return "─" * total_width


def format_region_kmpl_block(reporting_data):
    """
    Build the aligned TOT/NAC/AC Region KMPL block.

    The formatter does not:
        - calculate KMPL
        - round KMPL
        - modify KMPL values
        - classify slabs
        - change reporting data
    """

    if not isinstance(reporting_data, dict):
        raise ValueError("Region reporting data must be a dictionary.")

    required_categories = {"tot", "nac", "ac"}
    missing_categories = required_categories - reporting_data.keys()

    if missing_categories:
        raise ValueError(
            f"Region reporting data is missing categories: "
            f"{sorted(missing_categories)}"
        )

    header = (
        _pad_right("Metric", METRIC_COLUMN_WIDTH)
        + _pad_right("TOT", VALUE_COLUMN_WIDTH)
        + _pad_right("NAC", VALUE_COLUMN_WIDTH)
        + _pad_right("AC", VALUE_COLUMN_WIDTH)
    ).rstrip()

    total_width = len(header)

    lines = [
        header,
        _build_separator(total_width),
    ]

    for label, field_name in METRIC_LABELS:
        row = (
            _pad_right(label, METRIC_COLUMN_WIDTH)
            + _pad_right(
                _format_value(reporting_data["tot"].get(field_name)),
                VALUE_COLUMN_WIDTH,
            )
            + _pad_right(
                _format_value(reporting_data["nac"].get(field_name)),
                VALUE_COLUMN_WIDTH,
            )
            + _pad_right(
                _format_value(reporting_data["ac"].get(field_name)),
                VALUE_COLUMN_WIDTH,
            )
        ).rstrip()

        lines.append(row)

    return "\n".join(lines)
