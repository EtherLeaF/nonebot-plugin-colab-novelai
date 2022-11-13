# @Env: Python3.10
# -*- coding: utf-8 -*-
# @Author  : T_EtherLeaF
# @Email   : thetapilla@gmail.com
# @Software: PyCharm

from argparse import Namespace

from nonebot import require, get_driver
from nonebot.plugin import on_shell_command
from nonebot.params import ShellCommandArgs
from nonebot.permission import SUPERUSER
from nonebot.adapters.onebot.v11 import MessageEvent
from nonebot_plugin_apscheduler import scheduler

from .utils import chrome_driver
from .argparsers import naifu_draw_parser, naifu_perm_parser
from ._main import handle_recaptcha, access_colab_with_accounts
from .__meta__ import __plugin_meta__


nb_driver = get_driver()
require("nonebot_plugin_apscheduler")
scheduler.add_job(handle_recaptcha, "interval", id="checkReCaptcha", seconds=10)
scheduler.add_job(access_colab_with_accounts, "interval", id="runColab", seconds=30)

naifu_draw = on_shell_command("naifu", priority=10, parser=naifu_draw_parser)
naifu_permission = on_shell_command("naifu", priority=10, parser=naifu_perm_parser, permission=SUPERUSER)


@naifu_draw.handle()
async def _naifu_draw(event: MessageEvent, args: Namespace = ShellCommandArgs()) -> None:
    await args.draw(matcher=naifu_draw, event=event, args=args)


@naifu_permission.handle()
async def _operate_permission(event: MessageEvent, args: Namespace = ShellCommandArgs()) -> None:
    await args.operate(matcher=naifu_permission, event=event, user_id=args.uid, group_id=args.gid)


@nb_driver.on_shutdown
def _quit_webdriver() -> None:
    chrome_driver.quit()
