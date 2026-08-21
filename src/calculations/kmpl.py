def calculate_kmpl(total_kms, hsd):
    """
    Calculate KMPL from total kilometres and HSD consumption.

    KMPL = Total Kms / HSD

    Returns None when HSD is zero because KMPL
    cannot be calculated.
    """

    if hsd == 0:
        return None

    return total_kms / hsd