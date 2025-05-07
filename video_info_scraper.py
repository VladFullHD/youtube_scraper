import re
import time
import logging
from collections import OrderedDict
from selenium.common import TimeoutException, NoSuchElementException
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from utils import element_utils, click_element_css, get_functions_from_user

logger = logging.getLogger(__name__)

class VideoInfoBase:
    def __init__(self, driver, css_selectors):
        self.driver = driver
        self.css_selectors = css_selectors
        self.logger = logging.getLogger(__name__)

    def click_element_css(self, selector_key):
        click_element_css(self.driver, self.css_selectors, selector_key)

    def _get_elements(self, selector_key, error_message):
        return element_utils.get_elements(self.driver, self.css_selectors, selector_key, error_message)

    def _get_element_text(self, element, selector_key, error_message):
        return element_utils.get_element_text(element, self.css_selectors, selector_key, error_message)

    def _get_element_attribute(self, element, selector_key, attribute, error_message):
        return element_utils.get_element_attribute(element, self.css_selectors, selector_key, attribute, error_message)

    def is_video_unavailable(self):
        try:
            self.driver.find_element(By.CSS_SELECTOR, self.css_selectors['is_video_unavailable'])
            self.logger.info('Проверка на доступность Video: не пройдена.')
            return True
        except NoSuchElementException:
            self.logger.info('Проверка на доступность Video: пройдена успешно.')
            return False

    def is_video_unacceptable(self):
        try:
            self.driver.find_element(By.CSS_SELECTOR, self.css_selectors['is_video_unacceptable'])
            self.logger.info('Проверка на неприемлемое Video: не пройдена.')
            return True
        except NoSuchElementException:
            self.logger.info('Проверка на неприемлемое Video: пройдена успешно.')
            return False

    def is_shorts_unacceptable(self):
        try:
            self.driver.find_element(By.CSS_SELECTOR, self.css_selectors['is_shorts_unacceptable'])
            self.logger.info('Проверка на неприемлемый Shorts: не пройдена.')
            return True
        except NoSuchElementException:
            self.logger.info('Проверка на неприемлемый Shorts: пройдена успешно.')
            return False


