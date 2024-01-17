from components.hanja import scrape_hanja

# List of Hanja characters to search for
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
result = scrape_hanja(hanja_str)
# You can also call the function with a list of Hanja characters as input:
# result = scrape_hanja(hanja_list)

# Print the result
print(result)
