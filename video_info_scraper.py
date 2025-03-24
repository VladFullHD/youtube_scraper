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
    """
    Кликает на элемент веб-страницы, используя CSS-селектор.

    Args:
        driver (undetected_chromedriver.chrome.Chrome): Экземпляр веб-драйвера.
        css_selector (str): CSS-селектор для поиска элемента.
        timeout (int, optional): Максимальное время ожидания элемента в секундах. По умолчанию = 2.

    Returns:
        None
    """
    try:
        element = WebDriverWait(driver, timeout).until(
            EC.visibility_of_element_located((By.CSS_SELECTOR, css_selector))
        )
        actions = ActionChains(driver)
        actions.move_to_element(element).click().perform()
    except TimeoutException:
        pass

def is_video_unavailable(driver, css_selectors):
    """
    Проверяет, доступно ли видео на YouTube.

    Args:
        driver (undetected_chromedriver.chrome.Chrome): Экземпляр веб-драйвера.
        css_selectors (dict): Словарь с CSS-селектором для поиска элемента, указывающего на недоступность видео.

    Returns:
        bool: True, если видео недоступно, False в противном случае.
    """
    try:
        unavailable_element = driver.find_element(By.CSS_SELECTOR, css_selectors['is_video_unavailable'])
        return True
    except NoSuchElementException:
        return False

def is_video_unacceptable(driver, css_selectors):
    """
    Проверяет на наличие плашки "Это видео может оказаться неприемлемым для некоторых пользователей."

    Args:
        driver (undetected_chromedriver.chrome.Chrome): Экземпляр веб-драйвера.
        css_selectors (dict): Словарь с CSS-селектором для поиска элемента, указывающего на недоступность видео.

    Returns:
        bool: True, если видео недоступно, False в противном случае.
    """
    try:
        unavailable_element = driver.find_element(By.CSS_SELECTOR, css_selectors['is_video_unacceptable'])
        return True
    except NoSuchElementException:
        return False

def open_video_description(driver, css_selectors):
    """
    Открывает описание видео на YouTube, кликая на кнопку 'Ещё'.

    Args:
        driver (undetected_chromedriver.chrome.Chrome): Экземпляр веб-драйвера.
        css_selectors (dict): Словарь с CSS-селектором для кнопки "Ещё".

    Returns:
        None
    """
    try:
        description_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, css_selectors['description_button']))
        )
        actions = ActionChains(driver)
        actions.move_to_element(description_button).click().perform()
    except TimeoutException:
        print('Кнопка для развертывания описания Video не найдена!')

def get_video_description(driver, css_selectors):
    """
    Извлекает описание видео с YouTube.

    Args:
        driver (undetected_chromedriver.chrome.Chrome): Экземпляр веб-драйвера.
        css_selectors (dict): Словарь с CSS-селекторами для поиска описания.

    Returns:
        str: Текст описания видео. Если описание не найдено, возвращает 'Описание к Video не найдено!'.
    """
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
    """
    Извлекает количество лайков видео с YouTube.

    Args:
        driver (undetected_chromedriver.chrome.Chrome): Экземпляр веб-драйвера.
        css_selectors (dict): Словарь с CSS-селектором для поиска элемента с количеством лайков.

    Returns:
        str или None: Количество лайков в виде строки с форматированием (например, '1.234.567'),
                        или '0', если вместо числа мы получаем 'одному пользователю',
                        или '0', если элемент не найден, так как это означает что лайков 0,
                        или None, если произошла другая ошибка.
    """
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
        return '0'
    except Exception as e:
        print(f"Ошибка при извлечении лайков: {e}")
        return None

def get_video_comments(driver, css_selectors):
    """
    Извлекает количество комментариев к видео с YouTube.

    Args:
        driver (undetected_chromedriver.chrome.Chrome): Экземпляр веб-драйвера.
        css_selectors (dict): Словарь с CSS-селекторами для поиска элемента с количеством комментариев.

    Returns:
        str или None: Количество комментариев в виде строки,
                        или 'Комментарии отключены', если они отключены,
                        или None, если произошла ошибка.
    """
    max_attempts = 10
    attempts = 0
    try:
        try:
            driver.find_element(By.CSS_SELECTOR, css_selectors['comments_turned_off'])
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
                    driver.find_element("tag name", 'html').send_keys(Keys.PAGE_DOWN)
                    time.sleep(0.2)
            print('Достигнуто максимальное количество попыток поиска комментариев')
    except Exception as e:
        print(f'Произошла ошибка при сборе количества комментариев к видео: {e}')

