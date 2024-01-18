from components.hanja import scrape_hanja
from components.word import scrape_word

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

# Example usage of scrape_word function
criteria_hanja = "敎"
word_list = ["교육", "반며교사", "갸갸", "교재", "교학상장", "설교", "포교", "반면교사"]

# Call the scrape_word function with a Hanja character and a list of words as input
result = scrape_word(criteria_hanja, word_list)
print(result)
