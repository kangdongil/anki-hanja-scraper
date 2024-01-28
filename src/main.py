from components.input import process_hanja_txt
from utils.csv import export_to_csv
from utils.hanja_tool import format_num_to_hanja_rank
from functools import partial


def lowercase_modifier(data, column):
    for entry in data:
        if column in entry:
            entry[column] = entry[column].lower()
            # if there is no column found, raise error
    return data


result = process_hanja_txt(
    file_path="2401270216.txt",
    patterns=[
        "(?P<hanja>[\w]):?(?P<simplified_char>[\w])?",
        "(?P<meaning>[\w\s.;]+)",
        "(?P<rank>[\d.]+)/(?P<reference_idx>[\w]+)",
        ("(?P<words>.*)", "."),
    ],
    entry_list="hanja|simplified_char|meaning|meaning_official|radical|stroke_count|formation_letter|rank|unicode|reference_idx",
    hanja_modifiers=[
        partial(lowercase_modifier, column="unicode"),
        (format_num_to_hanja_rank, "rank"),
    ],
    words_modifiers=[],
)


hanja_list = result[0]
word_list = result[1]

export_to_csv(list(hanja_list[0].keys()), hanja_list, "hanja", is_header=False)
export_to_csv(list(word_list[0].keys()), word_list, "word", is_header=False)
