from bs4 import BeautifulSoup
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
from utils.logger import logger
from utils.selenium_driver import SeleniumDriver
from utils.hanja_tool import is_hanja, hanja_to_url
from utils.word_utils import filter_by_word_length, is_single_word
from utils.csv import export_to_csv


def match_word_to_hanja(hanja, word, browser):
    """
    Fetch word data from Naver dictionary for a given Hanja and Korean word.

    Args:
        hanja (str): The Hanja character to search for.
        word (str): The Korean word associated with the Hanja character.
        browser (SeleniumDriver): An instance of the SeleniumDriver for web scraping.

    Returns:
        list: A list of dictionaries containing word pairs (Hanja and Korean) matching the input Hanja and word.
    """
    # Construct the URL for searching the word
    url = f"https://hanja.dict.naver.com/search?page=1&query={word}"

    # Navigate to the URL using SeleniumDriver
    browser.get_await(url=url, locator=(By.CSS_SELECTOR, "#content .section"))

    try:
        # Check if the search page entry exists
        browser.find_element(By.ID, "searchPage_entry")
    except NoSuchElementException:
        logger.warning(f"{word} doesn't exist in naver dictionary")
        return

    # Find elements representing word candidates
    word_candids = browser.find_elements(By.CSS_SELECTOR, "#searchPage_entry .row")
    word_pairs = []

    for candid in word_candids:
        # Check if the meaning matches the word
        candid_name = candid.find_element(By.CSS_SELECTOR, ".mean").text
        if candid_name != word:
            break

        # Extract Hanja and Korean word pairs
        wordhanja = candid.find_element(By.CSS_SELECTOR, ".origin a").text
        if hanja in wordhanja:
            if "(" in wordhanja:
                wordhanja = wordhanja.split("(")[0].strip()
            word_pairs.append(
                {
                    "hanja": wordhanja,
                    "korean": word,
                }
            )

    if not word_pairs:
        logger.warning(f"{word} doesn't appeared. Did you mean {candid_name}?")
        return None

    return word_pairs


def fetch_word_id(word_pair, browser):
    """
    Fetch the word ID for a given word pair from the Korean dictionary.

    Args:
        word_pair (dict): A dictionary containing Hanja and Korean word pair.
        browser (SeleniumDriver): An instance of the SeleniumDriver for web scraping.

    Returns:
        dict: A dictionary containing the updated word pair with the fetched word ID.
    """
    # Construct the URL for searching the word in the Korean dictionary
    encoded_word = hanja_to_url(word_pair["hanja"])
    url = f"https://ko.dict.naver.com/#/search?query={encoded_word}"

    # Navigate to the URL using SeleniumDriver
    browser.get_await(url=url, locator=(By.CLASS_NAME, "component_keyword"))

    try:
        # Check if the search page entry exists
        browser.find_element(By.ID, "searchPage_entry")
    except:
        logger.warning(f"{word_pair['hanja']} doesn't exist in korean dictionary.")
        return

    # Check Hanja Word match with Keyword in Korean Dictionary
    keyword = (
        browser.find_elements(By.CSS_SELECTOR, ".row")[0]
        .find_element(By.CSS_SELECTOR, ".origin a")
        .text
    )

    if keyword.split(" ")[0] != word_pair["korean"]:
        logger.warning(f"Cannot fetch {word_pair['hanja']}'s word id.")
        return

    if len(keyword.split(" ")) > 1:
        word_pair["korean"] = keyword

    # Extract the word ID from the URL
    word_id = (
        browser.find_element(By.CSS_SELECTOR, ".component_keyword .row .origin a")
        .get_attribute("href")
        .split("/")[-1]
    )
    word_pair["word_id"] = word_id

    return word_pair


def fetch_word_data(word_id, browser):
    """
    Fetch additional data (meanings and examples) for a given word ID from the Korean dictionary.

    Args:
        word_id (str): The word ID to fetch data for.
        browser (SeleniumDriver): An instance of the SeleniumDriver for web scraping.

    Returns:
        dict: A dictionary containing meanings and examples for the given word ID.
    """
    pending_ids, mean_list, example_list = [word_id], [], []
    etymon_sign = "의 어근."
    is_meaning_fetched = False

    while pending_ids:
        # Process each word ID until id list is empty
        word_id = pending_ids.pop()
        detail_url = f"https://ko.dict.naver.com/#/entry/koko/{word_id}"
        browser.get_await(url=detail_url, locator=(By.CLASS_NAME, "mean_tray"))

        try:
            # Check if there are sub-items (derived words) and add up into list
            entry_info = browser.find_element(
                By.CSS_SELECTOR, ".component_entry .entry_infos dl.entry_default"
            )
            if entry_info.find_element(By.TAG_NAME, "dt").text == "파생어":
                # Extract sub-items and add their IDs to the pending list
                sub_items = entry_info.find_elements(By.CSS_SELECTOR, "dd a")
                for item in sub_items:
                    sub_id = item.get_attribute("href").split("/")[-1]
                    if sub_id not in pending_ids:
                        pending_ids.append(sub_id)

        except NoSuchElementException:
            pass

        # Extract meanings and examples for the current word ID
        mean_objs = browser.find_elements(
            By.CSS_SELECTOR, ".mean_tray ul.mean_list li.mean_item"
        )

        for mean_obj in mean_objs:
            if not is_meaning_fetched:
                # Extract meanings for each iteration if not fetched yet
                meaning_objs = mean_obj.find_elements(
                    By.CSS_SELECTOR, ".mean_desc .cont"
                )
                for meaning_obj in meaning_objs:
                    meaning = ""

                    meaning = meaning_obj.find_element(
                        By.CSS_SELECTOR, "span.mean"
                    ).text

                    # Retry fetching meaning if etymon_sign is founded
                    if meaning.endswith(etymon_sign):
                        meaning = None
                        continue

                    try:
                        # Check if there is word theme for the meaning
                        word_theme = meaning_obj.find_element(
                            By.CSS_SELECTOR, "span.mean_addition"
                        )
                        meaning = f"[{word_theme.text}] {meaning}"
                    except NoSuchElementException:
                        pass

                    # Append the completed meaning string to the list
                    mean_list.append(meaning)

            # Extract examples for each meaning
            examples = mean_obj.find_elements(
                By.CSS_SELECTOR, ".example .example_item p.origin span.text"
            )

            for example_obj in examples:
                # Extract and clean the example text using BeautifulSoup
                example = BeautifulSoup(
                    example_obj.get_attribute("innerHTML"), "html.parser"
                ).get_text()
                # Filter examples based on word length so that minor examples could be exlucded
                example = filter_by_word_length(
                    example.strip(), min_length=3, max_length=9
                )
                if example:
                    example_list.append(example)

        if meaning:
            is_meaning_fetched = True

    return {"means": mean_list, "examples": example_list}


