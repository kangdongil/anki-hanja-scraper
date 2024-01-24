from utils.logger import logger
from utils.selenium_driver import SeleniumDriver
from selenium.webdriver.common.by import By
from utils.hanja_tool import is_hanja, hanja_to_url, standardize_hanja
from utils.csv import export_to_csv


def fetch_hanja_data(hanja, browser):
    """
    Retrieve Hanja information from the Naver Hanja Dictionary website.

    :param hanja: The Hanja character to search for.
    :type hanja: str
    :param browser: An instance of the SeleniumDriver class for web automation.
    :type browser: SeleniumDriver
    :returns: A tuple containing Hanja character, its unique ID, and detailed information.
    :rtype: tuple
    """

    # Step 1: Fetch Hanja data from the Naver Dictionary website
    encoded_hanja = hanja_to_url(hanja)
    url = f"https://hanja.dict.naver.com/search?query={encoded_hanja}"
    browser.get_await(url=url, locator=(By.ID, "searchPage_letter"))

    hanja_obj = browser.find_elements(By.CSS_SELECTOR, ".row")[0].find_element(
        By.CSS_SELECTOR, ".hanja_word .hanja_link"
    )

    # Step 2: Extract the Hanja ID
    if hanja_obj.text == standardize_hanja(hanja):
        hanja_id = hanja_obj.get_attribute("href").split("/")[-1]
    else:
        return {"hanja": hanja}

    # Step 3: Access the Detail Webpage with Hanja ID
    detailed_url = f"https://hanja.dict.naver.com/#/entry/ccko/{hanja_id}"
    browser.get_await(url=detailed_url, locator=(By.CLASS_NAME, "component_entry"))

    # Step 4: Save WebElements for repetitive calls
    hanja_entry = browser.find_element(By.CSS_SELECTOR, ".component_entry")
    hanja_infos = hanja_entry.find_elements(By.CSS_SELECTOR, ".entry_infos .info_item")

    # Step 5: Extract Hanja Information from web crawling
    hanja_meaning = hanja_entry.find_element(By.CSS_SELECTOR, ".entry_title .mean").text
    hanja_radical = hanja_infos[0].find_element(By.TAG_NAME, "button").text
    hanja_stroke_count = int(
        hanja_entry.find_element(
            By.CSS_SELECTOR, ".entry_infos .stroke span.word"
        ).text[:-1]
    )
    if hanja_infos[1].find_element(By.CSS_SELECTOR, ".info_item .cate").text == "모양자":
        formation_letters = (
            hanja_infos[1].find_element(By.CSS_SELECTOR, ".desc").text.split(" + ")
        )
        formation_letter = tuple(seg[0] for seg in formation_letters)
    else:
        formation_letter = None
    unicode = hanja_infos[2].find_element(By.CLASS_NAME, "desc").text
    usage = tuple(
        usage.text
        for usage in hanja_entry.find_elements(
            By.CSS_SELECTOR, ".entry_condition .unit_tooltip"
        )
    )
    # Step 6: Create a dictionary with Hanja information
    hanja_data = {
        "hanja": hanja,
        "meaning_official": hanja_meaning,
        "radical": hanja_radical,
        "stroke_count": hanja_stroke_count,
        "formation_letter": formation_letter,
        "unicode": unicode,
        "usage": usage,
        "naver_hanja_id": hanja_id,
    }

    return hanja_data


def export_hanja_csv_data(hanja_objs, filename=None):
    """
    Export hanja data to a CSV file.

    :param hanja_objs: A list of dictionaries containing hanja data.
    :type hanja_objs: list
    :return: The name of the created CSV file.
    :rtype: str
    """
    # Define Keyword
    csv_keyword = "hanja"

    # Define the CSV header
    fieldnames = [
        "hanja",
        "meaning_official",
        "radical",
        "stroke_count",
        "formation_letter",
        "unicode",
        "usage",
        "naver_hanja_id",
    ]

    # Align data with fieldnames
    csv_data = []
    for hanja_item in hanja_objs:
        csv_data.append(
            {
                "hanja": hanja_item["hanja"],
                "meaning_official": hanja_item["meaning_official"],
                "radical": hanja_item["radical"],
                "stroke_count": hanja_item["stroke_count"],
                "formation_letter": "+".join(hanja_item["formation_letter"]),
                "unicode": hanja_item["unicode"],
                "usage": "·".join(hanja_item["usage"]),
                "naver_hanja_id": hanja_item["naver_hanja_id"],
            }
        )

    if filename:
        export_to_csv(fieldnames, csv_data, csv_keyword, filename)
    else:
        filename = export_to_csv(fieldnames, csv_data, csv_keyword)
    logger.info("CSV Export Finished")

    return filename


def scrape_hanja(hanja_input=None, instant_csv=False):
    """
    Scrape Hanja data from the Naver Hanja Dictionary website.

    :param hanja_input: The Hanja characters to search for, either as a string or a list.
    :type hanja_input: str or list, optional
    :param instant_csv: If True, export the data to a CSV file instantly, else return the results.
    :type instant_csv: bool, optional
    :return: A list of Hanja data tuples or None if instant_csv is True.
    :rtype: list or None
    """

    # Create a SeleniumDriver instance with common options
    with SeleniumDriver() as browser:
        # Create an empty list to store the hanja_objs
        hanja_objs = []

        # Handle various input formats(console, str, list)
        if hanja_input is None:
            hanja_input = input("Enter Hanja characters: ")
        if isinstance(hanja_input, str):
            hanja_input = [char for char in hanja_input if is_hanja(char)]
        if isinstance(hanja_input, list):
            hanja_list = hanja_input
        else:
            raise ValueError("Invalid hanja_input format")

        # Iterate through the list of Hanja characters and fetch their data
        for idx, hanja in enumerate(hanja_list, 1):
            hanja_obj = fetch_hanja_data(hanja, browser)
            hanja_objs.append(hanja_obj)
            if hanja_obj["naver_hanja_id"] != None:
                logger.info(
                    f"[{idx} / {len(hanja_list)}] {hanja}'s data has been fetched."
                )
            else:
                logger.error(f"[{idx} / {len(hanja_list)}] Fetch Failed: {hanja}'")

        # Close the browser session to relase resources
        logger.info("WebCrawling Finished.")

    if instant_csv == True:
        return export_hanja_csv_data(hanja_objs)

    return hanja_objs


if __name__ == "__main__":
    scrape_hanja(instant_csv=True)
