import re
import base64
from io import BytesIO
from typing import List, Tuple

from PIL import Image
from httpx import AsyncClient

from .cpolar import get_cpolar_url
from ..utils import NSFW_TAGS

SIZE = [i*64 for i in range(1, 17)]


def nsfw_tag_filtering(prompt: str, uc: str) -> Tuple[str, str]:
    uc += ','.join(NSFW_TAGS)

    prompts = set(prompt.split(','))
    for p in prompts.copy():
        for nsfw_tag in NSFW_TAGS:
            if re.match(nsfw_tag, p, flags=re.I) is not None:
                prompts.discard(p)
    if not prompts:
        raise ValueError("色鬼，好好检查一下你都放了些什么tag进来！")
    prompt = ','.join(prompts)

    return prompt, uc


# textual prompts -> picture
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


# original image + textual prompts -> picture
async def img2img(
    prompt: str,
    image: bytes,
    seed: int,
    n_samples: int = 1,
    sampler: str = "k_euler_ancestral",
    steps: int = 28,
    scale: int = 12,
    strength: float = 0.7,
    noise: float = 0.2,
    uc: str = "lowres, bad anatomy, bad hands, text, error, missing fingers, extra digit, fewer digits, cropped, "
              "worst quality, low quality, normal quality, jpeg artifacts, signature, watermark, username, blurry,",
    uc_preset: int = 0,
    nsfw: bool = False
) -> List[bytes]:
    # data preprocessing
    if not nsfw:
        prompt, uc = nsfw_tag_filtering(prompt, uc)

    image = Image.open(BytesIO(image))
    if (bound := max(image.size)) > 1024:
        target_size = tuple(map(lambda x: x/bound*1024, image.size))
    else:
        target_size = image.size
    width, height = map(
        lambda s: min(SIZE, key=lambda x: abs(x - s)),
        target_size
    )
    image = image.resize((width, height), resample=Image.ANTIALIAS)

    image_buf = BytesIO()
    image.save(image_buf, format='PNG')
    image_b64 = base64.b64encode(image_buf.getvalue()).decode()

    # fetch output
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
            "image": image_b64,
            "width": width, "height": height,
            "n_samples": n_samples,
            "sampler": sampler,
            "steps": steps,
            "scale": scale,
            "strength": strength,
            "noise": noise,
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

    except RuntimeError as exc:
        raise RuntimeError("暂时没有资源可供作图哦，可以稍后再来！") from exc
