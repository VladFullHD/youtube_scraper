import undetected_chromedriver as uc


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