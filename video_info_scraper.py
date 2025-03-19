import re
import time
from selenium.common import TimeoutException, NoSuchElementException
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from driver_utils import setup_options_webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from file_utils import save_json_file, load_json_file


def click_element(driver, css_selector, timeout=2):
    try:
        element = WebDriverWait(driver, timeout).until(
            EC.visibility_of_element_located((By.CSS_SELECTOR, css_selector))
        )
        actions = ActionChains(driver)
        actions.move_to_element(element).click().perform()
    except TimeoutException:
        pass

def is_video_unavailable(driver, css_selector):
    try:
        unavailable_element = driver.find_element(By.CSS_SELECTOR, css_selector['is_video_unavailable'])
        return True
    except NoSuchElementException:
        return False

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
        description_element = driver.find_element(By.CSS_SELECTOR, css_selectors['description'])
        return description_element.text.strip()
    except NoSuchElementException:
        print('Описание к Video не найдено!')
        return 'Описание к Video не найдено!'
    except Exception as e:
        print(f'Произошла ошибка при сборе описания к Video: {e}')

def get_video_likes(driver, css_selectors):
    try:
        like_element = driver.find_element(By.CSS_SELECTOR, css_selectors['likes'])
        aria_label = like_element.get_attribute("aria-label")
        if aria_label:
            if 'одному пользователю' in aria_label:
                return '0'
            else:
                match = re.search(r"и ещё ([\d\s\xa0]+)", aria_label)
                if match:
                    likes_str = match.group(1).replace("\xa0", "").replace(" ", "")
                    if "тыс" in aria_label:
                        likes = int(likes_str) * 1000
                    elif "млн" in aria_label:
                        likes = int(likes_str) * 1000000
                    else:
                        likes = int(likes_str)

                    formatted_likes = "{:,}".format(likes).replace(",", ".")
                    return formatted_likes
    except NoSuchElementException:
        print('Количество лайков в Video не найдено!')
        return 'Количество лайков в Video не найдено!'
    except Exception as e:
        print(f"Ошибка при извлечении лайков: {e}")
        return None

def get_video_comments(driver, css_selectors):
    max_attempts = 10
    attempts = 0
    try:
        try:
            driver.find_element(By.CSS_SELECTOR, css_selectors['comments_turned_off'])
            print('Комментарии отключены!')
            return 'Комментарии отключены!'
        except NoSuchElementException:
            while attempts < max_attempts:
                try:
                    video_comments_element = WebDriverWait(driver, 2).until(
                        EC.presence_of_element_located((By.CSS_SELECTOR, css_selectors['comments']))
                    )
                    return video_comments_element.text.strip()
                except TimeoutException:
                    attempts += 1
                    print('Количество комментариев в Video не найдено. Листаю страницу вниз...')
                    driver.find_element("tag name", 'html').send_keys(Keys.PAGE_DOWN)
                    time.sleep(0.2)
            print('Достигнуто максимальное количество попыток поиска комментариев')
    except Exception as e:
        print(f'Произошла ошибка при сборе количества комментариев к видео: {e}')

def get_video_views(driver, css_selectors):
    try:
        views_element = driver.find_element(By.CSS_SELECTOR, css_selectors['video_views'])
        views = views_element.text.strip()
        return views
    except NoSuchElementException:
        print('Количество просмотров Video не найдено')
        return 'Количество просмотров Video не найдено'
    except Exception as e:
        print(f'Произошла ошибка при сборе количества просмотров Video')

def get_video_release_date(driver, css_selectors):
    try:
        release_date_element = driver.find_element(By.CSS_SELECTOR, css_selectors['video_release_date'])
        release_date = release_date_element.text.strip()
        return release_date
    except NoSuchElementException:
        print('Дата релиза Video не найдена')
        return 'Дата релиза Video не найдена'
    except Exception as e:
        print(f'Произошла ошибка при сборе даты релиза Video')

def get_video_title(driver, css_selectors):
    try:
        video_title_element = driver.find_element(By.CSS_SELECTOR, css_selectors['video_title'])
        video_title = video_title_element.text.strip()
        return video_title
    except NoSuchElementException:
        print('Название Video не найдено!')
        return 'Название Video не найдено!'
    except Exception as e:
        print(f'Произошла ошибка при сборе названия Video: {e}')


