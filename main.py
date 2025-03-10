import time

from selenium.common import TimeoutException
from selenium.webdriver import ActionChains
from selenium.webdriver.support.wait import WebDriverWait
from driver_utils import setup_options_webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from file_utils import load_filters, load_css_selectors, save_json_file


def open_youtube(driver):
    try:
        driver.get('https://www.youtube.com')
    except Exception as e:
        print(f'Произошла ошибка при открытии YouTube: {e}')

def search_input(driver, search_text):
    try:
        search_box = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, '//*[@id="center"]/yt-searchbox/div[1]/form/input'))
        )
        actions = ActionChains(driver)
        actions.move_to_element(search_box).click().send_keys(search_text).perform()
        driver.execute_script('document.forms[0].submit()')

    except Exception as e:
        print(f'Произошла ошибка при вводе текста в поисковую строку: {e}')

def filter_settings(driver, filter_names):
    filters = load_filters()
    try:
        for filter_name in filter_names:
            filter_button = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, '//*[@id="filter-button"]/ytd-button-renderer/yt-button-shape/button'))
            )
            actions = ActionChains(driver)
            actions.move_to_element(filter_button).click().perform()
            time.sleep(0.4)

            xpath = filters.get(filter_name)
            if xpath:
                filter_element = WebDriverWait(driver, 10).until(
                    EC.element_to_be_clickable((By.XPATH, xpath))
                )
                actions.move_to_element(filter_element).click().perform()
                time.sleep(0.4)
    except Exception as e:
        print(f'Произошла ошибка при выборе фильтра: {e}')

def get_all_video_elements(driver, all_videos_css):
    try:
        videos_elements = WebDriverWait(driver, 10).until(
            EC.presence_of_all_elements_located((By.CSS_SELECTOR, all_videos_css))
        )
        return videos_elements
    except Exception as e:
        print(f'Произошла ошибка при сборе общей информации о роликах: {e}')
        return None

def get_video_titles(video_elements, title_css):
    titles = []
    for video_element in video_elements:
        try:
            title_element = WebDriverWait(video_element, 5).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, title_css))
            )
            title = title_element.text.strip()
            if title:
                titles.append(title)
        except TimeoutException:
            print('Название видео не найдено!')
            titles.append('Не найдено!')
        except Exception as e:
            print(f'Произошла ошибка при сборе заголовков видео: {e}')
    return titles

def get_video_views(video_elements, view_css):
    views = []
    for video_element in video_elements:
        try:
            view_element = WebDriverWait(video_element, 5).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, view_css))
            )
            view = view_element.text.strip()
            if view:
                views.append(view)
        except TimeoutException:
            print('Количество просмотров не найдено!')
            views.append('Не найдено!')
        except Exception as e:
            print(f'Произошла ошибка при сборе количества просмотров: {e}')
    return views

def get_video_release_date(video_elements, release_date_css):
    release_dates = []
    for video_element in video_elements:
        try:
            release_date_element = WebDriverWait(video_element, 5).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, release_date_css))
            )
            release_date = release_date_element.text.strip()
            if release_date:
                release_dates.append(release_date)
        except TimeoutException:
            print('Дата релиза не найдена!')
            release_dates.append('Не найдено!')
        except Exception as e:
            print(f'Произошла ошибка при сборе даты релиза: {e}')
    return release_dates

def get_channel_names(video_elements, channel_css):
    channel_names = []
    for video_element in video_elements:
        try:
            channel_element = WebDriverWait(video_element, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, channel_css))
            )
            channel_name = channel_element.text.strip()
            if channel_name:
                channel_names.append(channel_name)
        except TimeoutException:
            print('Название канала не найдено!')
            channel_names.append('Не найдено!')
        except Exception as e:
            print(f'Произошла ошибка при сборе наименований каналов: {e}')
    return channel_names

def get_channel_urls(video_elements, channel_css):
    channel_urls = []
    for video_element in video_elements:
        try:
            channel_element = WebDriverWait(video_element, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, channel_css))
            )
            channel_url = channel_element.get_attribute('href')
            if channel_url:
                channel_urls.append(channel_url)
        except TimeoutException:
            print('Ссылка на канал не найдена')
            channel_urls.append('Не найдено!')
        except Exception as e:
            print(f'Произошла ошибка при сборе ссылок на каналы: {e}')
    return channel_urls

def collect_video_data(driver, css_selectors):
    video_elements = get_all_video_elements(driver, css_selectors['all_videos'])
    titles = get_video_titles(video_elements, css_selectors['title'])
    views = get_video_views(video_elements, css_selectors['view'])
    release_dates = get_video_release_date(video_elements, css_selectors['release_date'])
    channel_names = get_channel_names(video_elements, css_selectors['channel_info'])
    channel_urls = get_channel_urls(video_elements, css_selectors['channel_url'])


    video_data = []
    for i, title in enumerate(titles):
        video_info = {
            'title': title,
            'views': views[i],
            'release': release_dates[i],
            'channel_name': channel_names[i],
            'channel_url': channel_urls[i]
        }
        video_data.append(video_info)
    save_json_file(video_data, 'video_data.json')


def main():
    driver = setup_options_webdriver()
    open_youtube(driver)

    search_text = 'Лига легенд'
    search_input(driver, search_text)

    filter_settings(driver, ['this_month', 'upload_date'])
    time.sleep(3)

    css_selectors = load_css_selectors()
    collect_video_data(driver, css_selectors)

    input('Нажмите Enter, чтобы закрыть драйвер!')
    driver.quit()

if __name__ == "__main__":
    main()