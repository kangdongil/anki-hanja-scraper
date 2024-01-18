from components.hanja import scrape_hanja
from components.word import scrape_word, scrape_multiple_words

""" # List of Hanja characters to search for
hanja_list = [
    "校",
    "六",
    "萬",
    "母",
    "木",
    "門",
    "民",
]

# Hanja characters as a string
hanja_str = "天地玄黃"

# Call the scrape_hanja function with a Hanja string as input
result = scrape_hanja(hanja_str) """

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
