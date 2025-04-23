import logging
from services import ChannelInfoService, ChannelVideoService, ChannelShortsService, UserChoiceHandler, \
    SearchVideoService
from utils.webdriver_utils import setup_options_webdriver
from utils.file_utils import load_json_file

logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(funcName)s - %(message)s",
        filename='channel_scraper_log/channels_info_scraper.log',
        filemode='a',
        encoding='utf-8'
    )

CREDENTIALS_FILE = 'C:/Users/User/PycharmProjects/youtube_scraper/channel_scraper_input_data/youtubescraper-456314-c11c71503d15.json'
SPREADSHEET_ID = '1LsrDyfNiK8MA0dsIza_4ULZyyOfRQnga_PqllawgmPE'

def main():
    driver = setup_options_webdriver()

    css_selectors = load_json_file('css_selectors.json')
    search_filters = load_json_file('search_filters.json')

    search_video_service = SearchVideoService(driver, css_selectors, search_filters, CREDENTIALS_FILE, SPREADSHEET_ID)
    channel_info_service = ChannelInfoService(driver, css_selectors, CREDENTIALS_FILE, SPREADSHEET_ID)
    channel_video_service = ChannelVideoService(driver, css_selectors, CREDENTIALS_FILE, SPREADSHEET_ID)
    channel_shorts_service = ChannelShortsService(driver, css_selectors, CREDENTIALS_FILE, SPREADSHEET_ID)

    user_choice_handler = UserChoiceHandler(
        driver,
        css_selectors,
        CREDENTIALS_FILE,
        SPREADSHEET_ID,
        search_video_service,
        channel_info_service,
        channel_video_service,
        channel_shorts_service
    )

    user_choice_handler.youtube_scraper_handler()


if __name__ == '__main__':
    main()