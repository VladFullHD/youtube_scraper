import re
import time
from selenium.common import TimeoutException
from selenium.webdriver import ActionChains
from driver_utils import setup_options_webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from file_utils import save_json_file, load_json_file


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
    filters = load_json_file('filters.json')
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

def get_all_elements_from_search(driver, all_videos_css):
    try:
        videos_elements = WebDriverWait(driver, 10).until(
            EC.presence_of_all_elements_located((By.CSS_SELECTOR, all_videos_css['all_videos']))
        )
        return videos_elements
    except Exception as e:
        print(f'Произошла ошибка при сборе общей информации о роликах: {e}')
        return None

def get_titles_from_search(video_elements, title_css):
    titles = []
    for video_element in video_elements:
        try:
            title_element = WebDriverWait(video_element, 5).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, title_css['title']))
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

def get_urls_from_search(video_elements, url_css):
    video_urls = []
    for video_element in video_elements:
        try:
            video_url_element = WebDriverWait(video_element, 5).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, url_css['video_url']))
            )
            video_url = video_url_element.get_attribute('href')
            if video_url:
                video_urls.append(video_url)
        except TimeoutException:
            print('Ссылка на видео не найдена')
            video_urls.append('Не найдено!')
        except Exception as e:
            print(f'Произошла ошибка при сборе ссылок на видео: {e}')
    return video_urls

def get_views_from_search(video_elements, views_css):
    views = []
    for video_element in video_elements:
        try:
            view_element = WebDriverWait(video_element, 5).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, views_css['views']))
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

def get_release_dates_from_search(video_elements, release_date_css):
    release_dates = []
    for video_element in video_elements:
        try:
            release_date_element = WebDriverWait(video_element, 5).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, release_date_css['release_date']))
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

def get_channel_names_from_search(video_elements, channel_name_css):
    channel_names = []
    for video_element in video_elements:
        try:
            channel_element = WebDriverWait(video_element, 5).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, channel_name_css['channel_info']))
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

def get_channel_urls_from_search(video_elements, channel_url_css):
    channel_urls = []
    for video_element in video_elements:
        try:
            channel_element = WebDriverWait(video_element, 5).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, channel_url_css['channel_url']))
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

def get_all_info_from_search(driver, css_selectors):
    video_elements = get_all_elements_from_search(driver, css_selectors['all_videos'])
    titles = get_titles_from_search(video_elements, css_selectors['title'])
    video_urls = get_urls_from_search(video_elements, css_selectors['video_url'])
    views = get_views_from_search(video_elements, css_selectors['views'])
    release_dates = get_release_dates_from_search(video_elements, css_selectors['release_date'])
    channel_names = get_channel_names_from_search(video_elements, css_selectors['channel_info'])
    channel_urls = get_channel_urls_from_search(video_elements, css_selectors['channel_url'])

    video_data = []
    for i, title in enumerate(titles):
        video_info = {
            'title': title,
            'video_url': video_urls[i],
            'views': views[i],
            'release': release_dates[i],
            'channel_name': channel_names[i],
            'channel_url': channel_urls[i]
        }
        video_data.append(video_info)

def get_likes(driver):
    try:
        like_element = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, 'button[aria-label^="Видео понравилось вам и ещё"]'))
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

            print(f"{formatted_likes} лайка/ов")
        else:
            return None
    except Exception as e:
        print(f"Ошибка при извлечении лайков: {e}")
        return None

def scraping_info_from_search(driver, css_selectors, selected_data):
    video_elements = get_all_elements_from_search(driver, css_selectors)

    collected_data = {key: data_functions[key](video_elements, css_selectors) for key in selected_data}
    video_data = []
    for i in range(len(video_elements)):
        video_info = {key: collected_data[key][i] for key in selected_data}
        video_data.append(video_info)
    return video_data

data_functions = {
    "names": get_titles_from_search,
    "urls": get_urls_from_search,
    "views": get_views_from_search,
    "release_dates": get_release_dates_from_search,
    "channel_names": get_channel_names_from_search,
    "channel_urls": get_channel_urls_from_search,
}

def main():
    driver = setup_options_webdriver()
    open_youtube(driver)

    css_selectors = load_json_file('css_selectors.json')
    filters = load_json_file('filters.json')

    search_text = input('Введите поисковый запрос для поиска в YouTube: ').strip()
    search_input(driver, search_text)
    time.sleep(2)

    available_filters = list(filters.keys())
    print(f'Доступные фильтры: {', '.join(available_filters)}')
    user_filter_input = input('Выберите фильтр (или оставьте пустым для пропуска): ').strip()

    filter_names = []
    selected_filters = []
    if user_filter_input:
        selected_filters = [f.strip() for f in user_filter_input.split(',') if f.strip() in filters]
    if not selected_filters:
        print('Ошибка: введены некорректные фильтры!')
    else:
        filter_names = selected_filters

    if filter_names:
        filter_settings(driver, filter_names)
        time.sleep(2)

    available_options = list(data_functions.keys())
    print(f'Доступные параметры: {', '.join(available_options)}')
    user_input = input('Введите через запятую, какие данные вы хотите собрать: ').strip()

    selected_data = [item.strip() for item in user_input.split(',') if item.strip() in data_functions]

    if not selected_data:
        print('Не выбраны корректные параметры! Завершение программы.')
        driver.quit()
        return

    video_data = scraping_info_from_search(driver, css_selectors, selected_data)

    save_json_file(video_data, 'video_data.json')

    input('Нажмите Enter, чтобы закрыть драйвер!')
    driver.quit()

if __name__ == "__main__":
    main()