from decimal import Decimal, ROUND_HALF_UP


def round_kmpl(kmpl):
    """
    Round KMPL to two decimal places using
    conventional decimal half-up rounding.

    Returns None when KMPL cannot be calculated.
    """

    if kmpl is None:
        return None

    value = Decimal(str(kmpl))

    return value.quantize(
        Decimal("0.01"),
        rounding=ROUND_HALF_UP,
    )