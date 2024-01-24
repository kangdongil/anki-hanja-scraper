import sys
from components.hanja import scrape_hanja
from components.word import scrape_word, scrape_multiple_words
from components.input import process_txt_file

input_data = process_txt_file(
    file_path="2401222259.txt",
    patterns=[
        "(?P<hanja>[\w]):(?P<meaning>[\w\s.;]+):?(?P<simplified_char>[\w])?",
        ("(?P<words>.*)", ";"),
        "(?P<reference_idx>[\w]+)",
    ],
)
scrapped_data = scrape_hanja([entry["hanja"] for entry in input_data])
print("input_data", input_data)
print("scrapped_data", scrapped_data)


def merge_hanja_data(input_data, scrapped_data):
    item_order = [
        "hanja",
        "simplified_char",
        "meaning",
        "meaning_official",
        "radical",
        "stroke_count",
        "formation_letter",
        "unicode",
        "usage",
        "words",
        "reference_idx",
        "naver_hanja_id",
    ]

    merged_list = []

    for input_dict, scrapped_dict in zip(input_data, scrapped_data):
        merged_dict = {key: input_dict.get(key, None) for key in item_order}
        merged_dict.update(scrapped_dict)
        merged_list.append(merged_dict)

    return merged_list


print(merge_hanja_data(input_data, scrapped_data))

sys.exit()

""" 
# Example usage of scrape_multiple_words function
search_list = [
    ("敎", ["교육", "반며교사", "갸갸", "교재", "교학상장", "설교", "포교", "반면교사"]),
    ("輝", ["휘황찬란"]),
    ("農", ["농부", "농번기", "농촌", "도농"]),
    ("答", ["답변", "응답", "답례", "보답"]),
    ("多", ["다독", "다수결", "다다익선"]),
]

# Call the scrape_multiple_words function with a list of word objs as input
scrape_multiple_words(search_list)
 """
