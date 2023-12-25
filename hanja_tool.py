import urllib.parse


class InvalidHanjaCharacterError(Exception):
    """Exception raised for invalid Hanja characters."""

    pass


def is_hanja(char):
    """Check if a charater is a valid Hanja character."""
    hanzi_ranges = [
        (0x4E00, 0x9FFF),  # Common Chinese characters
        (0x3400, 0x4DBF),  # Extension A (rarely used)
        (0x20000, 0x2A6DF),  # Extension B (rarely used)
        (0x2A700, 0x2B73F),  # Extension C (rarely used)
        (0x2B740, 0x2B81F),  # Extension D (rarely used)
        (0x2B820, 0x2CEAF),  # Extension E (rarely used)
        (0xF900, 0xFAFF),  # Compatibility Ideographs
    ]
    code_point = ord(char)
    for start, end in hanzi_ranges:
        if start <= code_point <= end:
            return True
    return False


def standardize_hanja(hanja):
    """
    Standardize a Hanja character based on a mapping file.

    :param hanja: The Hanja character to standardize.
    :type hanja: str
    :returns: The standardized Hanja character.
    :rtype: str
    """
    mapping_file = "hanja_mapping.txt"

    with open(mapping_file, "r", encoding="utf-8") as f:
        for line in f:
            standard_char, *variants = line.strip().split(":")
            if hanja in variants:
                return standard_char
    # If no mapping is found, return the original character
    return hanja


def hanja_to_url(hanja_text, length=0):
    """
    Encode a Hanja text into a URL-friendly format.

    :param str hanja_text: The Hanja text to encode.
    :param int length: Expected length of the Hanja text (optional).
    :raises InvalidHanjaCharacterError: If the input contains invalid Hanja characters or an invalid length.
    :returns: The URL-encoded Hanja text.
    :rtype: str
    """
    if length > 0 and len(hanja_text) == length:
        raise InvalidHanjaCharacterError(
            f"Invalid input length. Expected {length} characters."
        )

    for char in hanja_text:
        if not is_hanja(char):
            raise InvalidHanjaCharacterError(
                f"'{hanja_text}' is not a valid Hanja character. Please provide a valid Hanja character."
            )

    url_encoded = urllib.parse.quote(hanja_text, encoding="utf-8")
    return url_encoded
