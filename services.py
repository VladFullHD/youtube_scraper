import logging
import time
from channel_info_scraper import ChannelInfo, ChannelVideo, ChannelShorts
from search_info_scraper import SearchVideo
from utils import search_request_input, load_json_file
from utils.navigation_utils import click_element_css, sending_request, click_element_xpath
from utils.file_utils import save_json_file
from utils.string_utils import extract_channel_name
from utils.google_sheets_utils import save_to_googlesheets
from utils.user_input_utils import channel_filter_input, search_filter_input

logger = logging.getLogger(__name__)


class BaseService:
    def __init__(self, driver, css_selectors, credentials_file, spreadsheet_id):
        self.driver = driver
        self.css_selectors = css_selectors
        self.credentials_file = credentials_file
        self.spreadsheet_id = spreadsheet_id

    def channel_filter_click(self, filters):
        if filters == '1':
            click_element_css(self.driver, self.css_selectors, 'popular_filter')
            time.sleep(1)
        elif filters == '2':
            click_element_css(self.driver, self.css_selectors, 'old_filter')
            time.sleep(1)

    def search_filter_click(self, search_filters, filter_names):
        for filter_name in filter_names:
            click_element_css(self.driver, self.css_selectors, 'search_filters_button')
            time.sleep(1)
            click_element_xpath(self.driver, search_filters, filter_name)
            time.sleep(0.5)

    def youtube_search(self, search_request):
        click_element_css(self.driver, self.css_selectors, 'search_bar_button')
        sending_request(self.driver, search_request)


class UserChoiceHandler(BaseService):
    def __init__(
            self,
            driver,
            css_selectors,
            credentials_file,
            spreadsheet_id,
            search_video_service,
            channel_info_service,
            channel_video_service,
            channel_shorts_service
    ):
        super().__init__(
            driver,
            css_selectors,
            credentials_file,
            spreadsheet_id
        )

        self.search_video_service = search_video_service
        self.channel_info_service = channel_info_service
        self.channel_video_service = channel_video_service
        self.channel_shorts_service = channel_shorts_service

    def youtube_scraper_handler(self):
        while True:
            print(
                'Выберите, какую программу вы хотите запустить:\n'
                '1. Обработчик видео из поисковых запросов.\n'
                '2. Обработчик YouTube-каналов.'
            )

            user_choice = input('Введите номер для выбора: ')

            if user_choice == '1':
                logging.info('Запускаю обработчик видео из поисковых запросов.')
                selected_search_video_functions = self.search_video_service.get_search_video_functions()
                self.search_video_service.get_search_video(selected_search_video_functions)
                break

            elif user_choice == '2':
                logging.info('Запускаю обработчик YouTube-каналов.')
                channel_urls = load_json_file('channel_scraper_input_data/channel_links.json')
                self.channel_scraper_handler(channel_urls)
                break

            else:
                print('Ошибка: введён неверный номер!')
                logging.warning('Введен неверный номер при выборе программы.')

    def channel_scraper_handler(self, channel_urls):
        while True:
            print(
                'Выберите, какую информацию вы хотите собрать:\n1. Информация о канале.\n2. Информация о видео на канале.\n'
                '3. Информация о Shorts на канале.\n4. Вся информация.'
            )

            user_choice = input('Введите номер для выбора: ')

            if user_choice == '1':
                selected_info_functions = self.channel_info_service.get_channel_info_functions()
                self.channel_info_service.process_channel_info(channel_urls, selected_info_functions)
                break

            elif user_choice == '2':
                selected_video_functions = self.channel_video_service.get_channel_video_functions()
                filters = channel_filter_input()
                self.channel_video_service.process_channel_video(channel_urls, selected_video_functions, filters)
                break

            elif user_choice == '3':
                selected_shorts_functions = self.channel_shorts_service.get_channel_shorts_functions()
                filters = channel_filter_input()
                self.channel_shorts_service.process_channel_shorts(channel_urls, selected_shorts_functions, filters)
                break

            elif user_choice == '4':
                selected_info_functions = self.channel_info_service.get_channel_info_functions()
                selected_video_functions = self.channel_video_service.get_channel_video_functions()
                selected_shorts_functions = self.channel_shorts_service.get_channel_shorts_functions()
                filters = channel_filter_input()

                self.channel_info_service.process_channel_info(channel_urls, selected_info_functions)
                self.channel_video_service.process_channel_video(channel_urls, selected_video_functions, filters)
                self.channel_shorts_service.process_channel_shorts(channel_urls, selected_shorts_functions, filters)
                break

            else:
                print('Ошибка: введен неверный номер!')

