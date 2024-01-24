from utils.logger import logger
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager
from selenium.common.exceptions import NoSuchElementException, TimeoutException


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

    _with_depth = 0  # Counter to track the depth of nested 'with' statements

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

        # Initialize the WebDriver with configured options
        super().__init__(
            service=ChromeService(ChromeDriverManager().install()),
            options=chrome_options,
        )

    def __enter__(self):
        """
        Enter method for using the class with the 'with' statement. Increments the 'with' depth.
        """
        self._with_depth += 1
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        """
        Exit method for using the class with the 'with' statement. Decrements the 'with' depth.
        Quits the driver if it's the outermost 'with' statement.
        """
        self._with_depth -= 1
        if not self._with_depth:
            self.quit()

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

        # Navigate to the specified URL
        self.get(url)

        try:
            # Wait for the element to be present
            WebDriverWait(self, 5).until(
                EC.presence_of_element_located((locator[0], locator[1]))
            )
        except NoSuchElementException:
            logger.warning(f"{locator[1]}: Element not found on the page")
        except TimeoutException:
            logger.warning(
                f"{locator[1]}: Timeout occurred while waiting for the element"
            )
