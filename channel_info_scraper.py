import logging
import time
from collections import OrderedDict
from selenium.common import NoSuchElementException
from selenium.webdriver import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from utils import click_element, get_functions_from_user

logger = logging.getLogger(__name__)


class ChannelBase:
    def __init__(self, driver, css_selectors):
        self.driver = driver
        self.css_selectors = css_selectors
        self.logger = logging.getLogger(__name__)

    def click_element(self, selector_key, timeout=1):
        click_element(self.driver, self.css_selectors, selector_key)

    def channel_filter_click(self, filters):
        if filters == '1':
            self.click_element('popular_filter')
            time.sleep(1)
        elif filters == '2':
            self.click_element('old_filter')
            time.sleep(1)


class ChannelInfo(ChannelBase):

    def __init__(self, driver, css_selectors):
        super().__init__(driver, css_selectors)
        self.info_functions = {
            'subscribers': self.get_channel_subscribers,
            'number_of_videos': self.get_channel_number_videos,
            'full_name': self.get_channel_full_name,
            'name': self.get_channel_name,
            'main_description': self.get_channel_main_description,
            'links': self.get_channel_links,
            'country': self.get_channel_country,
            'registration_date': self.get_channel_registration_date,
            'total_views': self.get_channel_total_views,
            'banner': self.get_channel_banner,
            'profile_picture': self.get_channel_profile_picture
        }

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


    def scraping_channel_info(self, selected_channel_info):
        channel_data = {}
        for func in selected_channel_info:
            current_scraper_functions = {}
            if func in self.info_functions:
                self.logger.debug(f'Выбрана функция {func} для сбора информации.')
                current_scraper_functions[func] = self.info_functions[func]

            collected_data = {}
            for key in current_scraper_functions:
                collected_data[key] = current_scraper_functions[key]()
            channel_data.update(collected_data)

        self.click_element('channel_description_close_button')

        return channel_data

    def get_info_functions(self):
        available_info = list(self.info_functions.keys())
        return get_functions_from_user('канале', available_info)

class ChannelVideo(ChannelBase):
    def __init__(self, driver, css_selectors):
        super().__init__(driver, css_selectors)
        self.video_functions = {
            'title': self.get_channel_video_title,
            'url': self.get_channel_video_url,
            'views': self.get_channel_video_views,
            'release_date': self.get_channel_video_release_date,
            'preview': self.get_channel_video_preview
        }

    def get_channel_all_video_elements(self):
        try:
            all_video_elements = self.driver.find_elements(By.CSS_SELECTOR, self.css_selectors['channel_all_videos'])
            number_of_videos = len(all_video_elements)
            print(f'Найдено видеороликов на канале: {number_of_videos}.')
            self.logger.info(f'Все элементы видеороликов найдены успешно. \nНайдено всего: {number_of_videos} видео.')
            return all_video_elements
        except NoSuchElementException:
            self.logger.warning('Не удалось найти ни одного элемента видеороликов.')
            return 'Не удалось найти ни одного элемента видеороликов.'
        except Exception as e:
            self.logger.error(f'Произошла ошибка при сборе элементов видеороликов: {e}')

    def get_channel_video_title(self, video_element):
        try:
            video_title_element = video_element.find_element(By.CSS_SELECTOR, self.css_selectors['channel_video_title'])
            self.logger.info('Название видео найдено успешно.')
            return video_title_element.text.strip()
        except NoSuchElementException:
            self.logger.warning('Название видео не найдено.')
            return 'Название видео не найдено.'
        except Exception as e:
            self.logger.error(f'Произошла ошибка при сборе названия видео: {e}.')
            return None

    def get_channel_video_url(self, video_element):
        try:
            video_url_element = video_element.find_element(By.CSS_SELECTOR, self.css_selectors['channel_video_url'])
            video_url = video_url_element.get_attribute('href')
            self.logger.info('Ссылка на видео найдена успешно.')
            return video_url
        except NoSuchElementException:
            self.logger.warning('Ссылка на видео не найдена.')
            return 'Ссылка на видео не найдена.'
        except Exception as e:
            self.logger.error(f'Произошла ошибка при сборе ссылки на видео: {e}.')
            return None

    def get_channel_video_views(self, video_element):
        try:
            video_views_element = video_element.find_element(By.CSS_SELECTOR, self.css_selectors['channel_video_views'])
            self.logger.info('Количество просмотров к видео найдено успешно.')
            return video_views_element.text.strip()
        except NoSuchElementException:
            self.logger.warning('Количество просмотров к видео не найдено.')
            return 'Количество просмотров к видео не найдено.'
        except Exception as e:
            self.logger.error(f'Произошла ошибка при сборе количества просмотров к видео: {e}')
            return None

    def get_channel_video_release_date(self, video_element):
        try:
            video_release_date_element = video_element.find_element(By.CSS_SELECTOR, self.css_selectors['channel_video_release_date'])
            self.logger.info('Дата выхода видео найдена успешно.')
            return video_release_date_element.text.strip()
        except NoSuchElementException:
            self.logger.warning('Дата выхода видео не найдена.')
            return 'Дата выхода видео не найдена.'
        except Exception as e:
            self.logger.error(f'Произошла ошибка при сборе даты выхода видео: {e}.')
            return None

    def get_channel_video_preview(self, video_element):
        try:
            video_preview_element = video_element.find_element(By.CSS_SELECTOR, self.css_selectors['channel_video_preview'])
            video_preview = video_preview_element.get_attribute('src')
            self.logger.info('Превью к видео найдено успешно.')
            return video_preview
        except NoSuchElementException:
            self.logger.warning('Превью к видео не найдено.')
            return 'Превью к видео не найдено.'
        except Exception as e:
            self.logger.error(f'Произошла ошибка при сборе превью к видео: {e}.')
            return None


    def scraping_channel_videos(self, selected_video_info, filters):
        self.click_element('channel_video_button')
        time.sleep(1)

        self.channel_filter_click(filters)

        print('Начинаю прокрутку страницы!')
        body = self.driver.find_element('tag name', 'body')
        last_height = self.driver.execute_script('return window.pageYOffset;')
        while True:
            body.send_keys(Keys.PAGE_DOWN)
            time.sleep(1)
            new_height = self.driver.execute_script('return window.pageYOffset;')
            if new_height == last_height:
                print('Страница прокручена до конца!')
                break
            last_height = new_height

        video_elements = self.get_channel_all_video_elements()
        time.sleep(1)

        video_data = []
        total_videos = len(video_elements)
        for video_number, video_element in enumerate(video_elements, 1):
            self.logger.info(f'\nОбработка видео {video_number} из {total_videos}...')
            video_info = OrderedDict()
            for func in selected_video_info:
                if func in self.video_functions:
                    self.logger.debug(f'Выбрана функция {func} для сбора информации.')
                    current_scraper_functions = self.video_functions[func]
                    video_info[func] = current_scraper_functions(video_element)
                else:
                    self.logger.warning(f'Выбранная пользователем информация не соответствует словарю функций.')

            video_data.append(video_info)

        return video_data

    def get_video_functions(self):
        available_info = list(self.video_functions.keys())
        return get_functions_from_user('видео', available_info)