def get_shorts_title(driver, css_selectors):
    open_shorts_description(driver, css_selectors)
    selectors = ['shorts_title_1', 'shorts_title_2', 'shorts_title_3', 'shorts_title_4']
    for selector in selectors:
        try:
            shorts_title_element = WebDriverWait(driver, 0.5).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, css_selectors[selector]))
            )
            return shorts_title_element.text.strip()
        except TimeoutException:
            print('Не удалось найти название Shorts. Пробую с помощью другого селектора...')
        except Exception as e:
            print(f'Произошла ошибка при сборе названия Shorts: {e}')

    print('Название Shorts не найдено')
    return 'Название Shorts не найдено'

def get_shorts_likes(driver, css_selectors):
    try:
        shorts_likes_element = driver.find_element(By.CSS_SELECTOR, css_selectors['shorts_likes'])
        shorts_likes = shorts_likes_element.text.strip()
        if shorts_likes == '–':
            return '0'
        else:
            return shorts_likes
    except NoSuchElementException:
        return 'Количество лайков Shorts не найдено!'
    except Exception as e:
        print(f'Произошла ошибка при сборе количества лайков Shorts: {e}')

def get_shorts_comments(driver, css_selectors):
    try:
        shorts_comments_element = driver.find_element(By.CSS_SELECTOR, css_selectors['shorts_comments'])
        shorts_comments = shorts_comments_element.text.strip()
        return shorts_comments
    except NoSuchElementException:
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
            description_element = WebDriverWait(driver, 0.5).until(
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
        views_element = driver.find_element(By.CSS_SELECTOR, css_selectors['shorts_views'])
        views = views_element.text.strip()
        return views
    except NoSuchElementException:
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


def info_from_user():
    print('Выберите тип видео:\n1. Video\n2. Shorts')
    choice = input('Введите 1 или 2: ')

    if choice == '1':
        scraper_functions = video_scraper_functions
        video_type = 'Video'
    elif choice == '2':
        scraper_functions = shorts_scraper_functions
        video_type = 'Shorts'
    else:
        print('Некорректный выбор!')
        exit()

    available_info = list(scraper_functions.keys())
    print('Выберите, какую информацию требуется собрать:')
    for i, function in enumerate(available_info):
        print(f'{i + 1}. {function}')

    selected_numbers = input('Введите номера для сбора желаемой информации через пробел: ')
    selected_numbers = [int(i) - 1 for i in selected_numbers.split()]
    selected_info = [available_info[i] for i in selected_numbers]
    return video_type, selected_info, scraper_functions

def scraping_info_from_videos(
        driver,
        css_selectors,
        input_filename,
        selected_info,
        scraper_functions,
        video_type
):

    input_data = load_json_file(input_filename)
    filtered_data = [video for video in input_data if video['type'] == video_type]

    if not filtered_data:
        print(f'Видео типа "{video_type} не найдены в файле!')
        return []

    video_data = []
    total_videos = len(filtered_data)
    for video_number, video in enumerate(filtered_data, 1):
        print(f'Обработка видео {video_number} из {total_videos}...\n')
        driver.get(video['url'])
        time.sleep(1)

        video_info = {
            'title': None,
            'views': None,
            'likes': None,
            'comments': None,
            'release_date': None,
            'url': None,
            'description': None,
        }

        if scraper_functions == video_scraper_functions:
            if is_video_unavailable(driver, css_selectors):
                print('Video недоступно!')
                video_info['status'] = 'Видео удалено/недоступно'
                video_data.append(video_info)
                continue
            else:
                print('Video доступно')

        collected_data = {}
        for key in selected_info:
            collected_data[key] = scraper_functions[key](driver, css_selectors)

        video_info.update(collected_data)
        video_data.append(video_info)
    return video_data

video_scraper_functions = {
    'title': get_video_title,
    'description': get_video_description,
    'release_date': get_video_release_date,
    'views': get_video_views,
    'likes': get_video_likes,
    'comments': get_video_comments,
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

    video_type, selected_info, scraper_functions = info_from_user()

    video_data = scraping_info_from_videos(
        driver,
        css_selectors,
        'video_data.json',
        selected_info,
        scraper_functions,
        video_type
    )

    save_json_file(video_data, 'test_main_data.json')

    input('Нажмите Enter, чтобы закрыть драйвер!')
    driver.quit()

if __name__ == '__main__':
    main()