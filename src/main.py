from components.input import process_hanja_txt
from utils.csv import export_to_csv


def lowercase_unicode_modifier(data):
    for entry in data:
        if "unicode" in entry:
            entry["unicode"] = entry["unicode"].lower()
    return data


result = process_hanja_txt(
    file_path="2401270216.txt",
    patterns=[
        "(?P<hanja>[\w]):?(?P<simplified_char>[\w])?",
        "(?P<meaning>[\w\s.;]+)",
        "(?P<grade>[\w]+)/(?P<reference_idx>[\w]+)",
        ("(?P<words>.*)", "."),
    ],
    entry_list="hanja|simplified_char|meaning|meaning_official|radical|stroke_count|formation_letter|grade|unicode|reference_idx",
    hanja_modifiers=[lowercase_unicode_modifier],
    words_modifiers=[],
)


hanja_list = result[0]
word_list = result[1]

export_to_csv(list(hanja_list[0].keys()), hanja_list, "hanja", is_header=False)
export_to_csv(list(word_list[0].keys()), word_list, "word", is_header=False)
