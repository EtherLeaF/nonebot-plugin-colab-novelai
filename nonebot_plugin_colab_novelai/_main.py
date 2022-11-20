import time
from functools import reduce
from argparse import Namespace
from typing import Type, Any, Optional

import asyncio
from asyncer import asyncify
from nonebot.log import logger
from nonebot.params import T_State
from nonebot.matcher import Matcher
from nonebot.adapters.onebot.v11 import MessageEvent, GroupMessageEvent, MessageSegment

from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as ec
from selenium.common.exceptions import NoSuchElementException, TimeoutException

from .saveto import save_content
from .access.bce import recognize_audio
from .access.colab import NOTEBOOK_URL, run_colab
from .access.cpolar import get_cpolar_authtoken, get_cpolar_url
from .access.naifu import txt2img, img2img
from .config import plugin_config
from .utils import (
    chrome_driver as driver,
    fetch_image_in_message,
    force_refresh_webpage, wait_and_click_element,
    preprocess_painting_parameters
)
from .permissionManager import CooldownManager, NotSafeForWorkManager


# ———————————————————— scheduled jobs ———————————————————— #
@asyncify
def handle_recaptcha() -> None:
    # listen to recaptcha iframe
    try:
        driver.switch_to.frame(driver.find_element(By.XPATH, '/html/body/colab-recaptcha-dialog/div/div/iframe'))
    except NoSuchElementException:
        return

    # click recaptcha checkbox
    checkbox = WebDriverWait(driver, 3).until(ec.element_to_be_clickable(
        (By.CSS_SELECTOR, "div.recaptcha-checkbox-checkmark")
    ))
    driver.execute_script("arguments[0].click();", checkbox)
    driver.switch_to.default_content()

    # detect if reCaptcha iframe still exists
    try:
        time.sleep(2)
        driver.switch_to.frame(driver.find_element(
            By.XPATH, '//iframe[contains(@src,"https://www.google.com/recaptcha/api2/bframe")]'
        ))
    except NoSuchElementException:
        logger.success("Colab ReCaptcha passed!")
        return
    # switch to audio task
    try:
        wait_and_click_element(
            driver,
            by=By.CSS_SELECTOR, value='button#recaptcha-audio-button'
        )
    except TimeoutException:
        pass

    # analyze audio
    while True:
        # get audio link
        try:
            recap_audio_link = WebDriverWait(driver, 3).until(
                lambda t_driver: t_driver.find_element(
                    By.XPATH, '//*[@id="rc-audio"]/div[7]/a'
                )
            ).get_attribute("href")
        # if blocked by Google
        except TimeoutException:
            force_refresh_webpage(driver, NOTEBOOK_URL)
            logger.error("获取Colab ReCaptcha语音时被拦截！")
            return

        answer = recognize_audio(url=recap_audio_link)
        # input answer
        answer_box = wait_and_click_element(
            driver,
            by=By.XPATH, value='//*[@id="audio-response"]'
        )
        answer_box.send_keys(answer, Keys.ENTER)

        try:
            # if answer is wrong
            WebDriverWait(driver, 3).until(ec.visibility_of_element_located(
                (By.XPATH, '//div[@class="rc-audiochallenge-error-message"]')
            ))
            # refresh audio
            wait_and_click_element(
                driver,
                by=By.XPATH, value='//*[@id="recaptcha-reload-button"]'
            )
            logger.warning("Colab ReCaptcha音频验证答案错误！")
        # answer is correct
        except TimeoutException:
            logger.success("Colab ReCaptcha passed!")
            break

    # detect warning dialog: exceeding GPU usage limit
    driver.switch_to.default_content()
    try:
        WebDriverWait(driver, 3).until(
            lambda t_driver: t_driver.find_element(
                By.XPATH, '/html/body/colab-dialog'
            )
        )

        logger.error("当前账号已达到GPU用量上限！")
        force_refresh_webpage(driver, NOTEBOOK_URL)
    # no such warning
    except TimeoutException:
        pass


