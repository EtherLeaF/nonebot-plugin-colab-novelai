from nonebot.rule import ArgumentParser

from ._main import naifu_txt2img, naifu_img2img
from .permissionManager import CooldownManager, NotSafeForWorkManager


'''handle user commands'''
naifu_draw_parser = ArgumentParser()
naifu_draw_subparsers = naifu_draw_parser.add_subparsers()

naifu_txt2img_parser = naifu_draw_subparsers.add_parser("draw")
naifu_txt2img_parser.add_argument('-p', '--prompt', type=str, nargs='+', required=True)
naifu_txt2img_parser.add_argument('-s', '--size', type=str, default="512x768")
naifu_txt2img_parser.add_argument('-n', '--num', type=int, default=1)
naifu_txt2img_parser.add_argument('-r', '--seed', type=int, default=-1)
naifu_txt2img_parser.set_defaults(draw=naifu_txt2img)

naifu_img2img_parser = naifu_draw_subparsers.add_parser("imgdraw")
naifu_img2img_parser.add_argument('-p', '--prompt', type=str, nargs='+', required=True)
naifu_img2img_parser.add_argument('-s', '--size', type=str, default="default")
naifu_img2img_parser.add_argument('-n', '--num', type=int, default=1)
naifu_img2img_parser.add_argument('-r', '--seed', type=int, default=-1)
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
naifu_add_su_parser.add_argument('-u', '--uid', type=str, nargs='+', required=True)
naifu_add_su_parser.set_defaults(operate=CooldownManager.add_authorized_user, gid=[])

naifu_remove_su_parser = naifu_su_subparsers.add_parser("rm")
naifu_remove_su_parser.add_argument('-u', '--uid', type=str, nargs='+', required=True)
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
