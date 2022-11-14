import time

from asyncer import asyncify
from nonebot.log import logger

from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as ec
from selenium.common.exceptions import TimeoutException, JavascriptException

from ..utils import chrome_driver as driver, force_refresh_webpage, wait_and_click_element, PLUGIN_DIR

NOTEBOOK_URL = "https://colab.research.google.com/drive/1oAMaO-0_SxFSr8OEC1jJVkC84pGFzw-I?usp=sharing"


def login_google_acc(gmail: str, password: str) -> None:
    try:
        # No account logged in yet
        try:
            # click "Sign in"
            login = WebDriverWait(driver, 5).until(
                lambda t_driver: t_driver.find_element(By.XPATH, '//*[@id="gb"]/div/div/a')
            )
            driver.get(login.get_attribute('href'))

        # Already logged in
        except TimeoutException:
            # logout current account
            logout = WebDriverWait(driver, 5).until(
                lambda t_driver: t_driver.find_element(
                    By.XPATH, '//*[@id="gb"]/div/div[1]/div[2]/div/a'
                )
            )
            driver.get(logout.get_attribute('href'))
            driver.find_element(By.XPATH, '//*[@id="signout"]').click()

            # click "Sign in"
            login = WebDriverWait(driver, 5).until(
                lambda t_driver: t_driver.find_element(By.XPATH, '//*[@id="gb"]/div/div/a')
            )
            driver.get(login.get_attribute('href'))

        # if prompt, choose "Use another account" when login
        try:
            wait_and_click_element(
                driver,
                by=By.XPATH,
                value='//*[@id="view_container"]/div/div/div[2]/div/div[1]/div/form/span/section/div/div/div/div/ul'
                      '/li[@class="JDAKTe eARute W7Aapd zpCp3 SmR8" and not(@jsname="fKeql")]'
            )
        except TimeoutException:
            pass

        # input gmail and password
        gmail_input = WebDriverWait(driver, 5).until(ec.element_to_be_clickable(
            (By.XPATH, '//*[@id="identifierId"]')
        ))
        driver.execute_script("arguments[0].click();", gmail_input)
        time.sleep(0.5)
        gmail_input.send_keys(gmail, Keys.ENTER)

        pwd_input = WebDriverWait(driver, 5).until(ec.element_to_be_clickable(
            (By.XPATH, '//*[@id="password"]/div[1]/div/div[1]/input')
        ))
        driver.execute_script("arguments[0].click();", pwd_input)
        time.sleep(0.5)
        pwd_input.send_keys(password, Keys.ENTER)

        # check if the password is incorrect
        try:
            WebDriverWait(driver, 3).until(
                lambda t_driver: t_driver.find_element(
                    By.XPATH, '//*[@id="yDmH0d"]/c-wiz/div/div[2]/div/div[1]/div/form/span/div[1]/div[2]/div[1]'
                )
            )
            raise RuntimeError(f"Google账号{gmail}的密码填写有误！")
        except TimeoutException:
            logger.success(f"成功登入Google账号：{gmail}！")

    except TimeoutException:
        raise RuntimeError(f"登陆Google账号{gmail}发生超时，请检查网络和账密！")

    # In case of Google asking you to complete your account info
    try:
        # Wait for "not now" button occurs
        wait_and_click_element(
            driver,
            by=By.XPATH, value='//*[@id="yDmH0d"]/c-wiz/div/div/div/div[2]/div[4]/div[1]/button'
        )

    # If that doesn't happen
    except TimeoutException:
        pass


@asyncify
def run_colab(gmail: str, password: str, cpolar_authtoken: str) -> None:
    force_refresh_webpage(driver, NOTEBOOK_URL)

    login_google_acc(gmail, password)

    # input cpolar authtoken
    time.sleep(3)
    try:
        authtoken_box = driver.execute_script(
            'return document.querySelector("#cell-54WF-Om0X6tf > div.main-content > div.codecell-input-output > '
            'div.inputarea.horizontal.layout.both > colab-form > div > colab-form-input > div.layout.horizontal.grow > '
            'paper-input").shadowRoot.querySelector("#input-1 > input")'
        )
        authtoken_box.clear()
        authtoken_box.send_keys(cpolar_authtoken)
    except JavascriptException:
        # failed to fill input box
        # mostly, this happens when Google is asking you to do extra verification i.e. phone number
        # Colab page won't be loaded normally, then result in this error.
        raise RuntimeError(
            f"Google账密验证成功，但Colab页面没有被成功加载。可能是因为Google正在要求账号进行额外验证或账号不再可用！"
            f"当前账号：{gmail}"
        )

    # run all cells
    driver.find_element(By.XPATH, '/html/body').send_keys(Keys.CONTROL + Keys.F9)

    # If Google asks you to confirm running this notebook
    try:
        wait_and_click_element(
            driver,
            by=By.XPATH, value='/html/body/colab-dialog/paper-dialog/div[2]/paper-button[2]'
        )
    except TimeoutException:
        pass

    # keep webpage active
    with open(PLUGIN_DIR / "js" / "keepPageActive.js", 'r', encoding='utf-8') as js:
        driver.execute_script(js.read())
