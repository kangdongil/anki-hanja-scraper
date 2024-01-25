import os, re
from components.hanja import scrape_hanja
from components.word import scrape_multiple_words


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


def convert_txt_to_dict(file_path, patterns, entry_dict):
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


def merge_data_into_dict(entry_dict, input_hanja, scrapped_hanja):
    result = []

    for input_data, scrapped_data in zip(input_hanja, scrapped_hanja):
        hanja = input_data["hanja"]
        merged_dict = {"hanja": hanja}

        for key in entry_dict:
            merged_dict[key] = input_data.get(key, scrapped_data.get(key, None))

        result.append(merged_dict)

    return result


def process_txt_file(file_path, patterns, entry_list):
    entry_dict = {key: None for key in entry_list.split("|")}
    input_hanja = convert_txt_to_dict(
        file_path=file_path,
        patterns=patterns,
        entry_dict=entry_dict,
    )
    # Before Scrapping, check hanja is stored in DB
    scrapped_hanja = scrape_hanja([entry["hanja"] for entry in input_hanja])
    scrapped_words = scrape_multiple_words(
        [(input_data["hanja"], input_data["words"]) for input_data in input_hanja]
    )
    hanja_data = merge_data_into_dict(
        entry_dict,
        input_hanja,
        scrapped_hanja,
    )
    return (hanja_data, scrapped_words)
