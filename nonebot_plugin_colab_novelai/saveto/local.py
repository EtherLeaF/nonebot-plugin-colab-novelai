import os
import time
from typing import List
from pathlib import Path

import anyio
from nonebot.log import logger

from ..config import plugin_config


nai_save2local_path = plugin_config.nai_save2local_path

if nai_save2local_path is not None:
    nai_save2local_path = Path(nai_save2local_path).absolute()
    os.makedirs(nai_save2local_path, exist_ok=True)
    logger.info(f"NovelAI返回的数据将保存到{nai_save2local_path}！")


async def save_img_to_local(images: List[bytes], prompts: str) -> None:
    if nai_save2local_path is None:
        return

    localtime = time.asctime(time.localtime())
    folder_path = nai_save2local_path/localtime.replace(' ', '_').replace(':', '-')
    os.makedirs(folder_path, exist_ok=True)

    for i, image in enumerate(images):
        async with await anyio.open_file(folder_path/f"{i}.png", "wb") as f:
            await f.write(image)

    async with await anyio.open_file(folder_path/"prompts.txt", "w") as f:
        await f.write(prompts)

    logger.success("图片已保存至本地！")
