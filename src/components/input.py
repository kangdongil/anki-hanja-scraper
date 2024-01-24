import os, re


def parse_data_by_regex(data, patterns):
    """
    Parse data using regular expressions based on given patterns.

    Args:
        data (str): The input data to be parsed.
        patterns (list): List of patterns for extracting information.

    Returns:
        dict: A dictionary containing extracted information.

    Raises:
        ValueError: If an invalid pattern or datatype is encountered.
    """
    result = {}
    lines = data.strip().split("\n")

    for i, pattern in enumerate(patterns):
        # Handle single string pattern
        if isinstance(pattern, str):
            match = re.match(pattern, lines[i])
            if match:
                result.update(match.groupdict())
        elif isinstance(pattern, tuple):
            # Handle tuple pattern with regex, delimiter
            regex, delimiter, *rest = pattern
            if rest:
                raise ValueError(
                    f"Invalid number of elements in tuple pattern at index {i}. Expected 2, got {len(pattern)}"
                )
            match = re.match(regex, lines[i])
            if match:
                result.update(match.groupdict())
                key = list(match.groupdict().keys())[0]
                if key in result:
                    result[key] = result[key].split(delimiter)
        else:
            raise ValueError(f"Invalid datatype for pattern at index {i}")

    return result


def process_txt_file(file_path, patterns):
    """
    Process a text file using specified patterns and extract data into dictionaries.

    Args:
        file_path (str): The path to the text file.
        patterns (list): List of patterns for extracting information.

    Returns:
        list: List of dictionaries containing processed data.
    """
    if not file_path.startswith("data/input/"):
        file_path = os.path.join("data/input", file_path)

    with open(file_path, "r", encoding="utf-8") as file:
        content = file.read()

    # Split content into chunks based on double newline
    chunks = content.split("\n\n")
    processed_data = []

    # Process each chunk and extract data into dictionaries
    for chunk in chunks:
        entry = parse_data_by_regex(chunk, patterns)
        processed_data.append(entry)

    return processed_data