def get_video_views(driver, css_selectors):
    """
    Извлекает количество просмотров видео с YouTube.

    Args:
        driver (undetected_chromedriver.chrome.Chrome): Экземпляр веб-драйвера.
        css_selectors (dict): Словарь с CSS-селектором для поиска элемента с количеством просмотров.

    Returns:
        str или None: Количество просмотров в виде строки,
                        или 'Количество просмотров Video не найдено', если элемент не найден,
                        или None, если произошла другая ошибка.
    """
    try:
        views_element = driver.find_element(By.CSS_SELECTOR, css_selectors['video_views'])
        views = views_element.text.strip()
        return views
    except NoSuchElementException:
        return 'Количество просмотров Video не найдено'
    except Exception as e:
        print(f'Произошла ошибка при сборе количества просмотров Video')

def get_video_release_date(driver, css_selectors):
    """
    Извлекает дату публикации видео с YouTube.

    Args:
        driver (undetected_chromedriver.chrome.Chrome): Экземпляр веб-драйвера.
        css_selectors (dict): Словарь с CSS-селектором для поиска элемента с датой публикации.

    Returns:
        str или None: Дата публикации в виде строки,
                        или 'Дата релиза Video не найдена', если элемент не найден,
                        или None, если произошла другая ошибка.
    """
    try:
        release_date_element = driver.find_element(By.CSS_SELECTOR, css_selectors['video_release_date'])
        release_date = release_date_element.text.strip()
        return release_date
    except NoSuchElementException:
        return 'Дата релиза Video не найдена'
    except Exception as e:
        print(f'Произошла ошибка при сборе даты релиза Video')

def get_video_title(driver, css_selectors):
    """
    Извлекает заголовок видео с YouTube.

    Args:
         driver (undetected_chromedriver.chrome.Chrome): Экземпляр веб-драйвера.
        css_selectors (dict): Словарь с CSS-селектором для поиска элемента с заголовком видео.

    Returns:
        str или None: Заголовок видео в виде строки,
                        или 'Название Video не найдено!', если элемент не найден,
                        или None, если произошла другая ошибка.
    """
    try:
        video_title_element = driver.find_element(By.CSS_SELECTOR, css_selectors['video_title'])
        video_title = video_title_element.text.strip()
        return video_title
    except NoSuchElementException:
        print('Название Video не найдено!')
        return 'Название Video не найдено!'
    except Exception as e:
        print(f'Произошла ошибка при сборе названия Video: {e}')


def is_shorts_unavailable(driver, css_selectors):
    """
    Проверяет Shorts на наличие предупреждения о неприемлемом видео.

    Args:
        driver (undetected_chromedriver.chrome.Chrome): Экземпляр веб-драйвера.
        css_selectors (dict): Словарь с CSS-селектором для поиска элемента, указывающего на недоступность видео.

    Returns:
        bool: True, если видео недоступно, False в противном случае.
    """
    try:
        unavailable_element = driver.find_element(By.CSS_SELECTOR, css_selectors['shorts_age_disclaimer'])
        return True
    except NoSuchElementException:
        return False

