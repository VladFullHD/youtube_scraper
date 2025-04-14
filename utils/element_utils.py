import logging
from selenium.common import NoSuchElementException
from selenium.webdriver.common.by import By


logger = logging.getLogger(__name__)

def get_elements(driver, css_selectors, selector_key, error_message):
    try:
        elements = driver.find_elements(By.CSS_SELECTOR, css_selectors[selector_key])
        logger.info(f'Найдено {len(elements)} элементов видео.')
        return elements
    except NoSuchElementException:
        logger.warning(error_message)
        return []
    except Exception as e:
        logger.error(f'Произошла ошибка при получении элементов {selector_key}: {e}.')
        return []

def get_element_text(element, css_selectors, selector_key, error_message):
    try:
        element_text = element.find_element(By.CSS_SELECTOR, css_selectors[selector_key]).text.strip()
        logger.info(f'Текст элемента {selector_key} получен успешно.')
        return element_text
    except NoSuchElementException:
        logger.warning(error_message)
        return ''
    except Exception as e:
        logger.error(f'Произошла ошибка при получении текста элемента {selector_key}: {e}.')
        return ''

def get_element_attribute(element, css_selectors, selector_key, attribute, error_message):
    try:
        element_attribute = element.find_element(By.CSS_SELECTOR, css_selectors[selector_key]).get_attribute(attribute)
        logger.info(f'Атрибут {attribute} элемента {selector_key} получен успешно.')
        return element_attribute
    except NoSuchElementException:
        logger.warning(error_message)
        return ''
    except Exception as e:
        logger.error(f'Произошла ошибка при получении атрибута {attribute} элемента {selector_key}: {e}.')
        return ''