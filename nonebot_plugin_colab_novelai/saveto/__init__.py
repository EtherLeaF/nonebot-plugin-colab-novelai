from typing import List, Optional

from .local import save_img_to_local
from .webdav import save_img_to_webdav


async def save_content(images: List[bytes], prompts: str, uc: str, baseimage: Optional[bytes] = None) -> None:
    await save_img_to_local(images, prompts, uc, baseimage=baseimage)
    await save_img_to_webdav(images, prompts, uc, baseimage=baseimage)
