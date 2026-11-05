import os

import pytest
import sys
import logging
import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.firefox.options import Options as FirefoxOption
from pathlib import Path
from reportportal_client import RPLogger, RPLogHandler

from pages.login_and_signup_page import LoginAndSignUpPageClass
from utilities.helpers import load_json_data, generate_unique_id



TEST_DATA_PATH = (
    Path(__file__).parent / "data"
)

logger = logging.getLogger(__name__)


def pytest_addoption(parser):
    parser.addoption(
        '--browser', action="store", default=None,
        help="Browser type: Chrome or Firefox"
    )
    parser.addini(
        "browser",
        help="Default browser to use for test execution.",
        default="chrome",
    )
    parser.addoption(
        "--headless", action="store", default=False,
        help="Provide True for headless mode"
    )



@pytest.fixture(scope='session')
def get_driver(request):
    # Either this will be in pytest.ini file or provided from CLI
    browser = request.config.getoption("--browser") or request.config.getini("browser")
    browser = browser.strip().lower()
    driver = None
    if browser == 'chrome':
        options = ChromeOptions()
        options.add_argument("--start-maximized")
        driver = webdriver.Chrome()
    elif browser == 'firefox':
        driver = webdriver.Firefox()
    else:
        error_msg = f"Provided browser name '{browser}' is invalid. Expected 'chrome' or 'firefox'."
        logging.error(error_msg)
        pytest.exit(error_msg)
    driver.maximize_window()
    yield driver
    if driver:
        driver.quit()


@pytest.fixture(scope="session", autouse=True)
def configure_global_logging(request):
    # CRITICAL: Reconfigure the global logging class for ReportPortal compatibility
    logging.setLoggerClass(RPLogger)

    # Fetch the root logger - this controls logging across ALL imported modules
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.DEBUG)

    # Define a clean text format for your console and files
    log_format = logging.Formatter(
        fmt="%(asctime)s [%(levelname)s] %(name)s::%(funcName)s::%(lineno)d::%(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )

    # 1. Local File Handler (Tracks everything globally across POMs and tests)
    file_handler = logging.FileHandler("logs/execution_flow.log", mode="w", encoding="utf-8")
    file_handler.setLevel(logging.INFO)
    file_handler.setFormatter(log_format)
    root_logger.addHandler(file_handler)

    # 2. Extract the ReportPortal Service Orchestrator
    rp_plugin = request.config.pluginmanager.get_plugin("pytest-reportportal")
    rp_service = getattr(rp_plugin, "py_test_service", None)

    if rp_service:
        # ReportPortal Data Stream
        rp_handler = RPLogHandler(rp_client=rp_service)
        rp_handler.setLevel(logging.INFO)
        root_logger.addHandler(rp_handler)

        # Standard Terminal Output (Mirroring)
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(logging.INFO)
        console_handler.setFormatter(log_format)
        root_logger.addHandler(console_handler)
    else:
        # Fallback Terminal output if offline/not running with --reportportal
        fallback_console = logging.StreamHandler(sys.stdout)
        fallback_console.setLevel(logging.INFO)
        fallback_console.setFormatter(log_format)
        root_logger.addHandler(fallback_console)

    yield

    # Clean up handlers after the test session finishes
    handlers = root_logger.handlers[:]
    for handler in handlers:
        handler.close()
        root_logger.removeHandler(handler)


@pytest.fixture
def signup_data() -> dict:
    """Create unique signup test data for each test execution.

    Returns:
        Signup data containing a dynamically generated name, email and password.
    """
    data = load_json_data(f"{TEST_DATA_PATH}/signup_data.json")

    data["signup"]["name"] = f"TestUser{generate_unique_id()}"
    data["signup"]["email_address"] = (
        f"testuser_{generate_unique_id()}@example.com"
    )
    data["signup"]["password"]=f"test{generate_unique_id()}password"

    return data["signup"]

@pytest.fixture
def invalid_login_data(request) -> dict:
    file_path = TEST_DATA_PATH / "invalid_login_data.json"
    data = load_json_data(file_path)
    return data[request.param]


@pytest.fixture
def login_fixture(get_driver):
    """Authenticate a user before a test executes.

    Args:
        get_driver: Selenium WebDriver fixture.

    Raises:
        RuntimeError: If login credentials are unavailable.
    """
    username = os.getenv("test_username")
    password = os.getenv("test_password")

    if not username or not password:
        raise RuntimeError(
            "Missing test_username or test_password environment variables."
        )

    login_page = LoginAndSignUpPageClass(get_driver)

    logger.info("Navigating to application home page.")

    login_page.navigate_to_url(
        "https://www.automationexercise.com/"
    )

    logger.info(f"Logging in as user: {username}")

    login_page.login(username, password)

    logger.info("User successfully logged in.")


# pytesthook for reporting and adding the screenshots on failure
# Hook: ONLY attaches the outcome to the item, nothing else.
@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item, call):
    outcome = yield
    result = outcome.get_result()
    setattr(item, "rep_" + result.when, result)


# New function-scoped fixture: runs its teardown after EVERY test,
# even though get_driver (session-scoped) stays alive across tests.
@pytest.fixture(autouse=True)
def capture_screenshot_on_failure(request, get_driver):
    yield
    if request.node.rep_call.failed:
        driver = get_driver
        timestamp = time.strftime("%Y_%m_%d_%H_%M_%S")
        screenshot_filename = f"{request.node.name}_{timestamp}.png"
        screenshot_dir = Path(__file__).resolve().parent / "screenshots"
        screenshot_dir.mkdir(parents=True, exist_ok=True)

        screenshot_path = screenshot_dir / screenshot_filename
        driver.save_screenshot(str(screenshot_path))
        screenshot_bytes = driver.get_screenshot_as_png()

        logger.error(
            f"TEST FAILURE RECORDED: Case '{request.node.name}' collapsed during execution. Sending screenshot asset.",
            extra={
                "attachment": {
                    "name": f"failure_{request.node.name}.png",
                    "data": screenshot_bytes,
                    "mime": "image/png",
                }
            }
        )


