import logging
from typing import Any, Union

from selenium.common import NoSuchElementException,  ElementClickInterceptedException
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support.wait import WebDriverWait
from utilities.decorators import (
    logging_decorator,
    retry_on_exception,
)


logger = logging.getLogger(__name__)


class BasePageClass:
    """Base framework class providing automated browser interaction helpers."""

    def __init__(self, driver: Any) -> None:
        """Initializes BaseClass with a Selenium WebDriver instance.

        Args:
            driver: The Selenium WebDriver instance.
        """
        self.driver = driver
        self.wait = WebDriverWait(self.driver, timeout=5)

    @logging_decorator
    def navigate_to_url(self, url):
        self.driver.get(url)
        self.wait_for_exact_url(url)

    @logging_decorator
    def enter_text(self, locator, text: str) -> None:
        """Wait for an input element and enter the provided text.

        Args:
            locator: Selenium locator tuple used to find the input element.
            text: Text to enter into the input element.
        """
        element = self.locate_element(locator)
        self.wait_for_element_to_be_clickable(element)
        element.send_keys(text)

    @logging_decorator
    @retry_on_exception(times=3)
    def locate_element(self, locator:  tuple[str, str]) -> WebElement:
        """Waits for an element to be present and visible in the DOM.

        Args:
            locator: A tuple containing the locator strategy and target value
                (e.g., `(By.XPATH, "//div")`).

        Returns:
            WebElement: The located and visible Selenium WebElement.

        Raises:
            TimeoutException: If the element is not found/visible within timeout limits.
        """
        self.wait.until(EC.presence_of_element_located(locator))
        elem = self.wait.until(EC.visibility_of_element_located(locator))
        return elem

    @logging_decorator
    @retry_on_exception(times=3, exception_type=ElementClickInterceptedException)
    def click_element(self, element: WebElement):
        try:
            element.click()
        except ElementClickInterceptedException:
            # this is to handle the appearance of ad
            dismiss_button_elem = self.driver.find_element(By.ID,"dismiss-button-element")
            dismiss_button_elem.click()
            if dismiss_button_elem.is_element_invisible:
                element.click()
            else:
                raise ElementClickInterceptedException


    @logging_decorator
    @retry_on_exception
    def is_element_invisible(self, element: WebElement) -> WebElement | bool:
        """

        Args:
            element:

        Returns:

        """
        return self.wait.until(EC.invisibility_of_element(element))


    def is_element_visible(self, locator:  tuple[str, str]) ->  bool:
        """

        Args:
            locator:

        Returns:

        """

        element = self.locate_element(locator)
        if self.wait.until(EC.visibility_of(element)):
            return True
        else:
            return False

    @logging_decorator
    @retry_on_exception(times=3)
    def wait_for_element_to_be_clickable(
            self,
            element: WebElement,
    ) -> None:
        """Wait until an element becomes clickable.

        Args:
            element: Selenium WebElement to wait for.

        Raises:
            TimeoutException: If the element does not become clickable within
                the configured timeout.
        """
        self.wait.until(EC.element_to_be_clickable(element))


    @logging_decorator
    @retry_on_exception(times=3)
    def wait_for_url_contains(self, url_substring: str, timeout: int = 5) -> bool:
        """Waits until the current browser URL contains the given substring.

        Args:
            url_substring: Partial string expected to be in the URL.
            timeout: Maximum wait time in seconds.

        Returns:
            bool: True if the condition is met within the timeout.
        """

        return self.wait.until(EC.url_contains(url_substring))

    @logging_decorator
    @retry_on_exception(times=3)
    def wait_for_exact_url(self, expected_url: str, timeout: int = 5) -> bool:
        """Waits until the current browser URL exactly matches the given string.

        Args:
            expected_url: The full expected URL.
            timeout: Maximum wait time in seconds.

        Returns:
            bool: True if the condition is met within the timeout.
        """
        return self.wait.until(EC.url_to_be(expected_url))


    @logging_decorator
    @retry_on_exception(times=3, exception_type=NoSuchElementException)
    def select_option(
            self,
            locator:  tuple[str, str],
            value: Union[str, int],
            by: str = "text"
    ) -> None:
        """Selects an option from a standard HTML <select> dropdown element.

        Args:
            locator: A tuple containing the locator strategy and target value
                (e.g., `(By.ID, "country-dropdown")`).
            value: The target string (for 'text' or 'value') or integer (for 'index')
                to select.
            by: Selection strategy to use. Options are:
                - `"text"` (default): Matches visible text of the option.
                - `"value"`: Matches the HTML 'value' attribute of the option.
                - `"index"`: Matches zero-based index of the option.

        Raises:
            ValueError: If an invalid `by` strategy is provided or value type mismatches.
            NoSuchElementException: If the element or target option isn't found.
            UnexpectedTagNameException: If target element isn't an HTML `<select>`.
        """
        # 1. Wait until dropdown element is present and visible
        dropdown_element = self.locate_element(locator)

        # 2. Wrap element in Selenium's Select wrapper class
        select = Select(dropdown_element)

        # 3. Perform selection based on passed strategy
        if by == "text":
            select.select_by_visible_text(str(value))
        elif by == "value":
            select.select_by_value(str(value))
        elif by == "index":
            if not isinstance(value, int):
                raise ValueError(
                    f"Selection strategy 'index' requires an integer value, got {type(value)}"
                )
            select.select_by_index(value)
        else:
            raise ValueError(
                f"Invalid selection strategy '{by}'. Use 'text', 'value', or 'index'."
            )