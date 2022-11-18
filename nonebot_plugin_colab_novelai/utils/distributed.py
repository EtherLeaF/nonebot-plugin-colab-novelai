import os
import uuid
from pathlib import Path
from typing import Any, Type, TypeVar, Optional, Union

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
