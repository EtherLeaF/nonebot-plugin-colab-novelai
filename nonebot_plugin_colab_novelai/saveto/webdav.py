import time
from io import BytesIO
from typing import Dict, List, Optional

import asyncio
from asyncer import asyncify
from nonebot.log import logger

from webdav4.client import Client as WebDavClient, HTTPError

from ..config import plugin_config


webdav_config: Dict[str, Optional[str]] = plugin_config.nai_save2webdav_info


@asyncify
def upload_file(client: WebDavClient, img: bytes, path: str) -> None:
    try:
        client.upload_fileobj(BytesIO(img), to_path=path, overwrite=True)
        logger.info(f"WebDAV: 图片已保存至{path}！")
    except HTTPError as e:
        logger.warning(f"图片保存失败：{e}")


async def save_img_to_webdav(images: List[bytes], prompts: str) -> None:
    if None in webdav_config.values():
        return

    client = WebDavClient(
        webdav_config["url"],
        auth=(webdav_config["username"], webdav_config["password"]),
        timeout=None
    )

    localtime = time.asctime(time.localtime())
    folder_path = f"{webdav_config['path'].strip('/')}/{localtime}".replace(' ', '_').replace(':', '-')
    client.mkdir(folder_path)

    client.upload_fileobj(BytesIO(bytes(prompts, 'utf-8')), to_path=f"{folder_path}/prompts.txt", overwrite=True)
    img_upload_tasks = [
        asyncio.create_task(upload_file(client, img=image, path=f"{folder_path}/{i}.png"))
        for i, image in enumerate(images)
    ]
    await asyncio.gather(*img_upload_tasks)
