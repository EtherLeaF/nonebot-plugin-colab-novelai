import re
import os
import uuid
import random
from pathlib import Path
from argparse import Namespace
from typing import Tuple, Dict, Any, Type, TypeVar, Optional, Union

import av

from httpx import AsyncClient
from nonebot.matcher import Matcher
from nonebot.params import T_State, Arg
from nonebot.adapters.onebot.v11 import Message

from ..config import plugin_config


T_UserID = TypeVar("T_UserID", str, int)
T_AuthorizedUserID = TypeVar("T_AuthorizedUserID", str, int)
T_GroupID = TypeVar("T_GroupID", str, int)
T_AuthorizedGroupID = TypeVar("T_AuthorizedGroupID", str, int)

os.makedirs("./data/colab-novelai", exist_ok=True)
PLUGIN_DIR = Path(__file__).absolute().parent.parent

if plugin_config.nai_nsfw_tags is None:
    nai_nsfw_tags = set()

elif isinstance(plugin_config.nai_nsfw_tags, list):
    nai_nsfw_tags = set(plugin_config.nai_nsfw_tags)

elif isinstance(plugin_config.nai_nsfw_tags, str):
    with open(plugin_config.nai_nsfw_tags, 'r', encoding='utf-8') as f:
        content = f.read().replace('，', ',')
        nai_nsfw_tags = set(content.split(','))

NSFW_TAGS = nai_nsfw_tags | {
    'nsfw', 'r18', 'nude', 'dick', 'cock', 'penis', 'pussy', 'cum', 'condom', 'nipple', 'penis', 'sex', 'vaginal',
    'straddling', 'doggystyle', 'doggy style', 'doggy-style', 'missionary', 'lick', 'bukkake', 'armpit', 'breasts out',
    'pov', 'rape', 'anal', 'double penetration', 'bdsm', 'milking', 'vibrator', 'ball gag', 'not safe for work'
    'ejaculation', 'piercing', 'bukakke'
}


def get_mac_address() -> str:
    address = hex(uuid.getnode())[2:]
    return '-'.join(address[i:i+2] for i in range(0, len(address), 2))


def convert_audio2wav(fp_in: Any, fp_out: Any, sample_rate: int = 16000) -> None:
    with av.open(fp_in) as buf_in:
        in_stream = buf_in.streams.audio[0]

        with av.open(fp_out, 'w', 'wav') as buf_out:
            out_stream = buf_out.add_stream(
                "pcm_s16le",
                rate=sample_rate,
                layout="mono"
            )
            for frame in buf_in.decode(in_stream):
                for packet in out_stream.encode(frame):
                    buf_out.mux(packet)


async def fetch_image_in_message(message: Message) -> Optional[bytes]:
    try:
        img_url = message["image"][0].data["url"]
    except IndexError:
        return None

    async with AsyncClient() as client:
        resp = await client.get(url=img_url, timeout=30)
        img = await resp.aread()
        return img


async def inject_image_to_state(
    matcher: Matcher, state: T_State,
    image_arg: Union[bytes, Message] = Arg('baseimage')
) -> None:
    if isinstance(image_arg, bytes):
        return

    if (image := await fetch_image_in_message(image_arg)) is None:
        await matcher.finish("格式错误，请重新触发指令..")
    state["baseimage"] = image


def nsfw_tag_filter(prompt: str, uc: str, on: bool = True) -> Tuple[str, str]:
    if on:
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


async def preprocess_painting_parameters(matcher: Type[Matcher], args: Namespace, on_nsfw: bool) -> Dict[str, Any]:
    try:
        assert 1 <= args.num <= plugin_config.naifu_max, "图片数量超过上限！"
        assert -1 <= args.seed <= 2**32 - 1, "设置的种子需要在-1与2^32-1之间！"
        assert 1 <= args.steps <= 50, "设置的steps需要在1到50之间！"
        assert 1.1 <= args.scale <= 100, "设置的scale需要在1.1到100之间！"
    except AssertionError as e:
        await matcher.finish(str(e), at_sender=True)

    prompts, uc = nsfw_tag_filter(
        prompt="masterpiece,best quality," + ' '.join(args.prompt).replace('，', ','),
        uc="lowres, bad anatomy, bad hands, text, error, missing fingers, extra digit, fewer digits, cropped, "
           "worst quality, low quality, normal quality, jpeg artifacts, signature, watermark, username, blurry,"
           + ' '.join(args.undesired_content).replace('，', ',').strip(',') + ',',
        on=on_nsfw
    )
    return {
        "prompt": prompts,
        "uc": uc,
        "n_samples": args.num,
        "seed": random.randint(0, 2**32 - 1) if args.seed == -1 else args.seed,
        "sampler": args.sampling,
        "steps": args.steps,
        "scale": round(args.scale, 1)
    }