class VideoInfo(VideoInfoBase):
    def __init__(self, driver, css_selectors):
        super().__init__(driver, css_selectors)
        self.video_info_functions = {
            'name': self.get_video_title,
            'views': self.get_video_views,
            'likes': self.get_video_likes,
            'release_date': self.get_video_release_date,
            'comments': self.get_video_comments,
            'description': self.get_video_description
        }

    def get_video_description(self):
        self.click_element_css('video_description_button')
        return self._get_element_text(
            element=self.driver,
            selector_key='video_description',
            error_message='Описание к видео не найдено.'
        )

    def get_video_likes(self):
        aria_label = self._get_element_attribute(
            element=self.driver,
            selector_key='video_likes',
            attribute='aria-label',
            error_message='Лайки к видео не найдены.'
        )

        if aria_label:
            if 'одному пользователю' in aria_label:
                self.logger.info('В элементе "video_likes" содержится фраза "одному пользователю", количество лайков = 0')
                return '0'
            else:
                match = re.search(r"и ещё ([\d\s\xa0]+)", aria_label)
                if match:
                    likes_str = match.group(1).replace("\xa0", "").replace(" ", "")
                    if "тыс" in aria_label:
                        likes = int(likes_str) * 1000
                    elif "млн" in aria_label:
                        likes = int(likes_str) * 1000000
                    else:
                        likes = int(likes_str)

                    formatted_likes = "{:,}".format(likes).replace(",", ".")
                    self.logger.info('Количество лайков в Video найдено успешно.')
                    return formatted_likes

    def get_video_comments(self):
        max_attempts = 10
        attempts = 0
        try:
            try:
                self.driver.find_element(By.CSS_SELECTOR, self.css_selectors['comments_turned_off'])
                self.logger.warning('Комментарии к Video отключены.')
                return 'Комментарии к Video отключены.'
            except NoSuchElementException:
                while attempts < max_attempts:
                    attempts += 1
                    self.logger.info(f'Попытка {attempts}/{max_attempts} поиска количества комментариев в Video.')
                    try:
                        video_comments_element = WebDriverWait(self.driver, 2).until(
                            EC.presence_of_element_located((By.CSS_SELECTOR, self.css_selectors['video_comments']))
                        )
                        self.logger.info('Количество комментариев к Video найдено успешно.')
                        return video_comments_element.text.strip()
                    except TimeoutException:
                        self.logger.info(f'Попытка {attempts}/{max_attempts} не удалась. Приступаю к прокрутке страницы.')
                        self.driver.find_element("tag name", 'html').send_keys(Keys.PAGE_DOWN)
                        time.sleep(0.2)
                self.logger.warning('Достигнуто максимальное количество попыток поиска количества комментариев к Video.')
                return 'Количество комментариев к Video не найдено.'
        except Exception as e:
            self.logger.error(f'Произошла ошибка при сборе количества комментариев к Video: {e}.')
            return None

    def get_video_views(self):
        return self._get_element_text(
            element=self.driver,
            selector_key='video_views',
            error_message='Количество просмотров видео не найдено.'
        )

    def get_video_release_date(self):
        return self._get_element_text(
            element=self.driver,
            selector_key='video_release_date',
            error_message='Дата релиза видео не найдена.'
        )

    def get_video_title(self):
        return self._get_element_text(
            element=self.driver,
            selector_key='video_title',
            error_message='Название видео не найдено.'
        )

    def scraping_video_info(self, filtered_data, selected_video_info_functions):
        video_data = []
        total_videos = len(filtered_data)
        for video_number, video in enumerate(filtered_data, 1):
            self.logger.info(f'\nОбработка видео {video_number} из {total_videos}...')
            self.driver.get(video['url'])
            time.sleep(1)

            video_info = OrderedDict()

            if self.is_video_unavailable():
                video_info['status'] = 'Видео удалено/недоступно'
                video_data.append(video_info)
                continue
            elif self.is_video_unacceptable():
                video_info['status'] = 'YouTube посчитал данное видео неприемлемым!'
                video_data.append(video_info)
                continue

            for func_name in selected_video_info_functions:
                if func_name in self.video_info_functions:
                    self.logger.debug(f'Выбрана функция {func_name} для сбора информации.')
                    func = self.video_info_functions[func_name]
                    video_info[func_name] = func()
                else:
                    self.logger.warning(f'Выбранная пользователем информация не соответствует словарю функций.')

            video_data.append(video_info)
        return video_data

    def get_video_info_functions(self):
        available_info = list(self.video_info_functions.keys())
        return get_functions_from_user('видео', available_info)

