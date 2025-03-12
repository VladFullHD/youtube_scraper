import re
import time
from selenium.common import TimeoutException
from selenium.webdriver import ActionChains, Keys
from driver_utils import setup_options_webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from file_utils import save_json_file, load_json_file
from search_info_scraper import info_settings_input


def get_video_likes(driver, likes_css):
    try:
        like_element = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, likes_css['likes']))
        )
        aria_label = like_element.get_attribute("aria-label")
        match = re.search(r"и ещё ([\d\s\xa0]+)", aria_label)
        if match:
            likes_str = match.group(1).replace("\xa0", "").replace(" ", "")
            if "тыс" in aria_label:
                likes = int(likes_str) * 1000
            elif "млн" in aria_label:
                likes = int(likes_str) * 1000000
            else:
                likes = int(likes_str)

            # Форматирование числа с разделителями тысяч
            formatted_likes = "{:,}".format(likes).replace(",", ".")

            return formatted_likes
    except TimeoutException:
        return 'Количество лайков в видео не найдено!'
    except Exception as e:
        print(f"Ошибка при извлечении лайков: {e}")
        return None

def get_shorts_likes(driver, shorts_likes_css):
    try:
        shorts_likes_element = WebDriverWait(driver, 5).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, shorts_likes_css['shorts_likes']))
        )
        shorts_likes = shorts_likes_element.text.strip()
        return shorts_likes
    except TimeoutException:
        return 'Количество лайков Shorts не найдено!'
    except Exception as e:
        print(f'Произошла ошибка при сборе количества лайков Shorts: {e}')

def get_video_comments(driver, comments_css):
    try:
        video_comments_element = WebDriverWait(driver, 5).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, comments_css['comments']))
        )
        video_comments = video_comments_element.text.strip()
        print(video_comments)
        return video_comments
    except TimeoutException:
        return 'Количество комментариев к видео не найдено!'
    except Exception as e:
        print(f'Произошла ошибка при сборе количества комментариев к видео: {e}')

def get_shorts_comments(driver, shorts_comments_css):
    try:
        shorts_comments_element = WebDriverWait(driver, 5).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, shorts_comments_css['shorts_comments']))
        )
        shorts_comments = shorts_comments_element.text.strip()
        print(shorts_comments)
        return shorts_comments
    except TimeoutException:
        return 'Количество комментариев к Shorts не найдено!'
    except Exception as e:
        print(f'Произошла ошибка при сборе заголовков видео: {e}')

def scraping_info_from_videos(driver, css_selectors, input_filename, selected_data, video_functions, shorts_functions):
    input_data = load_json_file(input_filename)
    updated_video_data = []
    for video in input_data:
        driver.get(video['urls'])
        time.sleep(2)
        driver.find_element("tag name", 'html').send_keys(Keys.PAGE_DOWN)
        time.sleep(1)

        video_info = video.copy()

        if video['type'] == 'Video':
            for key in selected_data:
                video_info[key] = video_functions[key](driver, css_selectors)
            updated_video_data.append(video_info)
        else:
            for key in selected_data:
                video_info[key] = shorts_functions[key](driver, css_selectors)
            updated_video_data.append(video_info)
    return updated_video_data

all_scraper_functions = {
    'likes': '',
    'comments': ''
}

video_scraper_functions = {
    'likes': get_video_likes,
    'comments': get_video_comments
}

shorts_scraper_functions = {
    'likes': get_shorts_likes,
    'comments': get_shorts_comments
}

def main():
    driver = setup_options_webdriver()

    css_selectors = load_json_file('css_selectors.json')
    all_functions = all_scraper_functions
    video_functions = video_scraper_functions
    shorts_functions = shorts_scraper_functions
    selected_data = info_settings_input(driver, all_functions)

    video_data = scraping_info_from_videos(driver, css_selectors, 'video_data.json', selected_data, video_functions, shorts_functions)
    save_json_file(video_data, 'main_data.json')

    input('Нажмите Enter, чтобы закрыть драйвер!')
    driver.quit()

if __name__ == '__main__':
    main()