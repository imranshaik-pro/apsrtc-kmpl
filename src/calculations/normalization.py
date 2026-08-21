def normalize_for_day_record(parser_record):
    """
    Convert an APSRTC parser record into the calculation schema
    for the For-Day measurement group.
    """

    return {
        "vehicle_number": parser_record["vehicle_no"],
        "total_kms": parser_record["for_day_total_kms"],
        "hsd": parser_record["for_day_hsd"],
    }


def normalize_up_to_day_record(parser_record):
    """
    Convert an APSRTC parser record into the calculation schema
    for the Up-To-Day measurement group.
    """

    return {
        "vehicle_number": parser_record["vehicle_no"],
        "total_kms": parser_record["up_to_day_total_kms"],
        "hsd": parser_record["up_to_day_hsd"],
    }