class ChannelShorts(ChannelBase):
    def __init__(self, driver, css_selectors):
        super().__init__(driver, css_selectors)
        self.shorts_functions = {
            'title': self.get_channel_shorts_title,
            'views': self.get_channel_shorts_views,
            'preview': self.get_channel_shorts_preview
        }

    def get_channel_all_shorts_elements(self):
        try:
            all_shorts_elements = self.driver.find_elements(By.CSS_SELECTOR, self.css_selectors['channel_all_shorts'])
            number_of_shorts = len(all_shorts_elements)
            print(f'Найдено Shorts на канале: {number_of_shorts}.')
            self.logger.info(f'Все элементы Shorts найдены успешно. \nНайдено всего: {number_of_shorts} Shorts.')
            return all_shorts_elements
        except NoSuchElementException:
            self.logger.warning('Не удалось найти ни одного элемента Shorts.')
            return 'Не удалось найти ни одного элемента Shorts.'
        except Exception as e:
            self.logger.error(f'Произошла ошибка при сборе элементов Shorts: {e}.')

    def get_channel_shorts_title(self, video_element):
        try:
            shorts_title_element = video_element.find_element(By.CSS_SELECTOR, self.css_selectors['channel_shorts_title'])
            self.logger.info('Название Shorts найдено успешно.')
            return shorts_title_element.text.strip()
        except NoSuchElementException:
            self.logger.warning('Название Shorts не найдено.')
            return 'Название Shorts не найдено.'
        except Exception as e:
            self.logger.error(f'Произошла ошибка при сборе названия Shorts: {e}.')
            return None

    def get_channel_shorts_views(self, video_element):
        try:
            shorts_views_element = video_element.find_element(By.CSS_SELECTOR, self.css_selectors['channel_shorts_views'])
            self.logger.info('Количество просмотров Shorts найдено успешно.')
            return shorts_views_element.text.strip()
        except NoSuchElementException:
            self.logger.warning('Количество просмотров Shorts не найдено.')
            return 'Количество просмотров Shorts не найдено.'
        except Exception as e:
            self.logger.error(f'Произошла ошибка при сборе количества просмотров Shorts: {e}.')
            return None

    def get_channel_shorts_preview(self, video_element):
        try:
            shorts_preview_element = video_element.find_element(By.CSS_SELECTOR, self.css_selectors['channel_shorts_preview'])
            shorts_preview = shorts_preview_element.get_attribute('src')
            self.logger.info('Превью к Shorts найдено успешно.')
            return shorts_preview
        except NoSuchElementException:
            self.logger.warning('Превью к Shorts не найдено.')
            return 'Превью к Shorts не найдено.'
        except Exception as e:
            self.logger.error(f'Произошла ошибка при сборе превью к Shorts: {e}.')
            return None


    def scraping_channel_shorts(self, selected_shorts_info, filters):
        self.click_element('channel_shorts_button')
        time.sleep(1)

        self.channel_filter_click(filters)

        print('Начинаю прокрутку страницы!')
        body = self.driver.find_element('tag name', 'body')
        last_height = self.driver.execute_script('return window.pageYOffset;')
        while True:
            body.send_keys(Keys.PAGE_DOWN)
            time.sleep(1)
            new_height = self.driver.execute_script('return window.pageYOffset;')
            if new_height == last_height:
                print('Страница прокручена до конца!')
                break
            last_height = new_height

        shorts_elements = self.get_channel_all_shorts_elements()
        time.sleep(1)

        shorts_data = []
        total_shorts = len(shorts_elements)
        for shorts_number, shorts_element in enumerate(shorts_elements, 1):
            self.logger.info(f'\nОбработка Shorts {shorts_number} из {total_shorts}...')
            shorts_info = OrderedDict()
            for func in selected_shorts_info:
                if func in self.shorts_functions:
                    self.logger.debug(f'Выбрана функция {func} для сбора информации.')
                    current_scraper_functions = self.shorts_functions[func]
                    shorts_info[func] = current_scraper_functions(shorts_element)
                else:
                    self.logger.warning(f'Выбранная пользователем информация не соответствует словарю функций.')

            shorts_data.append(shorts_info)

        return shorts_data

    def get_shorts_functions(self):
        available_info = list(self.shorts_functions.keys())
        return get_functions_from_user('Shorts', available_info)