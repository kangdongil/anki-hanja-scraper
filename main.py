import csv
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager
from hanja_tool import hanja_to_url, standardize_hanja


class SeleniumDriver(webdriver.Chrome):
    """
    Custom class for Selenium WebDriver with common options and configurations.

    :param options: A list of additional command-line arguments for Chrome options.
    :type options: list

    Methods:
    get_await(url, locator):
        Navigates to the specified URL and waits for an element to be present based on the provided locator.

        :param url: The URL to navigate to.
        :type url: str
        :param locator: A tuple with two elements (By, value) specifying the element locator.
                        Example: (By.ID, 'element_id')
        :type locator: tuple
    """

    def __init__(self, options=None):
        chrome_options = webdriver.ChromeOptions()
        chrome_options.set_capability("pageLoadStrategy", "none")

        # If options is None or an empty list, use the default options
        if options is None:
            default_options = [
                "start-maximized",
                "disable-infobars",
                "--disable-extensions",
                "--log-level=3",
                "--headless",
                "--disable-logging",
                "--no-sandbox",
                "--disable-gpu",
            ]
            options = default_options

        for opt in options:
            chrome_options.add_argument(opt)

        super().__init__(
            service=ChromeService(ChromeDriverManager().install()),
            options=chrome_options,
        )

    def get_await(self, url, locator):
        """
        Navigate to the specified URL and wait for an element to be present based on the provided locator.

        :param url: The URL to navigate to.
        :type url: str
        :param locator: A tuple with two elements (By, value) specifying the element locator.
                        Example: (By.ID, 'element_id')
        :type locator: tuple
        """
        if not isinstance(locator, tuple) or len(locator) != 2:
            raise ValueError("Locator should be a tuple with 2 arguments (By, value)")

        self.get(url)

        try:
            WebDriverWait(self, 10).until(
                EC.presence_of_element_located((locator[0], locator[1]))
            )
        except Exception as e:
            raise RuntimeError(f"Error waiting for element: {e}")


def get_hanja_data(hanja, browser):
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
    with open("hanja_result.csv", "w", newline="", encoding="utf-8") as csvfile:
        csvwriter = csv.DictWriter(csvfile, fieldnames=fieldnames)
        csvwriter.writeheader()

        for row in data:
            csvwriter.writerow(row)


def main():
    """
    Main function for performing web scraping of Hanja data and exporting it to a CSV file.

    This function initializes a SeleniumDriver instance, fetches Hanja data for a list of Hanja characters,
    and exports the data to a CSV file named 'hanja_result.csv'.

    :return: None
    """
    # Create a SeleniumDriver instance with common options
    browser = SeleniumDriver()

    # Create an empty list to store the results
    results = []

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

    # Iterate through the list of Hanja characters and fetch their data
    for idx, hanja in enumerate(hanja_list, 1):
        result = get_hanja_data(hanja, browser)
        results.append(result)
        if result[1] != None:
            print(f"[{idx} / {len(hanja_list)}] {hanja}'s data has been fetched.")
        else:
            print(f"[{idx} / {len(hanja_list)}] Fetch Failed: {hanja}'")

    # Close the browser session to relase resources
    browser.quit()
    print("WebCrawling Finished.")

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

    # Epxort the results to CSV
    export_to_csv(fieldnames, csv_data)
    print("CSV Export Finished")


if __name__ == "__main__":
    main()
