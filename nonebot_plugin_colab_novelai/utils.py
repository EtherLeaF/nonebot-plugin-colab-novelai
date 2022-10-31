import os
import time
import uuid
from typing import Any
from pathlib import Path

import av

from selenium import webdriver
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.chrome.webdriver import WebDriver as ChromeWebDriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium_stealth import stealth

import asyncio
from nonebot.rule import ArgumentParser

from .config import plugin_config
from .access.cpolar import get_cpolar_authtoken


os.makedirs("/data/colab-novelai", exist_ok=True)
PLUGIN_DIR = Path(__file__).absolute().parent

# Initialize ArgumentParsers for nonebot matchers
naifu_txt2img_parser = ArgumentParser()
naifu_txt2img_parser.add_argument('-p', '--prompt', type=str, nargs='+', required=True)
naifu_txt2img_parser.add_argument('-s', '--size', type=str, default="512x768")
naifu_txt2img_parser.add_argument('-n', '--num', type=int, default=1)
naifu_txt2img_parser.add_argument('-r', '--seed', type=int, default=-1)

# Initialize WebDriver
options = webdriver.ChromeOptions()
if plugin_config.headless_webdriver:
    options.add_argument('--headless')
    options.add_argument("window-size=1920,1080")
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
chrome_driver = webdriver.Chrome(
    ChromeDriverManager(path="/data/colab-novelai/").install(),
    options=options
)

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


def get_mac_address() -> str:
    address = hex(uuid.getnode())[2:]
    return '-'.join(address[i:i+2] for i in range(0, len(address), 2))


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


def convert_audio2wav(fp_in: Any, fp_out: Any, sample_rate: int = 16000) -> None:
    with av.open(fp_in) as buf_in:
        in_stream = buf_in.streams.audio[0]

        with av.open(fp_out, 'w', 'wav') as buf_out:
            out_stream = buf_out.add_stream(
                "pcm_s16le",
                rate=sample_rate,
                layout="mono"
            )
            for frame in buf_in.decode(in_stream):
                for packet in out_stream.encode(frame):
                    buf_out.mux(packet)


# Startup autocheck
try:
    asyncio.run(get_cpolar_authtoken())
    chrome_driver.quit()
# already in event loop
except RuntimeError:
    pass
