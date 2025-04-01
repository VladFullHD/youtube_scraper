import logging
import time
from selenium.common import TimeoutException, NoSuchElementException
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from driver_utils import setup_options_webdriver
from file_utils import load_json_file, save_json_file


class ChannelScraper:

    def __init__(self, driver, css_selectors, url):
        self.driver = driver
        self.css_selectors = css_selectors
        self.url = url
        self.logger = logging.getLogger(__name__)


    # def _normalize_urls(self, urls):
    #     if isinstance(urls, str):
    #         return [urls]
    #     elif isinstance(urls, list):
    #         normalized_urls = []
    #         for item in urls:
    #             if isinstance(item, str):
    #                 normalized_urls.append(item)
    #             elif isinstance(item, dict) and 'channel_url' in item:
    #                 normalized_urls.append(item['channel_url'])
    #         return normalized_urls
    #     else:
    #         return []
    #
    # def get_channel_urls(self):
    #     while True:
    #         source = input('Откуда взять ссылки на каналы?\n1. Консоль.\n2. JSON-файл.')
    #         if source == '1':
    #             urls = input('Введите ссылки на каналы через пробел: ').split()
    #             return self._normalize_urls(urls)
    #         elif source == '2':
    #             filename = input('Введите имя JSON-файла: ')
    #             input_data = load_json_file(filename)
    #             return self._normalize_urls(input_data)

    def click_element(self, selector_key, timeout=1):
        """
        Кликает на элемент веб-страницы, используя CSS-селектор.

        Args:
            selector_key (str): Ключ для поиска значения в css_selectors.
            timeout (int, optional): Максимальное время ожидания элемента в секундах. По умолчанию = 2.

        Returns:
            None
        """
        try:
            element = WebDriverWait(self.driver, timeout).until(
                EC.visibility_of_element_located((By.CSS_SELECTOR, self.css_selectors[selector_key]))
            )
            ActionChains(self.driver).move_to_element(element).click().perform()
            self.logger.info(f'Клик на элемент {selector_key} выполнен успешно.')
        except TimeoutException:
            self.logger.warning(f'Не удалось кликнуть на элемент {selector_key}.')


    def get_channel_subscribers(self):
        try:
            subscribers_element = self.driver.find_element(By.CSS_SELECTOR, self.css_selectors['channel_subscribers'])
            self.logger.info('Количество подписчиков найдено успешно.')
            return subscribers_element.text.strip()
        except NoSuchElementException:
            self.logger.warning('Не удалось найти количество подписчиков.')
            return 'Не удалось найти количество подписчиков.'
        except Exception as e:
            self.logger.error(f'Произошла ошибка при сборе количества подписчиков: {e}.')
            return None

    def get_channel_number_videos(self):
        try:
            number_videos_element = self.driver.find_element(By.CSS_SELECTOR, self.css_selectors['channel_number_videos'])
            self.logger.info('Количество видеороликов найдено успешно.')
            return number_videos_element.text.strip()
        except NoSuchElementException:
            self.logger.warning('Не удалось найти количество видеороликов.')
            return 'Не удалось найти количество видеороликов.'
        except Exception as e:
            self.logger.error(f'Произошла ошибка при сборе количества видеороликов: {e}.')
            return None

    def get_channel_full_name(self):
        try:
            channel_full_name_element = self.driver.find_element(By.CSS_SELECTOR, self.css_selectors['channel_full_name'])
            self.logger.info('Полное название канала найдено успешно.')
            return channel_full_name_element.text.strip()
        except NoSuchElementException:
            self.logger.warning('Полное название канала не найдено.')
            return 'Полное название канала не найдено.'
        except Exception as e:
            self.logger.error(f'Произошла ошибка при сборе полного названия канала: {e}.')
            return None

    def get_channel_name(self):
        try:
            channel_name_element = self.driver.find_element(By.CSS_SELECTOR, self.css_selectors['channel_name'])
            self.logger.info('Название канала найдено успешно.')
            return channel_name_element.text.strip()
        except NoSuchElementException:
            self.logger.warning('Название канала не найдено.')
            return 'Название канала не найдено.'
        except Exception as e:
            self.logger.error(f'Произошла ошибка при сборе названия канала: {e}.')
            return None

    def get_channel_main_description(self):
        self.click_element('channel_description_button')
        try:
            main_description_element = WebDriverWait(self.driver, 1).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, self.css_selectors['channel_main_description']))
            )
            self.logger.info('Основное описание канала найдено успешно.')
            return main_description_element.text.strip()
        except NoSuchElementException:
            self.logger.warning('Основное описание канала не найдено.')
            return 'Основное описание канала не найдено.'
        except Exception as e:
            self.logger.error(f'Произошла ошибка при сборе основного описания канала: {e}.')
            return None

    def get_channel_links(self):
        try:
            channel_links_element = self.driver.find_element(By.CSS_SELECTOR, self.css_selectors['channel_links'])
            self.logger.info('Ссылки из описания канала найдены успешно.')
            return channel_links_element.text.strip()
        except NoSuchElementException:
            self.logger.warning('Ссылки из описания канала не найдены.')
            return 'Ссылки из описания канала не найдены.'
        except Exception as e:
            self.logger.error(f'Произошла ошибка при сборе ссылок из описания канала: {e}.')
            return None

    def get_channel_country(self):
        try:
            channel_country_element = self.driver.find_element(By.CSS_SELECTOR, self.css_selectors['channel_country'])
            self.logger.info('Страна канала найдена успешно.')
            return channel_country_element.text.strip()
        except NoSuchElementException:
            self.logger.warning('Страна канала не найдена.')
            return 'Страна канала не найдена.'
        except Exception as e:
            self.logger.error(f'Произошла ошибка при сборе информации о стране канала: {e}.')
            return None

    def get_channel_registration_date(self):
        try:
            channel_registration_element = self.driver.find_element(By.CSS_SELECTOR, self.css_selectors['channel_registration_date'])
            self.logger.info('Дата регистрации канала найдена успешно.')
            return channel_registration_element.text.strip()
        except NoSuchElementException:
            self.logger.warning('Дата регистрации канала не найдена.')
            return 'Дата регистрации канала не найдена.'
        except Exception as e:
            self.logger.error(f'Произошла ошибка при сборе информации о дате регистрации канала: {e}.')
            return None

    def get_channel_total_views(self):
        try:
            channel_total_views_element = self.driver.find_element(By.CSS_SELECTOR, self.css_selectors['channel_total_views'])
            self.logger.info('Общее количество просмотров на канале найдено успешно.')
            return channel_total_views_element.text.strip()
        except NoSuchElementException:
            self.logger.warning('Общее количество просмотров на канале не найдено.')
            return 'Общее количество просмотров на канале не найдено.'
        except Exception as e:
            self.logger.error(f'Произошла ошибка при сборе информации об общем количестве просмотров на канале: {e}.')
            return None

    def get_channel_banner(self):
        try:
            channel_banner_element = self.driver.find_element(By.CSS_SELECTOR, self.css_selectors['channel_banner'])
            channel_banner = channel_banner_element.get_attribute('src')
            self.logger.info('Баннер канала найден успешно.')
            return channel_banner
        except NoSuchElementException:
            self.logger.warning('Баннер канала не найден.')
            return 'Баннер канала не найден.'
        except Exception as e:
            self.logger.warning(f'Произошла ошибка при сборе ссылки на баннер канала: {e}.')
            return None

    def get_channel_profile_picture(self):
        try:
            channel_profile_picture_element = self.driver.find_element(By.CSS_SELECTOR, self.css_selectors['channel_banner'])
            channel_profile_picture = channel_profile_picture_element.get_attribute('src')
            self.logger.info('Фото профиля канала найдено успешно.')
            return channel_profile_picture
        except NoSuchElementException:
            self.logger.warning('Фото профиля канала не найдено.')
            return 'Фото профиля канала не найдено.'
        except Exception as e:
            self.logger.warning(f'Произошла ошибка при сборе ссылки на фото профиля канала: {e}.')
            return None

    channel_scraper_functions = {
        'subscribers': get_channel_subscribers,
        'number_of_videos': get_channel_number_videos,
        'full_name': get_channel_full_name,
        'name': get_channel_name,
        'main_description': get_channel_main_description,
        'links': get_channel_links,
        'country': get_channel_country,
        'registration_date': get_channel_registration_date,
        'total_views': get_channel_total_views,
        'banner': get_channel_banner,
        'profile_picture': get_channel_profile_picture
    }

    def info_from_user(self):
        """
        Запрашивает у пользователя, какую информацию необходимо собрать.

        Returns:
            list[str]: Список выбранных пользователем параметров для сбора данных.

        """
        available_info = list(self.channel_scraper_functions.keys())
        while True:
            print('Выберите, какую информацию необходимо собрать:')
            for i, function in enumerate(available_info):
                print(f'{i + 1}. {function}')

            selected_numbers = input('Введите номера для сбора желаемой информации через пробел\n(Или нажмите Enter для сбора всей информации): ')
            if not selected_numbers:
                self.logger.info('Выбор необходимой для сбора информации был пропущен.')
                selected_info = available_info
                break

            else:
                try:
                    selected_numbers = [int(i) - 1 for i in selected_numbers.split()]
                    selected_info = [available_info[i] for i in selected_numbers if 0 <= i <len(available_info)]
                    break
                except ValueError:
                    self.logger.warning('Некорректный ввод номеров функций.')
                    print('Некорректный ввод номеров функций!')

        return selected_info

    def scraping_info_from_channels(self, selected_info):
        input_data = self.url

        driver.get(input_data)
        time.sleep(1)

        channels_data = {}

        for func in selected_info:
            current_scraper_functions = {}
            if func in self.channel_scraper_functions:
                self.logger.debug(f'Выбрана функция {func} для сбора информации.')
                current_scraper_functions[func] = self.channel_scraper_functions[func]

            collected_data = {}
            for key in current_scraper_functions:
                collected_data[key] = current_scraper_functions[key](self)
            channels_data.update(collected_data)

        return channels_data

    def main(self, driver):
        selected_info = self.info_from_user()

        channels_data = self.scraping_info_from_channels(selected_info)

        save_json_file(channels_data, 'channels_data.json')

        input('Нажмите Enter, чтобы закрыть драйвер!')
        driver.quit()

if __name__ == '__main__':
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(funcName)s - %(message)s",
        filename='channels_info_scraper.log',
        filemode='a',
        encoding='utf-8'
    )
    url = 'https://www.youtube.com/@DarthZak'
    driver = setup_options_webdriver()
    css_selectors = load_json_file('css_selectors.json')
    scraper = ChannelScraper(driver, css_selectors, url)
    scraper.main(driver)