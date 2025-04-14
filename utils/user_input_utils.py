import logging

logger = logging.getLogger(__name__)

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