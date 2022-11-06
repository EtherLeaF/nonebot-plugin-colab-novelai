import os
import time
from typing import Any, Tuple, List, Dict, Set, TypeVar, Type

import yaml

from nonebot import get_driver
from nonebot.matcher import Matcher

from ..config import plugin_config


os.makedirs("./data/colab-novelai", exist_ok=True)

T_Quid = TypeVar("T_Quid", str, int)
T_AuthorizedQuid = TypeVar("T_AuthorizedQuid", str, int)


def load_cd_yml() -> Tuple[Dict[T_Quid, float], Set[T_AuthorizedQuid]]:
    with open("./data/colab-novelai/cd.yml", "a+") as f:
        f.seek(0)
        cd_data = yaml.load(f, Loader=yaml.CFullLoader)

        if cd_data is None:
            initial_data = ({}, get_driver().config.superusers)
            yaml.dump(initial_data, f)
            return initial_data

        return cd_data


def save_cd_yml(data: Any) -> None:
    with open("./data/colab-novelai/cd.yml", 'w') as f:
        yaml.dump(data, f)


async def add_authorized_user(matcher: Type[Matcher], user_id: List[T_AuthorizedQuid]) -> None:
    cd_data, authorized_users = load_cd_yml()
    authorized_users.update(user_id)
    save_cd_yml((cd_data, authorized_users))

    await matcher.send(f"成功将以下用户添加白名单：{', '.join(user_id)}")


async def remove_authorized_user(matcher: Type[Matcher], user_id: List[T_AuthorizedQuid]) -> None:
    user_id = set(user_id)
    cd_data, authorized_users = load_cd_yml()
    await matcher.send(f"成功将以下用户移出白名单：{', '.join(authorized_users & user_id)}")

    authorized_users -= user_id
    save_cd_yml((cd_data, authorized_users))


def record_cd(user_id: T_Quid, num: int) -> None:
    cd_data, authorized_users = load_cd_yml()
    if user_id in authorized_users:
        return

    cd_data[user_id] = time.time() + plugin_config.naifu_cd * num
    save_cd_yml((cd_data, authorized_users))


def get_user_cd(user_id: T_Quid) -> float:
    cd_data, authorized_user = load_cd_yml()
    if user_id in authorized_user:
        return 0

    try:
        return cd_data[user_id] - time.time()
    except KeyError:
        return 0
