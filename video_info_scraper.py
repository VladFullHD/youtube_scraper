import re
import time
from selenium.common import TimeoutException
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from driver_utils import setup_options_webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from file_utils import save_json_file, load_json_file
from search_info_scraper import info_settings_input

def click_element(driver, css_selector, timeout=2):
    try:
        element = WebDriverWait(driver, timeout).until(
            EC.visibility_of_element_located((By.CSS_SELECTOR, css_selector))
        )
        actions = ActionChains(driver)
        actions.move_to_element(element).click().perform()
    except TimeoutException:
        pass


def open_video_description(driver, css_selectors):
    try:
        description_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, css_selectors['description_button']))
        )
        actions = ActionChains(driver)
        actions.move_to_element(description_button).click().perform()
    except TimeoutException:
        print('Кнопка для развертывания описания Video не найдена!')

def get_video_description(driver, css_selectors):
    open_video_description(driver, css_selectors)
    try:
        description_element = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, css_selectors['description']))
        )
        description = description_element.text.strip()
        return description
    except TimeoutException:
        return 'Описание к Video не найдено!'
    except Exception as e:
        print(f'Произошла ошибка при сборе описания к Video: {e}')

def get_video_likes(driver, css_selectors):
    try:
        like_element = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, css_selectors['likes']))
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

def get_video_comments(driver, css_selectors):
    while True:
        try:
            video_comments_element = WebDriverWait(driver, 2).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, css_selectors['comments']))
            )
            video_comments = video_comments_element.text.strip()
            return video_comments
        except TimeoutException:
            driver.find_element("tag name", 'html').send_keys(Keys.PAGE_DOWN)
            time.sleep(0.2)
        except Exception as e:
            print(f'Произошла ошибка при сборе количества комментариев к видео: {e}')

def get_video_views(driver, css_selectors):
    try:
        views_element = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, css_selectors['video_views']))
        )
        views = views_element.text.strip()
        return views
    except TimeoutException:
        print('Количество просмотров Video не найдено')
        return 'Количество просмотров Video не найдено'
    except Exception as e:
        print(f'Произошла ошибка при сборе количества просмотров Video')

def get_video_release_date(driver, css_selectors):
    try:
        release_date_element = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, css_selectors['video_release_date']))
        )
        release_date = release_date_element.text.strip()
        return release_date
    except TimeoutException:
        print('Дата релиза Video не найдена')
        return 'Дата релиза Video не найдена'
    except Exception as e:
        print(f'Произошла ошибка при сборе даты релиза Video')

def get_video_title(driver, css_selectors):
    try:
        video_title_element = WebDriverWait(driver, 5).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, css_selectors['video_title']))
        )
        video_title = video_title_element.text.strip()
        print(video_title)
        return video_title
    except TimeoutException:
        return 'Название Video не найдено!'
    except Exception as e:
        print(f'Произошла ошибка при сборе названия Video: {e}')


def get_shorts_title(driver, css_selectors):
    open_shorts_description(driver, css_selectors)
    selectors = ['shorts_title_1', 'shorts_title_2']
    for selector in selectors:
        try:
            shorts_title_element = WebDriverWait(driver, 2).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, css_selectors[selector]))
            )
            return shorts_title_element.text.strip()
        except TimeoutException:
            pass
        except Exception as e:
            print(f'Произошла ошибка при сборе названия Shorts: {e}')

    return 'Название Shorts не найдено'

def get_shorts_likes(driver, css_selectors):
    try:
        shorts_likes_element = WebDriverWait(driver, 5).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, css_selectors['shorts_likes']))
        )
        shorts_likes = shorts_likes_element.text.strip()
        return shorts_likes
    except TimeoutException:
        return 'Количество лайков Shorts не найдено!'
    except Exception as e:
        print(f'Произошла ошибка при сборе количества лайков Shorts: {e}')

def get_shorts_comments(driver, css_selectors):
    try:
        shorts_comments_element = WebDriverWait(driver, 5).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, css_selectors['shorts_comments']))
        )
        shorts_comments = shorts_comments_element.text.strip()
        return shorts_comments
    except TimeoutException:
        return 'Количество комментариев к Shorts не найдено!'
    except Exception as e:
        print(f'Произошла ошибка при сборе комментариев в Shorts: {e}')

