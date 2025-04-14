import logging
from googleapiclient.discovery import build
from google.oauth2.service_account import Credentials
from selenium.common import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains

def extract_channel_name(text):
    at_position = text.find('@')
    if at_position != -1:
        channel_name = text[at_position + 1:]
        channel_name = channel_name.strip()
        return channel_name
    else:
        return None

def get_functions_from_user(info_type, available_info):
    while True:
        print(f'Выберите, какую информацию о {info_type} необходимо собрать:')
        for i, function in enumerate(available_info):
            print(f'{i + 1}. {function}')

        selected_numbers = input(
            'Введите номера, чтобы выбрать необходимую информацию через пробел\n(Или нажмите Enter для сбора всей информации): ')
        if not selected_numbers:
            logging.info(f'Выбор необходимой информации о {info_type} был пропущен.')
            return available_info

        try:
            selected_numbers = [int(i) - 1 for i in selected_numbers.split()]
            selected_info = [available_info[i] for i in selected_numbers if 0 <= i < len(available_info)]
            return selected_info
        except ValueError:
            logging.warning('Некорректный ввод номеров функций.')
            print('Некорректный ввод номеров функций!')

def save_to_googlesheets(data, spreadsheet_id, channel_name, credentials_file):
    try:
        SCOPES = ['https://www.googleapis.com/auth/spreadsheets']

        creds = Credentials.from_service_account_file(credentials_file, scopes=SCOPES)

        service = build('sheets', 'v4', credentials=creds)

        spreadsheet = service.spreadsheets().get(spreadsheetId=spreadsheet_id).execute()
        sheet_exists = False
        for sheet in spreadsheet.get('sheets', []):
            if sheet['properties']['title'] == channel_name:
                sheet_exists = True
                break

        if not sheet_exists:
            add_sheet_request = {
                'requests': [{
                    'addSheet': {
                        'properties': {
                            'title': channel_name
                        }
                    }
                }]
            }
            service.spreadsheets().batchUpdate(spreadsheetId=spreadsheet_id, body=add_sheet_request).execute()
            logging.info(f'Создан новый лист "{channel_name}".')
        else:
            logging.info(f'Лист "{channel_name}" уже существует.')

        if not data:
            logging.warning(f'Нет данных для выгрузки в Google Sheets')
            return

        headers = list(data[0].keys())
        values = [headers] + [list(item.values()) for item in data]

        range_ = f"'{channel_name}'!A1"

        body = {
            'values': values
        }

        result = service.spreadsheets().values().update(
            spreadsheetId=spreadsheet_id,
            range=range_,
            valueInputOption='USER_ENTERED',
            body=body
        ).execute()

        logging.info(f'Данные успешно выгружены в Google Sheets.')

    except Exception as e:
        logging.error(f'Произошла ошибка при работе с Google Sheets: {e}.')

def click_element(driver, css_selectors, selector_key, timeout=1):
    try:
        element = WebDriverWait(driver, timeout).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, css_selectors[selector_key]))
        )
        ActionChains(driver).move_to_element(element).click().perform()
        logging.info(f'Клик на элемент {selector_key} выполнен успешно.')
    except TimeoutException:
        logging.warning(f'Не удалось кликнуть на элемент {selector_key}.')

def channel_filter_input():
    while True:
        print(f'Доступные фильтры:\n1. popular\n2. old')
        user_filter_input = input(
            'Введите номер, чтобы выбрать необходимый фильтр (или нажмите Enter для дефолтного "New"): ').strip()

        if not user_filter_input:
            return None
        elif user_filter_input == '1':
            return '1'
        elif user_filter_input == '2':
            return '2'
        else:
            print('Ошибка: введен некорректный фильтр!')
