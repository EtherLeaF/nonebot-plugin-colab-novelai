<div align="center">
  <a href="https://v2.nonebot.dev/store"><img src="https://s2.loli.net/2022/06/16/opBDE8Swad5rU3n.png" width="180" height="180" alt="NoneBotPluginLogo"></a>
  <br>
  <p><img src="https://s2.loli.net/2022/06/16/xsVUGRrkbn1ljTD.png" width="240" alt="NoneBotPluginText"></p>
</div>

<div align="center">

# Nonebot-Plugin-Colab-NovelAI

_✨ 基于框架 [NoneBot2](https://v2.nonebot.dev/) 的AI绘图插件 ✨_
  
<p align="center">
  <img src="https://img.shields.io/github/license/EtherLeaF/nonebot-plugin-colab-novelai" alt="license">
  <img src="https://img.shields.io/badge/python-3.8+-blue.svg" alt="Python">
  <img src="https://img.shields.io/badge/nonebot-2.0.0b4+-red.svg" alt="NoneBot">
  <a href="https://pypi.org/project/nonebot-plugin-colab-novelai">
    <img src="https://badgen.net/pypi/v/nonebot-plugin-colab-novelai" alt="pypi">
  </a>
  <a href="https://pypi.python.org/pypi/nonebot-plugin-colab-novelai">
      <img src="https://img.shields.io/pypi/dm/nonebot-plugin-colab-novelai" alt="pypi download">
  </a>
</p>

</div>

## 功能

- 提供prompt让AI进行绘图
- 可选将图片保存至本地或WebDAV
- 权限管理: 绘图冷却时间与是否允许使用NSFW tag

## 安装

- 使用 nb-cli

```
nb plugin install nonebot_plugin_colab_novelai
```

- 使用 pip

```
pip install nonebot_plugin_colab_novelai
```

## 获取插件帮助与拓展功能

- 可选择接入 [nonebot-plugin-PicMenu](https://github.com/hamo-reid/nonebot_plugin_PicMenu) 以便用户获取插件相关信息与用法
- 可选择接入 [nonebot-plugin-manager](https://github.com/nonepkg/nonebot-plugin-manager) 管理插件黑名单
- 可选择接入 [nonebot-plugin-savor](https://github.com/A-kirami/nonebot-plugin-savor) 通过图片反推tag

## Requirements

- 一台能正常访问外网的服务器 (Colab在中国大陆无法访问）

- 确保服务器已正确安装了Chrome浏览器

- 注册一堆Google新帐号(建议六个以上)，建议绑定手机号以免登录时出现麻烦，<b>千万不要开启多余的安全设置。</b>

- 前往[百度智能云](https://ai.baidu.com/tech/speech)申请免费语音识别服务，注册APP并获取相关密钥
  - 用于绕过Colab ReCaptcha

- 前往[cpolar](https://www.cpolar.com/)注册免费账号
  - 用于Colab的内网穿透

## .env | .env.dev | .env.prod 配置项

```ini
headless_webdriver: bool = True                       # 是否使用无头模式启动浏览器
colab_proxy: Optional[str] = None                     # 如有需要可填写代理地址
google_accounts: Dict[str, str] = {}                  # Required, 填写要使用的谷歌账密 {"account": "password", ...}
cpolar_username: str = None                           # Required, 填写cpolar账号邮箱
cpolar_password: str = None                           # Required, 填写cpolar账号的密码
bce_apikey: str = None                                # Required, 填写百度智能云的API Key
bce_secretkey: str = None                             # Required, 填写百度智能云的Secret Key
naifu_max: int = 1                                    # 一次作图生成的最大图片数量
naifu_cd: int = 0                                     # 每个用户每生成一张图片的冷却时间
nai_save2local_path: Optional[str] = None             # 将图片保存至本地的存储目录, 不填写则不保存
nai_save2webdav_info: Dict[str, Optional[str]] = {
    "url": None,
    "username": None, "password": None,               # 将图片保存至WebDAV需要的相关配置，不填写则不保存
    "path": None
}
nai_nsfw_tags: Optional[List[str] | str] = None       # 自定义可能会生成NSFW图片的tag, 填写一个列表或者一个文件路径
                                                      # 列表: ["tag1", "tag2", "tag3", ...]
                                                      # 若使用文件存储, 需要将tag以逗号分隔，无需引号。
```

### 配置项额外说明

- 如果你正在使用没有图形界面的Linux服务器，请不要更改```headless_webdriver```

- 插件会尝试禁止未授权的用户绘画NSFW图片，通过屏蔽特定tag来实现。预设的一些tag集合位于[/utils/distributed.py](https://github.com/EtherLeaF/nonebot-plugin-colab-novelai/blob/main/nonebot_plugin_colab_novelai/utils/distributed.py)，如果有其他好的预设想法，欢迎pr。
  - 屏蔽的tag集合为```.env```配置项与预设项的并集，匹配时不区分大小写。

- 如需使用代理，支持填写```http://```or```https://```or```socks5://```+```ip:port```

## 如何使用？

触发指令: ```naifu <command> [<subcommands>] [<args>]```

- Command: ```draw```
- CommandPermission: ```Anyone```
- 用于告诉AI开始作图

- 用法: ```naifu draw <PROMPT>... [-i --undesired-content <UNDESIRED_CONTENT>...] [-a --sampling <SAMPLING>] [-t --steps <STEPS>] [-c --scale <SCALE>] [-n --num <NUM>] [-s --size <SIZE>] [-r --seed <SEED>]```
  - ```PROMPT``` 必选参数，指定作画的关键词，以逗号分隔，必须为英语
  - ```-i``` 可选参数，指定作画中想避免出现的内容，以逗号分隔，必须为英语
  - ```-a``` 可选参数，指定采样器，支持以下几种，默认为```k_euler_ancestral```：
    - ```k_euler_ancestral, k_euler, k_lms```
    - ```plms, ddim```
  - ```-t``` 可选参数，指定优化图像的迭代次数，取值范围```1~50```，默认值为```28```
  - ```-c``` 可选参数，值越大越接近描述意图，值越小细节越少自由度越大，取值范围```1.1~100```，默认值为```12```
  - ```-s``` 可选参数，指定图片生成大小，支持以下几种，默认为```512x768```：
    - ```384x640, 512x768, 512x1024 # Portrait```
    - ```640x384, 768x512, 1024x512 # Landscape```
    - ```512x512, 640x640, 1024x1024 # Square```
  - ```-n``` 可选参数，指定图片生成数量，最大值参考```.env```配置项，默认值为```1```
  - ```-r``` 可选参数，指定图片生成种子，取值范围```0 ~ 2³²-1```，默认值为```-1```即随机
<br>

- Command: ```imgdraw```
- CommandPermission: ```Anyone```
- 提供基准图片作图

- 用法: ```naifu imgdraw <PROMPT>... <IMAGE> [-i --undesired-content <UNDESIRED_CONTENT>...] [-a --sampling <SAMPLING>] [-t --steps <STEPS>] [-c --scale <SCALE>] [-n --num <NUM>] [-r --seed <SEED>] [-e strength <STRENGTH>] [-o noise <NOISE>]```
  - ```PROMPT``` 必选参数，指定作画的关键词，以逗号分隔，必须为英语
  - ```IMAGE``` 必选参数，指定作画基准图片
  - ```-i``` 可选参数，指定作画中想避免出现的内容，以逗号分隔，必须为英语
  - ```-a``` 可选参数，指定采样器，支持以下几种，默认为```k_euler_ancestral```：
    - ```k_euler_ancestral, k_euler, k_lms```
    - ```plms, ddim```
  - ```-t``` 可选参数，指定优化图像的迭代次数，取值范围```1~50```，默认值为```50```
  - ```-c``` 可选参数，值越大越接近描述意图，值越小细节越少自由度越大，取值范围```1.1~100```，默认值为```12```
  - ```-n``` 可选参数，指定图片生成数量，最大值参考```.env```配置项，默认值为```1```
  - ```-r``` 可选参数，指定图片生成种子，取值范围```0 ~ 2³²-1```，默认值为```-1```即随机
  - ```-e``` 可选参数，值越低越接近原始图像，取值范围```0~0.99```，默认值为```0.7```
  - ```-o``` 可选参数，值增加会增加细节，一般应低于参数```<STRENGTH>```，取值范围```0~0.99```，默认值为```0.2```
<br>

- Command: ```su```
- CommandPermission: ```Superuser```
- 用于管理插件白名单用户 (白名单用户无绘图cd，在```.env```中```naifu_cd```值为非零时生效)

  - Subcommand: ```ls```
  - 列出当前所有白名单用户
  - 用法: ```naifu su ls```
  <br>
  
  - Subcommand: ```add```
  - 添加白名单用户
  - 用法: ```naifu su add <USER ID>...```
    - 必须指定用户QQ号，可填写多个并以空格分隔
  <br>
  
  - Subcommand: ```rm```
  - 移除白名单用户
  - 用法: ```naifu su rm <USER ID>...```
    - 必须指定用户QQ号，可填写多个并以空格分隔
<br>
  
- Command: ```nsfw```
- CommandPermission: ```Superuser```
- 管理允许绘制NSFW内容的用户与群组
- <b>注意: 群聊中只有当用户和群聊均有权限时才能绘制NSFW内容！</b>

  - Subcommand: ```ls```
  - 列出当前所有允许NSFW内容的用户与群组
  - 用法: ```naifu nsfw ls```
  <br>
  
  - Subcommand: ```add```
  - 添加允许NSFW内容的用户或群组
  - 用法: ```naifu nsfw add [-u --uid <USER ID>...] [-g --gid <GROUP ID>...]```
    - ```-u``` 可选参数，为用户QQ号，可填写多个并以空格分隔
    - ```-g``` 可选参数，为群号，可填写多个并以空格分隔
    - 当两个可选参数均未填写时，默认添加当前所处群聊的群号。
  <br>
  
  - Subcommand: ```rm```
  - 移除允许NSFW内容的用户或群组
  - 用法: ```naifu nsfw rm [-u --uid <USER ID>...] [-g --gid <GROUP ID>...]```
    - ```-u``` 可选参数，为用户QQ号，可填写多个并以空格分隔
    - ```-g``` 可选参数，为群号，可填写多个并以空格分隔
    - 当两个可选参数均未填写时，默认移除当前所处群聊的群号。

在权限配置文件第一次加载时，会自动添加```.env```的```SUPERUSERS```为插件白名单用户以及分配NSFW权限。