def open_shorts_description(driver, css_selectors):
    click_element(driver, css_selectors['shorts_menu_button'])
    click_element(driver, css_selectors['shorts_description_button'])
    click_element(driver, css_selectors['shorts_more_button'])

def get_shorts_description(driver, css_selectors):
    selectors = ['shorts_description_1', 'shorts_description_2']
    for selector in selectors:
        try:
            description_element = WebDriverWait(driver, 1).until(
                EC.visibility_of_element_located((By.CSS_SELECTOR, css_selectors[selector]))
            )
            description_text = description_element.text.strip()
            if description_text:
                return description_text
        except TimeoutException:
            pass
        except Exception as e:
            print(f'Произошла ошибка при сборе описания к Shorts')

    return 'Описание Shorts не найдено'

def get_shorts_views(driver, css_selectors):
    try:
        views_element = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, css_selectors['shorts_views']))
        )
        views = views_element.text.strip()
        return views
    except TimeoutException:
        print('Количество просмотров Shorts не найдено')
        return 'Количество просмотров Shorts не найдено'
    except Exception as e:
        print(f'Произошла ошибка при сборе количества просмотров Shorts')

def get_shorts_release_date(driver, css_selectors):
    try:
        month_day_element = WebDriverWait(driver, 0.5).until(
            EC.visibility_of_element_located((By.CSS_SELECTOR, css_selectors['shorts_month_day']))
        )
        month_day = month_day_element.text.strip()

        year_element = WebDriverWait(driver, 0.5).until(
            EC.visibility_of_element_located((By.CSS_SELECTOR, css_selectors['shorts_year']))
        )
        year = year_element.text.strip()

        if month_day and year:
            return f'{month_day} {year} г.'

    except TimeoutException:
        try:
            hours_ago_element = WebDriverWait(driver, 0.5).until(
                EC.visibility_of_element_located((By.CSS_SELECTOR, css_selectors['shorts_hours_ago_1']))
            )
            hours_ago = hours_ago_element.text.strip()

            ago_element = WebDriverWait(driver, 0.5).until(
                EC.visibility_of_element_located((By.CSS_SELECTOR, css_selectors['shorts_hours_ago_2']))
            )
            ago = ago_element.text.strip()

            if hours_ago and ago:
                return f'{hours_ago} {ago}'
        except TimeoutException:
            print('Не удалось найти дату релиза для Shorts!')
            return 'Дата релиза Shorts не найдена!'

    return 'Дата релиза Shorts не найдена'


def scraping_info_from_videos(driver, css_selectors, input_filename, selected_data, video_functions, shorts_functions):
    input_data = load_json_file(input_filename)
    video_data = []
    for video in input_data:
        driver.get(video['urls'])
        time.sleep(2)

        if video['type'] == 'Video':
            functions = video_functions
        elif video['type'] == 'Shorts':
            functions = shorts_functions
        else:
            continue

        collected_data = {}
        for key in selected_data:
            collected_data[key] = functions[key](driver, css_selectors)

        video_info = {
            'urls': video['urls'],
            'type': video['type']
        }
        video_info.update(collected_data)

        video_data.append(video_info)
    return video_data

video_scraper_functions = {
    'title': get_video_title,
    'description': get_video_description,
    'release_date': get_video_release_date,
    'views': get_video_views,
    'likes': get_video_likes,
    'comments': get_video_comments
}

shorts_scraper_functions = {
    'title': get_shorts_title,
    'description': get_shorts_description,
    'release_date': get_shorts_release_date,
    'views': get_shorts_views,
    'likes': get_shorts_likes,
    'comments': get_shorts_comments
}

def main():
    driver = setup_options_webdriver()

    css_selectors = load_json_file('css_selectors.json')
    video_functions = video_scraper_functions
    shorts_functions = shorts_scraper_functions
    selected_data = info_settings_input(driver, shorts_functions)

    video_data = scraping_info_from_videos(driver, css_selectors, 'video_data.json', selected_data, video_functions, shorts_functions)
    save_json_file(video_data, 'main_data.json')

    input('Нажмите Enter, чтобы закрыть драйвер!')
    driver.quit()

if __name__ == '__main__':
    main()