def get_shorts_title(driver, css_selectors):
    """
    Извлекает заголовок Shorts-видео с YouTube.

    Args:
        driver (undetected_chromedriver.chrome.Chrome): Экземпляр веб-драйвера.
        css_selectors (dict): Словарь с CSS-селекторами для поиска элемента с заголовком Shorts.

    Returns:
        str или None: Заголовок Shorts-видео в виде строки,
                     или 'Название Shorts не найдено', если элемент не найден,
                     или None, если произошла другая ошибка.
    """
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
    """
    Извлекает количество лайков Shorts-видео с YouTube.

    Args:
        driver (undetected_chromedriver.chrome.Chrome): Экземпляр веб-драйвера.
        css_selectors (dict): Словарь с CSS-селектором для поиска элемента с количеством лайков Shorts.

    Returns:
        str или None: Количество лайков Shorts-видео в виде строки,
                     или '0', если лайки отображаются как '–',
                     или 'Количество лайков Shorts не найдено!', если элемент не найден,
                     или None, если произошла другая ошибка.
    """
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
    """
    Извлекает количество комментариев Shorts-видео с YouTube.

    Args:
        driver (undetected_chromedriver.chrome.Chrome): Экземпляр веб-драйвера.
        css_selectors (dict): Словарь с CSS-селектором для поиска элемента с количеством комментариев Shorts.

    Returns:
        str или None: Количество комментариев Shorts-видео в виде строки,
                     или 'Количество комментариев к Shorts не найдено!', если элемент не найден,
                     или None, если произошла другая ошибка.
    """
    try:
        shorts_comments_element = driver.find_element(By.CSS_SELECTOR, css_selectors['shorts_comments'])
        shorts_comments = shorts_comments_element.text.strip()
        return shorts_comments
    except NoSuchElementException:
        return 'Количество комментариев к Shorts не найдено!'
    except Exception as e:
        print(f'Произошла ошибка при сборе комментариев в Shorts: {e}')

def open_shorts_description(driver, css_selectors):
    """
    Открывает описание Shorts-видео на YouTube, кликая на необходимые кнопки.

    Args:
        driver (undetected_chromedriver.chrome.Chrome): Экземпляр веб-драйвера.
        css_selectors (dict): Словарь с CSS-селекторами для кнопок открытия описания.

    Returns:
        None
    """
    click_element(driver, css_selectors['shorts_menu_button'])
    click_element(driver, css_selectors['shorts_description_button'])
    click_element(driver, css_selectors['shorts_more_button'])

def get_shorts_description(driver, css_selectors):
    """
    Извлекает описание Shorts-видео с YouTube.

    Args:
        driver (undetected_chromedriver.chrome.Chrome): Экземпляр веб-драйвера.
        css_selectors (dict): Словарь с CSS-селекторами для поиска элементов описания.

    Returns:
        str: Текст описания Shorts-видео или 'Описание Shorts не найдено', если описание не найдено.
    """
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
    """
    Извлекает количество просмотров Shorts-видео с YouTube.

    Args:
        driver (undetected_chromedriver.chrome.Chrome): Экземпляр веб-драйвера.
        css_selectors (dict): Словарь с CSS-селектором для поиска элемента с количеством просмотров.

    Returns:
        str: Количество просмотров Shorts-видео или 'Количество просмотров Shorts не найдено', если элемент не найден.
    """
    try:
        views_element = driver.find_element(By.CSS_SELECTOR, css_selectors['shorts_views'])
        views = views_element.text.strip()
        return views
    except NoSuchElementException:
        return 'Количество просмотров Shorts не найдено'
    except Exception as e:
        print(f'Произошла ошибка при сборе количества просмотров Shorts')

def get_shorts_release_date(driver, css_selectors):
    """
    Извлекает дату публикации Shorts-видео с YouTube.

    Args:
        driver (undetected_chromedriver.chrome.Chrome): Экземпляр веб-драйвера.
        css_selectors (dict): Словарь с CSS-селекторами для поиска элементов даты публикации.

    Returns:
        str: Дата публикации Shorts-видео или 'Дата релиза Shorts не найдена', если дата не найдена.
    """
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
    """
    Запрашивает у пользователя тип видео и информацию для сбора.

    Returns:
        tuple[list[str], list[str], dict[str, Callable]]: Кортеж, содержащий:
            - Список типов видео ('Video' и/или 'Shorts').
            - Список выбранных пользователем параметров для сбора данных.
            - Словарь функций для сбора данных.
    """
    print('Выберите тип видео:\n1. Video\n2. Shorts\n3. Shorts и Video')
    choice = input('Введите 1, 2 или 3: ')

    if choice == '1':
        video_types = ['Video']
        scraper_functions = video_scraper_functions
    elif choice == '2':
        video_types = ['Shorts']
        scraper_functions = shorts_scraper_functions
    elif choice == '3':
        video_types = ['Video', 'Shorts']
        scraper_functions = {**video_scraper_functions, **shorts_scraper_functions}
    else:
        print('Некорректный выбор!')
        return None

    available_info = list(scraper_functions.keys())
    print('Выберите, какую информацию требуется собрать:')
    for i, function in enumerate(available_info):
        print(f'{i + 1}. {function}')

    selected_numbers = input('Введите номера для сбора желаемой информации через пробел\n(или нажмите Enter для сбора всей информации): ')

    if not selected_numbers:
        selected_info = available_info
    else:
        selected_numbers = [int(i) - 1 for i in selected_numbers.split()]
        selected_info = [available_info[i] for i in selected_numbers if 0 <= i <len(available_info)]

    selected_scraper_functions = {}
    for info_key in selected_info:
        if info_key in selected_info:
            selected_scraper_functions[info_key] = scraper_functions[info_key]
    return video_types, selected_info

