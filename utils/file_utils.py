import csv
import json

def save_csv_file(data, csv_path, header=None):
    """
    Save data to csv-file.

    Args:
        data(list[list]): List of lists with data.
        csv_path(str): Path to csv-file.
        header(list[str], optional): List of headers. Defaults to None.

    Returns:
        bool: True - success/False - failure.
    """
    try:
        with open(csv_path, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.writer(csvfile)
            if header:
                writer.writerow(header)
            writer.writerows(data)
        print(f'Данные успешно записаны в файл "{csv_path}"!')
        return True
    except OSError as e:
        print(f'Ошибка записи в файл "{csv_path}": {e}')
        return False
    except Exception as e:
        print(f'Неизвестная ошибка записи в файл "{csv_path}": {e}')
        return False

def save_json_file(data, filename):
    try:
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
        print(f'Данные успешно сохранены в {filename}')
    except Exception as e:
        print(f'Произошла ошибка при сохранении в JSON: {e}')

def load_json_file(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        return json.load(f)