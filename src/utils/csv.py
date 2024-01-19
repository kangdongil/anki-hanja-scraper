import csv
from datetime import datetime


def export_to_csv(fieldnames, data, keyword, filename=None):
    """
    Export data to a CSV file.

    :param fieldnames: A list of field names for the CSV header.
    :type fieldnames: list
    :param data: A list of dictionaries containing data to be exported to the CSV file.
    :type data: list
    :param keyword: A string representing the keyword for the CSV file name.
    :type keyword: str
    :param filename: The name of the CSV file to export. If None, a timestamped name with the keyword will be generated.
                     If provided, it should have the .csv extension.
    :type filename: str or None
    :return: The name of the created CSV file.
    :rtype: str
    """
    # Input validation for fieldnames and data
    if not isinstance(fieldnames, list) or not all(
        isinstance(field, str) for field in fieldnames
    ):
        raise ValueError("fieldnames should be a list of strings")

    if not isinstance(data, list) or not all(isinstance(row, dict) for row in data):
        raise ValueError("data should be a list of dictionaries")

    # Ensure keys in data dictionaries match the fieldnames
    if not all(set(fieldnames) == set(row.keys()) for row in data):
        raise ValueError("Keys in data dictionaries must match the fieldnames")

    # Generate timestamp for unique file name if filename is None
    if filename is None:
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        output_name = f"{keyword}_csv_{timestamp}.csv"
    else:
        # If filename is provided, use it and adjust file_mode to "a"
        if "/" in filename:
            raise ValueError("File name should not contain a path.")

        # Ensure the file has a .csv extension
        if not filename.endswith(".csv"):
            filename += ".csv"

        if filename.split(".")[-1] != "csv":
            raise ValueError("The provided file name must have the .csv extension.")

        output_name = filename

    # Write data to CSV file
    file_mode = "w" if filename is None else "a"
    with open(
        f"data/output/{output_name}", file_mode, newline="", encoding="utf-8"
    ) as csvfile:
        csvwriter = csv.DictWriter(csvfile, fieldnames=fieldnames)

        # Write header only if the file is newly created
        if file_mode == "w":
            csvwriter.writeheader()

        for row in data:
            csvwriter.writerow(row)

    return output_name
