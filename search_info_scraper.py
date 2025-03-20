import re
import time
from selenium.common import TimeoutException, NoSuchElementException
from selenium.webdriver.common.keys import Keys
from selenium.webdriver import ActionChains
from driver_utils import setup_options_webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from file_utils import save_json_file, load_json_file
from driver_utils import scroll_selenium_keys


def open_youtube(driver):
    try:
        driver.get('https://www.youtube.com')
    except Exception as e:
        print(f'Произошла ошибка при открытии YouTube: {e}')

def search_input(driver):
    search_text = input('Введите поисковый запрос для поиска в YouTube: ').strip()
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
    """
    Устанавливает фильтр и/или сортировку в поисковой строке YouTube.
    Args:
        driver (undetected_chromedriver.chrome.Chrome): Экземпляр веб-драйвера.
        filter_names (list[str]): Список строк, представляющих имена фильтров.

    Returns:
        None
    """
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
    """
    Собирает все HTML-элементы видеороликов со страницы результатов поиска YouTube.

    Args:
        driver (undetected_chromedriver.chrome.Chrome): Экземпляр веб-драйвера.
        all_videos_css (dict): Словарь с CSS-селекторами для поиска элементов видеороликов.

    Returns:
        list или None: Список найденных HTML-элементов видеороликов или None в случае ошибки.
    """
    try:
        print('Начинаю сбор всего HTML-кода страницы!')
        videos_elements = WebDriverWait(driver, 10).until(
            EC.presence_of_all_elements_located((By.CSS_SELECTOR, all_videos_css['all_videos']))
        )
        return videos_elements
    except Exception as e:
        print(f'Произошла ошибка при сборе общей информации о роликах: {e}')
        return None

def get_titles_from_search(video_elements, title_css):
    """
    Извлекает заголовки видеороликов из списка HTML-элементов.

    Args:
        video_elements (list[WebElement]): Список HTML-элементов видеороликов.
        title_css (dict): Словарь с CSS-селектором для поиска заголовков.

    Returns:
        list[str]: Список заголовков видеороликов. В случае NoSuchElementException - 'Не найдено!'.
    """
    titles = []
    for video_element in video_elements:
        try:
            title_element = video_element.find_element(By.CSS_SELECTOR, title_css['title'])
            title = title_element.text.strip()
            if title:
                titles.append(title)
        except NoSuchElementException:
            titles.append('Не найдено!')
        except Exception as e:
            print(f'Произошла ошибка при сборе заголовков видео: {e}')
    return titles

def get_urls_from_search(video_elements, url_css):
    """
    Извлекает URL-адреса видеороликов из списка HTML-элементов.

    Args:
        video_elements (list[WebElement]): Список HTML-элементов видеороликов.
        url_css (dict): Словарь с CSS-селектором для поиска URL-адресов.

    Returns:
        list[str]: Список URL-адресов видеороликов. В случае NoSuchElementException - 'Не найдено!'.
    """
    video_urls = []
    for video_element in video_elements:
        try:
            video_url_element = video_element.find_element(By.CSS_SELECTOR, url_css['video_url'])
            video_url = video_url_element.get_attribute('href')
            if video_url:
                video_urls.append(video_url)
        except NoSuchElementException:
            video_urls.append('Не найдено!')
        except Exception as e:
            print(f'Произошла ошибка при сборе ссылок на видео: {e}')
    return video_urls

def get_views_from_search(video_elements, views_css):
    """
    Извлекает количество просмотров в видеороликах из списка HTML-элементов.

    Args:
        video_elements (list[WebElement]): Список HTML-элементов видеороликов.
        views_css (dict): Словарь с CSS-селектором для поиска количества просмотров.

    Returns:
        list[str]: Список количества просмотров в видеороликах. В случае NoSuchElementException - 'Не найдено!'
    """
    views = []
    for video_element in video_elements:
        try:
            view_element = video_element.find_element(By.CSS_SELECTOR, views_css['views'])
            view = view_element.text.strip()
            if view:
                if 'Планируемая дата публикации' in view:
                    views.append(None)
                else:
                    views.append(view)
        except NoSuchElementException:
            views.append('Не найдено!')
        except Exception as e:
            print(f'Произошла ошибка при сборе количества просмотров: {e}')
    return views

