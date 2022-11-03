from typing import List

from .local import save_img_to_local
from .webdav import save_img_to_webdav


async def save_content(images: List[bytes], prompts: str) -> None:
    await save_img_to_local(images=images, prompts=prompts)
    await save_img_to_webdav(images=images, prompts=prompts)
