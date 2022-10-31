from typing import Optional, Dict

from nonebot import get_driver
from pydantic import BaseModel, Extra


class Config(BaseModel, extra=Extra.ignore):
    headless_webdriver: bool = True
    google_accounts: Dict[str, str] = {}
    cpolar_username: Optional[str] = None
    cpolar_password: Optional[str] = None
    bce_apikey: Optional[str] = None
    bce_secretkey: Optional[str] = None
    naifu_max: int = 1


plugin_config = Config.parse_obj(get_driver().config.dict())

# Startup autocheck
assert plugin_config.google_accounts, "至少需要填写一个Google账号！"
assert(
    plugin_config.cpolar_username is not None and plugin_config.cpolar_password is not None
), "需要同时填写cpolar的账号与密码！"
assert(
    plugin_config.bce_apikey is not None and plugin_config.bce_secretkey is not None
), "需要同时填写百度智能云的apiKey与SecretKey！"
