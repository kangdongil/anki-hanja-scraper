from selenium.webdriver.common.by import By
from utils.logger import logger
from utils.selenium_driver import SeleniumDriver
from utils.hanja_tool import hanja_to_url


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

            word_data.append(word_item)

        logger.info(f"[{idx} / {len(word_list)}] {word}'s data has been fetched.")

    # Close the browser session to release resources
    browser.quit()
    logger.info("WebCrawling Finished.")
    print(word_data)


if __name__ == "__main__":
    scrape_word()
