import logging
from googleapiclient.discovery import build
from google.oauth2.service_account import Credentials

logger = logging.getLogger(__name__)


def save_to_googlesheets(data, spreadsheet_id, sheet_name, credentials_file):
    try:
        SCOPES = ['https://www.googleapis.com/auth/spreadsheets']

        creds = Credentials.from_service_account_file(credentials_file, scopes=SCOPES)

        service = build('sheets', 'v4', credentials=creds)

        spreadsheet = service.spreadsheets().get(spreadsheetId=spreadsheet_id).execute()
        sheet_exists = False
        for sheet in spreadsheet.get('sheets', []):
            if sheet['properties']['title'] == sheet_name:
                sheet_exists = True
                break

        if not sheet_exists:
            add_sheet_request = {
                'requests': [{
                    'addSheet': {
                        'properties': {
                            'title': sheet_name
                        }
                    }
                }]
            }
            service.spreadsheets().batchUpdate(spreadsheetId=spreadsheet_id, body=add_sheet_request).execute()
            logging.info(f'Создан новый лист "{sheet_name}".')
        else:
            logging.info(f'Лист "{sheet_name}" уже существует.')

        if not data:
            logging.warning(f'Нет данных для выгрузки в Google Sheets')
            return

        headers = list(data[0].keys())
        values = [headers] + [list(item.values()) for item in data]

        range_ = f"'{sheet_name}'!A1"

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