def scraping_info_from_videos(
        driver,
        css_selectors,
        input_filename,
        selected_info,
        video_types
):
    """
    Собирает информацию о видеороликах из JSON-файла, применяя заданные функции сбора данных.

    Args:
        driver (undetected_chromedriver.chrome.Chrome): Экземпляр веб-драйвера.
        css_selectors (dict): Словарь с CSS-селекторами для поиска элементов видеороликов.
        input_filename (str): Имя JSON-файла с данными о видеороликах.
        selected_info (list[str]): Список ключей функций для сбора данных.
        video_types (list[str]): Тип видеороликов для фильтрации ('Video' или 'Shorts').

    Returns:
        list[dict]: Список словарей, где каждый словарь содержит информацию об одном видеоролике.
                   Возвращает пустой список, если видеоролики заданного типа не найдены.
    """
    input_data = load_json_file(input_filename)
    filtered_data = [video for video in input_data if video['type'] in video_types]

    if not filtered_data:
        print(f'Видео типов "{", ".join(video_types)}" не найдены в файле!')
        return []

    video_data = []
    total_videos = len(filtered_data)
    for video_number, video in enumerate(filtered_data, 1):
        print(f'\nОбработка видео {video_number} из {total_videos}...')
        driver.get(video['url'])
        time.sleep(1)

        video_info = {
            'title': None,
            'type': video['type'],
            'views': None,
            'likes': None,
            'comments': None,
            'release_date': None,
            'url': video['url'],
            'channel_name': video['channel_name'],
            'channel_url': video['channel_url'],
            'description': None,
            'preview_image': video['preview_image']
        }

        current_scraper_functions = {}
        if video['type'] == 'Video':
            for key in selected_info:
                if key in video_scraper_functions:
                    current_scraper_functions[key] = video_scraper_functions[key]
        elif video['type'] == 'Shorts':
            for key in selected_info:
                if key in shorts_scraper_functions:
                    current_scraper_functions[key] = shorts_scraper_functions[key]
        else:
            print(f'Неизвестный тип видео: {video['type']}, пропускаем...')
            continue

        if video['type'] == 'Video':
            if is_video_unavailable(driver, css_selectors):
                print('Video недоступно!')
                video_info['status'] = 'Видео удалено/недоступно'
                video_data.append(video_info)
                continue
            elif is_video_unacceptable(driver, css_selectors):
                print('YouTube посчитал данное видео неприемлемым!')
                video_info['status'] = 'YouTube посчитал данное видео неприемлемым!'
                video_data.append(video_info)
                continue

        elif video['type'] == 'Shorts' and is_shorts_unavailable(driver, css_selectors):
            print('Shorts недоступен, т.к. YouTube посчитал его неприемлемым.')
            video_info['status'] = 'Shorts недоступен, т.к. YouTube посчитал его неприемлемым.'
            continue

        collected_data = {}
        for key in current_scraper_functions:
            collected_data[key] = current_scraper_functions[key](driver, css_selectors)

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

    video_types, selected_info = info_from_user()

    video_data = scraping_info_from_videos(
        driver,
        css_selectors,
        'video_data.json',
        selected_info,
        video_types
    )

    save_json_file(video_data, 'test_main_data.json')

    input('Нажмите Enter, чтобы закрыть драйвер!')
    driver.quit()

if __name__ == '__main__':
    main()