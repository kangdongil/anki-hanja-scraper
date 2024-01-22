def process_txt_file(file_path):
    with open(file_path, "r", encoding="utf-8") as file:
        content = file.read()

    # Split content into chunks based on double newline
    chunks = content.split("\n\n")
    processed_data = []

    # Process each chunk and extract data into dictionaries
    for chunk in chunks:
        lines = chunk.split("\n")
        hanja, meaning, *simplified_chars = lines[0].split(":")
        simplified_char = simplified_chars[0] if simplified_chars else None
        words = lines[1].split(";")
        reference_idx = lines[2]

        entry = {
            "hanja": hanja,
            "meaning": meaning,
            "simplified_char": simplified_char,
            "words": words,
            "reference_idx": reference_idx,
        }

        processed_data.append(entry)

    return processed_data


# Replace 'your_file.txt' with the path to your actual file
result = process_txt_file("data/input/2401222258.txt")
print(result)
