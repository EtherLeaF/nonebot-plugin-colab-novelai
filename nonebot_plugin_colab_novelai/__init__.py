# @Env: Python3.10
# -*- coding: utf-8 -*-
# @Author  : T_EtherLeaF
# @Email   : thetapilla@gmail.com
# @Software: PyCharm

from argparse import Namespace

from nonebot import require, get_driver
from nonebot.plugin import on_shell_command
from nonebot.params import ShellCommandArgs
from nonebot.adapters.onebot.v11 import MessageEvent
from nonebot_plugin_apscheduler import scheduler

from .utils import naifu_txt2img_parser, chrome_driver
from ._main import naifu_txt2img, handle_recaptcha, access_colab_with_accounts


nb_driver = get_driver()
require("nonebot_plugin_apscheduler")
scheduler.add_job(handle_recaptcha, "interval", id="checkReCaptcha", seconds=10)
scheduler.add_job(access_colab_with_accounts, "interval", id="runColab", minutes=1)

txt2img = on_shell_command("naifu", priority=10, parser=naifu_txt2img_parser, block=True)


@txt2img.handle()
async def _naifu_txt2img(event: MessageEvent, args: Namespace = ShellCommandArgs()) -> None:
    await naifu_txt2img(matcher=txt2img, event=event, args=args)


@nb_driver.on_shutdown
def quit_webdriver() -> None:
    chrome_driver.quit()
