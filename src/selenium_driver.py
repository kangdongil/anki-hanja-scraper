from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager


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
