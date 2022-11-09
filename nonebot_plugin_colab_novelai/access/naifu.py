import re
import base64
from typing import List, Tuple

from httpx import AsyncClient

from .cpolar import get_cpolar_url
from ..utils import NSFW_TAGS


def nsfw_tag_filtering(prompt: str, uc: str) -> Tuple[str, str]:
    uc += ','.join(NSFW_TAGS)

    prompts = set(prompt.split(','))
    for p in prompts.copy():
        for nsfw_tag in NSFW_TAGS:
            if re.findall(nsfw_tag, p, flags=re.I):
                prompts.discard(p)
    if not prompts:
        raise ValueError("色鬼，好好检查一下你都放了些什么tag进来！")
    prompt = ','.join(prompts)

    return prompt, uc


# text prompts -> picture
async def txt2img(
    prompt: str,
    seed: int,
    width: int = 512, height: int = 768,
    n_samples: int = 1,
    sampler: str = "k_euler_ancestral",
    steps: int = 28,
    scale: int = 12,
    uc: str = "lowres, bad anatomy, bad hands, text, error, missing fingers, extra digit, fewer digits, cropped, "
              "worst quality, low quality, normal quality, jpeg artifacts, signature, watermark, username, blurry,",
    uc_preset: int = 0,
    nsfw: bool = False
) -> List[bytes]:
    # data preprocessing
    if not nsfw:
        prompt, uc = nsfw_tag_filtering(prompt, uc)

    try:
        cpolar_url = await get_cpolar_url()
        api_url = cpolar_url + "/generate-stream"
        headers = {
            "content-type": "application/json",
            "accept-encoding": "gzip, deflate, br",
            "authorization": "Bearer"
        }
        data = {
            "prompt": "masterpiece,best quality," + prompt,
            "width": width, "height": height,
            "n_samples": n_samples,
            "sampler": sampler,
            "steps": steps,
            "scale": scale,
            "seed": seed,
            "uc": uc, "ucPreset": uc_preset
        }

        async with AsyncClient() as client:
            resp = await client.get(cpolar_url, timeout=None)
            if resp.status_code in [404, 502]:
                raise RuntimeError("APP暂时还未就绪！")

            result = (await client.post(api_url, json=data, headers=headers, timeout=600)).text
            result = re.findall(r"data:\S+", result)
            images = [base64.b64decode(i[5:]) for i in result]

        return images

    # catch all unexpected events
    except RuntimeError as exc:
        raise RuntimeError("暂时没有资源可供作图哦，可以稍后再来！") from exc


# Upcoming!
async def img2img() -> bytes:
    pass