class ShortsInfo(VideoInfoBase):
    def __init__(self, driver, css_selectors):
        super().__init__(driver, css_selectors)
        self.shorts_info_functions = {
            'name': self.get_shorts_title,
            'views': self.get_shorts_views,
            'likes': self.get_shorts_likes,
            'release_date': self.get_shorts_release_date,
            'comments': self.get_shorts_comments,
            'description': self.get_shorts_description
        }

    def get_shorts_title(self):
        selectors = ['shorts_title_1', 'shorts_title_2', 'shorts_title_3']
        for selector in selectors:
            try:
                shorts_title_element = WebDriverWait(self.driver, 0.5).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, self.css_selectors[selector]))
                )
                self.logger.info('Заголовок Shorts найден успешно.')
                return shorts_title_element.text.strip()
            except TimeoutException:
                self.logger.info(f'Не удалось найти название Shorts. Пробую другой CSS-селектор: {selector}...')
            except Exception as e:
                self.logger.error(f'Произошла ошибка при сборе заголовка Shorts: {e}.')
                return None
        self.logger.warning('Заголовок Shorts не найден.')
        return 'Название Shorts не найдено.'

    def get_shorts_likes(self):
        shorts_likes = self._get_element_text(
            element=self.driver,
            selector_key='shorts_likes',
            error_message='Количество лайков к Shorts не найдено.'
        )

        if shorts_likes == '–':
            self.logger.info('При извлечении количества лайков Shorts был обнаружен символ "-". Количество лайков = 0.')
            return '0'
        else:
            return shorts_likes

    def get_shorts_comments(self):
        return self._get_element_text(
            element=self.driver,
            selector_key='shorts_comments',
            error_message='Количество комментариев к Shorts не найдено.'
        )

    def get_shorts_description(self):
        """
        Извлекает описание Shorts-видео с YouTube.

        Returns:
            str: Текст описания Shorts-видео или 'Описание к Shorts не найдено', если описание не найдено.
        """
        selectors = ['shorts_description_1', 'shorts_description_2']
        for selector in selectors:
            try:
                description_element = WebDriverWait(self.driver, 0.5).until(
                    EC.visibility_of_element_located((By.CSS_SELECTOR, self.css_selectors[selector]))
                )
                self.logger.info('Описание к Shorts найдено успешно.')
                return description_element.text.strip()
            except TimeoutException:
                self.logger.info(f'Не удалось найти описание к Shorts. Пробую другой CSS-селектор: {selector}...')
            except Exception as e:
                self.logger.error(f'Произошла ошибка при сборе описания к Shorts: {e}.')
                return None
        self.logger.warning('Описание к Shorts не найдено.')
        return 'Описание к Shorts не найдено.'

    def get_shorts_views(self):
        return self._get_element_text(
            element=self.driver,
            selector_key='shorts_views',
            error_message='Количество просмотров Shorts не найдено.'
        )

    def get_shorts_release_date(self):
        """
        Извлекает дату публикации Shorts-видео с YouTube.

        Returns:
            str: Дата публикации Shorts-видео или 'Дата релиза Shorts не найдена', если дата не найдена.
        """
        try:
            day_month_element = WebDriverWait(self.driver, 0.5).until(
                EC.visibility_of_element_located((By.CSS_SELECTOR, self.css_selectors['shorts_day_month']))
            )
            day_month = day_month_element.text.strip()

            year_element = WebDriverWait(self.driver, 0.5).until(
                EC.visibility_of_element_located((By.CSS_SELECTOR, self.css_selectors['shorts_year']))
            )
            year = year_element.text.strip()

            if day_month and year:
                self.logger.info(f'Дата релиза Shorts в формате "{day_month} {year} г." найдена успешно.')
                return f'{day_month} {year} г.'

        except TimeoutException:
            self.logger.info('Дата релиза Shorts в формате "день/месяц/год" не найдена. Пробую найти в формате "X часов назад"...')
            try:
                hours_ago_element = WebDriverWait(self.driver, 0.5).until(
                    EC.visibility_of_element_located((By.CSS_SELECTOR, self.css_selectors['shorts_hours_ago_1']))
                )
                hours_ago = hours_ago_element.text.strip()

                ago_element = WebDriverWait(self.driver, 0.5).until(
                    EC.visibility_of_element_located((By.CSS_SELECTOR, self.css_selectors['shorts_hours_ago_2']))
                )
                ago = ago_element.text.strip()

                if hours_ago and ago:
                    self.logger.info(f'Дата релиза Shorts в формате "{hours_ago} {ago}" найдена успешно.')
                    return f'{hours_ago} {ago}'
            except TimeoutException:
                self.logger.warning('Дата релиза Shorts не найдена.')
                return 'Дата релиза Shorts не найдена.'
        except Exception as e:
            self.logger.error(f'Произошла ошибка при поиске даты релиза Shorts: {e}.')
            return None

    def scraping_shorts_info(self, filtered_data, selected_shorts_info_functions):
        shorts_data = []
        total_videos = len(filtered_data)
        for video_number, video in enumerate(filtered_data, 1):
            self.logger.info(f'\nОбработка Shorts {video_number} из {total_videos}...')
            self.driver.get(video['url'])
            time.sleep(1)

            shorts_info = OrderedDict()

            if self.is_shorts_unacceptable():
                shorts_info['status'] = 'Shorts недоступен, т.к. YouTube посчитал его неприемлемым.'
                continue

            self.click_element_css('shorts_menu_button')
            self.click_element_css('shorts_description_button')
            self.click_element_css('shorts_more_button')

            for func_name in selected_shorts_info_functions:
                if func_name in self.shorts_info_functions:
                    self.logger.debug(f'Выбрана функция {func_name} для сбора информации.')
                    func = self.shorts_info_functions[func_name]
                    shorts_info[func_name] = func()
                else:
                    self.logger.warning(f'Выбранная пользователем информация не соответствует словарю функций.')

            shorts_data.append(shorts_info)
        return shorts_data

    def get_shorts_info_functions(self):
        available_info = list(self.shorts_info_functions.keys())
        return get_functions_from_user('Shorts', available_info)