class SearchVideoService(BaseService):
    def __init__(self, driver, css_selectors, search_filters, credentials_file, spreadsheet_id):
        super().__init__(driver, css_selectors, credentials_file, spreadsheet_id)
        self.search_video_scraper = SearchVideo(driver, css_selectors)
        self.search_filters = search_filters

    def get_search_video_functions(self):
        selected_search_video_functions = self.search_video_scraper.get_search_video_functions()
        return selected_search_video_functions

    def get_search_video(self, selected_search_video_functions):
        search_request = search_request_input()

        self.driver.get('https://www.youtube.com')
        time.sleep(1)

        self.youtube_search(search_request)
        time.sleep(1)

        filter_names = search_filter_input(self.search_filters)
        self.search_filter_click(self.search_filters, filter_names)
        time.sleep(0.5)

        search_video_data = self.search_video_scraper.scraping_search_video(selected_search_video_functions)

        save_json_file(search_video_data, f'search_scraper_output_data/{search_request}.json')
        save_to_googlesheets(search_video_data, self.spreadsheet_id, search_request, self.credentials_file)

class ChannelInfoService(BaseService):
    def __init__(self, driver, css_selectors, credentials_file, spreadsheet_id):
        super().__init__(driver, css_selectors, credentials_file, spreadsheet_id)
        self.channel_info_scraper = ChannelInfo(driver, css_selectors)

    def get_channel_info_functions(self):
        selected_info_functions = self.channel_info_scraper.get_info_functions()
        return selected_info_functions

    def get_channel_info(self, channel_url, selected_info_functions):
        channel_name = extract_channel_name(channel_url)

        self.driver.get(channel_url)
        time.sleep(1)

        channel_data = self.channel_info_scraper.scraping_channel_info(selected_info_functions)

        save_json_file(channel_data, f'channel_scraper_output_data/{channel_name}.json')
        save_to_googlesheets([channel_data], self.spreadsheet_id, channel_name, self.credentials_file)

        return channel_data

    def process_channel_info(self, channel_urls, selected_info_functions):
        for channel_url in channel_urls:
            self.get_channel_info(channel_url, selected_info_functions)

class ChannelVideoService(BaseService):
    def __init__(self, driver, css_selectors, credentials_file, spreadsheet_id):
        super().__init__(driver, css_selectors, credentials_file, spreadsheet_id)
        self.channel_video_scraper = ChannelVideo(driver, css_selectors)

    def get_channel_video_functions(self):
        selected_video_functions = self.channel_video_scraper.get_video_functions()
        return selected_video_functions

    def get_channel_video(self, channel_url, selected_video_functions, filters):
        channel_name = extract_channel_name(channel_url)

        self.driver.get(channel_url)
        time.sleep(1)

        click_element_css(self.driver, self.css_selectors, 'channel_video_button')
        time.sleep(0.5)

        self.channel_filter_click(filters)
        time.sleep(0.5)

        video_data = self.channel_video_scraper.scraping_channel_videos(selected_video_functions)

        save_json_file(video_data, f'channel_scraper_output_data/{channel_name}_video.json')
        save_to_googlesheets(video_data, self.spreadsheet_id, f'{channel_name}_video', self.credentials_file)

        return video_data

    def process_channel_video(self, channel_urls, selected_video_functions, filters):
        for channel_url in channel_urls:
            self.get_channel_video(channel_url, selected_video_functions, filters)

class ChannelShortsService(BaseService):
    def __init__(self, driver, css_selectors, credentials_file, spreadsheet_id):
        super().__init__(driver, css_selectors, credentials_file, spreadsheet_id)
        self.channel_shorts_scraper = ChannelShorts(driver, css_selectors)

    def get_channel_shorts_functions(self):
        selected_shorts_functions = self.channel_shorts_scraper.get_shorts_functions()
        return selected_shorts_functions

    def get_channel_shorts(self, channel_url, selected_shorts_functions, filters):
        channel_name = extract_channel_name(channel_url)

        self.driver.get(channel_url)
        time.sleep(1)

        click_element_css(self.driver, self.css_selectors, 'channel_shorts_button')
        time.sleep(0.5)

        self.channel_filter_click(filters)
        time.sleep(0.5)

        shorts_data = self.channel_shorts_scraper.scraping_channel_shorts(selected_shorts_functions)

        save_json_file(shorts_data, f'channel_scraper_output_data/{channel_name}_shorts.json')
        save_to_googlesheets(shorts_data, self.spreadsheet_id, f'{channel_name}_shorts', self.credentials_file)

        return shorts_data

    def process_channel_shorts(self, channel_urls, selected_shorts_functions, filters):
        for channel_url in channel_urls:
            self.get_channel_shorts(channel_url, selected_shorts_functions, filters)