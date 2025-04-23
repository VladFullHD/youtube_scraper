import logging
import time
from collections import OrderedDict
from utils.navigation_utils import click_element_css, scroll_selenium_keys
from utils.user_input_utils import get_functions_from_user
from utils import element_utils


logger = logging.getLogger(__name__)


class ChannelBase:
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
        return self._get_element_text(
            element=self.driver,
            selector_key='channel_subscribers',
            error_message='Количество подписчиков на канале не найдено.'
        )

    def get_channel_number_videos(self):
        return self._get_element_text(
            element=self.driver,
            selector_key='channel_number_videos',
            error_message='Количество видео не найдено.'
        )

    def get_channel_full_name(self):
        return self._get_element_text(
            element=self.driver,
            selector_key='channel_full_name',
            error_message='Полное наименование канала не найдено.'
        )

    def get_channel_name(self):
        return self._get_element_text(
            element=self.driver,
            selector_key='channel_name',
            error_message='Наименование канала не найдено.'
        )

    def get_channel_main_description(self):
        self.click_element_css('channel_description_button')
        time.sleep(0.5)
        return self._get_element_text(
            element=self.driver,
            selector_key='channel_main_description',
            error_message='Описание канала не найдено.'
        )

    def get_channel_links(self):
        return self._get_element_text(
            element=self.driver,
            selector_key='channel_links',
            error_message='Ссылки в описании канала не найдены.'
        )

    def get_channel_country(self):
        return self._get_element_text(
            element=self.driver,
            selector_key='channel_country',
            error_message='Страна регистрации канала не найдена.'
        )

    def get_channel_registration_date(self):
        return self._get_element_text(
            element=self.driver,
            selector_key='channel_registration_date',
            error_message='Дата регистрации канала не найдена.'
        )

    def get_channel_total_views(self):
        return self._get_element_text(
            element=self.driver,
            selector_key='channel_total_views',
            error_message='Общее количество просмотров на канале не найдено.'
        )

    def get_channel_banner(self):
        return self._get_element_attribute(
            element=self.driver,
            selector_key='channel_banner',
            attribute='src',
            error_message='Баннер канала не найден.'
        )

    def get_channel_profile_picture(self):
        return self._get_element_attribute(
            element=self.driver,
            selector_key='channel_profile_picture',
            attribute='src',
            error_message='Фото профиля канала не найдено.'
        )


    def scraping_channel_info(self, selected_info_functions):
        channel_data = {}
        for func_name in selected_info_functions:
            if func_name in self.info_functions:
                self.logger.debug(f'Выбрана функция {func_name} для сбора информации.')
                func = self.info_functions[func_name]
                channel_data[func_name] = func()
            else:
                self.logger.warning(f'Выбранная пользователем функция "{func_name}" не соответствует словарю функций.')

        self.click_element_css('channel_description_close_button')
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
        return self._get_elements(
            selector_key='channel_all_videos',
            error_message='Не удалось найти ни одного элемента видео.'
        )

    def get_channel_video_title(self, video_element):
        return self._get_element_text(
            element=video_element,
            selector_key='channel_video_title',
            error_message='Название видео не найдено.'
        )

    def get_channel_video_url(self, video_element):
        return self._get_element_attribute(
            element=video_element,
            selector_key='channel_video_url',
            attribute='href',
            error_message='Ссылка на видео не найдена.'
        )

    def get_channel_video_views(self, video_element):
        return self._get_element_text(
            element=video_element,
            selector_key='channel_video_views',
            error_message='Количество просмотров видео не найдено.'
        )

    def get_channel_video_release_date(self, video_element):
        return self._get_element_text(
            element=video_element,
            selector_key='channel_video_release_date',
            error_message='Дата выхода видео не найдена.'
        )

    def get_channel_video_preview(self, video_element):
        return self._get_element_attribute(
            element=video_element,
            selector_key='channel_video_preview',
            attribute='src',
            error_message='Превью к видео не найдено.'
        )


    def scraping_channel_videos(self, selected_video_functions):
        scroll_selenium_keys(self.driver)

        video_elements = self.get_channel_all_video_elements()
        time.sleep(1)

        video_data = []
        total_videos = len(video_elements)
        for video_number, video_element in enumerate(video_elements, 1):
            self.logger.info(f'\nОбработка видео {video_number} из {total_videos}...')
            video_info = OrderedDict()
            for func_name in selected_video_functions:
                if func_name in self.video_functions:
                    self.logger.debug(f'Выбрана функция {func_name} для сбора информации.')
                    func = self.video_functions[func_name]
                    video_info[func_name] = func(video_element)
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
        return self._get_elements(
            selector_key='channel_all_shorts',
            error_message='Не удалось найти ни одного элемента Shorts.'
        )

    def get_channel_shorts_title(self, video_element):
        return self._get_element_text(
            element=video_element,
            selector_key='channel_shorts_title',
            error_message='Название Shorts не найдено.'
        )

    def get_channel_shorts_views(self, video_element):
        return self._get_element_text(
            element=video_element,
            selector_key='channel_shorts_views',
            error_message='Количество просмотров Shorts не найдено.'
        )

    def get_channel_shorts_preview(self, video_element):
        return self._get_element_attribute(
            element=video_element,
            selector_key='channel_shorts_preview',
            attribute='src',
            error_message='Превью к Shorts не найдено.'
        )


    def scraping_channel_shorts(self, selected_shorts_functions):
        scroll_selenium_keys(self.driver)

        shorts_elements = self.get_channel_all_shorts_elements()
        time.sleep(1)

        shorts_data = []
        total_shorts = len(shorts_elements)
        for shorts_number, shorts_element in enumerate(shorts_elements, 1):
            self.logger.info(f'\nОбработка Shorts {shorts_number} из {total_shorts}...')
            shorts_info = OrderedDict()
            for func_name in selected_shorts_functions:
                if func_name in self.shorts_functions:
                    self.logger.debug(f'Выбрана функция {func_name} для сбора информации.')
                    func = self.shorts_functions[func_name]
                    shorts_info[func_name] = func(shorts_element)
                else:
                    self.logger.warning(f'Выбранная пользователем информация не соответствует словарю функций.')

            shorts_data.append(shorts_info)
        return shorts_data

    def get_shorts_functions(self):
        available_info = list(self.shorts_functions.keys())
        return get_functions_from_user('Shorts', available_info)