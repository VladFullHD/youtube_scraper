import re
import time
import logging
from collections import OrderedDict
from selenium.common import TimeoutException, NoSuchElementException
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from driver_utils import setup_options_webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from file_utils import save_json_file, load_json_file


class YouTubeScraper:

    def __init__(self, driver, css_selectors):
        self.driver = driver
        self.css_selectors = css_selectors
        self.logger = logging.getLogger(__name__)

    def click_element(self, selector_key, timeout=1):
        """
        Кликает на элемент веб-страницы, используя CSS-селектор.

        Args:
            selector_key (str): Ключ для поиска значения в css_selectors.
            timeout (int, optional): Максимальное время ожидания элемента в секундах. По умолчанию = 2.

        Returns:
            None
        """
        try:
            element = WebDriverWait(self.driver, timeout).until(
                EC.visibility_of_element_located((By.CSS_SELECTOR, self.css_selectors[selector_key]))
            )
            ActionChains(self.driver).move_to_element(element).click().perform()
            self.logger.info(f'Клик на элемент {selector_key} выполнен успешно.')
        except TimeoutException:
            self.logger.warning(f'Не удалось кликнуть на элемент {selector_key}.')

    def is_video_unavailable(self):
        """
        Проверяет, доступно ли видео на YouTube.

        Returns:
            bool: True, если видео недоступно, False в противном случае.
        """
        try:
            self.driver.find_element(By.CSS_SELECTOR, self.css_selectors['is_video_unavailable'])
            self.logger.info('Проверка на доступность Video: не пройдена.')
            return True
        except NoSuchElementException:
            self.logger.info('Проверка на доступность Video: пройдена успешно.')
            return False

    def is_video_unacceptable(self):
        """
        Проверяет на наличие плашки "Это видео может оказаться неприемлемым для некоторых пользователей."

        Returns:
            bool: True, если видео недоступно, False в противном случае.
        """
        try:
            self.driver.find_element(By.CSS_SELECTOR, self.css_selectors['is_video_unacceptable'])
            self.logger.info('Проверка на неприемлемое Video: не пройдена.')
            return True
        except NoSuchElementException:
            self.logger.info('Проверка на неприемлемое Video: пройдена успешно.')
            return False

    def get_video_description(self):
        """
        Открывает описание Video и извлекает его.

        Returns:
            str: Текст описания видео. Если описание не найдено, возвращает 'Описание к Video не найдено!'.
        """
        self.click_element('video_description_button')
        try:
            description_element = self.driver.find_element(By.CSS_SELECTOR, self.css_selectors['video_description'])
            self.logger.info('Описание к Video найдено успешно.')
            return description_element.text.strip()
        except NoSuchElementException:
            self.logger.warning('Описание к Video не найдено.')
            return 'Описание к Video не найдено.'
        except Exception as e:
            self.logger.error(f'Произошла ошибка при сборе описания к Video: {e}.')
            return None

    def get_video_likes(self):
        """
        Извлекает количество лайков видео с YouTube.

        Returns:
            str или None: Количество лайков в виде строки с форматированием (например, '1.234.567'),
                            или '0', если вместо числа мы получаем 'одному пользователю',
                            или '0', если элемент не найден, так как это означает что лайков 0,
                            или None, если произошла другая ошибка.
        """
        try:
            like_element = self.driver.find_element(By.CSS_SELECTOR, self.css_selectors['video_likes'])
            aria_label = like_element.get_attribute("aria-label")
            if aria_label:
                if 'одному пользователю' in aria_label:
                    self.logger.info('В элементе "video_likes" содержится фраза "одному пользователю", количество лайков = 0')
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
                        self.logger.info('Количество лайков в Video найдено успешно.')
                        return formatted_likes
        except NoSuchElementException:
            self.logger.info('Элемент "video_likes" не найден, количество лайков = 0.')
            return '0'
        except Exception as e:
            self.logger.error(f"Произошла ошибка при сборе количества лайков в Video: {e}.")
            return None

    def get_video_comments(self):
        """
        Извлекает количество комментариев к видео с YouTube.

        Returns:
            str или None: Количество комментариев в виде строки,
                            или 'Комментарии отключены', если они отключены,
                            или None, если произошла ошибка.
        """
        max_attempts = 10
        attempts = 0
        try:
            try:
                self.driver.find_element(By.CSS_SELECTOR, self.css_selectors['comments_turned_off'])
                self.logger.warning('Комментарии к Video отключены.')
                return 'Комментарии к Video отключены.'
            except NoSuchElementException:
                while attempts < max_attempts:
                    attempts += 1
                    self.logger.info(f'Попытка {attempts}/{max_attempts} поиска количества комментариев в Video.')
                    try:
                        video_comments_element = WebDriverWait(self.driver, 2).until(
                            EC.presence_of_element_located((By.CSS_SELECTOR, self.css_selectors['video_comments']))
                        )
                        self.logger.info('Количество комментариев к Video найдено успешно.')
                        return video_comments_element.text.strip()
                    except TimeoutException:
                        self.logger.info(f'Попытка {attempts}/{max_attempts} не удалась. Приступаю к прокрутке страницы.')
                        self.driver.find_element("tag name", 'html').send_keys(Keys.PAGE_DOWN)
                        time.sleep(0.2)
                self.logger.warning('Достигнуто максимальное количество попыток поиска количества комментариев к Video.')
                return 'Количество комментариев к Video не найдено.'
        except Exception as e:
            self.logger.error(f'Произошла ошибка при сборе количества комментариев к Video: {e}.')
            return None

    def get_video_views(self):
        """
        Извлекает количество просмотров видео с YouTube.

        Returns:
            str или None: Количество просмотров в виде строки,
                            или 'Количество просмотров Video не найдено', если элемент не найден,
                            или None, если произошла другая ошибка.
        """
        try:
            views_element = self.driver.find_element(By.CSS_SELECTOR, self.css_selectors['video_views'])
            self.logger.info('Количество просмотров Video найдено успешно.')
            return views_element.text.strip()
        except NoSuchElementException:
            self.logger.warning('Количество просмотров Video не найдено.')
            return 'Количество просмотров Video не найдено.'
        except Exception as e:
            self.logger.error(f'Произошла ошибка при сборе количества просмотров Video: {e}.')
            return None

    def get_video_release_date(self):
        """
        Извлекает дату публикации видео с YouTube.

        Returns:
            str или None: Дата публикации в виде строки,
                            или 'Дата релиза Video не найдена', если элемент не найден,
                            или None, если произошла другая ошибка.
        """
        try:
            release_date_element = self.driver.find_element(By.CSS_SELECTOR, self.css_selectors['video_release_date'])
            self.logger.info('Дата релиза Video найдена успешно.')
            return release_date_element.text.strip()
        except NoSuchElementException:
            self.logger.warning('Дата релиза Video не найдена.')
            return 'Дата релиза Video не найдена.'
        except Exception as e:
            self.logger.error(f'Произошла ошибка при сборе даты релиза Video: {e}.')
            return None

    def get_video_title(self):
        """
        Извлекает заголовок видео с YouTube.

        Returns:
            str или None: Заголовок видео в виде строки,
                            или 'Название Video не найдено!', если элемент не найден,
                            или None, если произошла другая ошибка.
        """
        try:
            video_title_element = self.driver.find_element(By.CSS_SELECTOR, self.css_selectors['video_title'])
            self.logger.info('Заголовок к Video найден успешно.')
            return video_title_element.text.strip()
        except NoSuchElementException:
            self.logger.warning('Заголовок к Video не найден.')
            return 'Название Video не найдено.'
        except Exception as e:
            self.logger.error(f'Произошла ошибка при сборе заголовка Video: {e}.')
            return None


    def is_shorts_unacceptable(self):
        """
        Проверяет Shorts на наличие предупреждения о неприемлемом видео.

        Returns:
            bool: True, если Shorts недоступно, False в противном случае.
        """
        try:
            self.driver.find_element(By.CSS_SELECTOR, self.css_selectors['is_shorts_unacceptable'])
            self.logger.info('Проверка на неприемлемый Shorts: не пройдена.')
            return True
        except NoSuchElementException:
            self.logger.info('Проверка на неприемлемый Shorts: пройдена успешно.')
            return False

    def get_shorts_title(self):
        """
        Извлекает заголовок Shorts-видео с YouTube.

        Returns:
            str или None: Заголовок Shorts-видео в виде строки,
                         или 'Название Shorts не найдено', если элемент не найден,
                         или None, если произошла другая ошибка.
        """
        self.click_element('shorts_menu_button')
        self.click_element('shorts_description_button')
        self.click_element('shorts_more_button')

        selectors = ['shorts_title_1', 'shorts_title_2', 'shorts_title_3', 'shorts_title_4']
        for selector in selectors:
            try:
                shorts_title_element = WebDriverWait(self.driver, 0.5).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, self.css_selectors[selector]))
                )
                self.logger.info('Заголовок Shorts найден успешно.')
                return shorts_title_element.text.strip()
            except TimeoutException:
                self.logger.info(f'Не удалось найти название Shorts. Пробую другой CSS-селектор: {selector}...')
            except Exception as e:
                self.logger.error(f'Произошла ошибка при сборе заголовка Shorts: {e}.')
                return None
        self.logger.warning('Заголовок Shorts не найден.')
        return 'Название Shorts не найдено.'

    def get_shorts_likes(self):
        """
        Извлекает количество лайков Shorts-видео с YouTube.

        Returns:
            str или None: Количество лайков Shorts-видео в виде строки,
                         или '0', если лайки отображаются как '–',
                         или 'Количество лайков Shorts не найдено!', если элемент не найден,
                         или None, если произошла другая ошибка.
        """
        try:
            shorts_likes_element = self.driver.find_element(By.CSS_SELECTOR, self.css_selectors['shorts_likes'])
            shorts_likes = shorts_likes_element.text.strip()
            if shorts_likes == '–':
                self.logger.info('При извлечении количества лайков Shorts был обнаружен символ "-". Количество лайков = 0.')
                return '0'
            else:
                self.logger.info('Количество лайков Shorts найдено успешно.')
                return shorts_likes
        except NoSuchElementException:
            self.logger.warning('Количество лайков Shorts не найдено.')
            return 'Количество лайков Shorts не найдено.'
        except Exception as e:
            self.logger.error(f'Произошла ошибка при сборе количества лайков Shorts: {e}.')
            return None

    def get_shorts_comments(self):
        """
        Извлекает количество комментариев Shorts-видео с YouTube.

        Returns:
            str или None: Количество комментариев Shorts-видео в виде строки,
                         или 'Количество комментариев к Shorts не найдено!', если элемент не найден,
                         или None, если произошла другая ошибка.
        """
        try:
            shorts_comments_element = self.driver.find_element(By.CSS_SELECTOR, self.css_selectors['shorts_comments'])
            self.logger.info('Количество комментариев к Shorts найдено успешно.')
            return shorts_comments_element.text.strip()
        except NoSuchElementException:
            self.logger.warning('Количество комментариев к Shorts не найдено.')
            return 'Количество комментариев к Shorts не найдено.'
        except Exception as e:
            self.logger.error(f'Произошла ошибка при сборе количества комментариев в Shorts: {e}.')
            return None

    def get_shorts_description(self):
        """
        Извлекает описание Shorts-видео с YouTube.

        Returns:
            str: Текст описания Shorts-видео или 'Описание к Shorts не найдено', если описание не найдено.
        """
        selectors = ['shorts_description_1', 'shorts_description_2']
        for selector in selectors:
            try:
                description_element = WebDriverWait(self.driver, 0.5).until(
                    EC.visibility_of_element_located((By.CSS_SELECTOR, self.css_selectors[selector]))
                )
                self.logger.info('Описание к Shorts найдено успешно.')
                return description_element.text.strip()
            except TimeoutException:
                self.logger.info(f'Не удалось найти описание к Shorts. Пробую другой CSS-селектор: {selector}...')
            except Exception as e:
                self.logger.error(f'Произошла ошибка при сборе описания к Shorts: {e}.')
                return None
        self.logger.warning('Описание к Shorts не найдено.')
        return 'Описание к Shorts не найдено.'

    def get_shorts_views(self):
        """
        Извлекает количество просмотров Shorts-видео с YouTube.

        Returns:
            str: Количество просмотров Shorts-видео или 'Количество просмотров Shorts не найдено', если элемент не найден.
        """
        try:
            views_element = self.driver.find_element(By.CSS_SELECTOR, self.css_selectors['shorts_views'])
            self.logger.info('Количество просмотров Shorts найдено успешно.')
            return views_element.text.strip()
        except NoSuchElementException:
            self.logger.warning('Количество просмотров Shorts не найдено.')
            return 'Количество просмотров Shorts не найдено.'
        except Exception as e:
            self.logger.error(f'Произошла ошибка при сборе количества просмотров Shorts: {e}.')
            return None

    def get_shorts_release_date(self):
        """
        Извлекает дату публикации Shorts-видео с YouTube.

        Returns:
            str: Дата публикации Shorts-видео или 'Дата релиза Shorts не найдена', если дата не найдена.
        """
        try:
            day_month_element = WebDriverWait(self.driver, 0.5).until(
                EC.visibility_of_element_located((By.CSS_SELECTOR, self.css_selectors['shorts_day_month']))
            )
            day_month = day_month_element.text.strip()

            year_element = WebDriverWait(self.driver, 0.5).until(
                EC.visibility_of_element_located((By.CSS_SELECTOR, self.css_selectors['shorts_year']))
            )
            year = year_element.text.strip()

            if day_month and year:
                self.logger.info(f'Дата релиза Shorts в формате "{day_month} {year} г." найдена успешно.')
                return f'{day_month} {year} г.'

        except TimeoutException:
            self.logger.info('Дата релиза Shorts в формате "день/месяц/год" не найдена. Пробую найти в формате "X часов назад"...')
            try:
                hours_ago_element = WebDriverWait(self.driver, 0.5).until(
                    EC.visibility_of_element_located((By.CSS_SELECTOR, self.css_selectors['shorts_hours_ago_1']))
                )
                hours_ago = hours_ago_element.text.strip()

                ago_element = WebDriverWait(self.driver, 0.5).until(
                    EC.visibility_of_element_located((By.CSS_SELECTOR, self.css_selectors['shorts_hours_ago_2']))
                )
                ago = ago_element.text.strip()

                if hours_ago and ago:
                    self.logger.info(f'Дата релиза Shorts в формате "{hours_ago} {ago}" найдена успешно.')
                    return f'{hours_ago} {ago}'
            except TimeoutException:
                self.logger.warning('Дата релиза Shorts не найдена.')
                return 'Дата релиза Shorts не найдена.'
        except Exception as e:
            self.logger.error(f'Произошла ошибка при поиске даты релиза Shorts: {e}.')
            return None


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

    def info_from_user(self):
        """
        Запрашивает у пользователя тип видео и информацию для сбора.

        Returns:
            tuple[list[str], list[str], dict[str, Callable]]: Кортеж, содержащий:
                - Список типов видео ('Video' и/или 'Shorts').
                - Список выбранных пользователем параметров для сбора данных.
                - Словарь функций для сбора данных.
        """
        while True:
            print('Выберите тип видео:\n1. Video\n2. Shorts\n3. Shorts и Video')
            choice = input('Введите 1, 2 или 3: ')

            if choice == '1':
                self.logger.info('Выбран тип видео: "Video".')
                video_types = ['Video']
                scraper_functions = self.video_scraper_functions
                break
            elif choice == '2':
                self.logger.info('Выбран тип видео: "Shorts".')
                video_types = ['Shorts']
                scraper_functions = self.shorts_scraper_functions
                break
            elif choice == '3':
                self.logger.info('Выбран тип видео: "Video и Shorts".')
                video_types = ['Video', 'Shorts']
                scraper_functions = {**self.video_scraper_functions, **self.shorts_scraper_functions}
                break
            else:
                self.logger.warning('Некорректный выбор типа видео.')
                print('Некорректный выбор типа видео! Попробуйте еще раз.')

        base_info = ['type', 'url', 'channel_name', 'channel_url', 'preview_image']
        available_info = list(scraper_functions.keys()) + base_info
        while True:
            print('Выберите, какую информацию требуется собрать:')
            for i, function in enumerate(available_info):
                print(f'{i + 1}. {function}')

            selected_numbers = input('Введите номера для сбора желаемой информации через пробел\n(или нажмите Enter для сбора всей информации): ')

            if not selected_numbers:
                self.logger.info('Выбор необходимой для сбора информации был пропущен.')
                selected_info = available_info
                break
            else:
                try:
                    selected_numbers = [int(i) - 1 for i in selected_numbers.split()]
                    selected_info = [available_info[i] for i in selected_numbers if 0 <= i <len(available_info)]
                    break
                except ValueError:
                    self.logger.warning('Некорректный ввод номеров функций.')
                    print('Некорректный ввод номеров функций!')

        return video_types, selected_info

    def scraping_info_from_videos(self, input_filename, selected_info, video_types):
        """
        Собирает информацию о видеороликах из JSON-файла, применяя заданные функции сбора данных.

        Args:
            input_filename (str): Имя JSON-файла с данными о видеороликах.
            selected_info (list[str]): Список ключей функций для сбора данных.
            video_types (list[str]): Тип видеороликов для фильтрации ('Video' или 'Shorts').

        Returns:
            list[dict]: Список словарей, где каждый словарь содержит информацию об одном видеоролике.
                       Возвращает пустой список, если видеоролики заданного типа не найдены.
        """
        input_data = load_json_file(input_filename)
        #Фильтруем по указанному пользователем типу видео.
        filtered_data = [video for video in input_data if video['type'] in video_types]

        if not filtered_data:
            self.logger.warning(f'Видео типов "{", ".join(video_types)}" не найдены в файле!')
            return []

        video_data = []
        total_videos = len(filtered_data)
        for video_number, video in enumerate(filtered_data, 1):
            self.logger.info(f'\nОбработка видео {video_number} из {total_videos}...')
            self.driver.get(video['url'])
            time.sleep(1)

            video_info = OrderedDict()

            #Для перебора функций, которые выбрал пользователь.
            for func in selected_info:
                #Если выбранная пользователем функция присутствует в одном из словарей с функциями - собираем данные с веб-страницы.
                if func in self.video_scraper_functions or func in self.shorts_scraper_functions:
                    current_scraper_functions = {}
                    if video['type'] == 'Video' and func in self.video_scraper_functions:
                        self.logger.info(f'Выбрана функция {func} для сбора информации.')
                        current_scraper_functions[func] = self.video_scraper_functions[func]
                    elif video['type'] == 'Shorts' and func in self.shorts_scraper_functions:
                        self.logger.info(f'Выбрана функция {func} для сбора информации.')
                        current_scraper_functions[func] = self.shorts_scraper_functions[func]
                    else:
                        self.logger.warning(f'Неизвестный тип видео: {video['type']}, пропускаем...')
                        continue

                    if video['type'] == 'Video':
                        if self.is_video_unavailable():
                            video_info['status'] = 'Видео удалено/недоступно'
                            video_data.append(video_info)
                            continue
                        elif self.is_video_unacceptable():
                            video_info['status'] = 'YouTube посчитал данное видео неприемлемым!'
                            video_data.append(video_info)
                            continue

                    elif video['type'] == 'Shorts' and self.is_shorts_unacceptable():
                        video_info['status'] = 'Shorts недоступен, т.к. YouTube посчитал его неприемлемым.'
                        continue

                    collected_data = {}
                    for key in current_scraper_functions:
                        collected_data[key] = current_scraper_functions[key](self)

                    video_info.update(collected_data)
                #Если выбранная пользователем функция отсутствует в словарях - подтягиваем информацию из исходного файла.
                elif func in video:
                    video_info[func] = video[func]
            video_data.append(video_info)
        return video_data


    def main(self, driver):

        video_types, selected_info = self.info_from_user()

        video_data = self.scraping_info_from_videos('video_data.json', selected_info, video_types)

        save_json_file(video_data, 'test_main_data.json')

        input('Нажмите Enter, чтобы закрыть драйвер!')
        driver.quit()

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO,
                        format="%(asctime)s - %(levelname)s - %(funcName)s - %(message)s",
                        filename='video_info_scraper.log',
                        filemode='a',
                        encoding='utf-8'
                        )

    driver = setup_options_webdriver()
    css_selectors = load_json_file('css_selectors.json')
    scraper = YouTubeScraper(driver, css_selectors)
    scraper.main(driver)