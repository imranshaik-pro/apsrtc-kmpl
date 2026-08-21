def consolidate_measurements(records):
    """
    Consolidate vehicle measurement records by vehicle number.

    Total Kms and HSD are summed across records belonging
    to the same vehicle.
    """

    consolidated = {}

    for record in records:
        vehicle_number = record["vehicle_number"]

        if vehicle_number not in consolidated:
            consolidated[vehicle_number] = {
                "vehicle_number": vehicle_number,
                "total_kms": 0,
                "hsd": 0,
            }

        consolidated[vehicle_number]["total_kms"] += record["total_kms"]
        consolidated[vehicle_number]["hsd"] += record["hsd"]

    return list(consolidated.values())