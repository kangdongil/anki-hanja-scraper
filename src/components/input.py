import re


def parse_data_by_regex(data, patterns):
    result = {}
    lines = data.strip().split("\n")

    for i, pattern in enumerate(patterns):
        if isinstance(pattern, str):
            match = re.match(pattern, lines[i])
            if match:
                result.update(match.groupdict())
        elif isinstance(pattern, tuple):
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


# Replace 'your_file.txt' with the path to your actual file
patterns = [
    "(?P<hanja>[\w]):(?P<meaning>[\w\s.;]+):?(?P<simplified_char>[\w])?",
    ("(?P<words>.*)", ";"),
    "(?P<reference_idx>[\w]+)",
]

output = process_txt_file("data/input/2401222258.txt", patterns)

print(output)
