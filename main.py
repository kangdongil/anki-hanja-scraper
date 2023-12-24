"""
SeleniumDriver is a custom class based on Selenium's webdriver.Chrome for web automation.

It simplifies the creation of WebDriver instances with common options and configurations,
making it easy to set up a Chrome WebDriver for web scraping or automation.

Attributes:
    options (list): A list of additional command-line arguments for Chrome options.

Methods:
    get_await(url, locator):
        Navigates to the specified URL and waits for an element to be present based on the provided locator.
        Args:
            url (str): The URL to navigate to.
            locator (tuple): A tuple with two elements (By, value) specifying the element locator.
                Example: (By.ID, 'element_id')

# Use the instance to navigate to a URL and wait for an element to load
    browser.get_await("https://example.com", (By.ID, 'element_id'))
"""


from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager
from hanja_encoder import hanja_to_url


class SeleniumDriver(webdriver.Chrome):
    def __init__(self, options=None):
        chrome_options = webdriver.ChromeOptions()
        chrome_options.set_capability("pageLoadStrategy", "none")
        if options:
            for opt in options:
                chrome_options.add_argument(opt)

        super().__init__(
            service=ChromeService(ChromeDriverManager().install()),
            options=chrome_options,
        )

    def get_await(self, url, locator):
        if not isinstance(locator, tuple) or len(locator) != 2:
            raise ValueError("Locator should be a tuple with 2 arguments (By, value)")

        self.get(url)

        try:
            WebDriverWait(self, 10).until(
                EC.presence_of_element_located((locator[0], locator[1]))
            )
        except Exception as e:
            raise RuntimeError(f"Error waiting for element: {e}")


# Create a SeleniumDriver instance with common options
browser = SeleniumDriver(
    [
        "start-maximized",
        "disable-infobars",
        "--disable-extensions",
        "--log-level=3",
        "--headless",
        "--disable-logging",
        "--no-sandbox",
        "--disable-gpu",
    ]
)


def get_hanja_data(hanja, browser):
    """
     Retrieve Hanja information from the Naver Hanja Dictionary website.

    :param str hanja: The Hanja character to search for.
    :param browser: An instance of the SeleniumDriver class for web automation.
    :type browser: SeleniumDriver
    :returns: A tuple containing Hanja character and its unique ID.
    :rtype: tuple
    """

    # Fetch Hanja data from the Naver Dictionary website
    encoded_hanja = hanja_to_url(hanja)
    url = f"https://hanja.dict.naver.com/search?query={encoded_hanja}"
    browser.get_await(url=url, locator=(By.ID, "searchPage_letter"))
    hanja_obj = browser.find_elements(By.CSS_SELECTOR, ".row")[0].find_element(
        By.CSS_SELECTOR, ".hanja_word .hanja_link"
    )

    # Extract the Hanja ID
    if hanja_obj.text == hanja:
        hanja_id = hanja_obj.get_attribute("href").split("/")[-1]

    # Create a tuple with Hanja character and its unique ID
    data = (hanja, hanja_id)

    return data


# Create an empty list to store the results
results = []

# List of Hanja characters to search for
hanja_list = ["校", "敎", "九", "國", "軍"]

# Iterate through the list of Hanja characters and fetch their data
for hanja in hanja_list:
    result = get_hanja_data(hanja, browser)
    results.append(result)

# Close the browser session to relase resources
browser.quit()

# Print the result
print(results)
