import os, re
from components.hanja import scrape_hanja
from components.word import scrape_multiple_words
from utils.logger import logger
from utils.anki_utils import create_anki_tags


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


def process_txt_file(file_path, patterns, delimiter="\n\n"):
    """
    Read a text file, process it using specified patterns, and extract data into dictionaries.

    Args:
        file_path (str): The path to the text file.
        patterns (list): List of patterns for extracting information.
        delimiter (str, optional): The delimiter used to split the content of the file. Defaults to "\n\n".

    Returns:
        list: List of dictionaries containing processed data.
    """
    # Check if file path is relative, if so, join it with default input directory
    if not file_path.startswith("data/input/"):
        file_path = os.path.join("data/input", file_path)

    # Read txt file in UTF-8
    with open(file_path, "r", encoding="utf-8") as file:
        content = file.read()

    # Split content into chunks based on delimiter
    chunks = content.split(delimiter)
    processed_data = []

    # Process each chunk and extract data into dictionaries using specified patterns
    for chunk in chunks:
        entry = parse_data_by_regex(chunk, patterns)
        processed_data.append(entry)

    return processed_data


def scrape_data(input_data):
    """
    Scrape additional data using the input data.

    Args:
        input_data (list): List of dictionaries containing input data.

    Returns:
        list: A list of dictionaries containing merged input data with scraped data.
    """

    ## Before Scrapping, check hanja is stored in DB

    # Scrape hanja data using input hanja entries
    scrapped_hanja = scrape_hanja([entry["hanja"] for entry in input_data])
    # Create Anki Tags

    # Merge input data with scraped hanja data
    hanja_data = merge_list_of_dicts(input_data, scrapped_hanja)

    return hanja_data


def apply_modifiers(data, modifiers):
    """
    Apply modifiers to the data before returning.

    Args:
        data (tuple): A tuple containing hanja and words data.
        modifiers (list): List of modifier functions.

    Returns:
        tuple: A tuple containing hanja and words data after applying modifiers.
    """

    # If no modifiers are provided, return the original data
    if not modifiers:
        return data

    for modifier in modifiers:
        try:
            # Check if the modifier is a tuple containing a function and a column name
            if isinstance(modifier, tuple):
                # Apply the modifier function to each entry in the data
                func, column = modifier
                for entry in data:
                    if column in entry:
                        entry[column] = func(entry[column])
            else:
                # If the modifier is not a tuple, assume it's a single function and apply it to the entire data
                data = modifier(data)
        except Exception as e:
            logger.warning(
                f"Error occurred in modifier: {modifier.__name__ if callable(modifier) else modifier}, {e}"
            )
            logger.warning(f"Error in entry: {entry}")

    return data


def merge_list_of_dicts(data1, data2):
    """
    Merge two lists of dictionaries.

    Args:
        data1 (list): The first list of dictionaries.
        data2 (list): The second list of dictionaries.

    Returns:
        list: A list containing merged dictionaries.
    """
    merged_list = []

    for entry1, entry2 in zip(data1, data2):
        merged_dict = entry1.copy()

        for key, value in entry2.items():
            if key in merged_dict:
                if isinstance(merged_dict[key], list):
                    merged_dict[key] = merged_dict[key][0]
                else:
                    merged_dict[key] = value
            else:
                merged_dict[key] = value
        merged_list.append(merged_dict)

    return merged_list


def arrange_dict_order(data, key_order):
    """
    Arrange the order of keys in dictionaries in a list.

    Args:
        data (list): The list of dictionaries to be arranged.
        key_order (list): The desired order of keys.

    Returns:
        list: A list of dictionaries with keys arranged according to key_order.
    """
    arranged_data = []

    for entry in data:
        # Create a new dictionary with keys arranged according to key_order
        new_entry = {key: entry[key] for key in key_order if key in entry}
        arranged_data.append(new_entry)

    return arranged_data


def process_hanja_txt(
    file_path,
    patterns,
    hanja_entry,
    word_entry,
    hanja_modifiers=None,
    words_modifiers=None,
):
    """
    Process a text file, extract and merge data, and apply modifiers.

    Args:
        file_path (str): The path to the text file.
        patterns (list): List of patterns for extracting information.
        hanja_entry (str): Pipe-separated list of entry keys.
        word_entry (str): Pipe-separated list of entry keys for words.
        hanja_modifiers (list, optional): List of modifier functions for hanja data.
        words_modifiers (list, optional): List of modifier functions for words data.

    Returns:
        tuple: A tuple containing processed hanja and words data.
    """

    # Initialize dictionaries for hanja and words entry keys
    hanja_entry = {key: None for key in hanja_entry.split("|")}
    word_entry = {key: None for key in word_entry.split("|")}

    # Read the text file and extract information based on patterns
    input_hanja = process_txt_file(
        file_path=file_path,
        patterns=patterns,
    )

    ## Before Scrapping, check hanja is stored in DB

    # Scraping additional data and applying modifiers for hanja data
    hanja_data = scrape_data(input_hanja)
    hanja_data = apply_modifiers(hanja_data, hanja_modifiers)
    hanja_data = create_anki_tags(
        data=hanja_data,
        tag_template="{{'{}': ['{}', {{'{}': '{}'}}]}}",
        values=("漢字", "{rank}", "暗記博士1", "{reference_idx}"),
    )

    # Scraping words data and applying modifiers
    scrapped_words = scrape_multiple_words(hanja_data)
    scrapped_words = apply_modifiers(scrapped_words, words_modifiers)
    scrapped_words = create_anki_tags(
        data=scrapped_words,
        tag_template="{{'{}': {{'{}': '{}'}}}}",
        values=("漢字語", "暗記博士1", "{reference_idx}"),
    )

    # Arrange dictionary order for hanja and words data
    hanja_data = arrange_dict_order(hanja_data, hanja_entry)
    scrapped_words = arrange_dict_order(scrapped_words, word_entry)

    return (hanja_data, scrapped_words)
