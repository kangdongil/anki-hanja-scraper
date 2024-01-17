from bs4 import BeautifulSoup
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
from utils.logger import logger
from utils.selenium_driver import SeleniumDriver
from utils.hanja_tool import hanja_to_url
from utils.word_utils import filter_by_word_length


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
    except:
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
        wordhanja = candid.find_element(By.CSS_SELECTOR, ".origin a")
        if hanja in wordhanja.text:
            word_pair = {
                "hanja": wordhanja.text,
                "korean": word,
            }
            word_pairs.append(word_pair)

    if not word_pairs:
        logger.warning(f"{word} doesn't appeared. Did you mean {candid_name}?")
        return

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
    first_iteration = True

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
            if first_iteration:
                # Extract meanings for the first iteration
                meaning_objs = mean_obj.find_elements(
                    By.CSS_SELECTOR, ".mean_desc .cont"
                )
                for meaning_obj in meaning_objs:
                    meaning = ""
                    try:
                        # Check if there is word theme for the meaning
                        word_theme = meaning_obj.find_element(
                            By.CSS_SELECTOR, "span.mean_addition"
                        )
                        meaning = f"[{word_theme.text}] "
                    except NoSuchElementException:
                        pass
                    # Complete string about word meaning whether there is word_theme or not
                    meaning += meaning_obj.find_element(
                        By.CSS_SELECTOR, "span.mean"
                    ).text
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

        first_iteration = False

    return {"means": mean_list, "examples": example_list}


def scrape_word():
    """
    Scrape word data for a list of Korean words associated with a Hanja character.

    The function fetches word data from Naver dictionary for a specified Hanja character and a list of Korean words.
    """
    # Create an instance of SeleniumDriver for web scraping
    browser = SeleniumDriver()
    word_data = []

    # Specify the Hanja character and a list of Korean words
    hanja = "敎"
    word_list = ["교육", "반며교사", "갸갸", "교재", "교학상장", "설교", "포교", "반면교사"]

    # Iterate through the list of Korean words and fetch their data
    for idx, word in enumerate(word_list, 1):
        word_pairs = match_word_to_hanja(hanja, word, browser)

        if word_pairs is None:
            logger.error(f"[{idx} / {len(word_list)}] Fetch Failed: {word}")
            continue  # Skip to the next word on failure

        # Fetch word IDs and additional data for each word
        for word_pair in word_pairs:
            word_item = fetch_word_id(word_pair, browser)

            if word_item is None:
                logger.error(
                    f"[{idx} / {len(word_list)}] Word ID {word_item['word_id']} fetch failed for {word}."
                )
                continue  # Skip to the next word on failure

            word_item = {**word_item, **fetch_word_data(word_item["word_id"], browser)}
            word_data.append(word_item)

        logger.info(f"[{idx} / {len(word_list)}] {word}'s data has been fetched.")

    # Close the browser session to release resources
    browser.quit()
    logger.info("WebCrawling Finished.")
    print(word_data)


if __name__ == "__main__":
    scrape_word()
