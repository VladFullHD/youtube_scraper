import time
from channel_info_scraper import ChannelInfo, ChannelVideo, ChannelShorts
from utils.navigation_utils import click_element
from utils.file_utils import save_json_file
from utils.string_utils import extract_channel_name
from utils.google_sheets_utils import save_to_googlesheets
from utils.user_input_utils import channel_filter_input


class ChannelBaseService:
    def __init__(self, driver, css_selectors, credentials_file, spreadsheet_id):
        self.driver = driver
        self.css_selectors = css_selectors
        self.credentials_file = credentials_file
        self.spreadsheet_id = spreadsheet_id

    def channel_filter_click(self, filters):
        if filters == '1':
            click_element(self.driver, self.css_selectors, 'popular_filter')
            time.sleep(1)
        elif filters == '2':
            click_element(self.driver, self.css_selectors, 'old_filter')
            time.sleep(1)


class UserChoiceHandler(ChannelBaseService):
    def __init__(
            self,
            driver,
            css_selectors,
            credentials_file,
            spreadsheet_id,
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

        self.channel_info_service = channel_info_service
        self.channel_video_service = channel_video_service
        self.channel_shorts_service = channel_shorts_service

    def handler_user_choice(self, channel_urls):
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

class ChannelInfoService(ChannelBaseService):
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

class ChannelVideoService(ChannelBaseService):
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

        click_element(self.driver, self.css_selectors, 'channel_video_button')
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

class ChannelShortsService(ChannelBaseService):
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

        click_element(self.driver, self.css_selectors, 'channel_shorts_button')
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