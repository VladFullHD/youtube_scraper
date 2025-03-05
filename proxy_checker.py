import requests


def proxy_checker(proxy):
    try:
        proxies = {
            "http": f"socks5://{proxy}",
            "https": f"socks5://{proxy}"
        }
        requests.get('https://www.google.com/intl/ru/account/about/', proxies=proxies, timeout=5)
        print('Работает')
        return True
    except:
        print('Не работает')
        return False