def get_release_dates_from_search(video_elements, release_date_css):
    """
            Извлекает даты выхода видеороликов из списка HTML-элементов.

            Args:
                video_elements (list[WebElement]): Список HTML-элементов видеороликов.
                release_date_css (dict): Словарь с CSS-селектором для поиска даты выхода видеороликов.

            Returns:
                list[str]: Список дат выхода видеороликов. В случае NoSuchElementException - 'Не найдено!'
    """
    release_dates = []
    for video_element in video_elements:
        try:
            release_date_element = video_element.find_element(By.CSS_SELECTOR, release_date_css['release_date'])
            release_date = release_date_element.text.strip()
            if release_date:
                release_dates.append(release_date)
        except NoSuchElementException:
            release_dates.append('Не найдено!')
        except Exception as e:
            print(f'Произошла ошибка при сборе даты релиза: {e}')
    return release_dates

def get_channel_names_from_search(video_elements, channel_name_css):
    """
    Извлекает названия YouTube-каналов, выпустивших видеоролики из списка HTML-элементов.

    Args:
        video_elements (list[WebElement]): Список HTML-элементов видеороликов.
        channel_name_css (dict): Словарь с CSS-селектором для поиска названий YouTube-каналов.

    Returns:
        list[str]: Список названий YouTube-каналов, выпустивших видеоролики. В случае NoSuchElementException - 'Не найдено!'
    """
    channel_names = []
    for video_element in video_elements:
        try:
            channel_element = video_element.find_element(By.CSS_SELECTOR, channel_name_css['channel_info'])
            channel_name = channel_element.text.strip()
            if channel_name:
                channel_names.append(channel_name)
        except NoSuchElementException:
            channel_names.append('Не найдено!')
        except Exception as e:
            print(f'Произошла ошибка при сборе наименований каналов: {e}')
    return channel_names

def get_channel_urls_from_search(video_elements, channel_url_css):
    """
    Извлекает URL-адреса YouTube-каналов, выпустивших видеоролики из списка HTML-элементов.

    Args:
        video_elements (list[WebElement]): Список HTML-элементов видеороликов.
        channel_url_css (dict): Словарь с CSS-селектором для поиска URL-адресов YouTube-каналов.

    Returns:
        list[str]: Список URL-адресов YouTube-каналов, выпустивших видеоролики. В случае NoSuchElementException - 'Не найдено!'
    """
    channel_urls = []
    for video_element in video_elements:
        try:
            channel_element = video_element.find_element(By.CSS_SELECTOR, channel_url_css['channel_url'])
            channel_url = channel_element.get_attribute('href')
            if channel_url:
                channel_urls.append(channel_url)
        except NoSuchElementException:
            channel_urls.append('Не найдено!')
        except Exception as e:
            print(f'Произошла ошибка при сборе ссылок на каналы: {e}')
    return channel_urls

def get_preview_image_from_search(video_elements, preview_image_css):
    """
    Извлекает URL-адреса на превью видеороликов из списка HTML-элементов.

    Args:
        video_elements (list[WebElement]): Список HTML-элементов видеороликов.
        preview_image_css (dict): Словарь с CSS-селектором для поиска URL-адресов превью видеороликов.

    Returns:
        list[str]: Список URL-адресов на превью видеороликов. В случае NoSuchElementException - 'Не найдено!'
    """
    preview_images = []
    for video_element in video_elements:
        try:
            preview_image_element = video_element.find_element(By.CSS_SELECTOR, preview_image_css['preview_image_url'])
            preview_image = preview_image_element.get_attribute('src')
            if preview_image is None:
                preview_images.append('Не найдено!')
            else:
                preview_images.append(preview_image)
        except NoSuchElementException:
            preview_images.append('Не найдено!')
        except Exception as e:
            print(f'Произошла ошибка при сборе ссылок на превью: {e}')
    return preview_images


