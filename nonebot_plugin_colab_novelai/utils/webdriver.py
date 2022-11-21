import time
import asyncio
from typing import Any

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import NoAlertPresentException
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.chrome.webdriver import WebDriver as ChromeWebDriver
from selenium_stealth import stealth
from webdriver_manager.chrome import ChromeDriverManager

from .distributed import PLUGIN_DIR
from ..config import plugin_config
from ..access.cpolar import get_cpolar_authtoken


options = webdriver.ChromeOptions()

if plugin_config.headless_webdriver:
    options.add_argument('--headless')
    options.add_argument("--no-sandbox")
    options.add_argument("window-size=1920,1080")
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument("--disable-setuid-sandbox")
    options.add_argument("--remote-debugging-port=9222")
else:
    options.add_argument("--start-maximized")
if (proxy := plugin_config.colab_proxy) is not None:
    options.add_argument(f'--proxy-server={proxy}')

options.add_argument("--disable-blink-features")
options.add_argument("--disable-blink-features=AutomationControlled")
options.add_argument('--incognito')
options.add_argument("--disable-extensions")
options.add_argument("--disable-infobars")
options.add_argument("--no-default-browser-check")
options.add_experimental_option("excludeSwitches", ["enable-automation"])
options.add_experimental_option("useAutomationExtension", False)

driver_path = ChromeDriverManager(path="./data/colab-novelai/").install()
chrome_driver = webdriver.Chrome(service=Service(driver_path), options=options)

for filename in ("undefineWebDriver.js", "objKeySort.js"):
    with open(PLUGIN_DIR / "js" / filename, 'r', encoding='utf-8') as js:
        chrome_driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
            "source": js.read()
        })

stealth(
    chrome_driver,
    languages=["en-US", "en"],
    vendor="Google Inc.",
    platform="Win32",
    webgl_vendor="Intel Inc.",
    renderer="Intel Iris OpenGL Engine",
    fix_hairline=True,
)


def force_refresh_webpage(driver: ChromeWebDriver, url: str) -> None:
    driver.get(url)
    try:
        driver.switch_to.alert.accept()
    except NoAlertPresentException:
        pass


def wait_and_click_element(driver: ChromeWebDriver, by: str, value: str) -> Any:
    element = WebDriverWait(driver, 5).until(
        lambda t_driver: t_driver.find_element(by, value)
    )
    WebDriverWait(driver, 3).until(
        ec.element_to_be_clickable((by, value))
    )
    element.click()

    time.sleep(0.1)
    return element


# Startup autocheck
try:
    asyncio.run(get_cpolar_authtoken())
    chrome_driver.quit()
# already in event loop
except RuntimeError:
    pass
