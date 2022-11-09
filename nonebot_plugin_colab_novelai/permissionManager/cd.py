import time
from typing import Any, Tuple, List, Dict, Set, Type

import yaml

from nonebot import get_driver
from nonebot.matcher import Matcher

from ..config import plugin_config
from ..utils import T_UserID, T_AuthorizedUserID


class CooldownManager(object):
    @staticmethod
    def _load_yml() -> Tuple[Dict[T_UserID, float], Set[T_AuthorizedUserID]]:
        with open("./data/colab-novelai/cd.yml", "a+") as f:
            f.seek(0)
            cd_data = yaml.load(f, Loader=yaml.CFullLoader)

            if cd_data is None:
                initial_data = ({}, get_driver().config.superusers)
                yaml.dump(initial_data, f)
                return initial_data

            return cd_data

    @staticmethod
    def _save_yml(data: Any) -> None:
        with open("./data/colab-novelai/cd.yml", 'w') as f:
            yaml.dump(data, f)

    @classmethod
    async def list_authorized_users(cls, matcher: Type[Matcher], **kwargs: Any) -> None:
        authorized_users = cls._load_yml()[1]
        await matcher.send("当前有以下白名单用户：\n{}".format('\n'.join(authorized_users)))

    @classmethod
    async def add_authorized_user(
        cls,
        matcher: Type[Matcher],
        user_id: List[T_UserID],
        **kwargs: Any
    ) -> None:
        cd_data, authorized_users = cls._load_yml()
        authorized_users.update(user_id)
        cls._save_yml((cd_data, authorized_users))

        await matcher.send(f"成功将以下用户添加白名单：{', '.join(set(user_id))}")

    @classmethod
    async def remove_authorized_user(
        cls,
        matcher: Type[Matcher],
        user_id: List[T_AuthorizedUserID],
        **kwargs: Any
    ) -> None:
        user_id = set(user_id)
        cd_data, authorized_users = cls._load_yml()
        await matcher.send(f"成功将以下用户移出白名单：{', '.join(authorized_users & user_id)}")

        authorized_users -= user_id
        cls._save_yml((cd_data, authorized_users))

    @classmethod
    def record_cd(cls, user_id: T_UserID, num: int) -> None:
        cd_data, authorized_users = cls._load_yml()
        if user_id in authorized_users:
            return

        cd_data[user_id] = time.time() + plugin_config.naifu_cd * num
        cls._save_yml((cd_data, authorized_users))

    @classmethod
    def get_user_cd(cls, user_id: T_UserID) -> float:
        cd_data, authorized_user = cls._load_yml()
        if user_id in authorized_user:
            return 0

        try:
            return cd_data[user_id] - time.time()
        except KeyError:
            return 0
