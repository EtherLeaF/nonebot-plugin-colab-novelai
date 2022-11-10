import re

from httpx import AsyncClient

from ..config import plugin_config


CPOLAR_USER_INFO = {
    "login": plugin_config.cpolar_username,
    "password": plugin_config.cpolar_password
}


async def get_cpolar_authtoken() -> str:
    async with AsyncClient() as client:
        dashboard_resp = await client.post(
            url="https://dashboard.cpolar.com/login",
            data=CPOLAR_USER_INFO,
            follow_redirects=True,
            timeout=None
        )

    try:
        cpolar_authtoken = re.findall(r"authtoken\s.+<", dashboard_resp.text)[0][10:-1]
        return cpolar_authtoken
    except IndexError:
        raise ValueError("cpolar帐密填写有误！")


async def get_cpolar_url() -> str:
    async with AsyncClient() as client:
        await client.post(
            url="https://dashboard.cpolar.com/login",
            data=CPOLAR_USER_INFO,
            timeout=None
        )
        dashboard_resp = await client.get("https://dashboard.cpolar.com/status", timeout=None)

    try:
        cpolar_url = re.findall(r">https://.+\.cpolar\..+</a>", dashboard_resp.text)[0][1:-4]
        return cpolar_url
    except IndexError:
        raise RuntimeError("cpolar不存在正在运行的tunnel！")
