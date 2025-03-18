import undetected_chromedriver as uc
from selenium.webdriver.common.keys import Keys
import time

def scroll_javascript(driver):
    """Плавная прокрутка страницы вниз"""
    last_height = driver.execute_script("return document.body.scrollHeight")
    while True:
        driver.execute_script("window.scrollBy(0, document.body.scrollHeight);")
        time.sleep(1.5)
        new_height = driver.execute_script("return document.body.scrollHeight")
        if new_height == last_height:
            break
        last_height = new_height

def scroll_selenium_keys(driver):
    body = driver.find_element('tag name', 'body')
    last_height = driver.execute_script('return window.pageYOffset;')
    while True:
        body.send_keys(Keys.PAGE_DOWN)
        time.sleep(1)
        new_height = driver.execute_script('return window.pageYOffset;')
        if new_height == last_height:
            print('Страница прокручена до конца!')
            break
        last_height = new_height

def setup_options_webdriver(use_proxy=False, proxy=None):
    options = uc.ChromeOptions()
    if use_proxy and proxy:
        proxy_string = f"--proxy-server=socks5://{proxy}"
        options.add_argument(proxy_string)

    options.add_argument("--lang=ru-RU")
    options.add_argument("--guest")  # Гостевой режим (альтернатива инкогнито)
    options.add_argument(
        "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/133.0.0.0 Safari/537.36"
    )
    options.add_argument("--disable-webrtc")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument('--mute-audio')

    driver = uc.Chrome(options=options)
    driver.maximize_window()

    driver.execute_script("delete navigator.webdriver;")

    return driver