def scraping_info_from_search(driver, css_selectors, selected_data, functions):
    """
    Собирает информацию о видеороликах со страницы результатов поиска YouTube.

    Args:
        driver (undetected_chromedriver.chrome.Chrome): Экземпляр веб-драйвера.
        css_selectors (dict): Словарь с CSS-селекторами для поиска элементов видеороликов.
        selected_data (list[str]): Список ключей функций для сбора данных.
        functions (dict[str, Callable]): Словарь функций для сбора данных.

    Returns:
        list[dict]: Список словарей, где каждый словарь содержит информацию об одном видеоролике.

    """
    print('Начинаем прокрутку страницы')
    scroll_selenium_keys(driver)
    print('Прокрутка страницы завершена\n')

    video_elements = get_all_elements_from_search(driver, css_selectors)
    print(f'Найдено {len(video_elements)} элементов видео.\n')

    collected_data = {}
    for key in selected_data:
        print(f'Выполняем функцию {functions[key].__name__}')
        collected_data[key] = functions[key](video_elements, css_selectors)
        print(f'Сбор данных "{key}" завершен.\n')

    video_data = []
    for i in range(len(video_elements)):
        video_info = {key: collected_data[key][i] for key in selected_data}
        video_data.append(video_info)
    return video_data

def filters_input(driver):
    """
    Запрашивает у пользователя фильтры для применения на странице результатов поиска YouTube.

    Args:
         driver (undetected_chromedriver.chrome.Chrome): Экземпляр веб-драйвера.

    Returns:
        None
    """
    filters = load_json_file('filters.json')

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

def info_settings_input(driver, functions):
    """
    Запрашивает у пользователя, какие данные необходимо собрать со страницы результатов поиска YouTube.

    Args:
        driver (undetected_chromedriver.chrome.Chrome): Экземпляр веб-драйвера.
        functions (dict[str, Callable]): Словарь функций для сбора данных.

    Returns:
        list[str]: Список выбранных пользователем параметров для сбора данных.
    """
    available_options = list(functions.keys())
    print(f'Доступные параметры: {', '.join(available_options)}')
    user_input = input('Введите через запятую, какие данные вы хотите собрать: ').strip()

    if not user_input:
        print('Не указано, какие данные необходимо собрать. Запускаю сбор всех данных...')
        selected_data = available_options
    else:
        selected_data = [item.strip() for item in user_input.split(',') if item.strip() in functions]
    if not selected_data:
        print('Не выбраны корректные параметры! Завершение программы.')
        driver.quit()

    return selected_data

def video_type_checker(video_elements, css_selectors):
    """
    Определяет тип видеороликов (Shorts, Live, Video) на основе url-адресов и дат публикации.

    Args:
        video_elements (list[WebElement]): Список HTML-элементов видеороликов.
        css_selectors (dict): Словарь с CSS-селекторами для поиска элементов видеороликов.

    Returns:
        list[str]: Список типов видеороликов ('Shorts', 'Live', 'Video') или 'Неизвестно' в случае ошибки.
    """
    video_urls = get_urls_from_search(video_elements, css_selectors)
    release_dates = get_release_dates_from_search(video_elements, css_selectors)
    video_types = []
    for i, url in enumerate(video_urls):
        try:
            if re.search(r'/shorts/', url):
                video_types.append('Shorts')
            elif release_dates[i] is None:
                video_types.append('Live')
            else:
                video_types.append('Video')
        except Exception as e:
            video_types.append('Неизвестно')
    return video_types


search_scraper_functions = {
    "name": get_titles_from_search,
    "url": get_urls_from_search,
    "type": video_type_checker,
    "views": get_views_from_search,
    "release_date": get_release_dates_from_search,
    "channel_name": get_channel_names_from_search,
    "channel_url": get_channel_urls_from_search,
    "preview_image": get_preview_image_from_search
}


def main():
    driver = setup_options_webdriver()
    open_youtube(driver)

    css_selectors = load_json_file('css_selectors.json')
    functions = search_scraper_functions

    search_input(driver)
    time.sleep(2)

    filters_input(driver)
    selected_data = info_settings_input(driver, functions)

    video_data = scraping_info_from_search(driver, css_selectors, selected_data, functions)

    save_json_file(video_data, 'video_data.json')

    input('Нажмите Enter, чтобы закрыть драйвер!')
    driver.quit()

if __name__ == "__main__":
    main()