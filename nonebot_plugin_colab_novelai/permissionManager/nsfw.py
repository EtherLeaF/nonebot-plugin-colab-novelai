from typing import Type, Tuple, List, Set, Any, Optional

import yaml

from nonebot import get_driver
from nonebot.matcher import Matcher
from nonebot.adapters.onebot.v11 import MessageEvent, GroupMessageEvent

from ..utils import T_UserID, T_AuthorizedUserID, T_GroupID, T_AuthorizedGroupID


class NotSafeForWorkManager(object):
    @staticmethod
    def _load_yml() -> Tuple[Set[T_AuthorizedUserID], Set[T_AuthorizedGroupID]]:
        with open("./data/colab-novelai/nsfw.yml", "a+") as f:
            f.seek(0)
            nsfw_conf = yaml.load(f, Loader=yaml.CFullLoader)

            if nsfw_conf is None:
                initial_data = (get_driver().config.superusers, set())
                yaml.dump(initial_data, f)
                return initial_data

            return nsfw_conf

    @staticmethod
    def _save_yml(data: Any) -> None:
        with open("./data/colab-novelai/nsfw.yml", 'w') as f:
            yaml.dump(data, f)

    @classmethod
    async def list_authorized_users(cls, matcher: Type[Matcher], **kwargs: Any) -> None:
        authorized_users, authorized_groups = cls._load_yml()
        await matcher.send(
            "当前允许以下用户使用nsfw tag:\n{}".format('\n'.join(authorized_users)) +
            "\n当前允许以下群组使用nsfw tag:\n{}".format('\n'.join(authorized_groups))
        )

    @classmethod
    async def add_authorized_user(
        cls,
        matcher: Type[Matcher],
        event: MessageEvent,
        user_id: List[T_UserID], group_id: List[T_GroupID]
    ) -> None:
        authorized_users, authorized_groups = cls._load_yml()

        if user_id:
            authorized_users.update(user_id)
            await matcher.send(f"已允许以下用户使用nsfw tag:{', '.join(set(user_id))}")
        if group_id:
            authorized_groups.update(group_id)
            await matcher.send(f"已允许以下群组使用nsfw tag:{', '.join(set(group_id))}")

        if not user_id and not group_id and isinstance(event, GroupMessageEvent):
            group_id = [str(event.group_id)]
            authorized_groups.update(group_id)
            await matcher.send(f"已允许本群使用nsfw tag!")

        cls._save_yml((authorized_users, authorized_groups))

    @classmethod
    async def remove_authorized_user(
        cls,
        matcher: Type[Matcher],
        event: MessageEvent,
        user_id: List[T_AuthorizedUserID], group_id: List[T_AuthorizedGroupID]
    ) -> None:
        user_id = set(user_id)
        group_id = set(group_id)
        authorized_users, authorized_groups = cls._load_yml()

        if user_id:
            await matcher.send(f"已禁止以下用户使用nsfw tag:{', '.join(authorized_users & user_id)}")
            authorized_users -= user_id
        if group_id:
            await matcher.send(f"已禁止以下群组使用nsfw tag:{', '.join(authorized_groups & group_id)}")
            authorized_groups -= group_id

        if not user_id and not group_id and isinstance(event, GroupMessageEvent):
            group_id = {str(event.group_id)}
            await matcher.send(f"已禁止本群使用nsfw tag!")
            authorized_groups -= group_id

        cls._save_yml((authorized_users, authorized_groups))

    @classmethod
    def check_nsfw_available(cls, user_id: T_UserID, group_id: Optional[T_GroupID]) -> bool:
        authorized_users, authorized_groups = cls._load_yml()

        if user_id in authorized_users and group_id is None:
            return True
        if user_id in authorized_users and group_id in authorized_groups:
            return True
        return False
