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

# Usage Example:
# Navigates to a URL and waits for an element to load
url = "https://www.naver.com"
browser.get_await(url=url, locator=(By.ID, "newsstand"))

# Captures a screenshot
browser.get_screenshot_as_file("result.png")

# Quits the browser session
browser.quit()
