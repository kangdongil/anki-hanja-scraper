from components.input import process_hanja_txt
from utils.csv import export_to_csv
from utils.hanja_tool import (
    format_num_to_hanja_rank,
    add_sup_word_index,
    add_numbering_to_list,
    create_unordered_list,
)
from functools import partial


result = process_hanja_txt(
    file_path="2401270216.txt",
    patterns=[
        "(?P<hanja>[\w]):?(?P<simplified_char>[\w])?",
        "(?P<meaning>[\w\s.;]+)",
        "(?P<rank>[\d.]+)/(?P<reference_idx>[\d]+)",
        ("(?P<words>.*)", "."),
    ],
    hanja_entry="hanja|simplified_char|meaning|meaning_official|radical|stroke_count|formation_letter|rank|unicode|tags",
    word_entry="hanja|korean|means|examples|tags",
    hanja_modifiers=[
        (format_num_to_hanja_rank, "rank"),
    ],
    words_modifiers=[
        (add_sup_word_index, "korean"),
        (add_numbering_to_list, "means"),
        (create_unordered_list, "examples"),
    ],
)

hanja_list = result[0]
word_list = result[1]

export_to_csv(list(hanja_list[0].keys()), hanja_list, "hanja", is_header=False)
export_to_csv(list(word_list[0].keys()), word_list, "word", is_header=False)
