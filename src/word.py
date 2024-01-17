from utils.logger import logger
from utils.selenium_driver import SeleniumDriver
from selenium.webdriver.common.by import By


def fetch_word_data(hanja, word, browser):
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
            word_pairs.append(
                {
                    "hanja": wordhanja.text,
                    "kor": word,
                }
            )
    if len(word_pairs) == 0:
        logger.warning(f"{word} doesn't appeared. Did you mean {candid_name}?")
        return

    return word_pairs
    # ... Search Word Pair on Korean Dictionary and scrap meaning and examples


def scrape_word():
    """
    Scrape word data for a list of Korean words associated with a Hanja character.

    The function fetches word data from Naver dictionary for a specified Hanja character and a list of Korean words.
    """
    # Create an instance of SeleniumDriver for web scraping
    browser = SeleniumDriver()
    results = []

    # Specify the Hanja character and a list of Korean words
    hanja = "敎"
    word_list = ["교육", "반며교사", "갸갸", "교재", "교학상장", "설교", "포교", "반면교사"]

    # Iterate through the list of Korean words and fetch their data
    for idx, word in enumerate(word_list, 1):
        result = fetch_word_data(hanja, word, browser)
        results.append(result)
        if result is not None:
            logger.info(f"[{idx} / {len(word_list)}] {word}'s data has been fetched.")
        else:
            logger.error(f"[{idx} / {len(word_list)}] Fetch Failed: {word}'")

    # Close the browser session to release resources
    browser.quit()
    logger.info("WebCrawling Finished.")
    print(results)


if __name__ == "__main__":
    scrape_word()
