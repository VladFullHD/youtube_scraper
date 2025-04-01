import logging
import time

from selenium.common import TimeoutException, NoSuchElementException
from selenium.webdriver.common.keys import Keys
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

    channel_scraper_functions = {
        'subscribers': get_channel_subscribers,
        'number_of_videos': get_channel_number_videos
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