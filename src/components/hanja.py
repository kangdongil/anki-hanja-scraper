import csv
from datetime import datetime
from utils.logger import logger
from utils.selenium_driver import SeleniumDriver
from selenium.webdriver.common.by import By
from utils.hanja_tool import is_hanja, hanja_to_url, standardize_hanja


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
        return (hanja, None, None)

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
    hanja_info = {
        "Meaning": hanja_meaning,
        "Radical": hanja_radical,
        "Stroke Count": hanja_stroke_count,
        "Formation Letter": formation_letter,
        "Unicode": unicode,
        "Usage": usage,
    }

    # Step 7: Create a tuple with Hanja character, its unique ID, and detailed information
    data = (hanja, hanja_id, hanja_info)

    return data


def export_to_csv(fieldnames, data):
    """
    Export data to a CSV file.

    :param file_name: The name of the CSV file to export.
    :type file_name: str
    :param fieldnames: A list of field names for the CSV header.
    :type fieldnames: list
    :param data: A list of dictionaries containing data to be exported to the CSV file.
    :type data: list
    """
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    output_name = f"data/hanja_csv_{timestamp}.csv"
    with open(output_name, "w", newline="", encoding="utf-8") as csvfile:
        csvwriter = csv.DictWriter(csvfile, fieldnames=fieldnames)
        csvwriter.writeheader()

        for row in data:
            csvwriter.writerow(row)


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
    browser = SeleniumDriver()

    # Create an empty list to store the results
    results = []

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
        result = fetch_hanja_data(hanja, browser)
        results.append(result)
        if result[1] != None:
            logger.info(f"[{idx} / {len(hanja_list)}] {hanja}'s data has been fetched.")
        else:
            logger.error(f"[{idx} / {len(hanja_list)}] Fetch Failed: {hanja}'")

    # Close the browser session to relase resources
    browser.quit()
    logger.info("WebCrawling Finished.")

    if instant_csv != True:
        return results
    else:
        # Define the CSV header
        fieldnames = [
            "hanja",
            "meaning",
            "radical",
            "stroke_count",
            "formation_letter",
            "unicode",
            "usage",
            "naver_hanja_id",
        ]

        # Align data with fieldnames
        csv_data = []
        for result in results:
            if result[1] is not None:  # Temporary for fixing bug
                csv_data.append(
                    {
                        "hanja": result[0],
                        "meaning": result[2]["Meaning"],
                        "radical": result[2]["Radical"],
                        "stroke_count": result[2]["Stroke Count"],
                        "formation_letter": ", ".join(result[2]["Formation Letter"]),
                        "unicode": result[2]["Unicode"],
                        "usage": ", ".join(result[2]["Usage"]),
                        "naver_hanja_id": result[1],
                    }
                )

        # Export the results to CSV
        export_to_csv(fieldnames, csv_data)
        logger.info("CSV Export Finished")


if __name__ == "__main__":
    scrape_hanja(instant_csv=True)
