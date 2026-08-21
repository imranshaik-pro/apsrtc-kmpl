def classify_kmpl(kmpl):
    """
    Classify KMPL into exactly one of the five
    APSRTC KMPL slabs.

    Returns None when KMPL cannot be calculated.
    """

    if kmpl is None:
        return None

    if kmpl <= 5.00:
        return 1

    if kmpl <= 5.10:
        return 2

    if kmpl <= 5.20:
        return 3

    if kmpl <= 5.30:
        return 4

    return 5