def export_word_csv_data(word_data, filename=None):
    """
    Export word data to a CSV file.

    :param word_data: A list of dictionaries containing word data.
    :type word_data: list
    :return: The name of the created CSV file.
    :rtype: str
    """
    # Define Keyword
    csv_keyword = "word"

    # Define the CSV header
    fieldnames = [
        "word_hanja",
        "word_korean",
        "means",
        "examples",
        "naver_word_id",
    ]

    # Align data with fieldnames
    csv_data = []
    for word_item in word_data:
        csv_data.append(
            {
                "word_hanja": word_item["hanja"],
                "word_korean": word_item["korean"],
                "means": "<br>".join(word_item["means"]),
                "examples": "<br>".join(word_item["examples"]),
                "naver_word_id": word_item["word_id"],
            }
        )

    if filename:
        export_to_csv(fieldnames, csv_data, csv_keyword, filename)
    else:
        filename = export_to_csv(fieldnames, csv_data, csv_keyword)
    logger.info("CSV Export Finished")

    return filename


def scrape_word(
    criteria_hanja,
    word_list,
    reference_idx=None,
    instant_csv=False,
    selenium_driver=None,
):
    """
    Scrape word data for a list of Korean words associated with a Hanja character.

    The function fetches word data from Naver dictionary for a specified Hanja character and a list of Korean words.

    :param criteria_hanja: The Hanja character to search for.
    :type criteria_hanja: str or None
    :param word_list: A list of Korean words associated with the Hanja character.
    :type word_list: list or None
    :param instant_csv: Flag to indicate whether to export data to CSV instantly.
    :type instant_csv: bool
    :param selenium_driver: (Optional) An instance of SeleniumDriver for web scraping.
                           If not provided, a new instance will be created and managed internally.
    :type selenium_driver: SeleniumDriver or None
    :return: The scraped word data or the name of the created CSV file.
    :rtype: list or str
    """

    # Validation for criteria_hanja and word_list
    if not is_hanja(criteria_hanja):
        raise ValueError("criteria_hanja should be a valid single Chinese character.")

    if not is_single_word(word_list):
        raise ValueError(
            f"word_list should contain valid single words without whitespace or newline characters. Found: {criteria_hanja}: {word_list}"
        )

    # Create an instance of SeleniumDriver for web scraping if not provided
    with selenium_driver or SeleniumDriver() as browser:
        logger.info(f"Scrapping {criteria_hanja}'s words:")
        word_data = []

        # Iterate through the list of Korean words and fetch their data
        for idx, word in enumerate(word_list, 1):
            word_pairs = match_word_to_hanja(criteria_hanja, word, browser)

            if word_pairs is None:
                logger.error(f"[{idx} / {len(word_list)}] Fetch Failed: {word}")
                continue  # Skip to the next word on failure

            # Fetch word IDs and additional data for each word
            for word_pair in word_pairs:
                word_item = fetch_word_id(word_pair, browser)

                if word_item is None:
                    continue  # Skip to the next word on failure

                word_item = {
                    **word_item,
                    **fetch_word_data(word_item["word_id"], browser),
                    "reference_idx": reference_idx,
                }
                word_data.append(word_item)

                logger.info(
                    f"[{idx} / {len(word_list)}] {word}({word_item['hanja']})'s data has been fetched."
                )

    logger.info("WebCrawling Finished.")

    if instant_csv == True:
        return export_word_csv_data(word_data)

    return word_data


def scrape_multiple_words(word_objs, instant_csv=False):
    """
    Scrape word data for a list of word pairs and export to CSV.

    :param word_objs: A list of tuples containing word pairs (criteria_hanja, word_list).
    :type word_objs: list
    """

    # Create an instance of SeleniumDriver for web scraping
    with SeleniumDriver() as browser:
        word_data_list = []
        csv_filename = None

        for word_obj in word_objs:
            word_data = scrape_word(
                word_obj["hanja"],
                word_obj["words"],
                word_obj["reference_idx"],
                selenium_driver=browser,
            )
            word_data_list.extend(word_data)
            if instant_csv:
                if not csv_filename:
                    csv_filename = export_word_csv_data(word_data)
                else:
                    export_word_csv_data(word_data, csv_filename)
    return word_data_list


if __name__ == "__main__":
    scrape_word()
