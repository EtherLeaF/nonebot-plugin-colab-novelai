from nonebot.rule import ArgumentParser

from ._main import naifu_txt2img, naifu_img2img
from .permissionManager import CooldownManager, NotSafeForWorkManager


'''handle user commands'''
naifu_draw_parser = ArgumentParser()
naifu_draw_subparsers = naifu_draw_parser.add_subparsers()

# text to image
naifu_txt2img_parser = naifu_draw_subparsers.add_parser("draw")
naifu_txt2img_parser.add_argument('prompt', type=str, nargs='+')
naifu_txt2img_parser.add_argument('-i', '--undesired-content', type=str, nargs='+', default=[])
naifu_txt2img_parser.add_argument(
    '-a', '--sampling', type=str, default="k_euler_ancestral",
    choices=[
        "k_euler_ancestral", "k_euler", "k_lms",  # Recommended
        "plms", "ddim"                            # Other
    ]
)
naifu_txt2img_parser.add_argument('-t', '--steps', type=int, default=28)
naifu_txt2img_parser.add_argument('-c', '--scale', type=float, default=12)
naifu_txt2img_parser.add_argument(
    '-s', '--size', type=str, default="512x768",
    choices=[
        "384x640", "512x768", "512x1024",  # Portrait
        "640x384", "768x512", "1024x512",  # Landscape
        "512x512", "640x640", "1024x1024"  # Square
    ]
)
naifu_txt2img_parser.add_argument('-n', '--num', type=int, default=1)
naifu_txt2img_parser.add_argument('-r', '--seed', type=int, default=-1)
naifu_txt2img_parser.set_defaults(draw=naifu_txt2img)

# image to image
naifu_img2img_parser = naifu_draw_subparsers.add_parser("imgdraw")
naifu_img2img_parser.add_argument('prompt', type=str, nargs='+')
naifu_img2img_parser.add_argument('-i', '--undesired-content', type=str, nargs='+', default=[])
naifu_img2img_parser.add_argument(
    '-a', '--sampling', type=str, default="k_euler_ancestral",
    choices=[
        "k_euler_ancestral", "k_euler", "k_lms",  # Recommended
        "plms", "ddim"                            # Other
    ]
)
naifu_img2img_parser.add_argument('-t', '--steps', type=int, default=50)
naifu_img2img_parser.add_argument('-c', '--scale', type=float, default=12)
naifu_img2img_parser.add_argument('-n', '--num', type=int, default=1)
naifu_img2img_parser.add_argument('-r', '--seed', type=int, default=-1)
naifu_img2img_parser.add_argument('-e', '--strength', type=float, default=0.7)
naifu_img2img_parser.add_argument('-o', '--noise', type=float, default=0.2)
naifu_img2img_parser.set_defaults(draw=naifu_img2img)


'''permission management'''
naifu_perm_parser = ArgumentParser()
naifu_perm_subparsers = naifu_perm_parser.add_subparsers()

# superuser (without cd)
naifu_su_parser = naifu_perm_subparsers.add_parser("su")
naifu_su_subparsers = naifu_su_parser.add_subparsers()

naifu_ls_su_parser = naifu_su_subparsers.add_parser("ls")
naifu_ls_su_parser.set_defaults(operate=CooldownManager.list_authorized_users, uid=[], gid=[])

naifu_add_su_parser = naifu_su_subparsers.add_parser("add")
naifu_add_su_parser.add_argument('uid', type=str, nargs='+')
naifu_add_su_parser.set_defaults(operate=CooldownManager.add_authorized_user, gid=[])

naifu_remove_su_parser = naifu_su_subparsers.add_parser("rm")
naifu_remove_su_parser.add_argument('uid', type=str, nargs='+')
naifu_remove_su_parser.set_defaults(operate=CooldownManager.remove_authorized_user, gid=[])

# nsfw mode
naifu_nsfw_parser = naifu_perm_subparsers.add_parser("nsfw")
naifu_nsfw_subparsers = naifu_nsfw_parser.add_subparsers()

naifu_ls_nsfw_parser = naifu_nsfw_subparsers.add_parser("ls")
naifu_ls_nsfw_parser.set_defaults(operate=NotSafeForWorkManager.list_authorized_users, uid=[], gid=[])

naifu_add_nsfw_parser = naifu_nsfw_subparsers.add_parser("add")
naifu_add_nsfw_parser.add_argument('-u', '--uid', type=str, nargs='+', default=[])
naifu_add_nsfw_parser.add_argument('-g', '--gid', type=str, nargs='+', default=[])
naifu_add_nsfw_parser.set_defaults(operate=NotSafeForWorkManager.add_authorized_user)

naifu_remove_nsfw_parser = naifu_nsfw_subparsers.add_parser("rm")
naifu_remove_nsfw_parser.add_argument('-u', '--uid', type=str, nargs='+', default=[])
naifu_remove_nsfw_parser.add_argument('-g', '--gid', type=str, nargs='+', default=[])
naifu_remove_nsfw_parser.set_defaults(operate=NotSafeForWorkManager.remove_authorized_user)
