import requests
from io import BytesIO

from ..config import plugin_config
from ..utils import convert_audio2wav, get_mac_address

API_KEY = plugin_config.bce_apikey
SECRET_KEY = plugin_config.bce_secretkey
API_URL = "http://vop.baidu.com/server_api"
TOKEN_URL = "https://aip.baidubce.com/oauth/2.0/token"


def fetch_token(api_key: str, secret_key: str) -> str:
    params = {
        "grant_type": "client_credentials",
        "client_id": api_key,
        "client_secret": secret_key
    }
    result = requests.post(TOKEN_URL, data=params).json()

    try:
        err_des = result["error_description"]
        if err_des == "unknown client id":
            raise RuntimeError("请检查百度API Key！")
        elif err_des == "Client authentication failed":
            raise RuntimeError("请检查百度Secret Key！")
    # as expected
    except KeyError:
        return result["access_token"]


def recognize_audio(url: str) -> str:
    audio_content = requests.get(url).content

    buf_in = BytesIO(audio_content)
    buf_out = BytesIO()
    convert_audio2wav(buf_in, buf_out)

    audio_content = buf_out.getvalue()
    bce_token = fetch_token(API_KEY, SECRET_KEY)
    mac_address = get_mac_address()

    header = {
        "Content-Type": "audio/wav;rate=16000"
    }
    params = {
        "cuid": mac_address,
        "token": bce_token,
        "dev_pid": 1737,
    }
    result = requests.post(API_URL, params=params, data=audio_content, headers=header).json()
    if result["err_no"] != 0:
        raise RuntimeError(
            f"百度API返回错误码：{result['err_no']}，"
            f"请参考文档：https://ai.baidu.com/ai-doc/SPEECH/pkgw0bw1p"
        )

    answer = ' '.join(result["result"])
    if answer == '':
        raise ValueError("语音未识别出结果！")
    return answer


# Startup autocheck
fetch_token(API_KEY, SECRET_KEY)
