import os
import uuid
import time
from pathlib import Path
from typing import Any, TypeVar

import av

from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.chrome.webdriver import WebDriver as ChromeWebDriver


os.makedirs("./data/colab-novelai", exist_ok=True)
PLUGIN_DIR = Path(__file__).absolute().parent.parent

T_UserID = TypeVar("T_UserID", str, int)
T_AuthorizedUserID = TypeVar("T_AuthorizedUserID", str, int)
T_GroupID = TypeVar("T_GroupID", str, int)
T_AuthorizedGroupID = TypeVar("T_AuthorizedGroupID", str, int)


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
