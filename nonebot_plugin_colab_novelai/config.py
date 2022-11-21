from typing import Optional, Dict, List, Union

from nonebot import get_driver
from pydantic import BaseModel, Extra


class Config(BaseModel, extra=Extra.ignore):
    headless_webdriver: bool = True
    colab_proxy: Optional[str] = None
    google_accounts: Dict[str, str] = {}
    cpolar_username: str = None
    cpolar_password: str = None
    bce_apikey: str = None
    bce_secretkey: str = None
    naifu_max: int = 1
    naifu_cd: int = 0
    nai_save2local_path: Optional[str] = None
    nai_save2webdav_info: Dict[str, Optional[str]] = {
        "url": None,
        "username": None, "password": None,
        "path": None
    }
    nai_nsfw_tags: Optional[Union[List[str], str]] = None


plugin_config = Config.parse_obj(get_driver().config.dict())

# Startup autocheck
assert plugin_config.google_accounts, "至少需要填写一个Google账号！"
assert(
    plugin_config.cpolar_username is not None and plugin_config.cpolar_password is not None
), "需要同时填写cpolar的账号与密码！"
assert(
    plugin_config.bce_apikey is not None and plugin_config.bce_secretkey is not None
), "需要同时填写百度智能云的apiKey与SecretKey！"
assert(
    all(plugin_config.nai_save2webdav_info.values()) or
    all(i is None for i in plugin_config.nai_save2webdav_info.values())
), "请检查WebDAV的Config是否完整填写！"
