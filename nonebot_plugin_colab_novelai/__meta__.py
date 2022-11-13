from nonebot.plugin import PluginMetadata
from nonebot.adapters.onebot.v11 import Adapter as OneBotV11Adapter

from .config import Config as __PluginConfigModel__, plugin_config


__plugin_name__ = "Colab-NovelAI"
__plugin_version__ = "0.1.1"
__plugin_author__ = "T_EtherLeaF <thetapilla@gmail.com>"

__plugin_adapters__ = [OneBotV11Adapter]
__plugin_des__ = "由Colab提供算力进行AI作画！"
__plugin_usage__ = (
    "让AI帮你画出好康的图片吧！\n"
    "触发指令：naifu <command> [<subcommands>] [<args>]\n"
    ".\n"
    "查看具体用法请发送指令：菜单 NovelAI <功能序号>\n"
    "子命令集如下："
)


__plugin_meta__ = PluginMetadata(
    name="NovelAI",
    description=__plugin_des__,
    usage=__plugin_usage__,
    config=__PluginConfigModel__,
    extra={
        'unique_name': __plugin_name__,
        'author': __plugin_author__,
        'version': __plugin_version__,
        'adapters': __plugin_adapters__,
        'menu_data': [
            {
                'func': '作图',
                'trigger_method': '子命令：draw',
                'trigger_condition': 'Anyone',
                'brief_des': '告诉AI开始作图',
                'detail_des': f'naifu draw <-p --prompt <PROMPT>...> '
                              f'[-s --size <SIZE>] [-n --num <NUM>] [-s --seed <SEED>]\n'
                              f' \n'
                              f'-p: 必选参数，指定作画的关键词，以逗号分隔，必须为英语\n'
                              f'-s: 可选参数，指定图片生成大小，支持以下几种，默认为512x768：\n'
                              f'  384x640, 512x768, 512x1024   # Portrait\n'
                              f'  640x384, 768x512, 1024x512   # Landscape\n'
                              f'  512x512, 640x640, 1024x1024  # Square\n'
                              f'-n: 可选参数，指定图片生成数量，最大为{plugin_config.naifu_max}，默认值为1\n'
                              f'-r: 可选参数，指定图片生成种子，取值范围0 ~ 2^32-1，默认值为-1即随机'
            },
            {
                'func': '白名单管理',
                'trigger_method': '子命令：su',
                'trigger_condition': 'Superuser',
                'brief_des': '插件白名单用户组管理(无cd)',
                'detail_des': 'naifu su <subcommand> [<args>]\n'
                              ' \n'
                              ' \n'
                              '# Subcommand 1:\n'
                              'naifu su ls\n'
                              '列出当前所有白名单用户\n'
                              ' \n'
                              '# Subcommand 2:\n'
                              'naifu su add <-u --uid <USER ID>...>\n'
                              '添加白名单用户\n'
                              '-u: 必选参数，为用户QQ号，可填写多个并以空格分隔\n'
                              ' \n'
                              '# Subcommand 3:\n'
                              'naifu su rm <-u --uid <USER ID>...>\n'
                              '移除白名单用户\n'
                              '-u: 必选参数，为用户QQ号，可填写多个并以空格分隔'
            },
            {
                'func': 'NSFW权限管理',
                'trigger_method': '子命令：nsfw',
                'trigger_condition': 'Superuser',
                'brief_des': '管理允许绘制NSFW内容的用户与群组',
                'detail_des': 'naifu nsfw <subcommand> [<args>]\n'
                              ' \n'
                              ' \n'
                              '# Subcommand 1:\n'
                              'naifu nsfw ls\n'
                              '列出当前所有允许NSFW内容的用户与群组\n'
                              ' \n'
                              '# Subcommand 2:\n'
                              'naifu nsfw add [-u --uid <USER ID>...] [-g --gid <GROUP ID>...]\n'
                              '添加允许NSFW内容的用户或群组\n'
                              '-u: 可选参数，为用户QQ号，可填写多个并以空格分隔\n'
                              '-g: 可选参数，为群号，可填写多个并以空格分隔\n'
                              '当两个可选参数均未填写时，默认添加当前所处群聊的群号。\n'
                              ' \n'
                              '# Subcommand 3:\n'
                              'naifu nsfw rm [-u --uid <USER ID>...] [-g --gid <GROUP ID>...]\n'
                              '移除允许NSFW内容的用户或群组\n'
                              '-u: 可选参数，为用户QQ号，可填写多个并以空格分隔\n'
                              '-g: 可选参数，为群号，可填写多个并以空格分隔\n'
                              '当两个可选参数均未填写时，默认移除当前所处群聊的群号。'
            }
        ]
    }
)
