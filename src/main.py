from components.input import process_txt_file

result = process_txt_file(
    file_path="2401222259.txt",
    patterns=[
        "(?P<hanja>[\w]):(?P<meaning>[\w\s.;]+):?(?P<simplified_char>[\w])?",
        ("(?P<words>.*)", ";"),
        "(?P<reference_idx>[\w]+)",
    ],
    entry_list="hanja|simplified_char|meaning|meaning_official|radical|stroke_count|formation_letter|unicode|usage|reference_idx|naver_hanja_id",
)

print(result)
