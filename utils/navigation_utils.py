import logging
import time

from selenium.common import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains


logger = logging.getLogger(__name__)

def click_element(driver, css_selectors, selector_key, timeout=1):
    try:
        element = WebDriverWait(driver, timeout).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, css_selectors[selector_key]))
        )
        ActionChains(driver).move_to_element(element).click().perform()
        logging.info(f'Клик на элемент {selector_key} выполнен успешно.')
    except TimeoutException:
        logging.warning(f'Не удалось кликнуть на элемент {selector_key}.')

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