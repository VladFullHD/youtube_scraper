import logging
import re
import time
from collections import OrderedDict
from utils import element_utils, scroll_selenium_keys, get_functions_from_user

logger = logging.getLogger(__name__)

class SearchVideoBase:
    def __init__(self, driver, css_selectors):
        self.driver = driver
        self.css_selectors = css_selectors
        self.logger = logging.getLogger(__name__)

    def _get_elements(self, selector_key, error_message):
        return element_utils.get_elements(self.driver, self.css_selectors, selector_key, error_message)

    def _get_element_text(self, element, selector_key, error_message):
        return element_utils.get_element_text(element, self.css_selectors, selector_key, error_message)

    def _get_element_attribute(self, element, selector_key, attribute, error_message):
        return element_utils.get_element_attribute(element, self.css_selectors, selector_key, attribute, error_message)


class SearchVideo(SearchVideoBase):
    def __init__(self, driver, css_selectors):
        super().__init__(driver, css_selectors)
        self.search_video_functions = {
            'name': self.get_search_video_title,
            'url': self.get_search_video_url,
            'views': self.get_search_video_views,
            'release_date': self.get_search_video_release_date,
            'channel_name': self.get_search_video_channel_name,
            'channel_url': self.get_search_video_channel_url,
            'preview': self.get_search_video_preview
        }

    def get_search_all_video_elements(self):
        return self._get_elements(
            selector_key='search_all_videos',
            error_message='Не удалось найти ни одного элемента видео.'
        )

    def _get_search_video_type(self, video_element, element_data):
        try:
            video_url = element_data.get('url', '')
            release_date = element_data.get('release_date', '')

            if re.search(r'/shorts', video_url):
                return 'Shorts'
            elif 'Не найдено' in release_date or not release_date:
                return 'Live'
            else:
                return 'Video'
        except Exception as e:
            self.logger.error(f'Ошибка при определении типа видео: {e}.')
            return 'Неизвестно'


    def get_search_video_title(self, video_element):
        return self._get_element_text(
            element=video_element,
            selector_key='search_video_title',
            error_message='Название видео не найдено.'
        )

    def get_search_video_url(self, video_element):
        return self._get_element_attribute(
            element=video_element,
            selector_key='search_video_url',
            attribute='href',
            error_message='Ссылка на видео не найдена.'
        )

    def get_search_video_views(self, video_element):
        #Добавить обработку случая, когда получаем текст "Планируемая дата публикации"
        return self._get_element_text(
            element=video_element,
            selector_key='search_video_views',
            error_message='Количество просмотров видео не найдено.'
        )

    def get_search_video_release_date(self, video_element):
        return self._get_element_text(
            element=video_element,
            selector_key='search_video_release_date',
            error_message='Дата выхода видео не найдена.'
        )

    def get_search_video_channel_name(self, video_element):
        return self._get_element_text(
            element=video_element,
            selector_key='search_video_channel_name',
            error_message='Название канала не найдено.'
        )

    def get_search_video_channel_url(self, video_element):
        return self._get_element_attribute(
            element=video_element,
            selector_key='search_video_channel_url',
            attribute='href',
            error_message='Ссылка на канал не найдена.'
        )

    def get_search_video_preview(self, video_element):
        return self._get_element_attribute(
            element=video_element,
            selector_key='search_video_preview',
            attribute='src',
            error_message='Превью к видео не найдено.'
        )

    def get_search_video_functions(self):
        available_info = list(self.search_video_functions.keys())
        available_info.append('type')
        return get_functions_from_user('видео из поисковой выдачи', available_info)

    def scraping_search_video(self, selected_search_video_functions):
        scroll_selenium_keys(self.driver)

        video_elements = self.get_search_all_video_elements()
        time.sleep(1)

        search_data = []
        total_videos = len(video_elements)
        for video_number, video_element in enumerate(video_elements, 1):
            self.logger.info(f'\nОбработка видео {video_number} из {total_videos}...')
            search_info = OrderedDict()

            element_data = {}

            element_data['url'] = self.get_search_video_url(video_element)
            element_data['release_date'] = self.get_search_video_release_date(video_element)

            video_type = self._get_search_video_type(video_element, element_data)

            for func_name in selected_search_video_functions:
                if func_name == 'type':
                    search_info['type'] = video_type
                elif func_name in self.search_video_functions:
                    if func_name in element_data:
                        search_info[func_name] = element_data[func_name]
                    else:
                        func = self.search_video_functions[func_name]
                        search_info[func_name] = func(video_element)
                else:
                    self.logger.warning(f'Выбранная пользователем информация не соответствует словарю функций.')

            search_data.append(search_info)
        return search_data


