import asyncio

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium_stealth import stealth

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
options.add_argument("--disable-blink-features")
options.add_argument("--disable-blink-features=AutomationControlled")
options.add_argument('--incognito')
options.add_argument("--disable-extensions")
options.add_argument("--disable-infobars")
options.add_argument("--no-default-browser-check")
options.add_experimental_option("excludeSwitches", ["enable-automation"])
options.add_experimental_option("useAutomationExtension", False)
# options.add_experimental_option('mobileEmulation', {'deviceName': 'iPhone X'})
driver_path = ChromeDriverManager(path="./data/colab-novelai/").install()
chrome_driver = webdriver.Chrome(service=Service(driver_path), options=options)

with open(PLUGIN_DIR / "js" / "undefineWebDriver.js", 'r', encoding='utf-8') as js:
    chrome_driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
        "source": js.read()
    })
with open(PLUGIN_DIR / "js" / "objKeySort.js", 'r', encoding='utf-8') as js:
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


# Startup autocheck
try:
    asyncio.run(get_cpolar_authtoken())
    chrome_driver.quit()
# already in event loop
except RuntimeError:
    pass