async def access_colab_with_accounts() -> None:
    cpolar_authtoken = await get_cpolar_authtoken()

    # iter Google accounts
    for gmail, password in plugin_config.google_accounts.items():
        try:
            await run_colab(gmail, password, cpolar_authtoken)
        except RuntimeError as e:
            logger.error(e)
            logger.info("尝试切换Google账号中...")
            continue

        # wait 10min until application startup complete
        start = time.time()
        while time.time() - start < 600:
            try:
                await get_cpolar_url()
                break
            except RuntimeError:
                logger.info(f"等待APP启动中... ({round(time.time() - start, 1)}s/600s) 当前账号：{gmail}")
                await asyncio.sleep(5)
        if time.time() - start >= 600:
            logger.error(f"Colab未成功启动，可能是因为ReCaptcha验证失败或已达到用量上限！当前账号：{gmail}")
            logger.info("尝试切换Google账号中...")
            continue

        logger.success("成功连接至APP！")
        while True:
            await asyncio.sleep(30)

            try:
                await get_cpolar_url()
                logger.info(f"当前Colab账号在线中：{gmail}")
            except RuntimeError:
                logger.warning(f"当前Colab账号已掉线：{gmail}")
                logger.info("尝试切换Google账号中...")
                break


# ———————————————————— user interactions ———————————————————— #
async def naifu_txt2img(matcher: Type[Matcher], event: MessageEvent, args: Namespace, **kwargs: Any) -> None:
    # check user cd
    user_id = event.get_user_id()
    remaining_cd = CooldownManager.get_user_cd(user_id)
    if remaining_cd > 0:
        await matcher.finish(f"你的cd还有{round(remaining_cd)}秒哦，可以稍后再来！", at_sender=True)
    # record user cd
    CooldownManager.record_cd(user_id, num=args.num)

    # check nsfw tag availability
    if isinstance(event, GroupMessageEvent):
        group_id = event.group_id
    else:
        group_id = None
    nsfw_available = NotSafeForWorkManager.check_nsfw_available(user_id, group_id)

    # preprocess parameters for painting
    try:
        params = await preprocess_painting_parameters(matcher=matcher, args=args, on_nsfw=nsfw_available)
    except ValueError as e:
        await matcher.finish(str(e), at_sender=True)
    width, height = map(int, args.size.split('x'))

    # draw the images
    try:
        await matcher.send("少女作画中...", at_sender=True)
        images = await txt2img(**params, width=width, height=height)
        image_segment = reduce(
            lambda img1, img2: img1+img2,
            [MessageSegment.image(image) for image in images]
        )
        await matcher.send(image_segment, at_sender=True)

        # save the images
        await save_content(images, params["prompt"], params["uc"])
        await matcher.finish()

    # if any exception occurs
    except (ValueError, RuntimeError) as e:
        # reset user cd
        CooldownManager.record_cd(user_id, num=0)
        await matcher.finish(str(e), at_sender=True)


async def naifu_img2img(
    matcher: Type[Matcher], event: MessageEvent, state: T_State, args: Namespace,
    img: Optional[bytes] = None
) -> None:
    user_id = event.get_user_id()

    # baseimage already fetched
    if img is not None:
        # record user cd
        CooldownManager.record_cd(user_id, num=args.num)

        # draw the images
        try:
            await matcher.send("少女作画中...", at_sender=True)
            images = await img2img(**state, image=img)
            image_segment = reduce(
                lambda img1, img2: img1 + img2,
                [MessageSegment.image(image) for image in images]
            )
            await matcher.send(image_segment, at_sender=True)

            # save the images
            await save_content(images, state["prompt"], state["uc"], baseimage=img)
            await matcher.finish()

        except (ValueError, RuntimeError) as e:
            CooldownManager.record_cd(user_id, num=0)
            await matcher.finish(str(e), at_sender=True)

    # baseimage isn't fetched yet

    # check user cd
    remaining_cd = CooldownManager.get_user_cd(user_id)
    if remaining_cd > 0:
        await matcher.finish(f"你的cd还有{round(remaining_cd)}秒哦，可以稍后再来！", at_sender=True)

    # check if nsfw tags are allowed in current chat
    if isinstance(event, GroupMessageEvent):
        group_id = event.group_id
    else:
        group_id = None
    nsfw_available = NotSafeForWorkManager.check_nsfw_available(user_id, group_id)

    # preprocess parameters for painting
    try:
        params = await preprocess_painting_parameters(matcher=matcher, args=args, on_nsfw=nsfw_available)
        assert 0 <= args.strength <= 0.99, "设置的strength需要在0到0.99之间！"
        assert 0 <= args.noise <= 0.99, "设置的noise需要在0到0.99之间！"
    except (ValueError, AssertionError) as e:
        await matcher.finish(str(e), at_sender=True)

    # inject parameters
    state.update(
        params,
        strength=round(args.strength, 2),
        noise=round(args.noise, 2)
    )

    if event.reply:
        if (image := await fetch_image_in_message(event.reply.message)) is not None:
            state["baseimage"] = image
    if (image := await fetch_image_in_message(event.message)) is not None:
        state["baseimage"] = image

    # wait for "got" procedure and call this function again, with image injected
    # draw the images
