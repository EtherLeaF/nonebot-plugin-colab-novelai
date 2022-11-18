from typing import List, Optional

from .local import save_img_to_local
from .webdav import save_img_to_webdav


async def save_content(images: List[bytes], prompts: str, original: Optional[bytes] = None) -> None:
    await save_img_to_local(images=images, prompts=prompts, original=original)
    await save_img_to_webdav(images=images, prompts=prompts, original=original)
