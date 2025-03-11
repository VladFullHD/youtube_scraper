import os
import csv
import json

def save_html_file(html, html_path):
    """
    Saves the HTML-code file to the given path.

    Args:
        html: The HTML code of the page written to the variable.
        html_path: The location to which the HTML-code file will be saved.

    Returns:
        True/False - Saved/error writing to file.
    """
    try:
        with open(html_path, 'w', encoding='utf-8') as f:
            f.write(html)
        print(f'HTML-код страницы успешно сохранен в: "{html_path}"')
        return True
    except OSError as e:
        print(f'Ошибка записи в файл "{html_path}": {e}')
        return False
    except Exception as e:
        print(f'Неизвестная ошибка записи в файл "{html_path}": {e}')
        return False

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

def load_html_file(html_path):
    """
    Reads the saved HTML-code file.

    Args:
        html_path(str): The path to the HTML-code file.

    Returns:
        str: The HTML code of the page.
        None: If the file is not found or an error occurred when opening the file.
    """
    try:
        with open(html_path, 'r', encoding='utf-8') as f:
            html = f.read()
        return html
    except FileNotFoundError:
        print(f'Ошибка: Файл "{html_path}" не найден.')
        return None
    except OSError as e:
        print(f'Ошибка при открытии файла "{html_path}": {e}')
    except Exception as e:
        print(f'Неизвестная ошибка при открытии файла "{html_path}": {e}')
        return None

def html_file_path(folder_name, html_filename):
    """
    Combines the name of the folder where HTML pages are stored with the name of the file containing the HTML page.

    Args:
        folder_name: The name of the folder for storing.
        html_filename: The name of the file containing the HTML page.

    Returns:
        The path to the file we need.
    """
    return os.path.join(folder_name, html_filename)

def csv_file_path(folder_name, csv_filename):
    """
    Combines the name of the folder where csv-files are stored with the name of the file.

    Args:
        folder_name: The name of the folder for storing.
        csv_filename: The name of the file containing the HTML page.

    Returns:
        The path to the file we need.
        """
    return os.path.join(folder_name, csv_filename)

def create_folder(folder_name):
    """
    Creates a folder with a specific name.

    Args:
        folder_name: The name of the folder.

    Returns:
        True/False - folder created/error.
    """
    try:
        os.makedirs(folder_name, exist_ok=True)
        print(f'Папка под названием "{folder_name}" успешно создана!')
        return True
    except Exception as e:
        print(f'Произошла ошибка при создании папки "{folder_name}": {e}')
        return False
