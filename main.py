import logging
from services import ChannelInfoService, ChannelVideoService, ChannelShortsService, UserChoiceHandler
from utils import load_json_file
from driver_utils import setup_options_webdriver

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
    channel_urls = load_json_file('channel_scraper_input_data/channel_links.json')
    css_selectors = load_json_file('css_selectors.json')

    channel_info_service = ChannelInfoService(driver, css_selectors, CREDENTIALS_FILE, SPREADSHEET_ID)
    channel_video_service = ChannelVideoService(driver, css_selectors, CREDENTIALS_FILE, SPREADSHEET_ID)
    channel_shorts_service = ChannelShortsService(driver, css_selectors, CREDENTIALS_FILE, SPREADSHEET_ID)

    user_choice_handler = UserChoiceHandler(
        driver,
        css_selectors,
        CREDENTIALS_FILE,
        SPREADSHEET_ID,
        channel_info_service,
        channel_video_service,
        channel_shorts_service
    )

    user_choice_handler.handler_user_choice(channel_urls)

if __name__ == '__main__':
    main()