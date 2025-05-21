"""
Вспомогательные функции и утилиты
"""
import os
import uuid
import secrets
import re
from datetime import datetime, timedelta
from werkzeug.utils import secure_filename
from flask import current_app
from sqlalchemy import or_

def generate_unique_filename(filename):
    """
    Генерация уникального имени файла
    :param filename: исходное имя файла
    :return: уникальное имя файла
    """
    ext = os.path.splitext(filename)[1]
    return f"{uuid.uuid4().hex}{ext}"

def allowed_file(filename):
    """
    Проверка разрешенного расширения файла
    :param filename: имя файла
    :return: bool
    """
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in current_app.config['ALLOWED_EXTENSIONS']

def save_file(file, subfolder=''):
    """
    Сохранение файла
    :param file: объект файла
    :param subfolder: подпапка для сохранения
    :return: (filename, file_path, file_size)
    """
    if not file:
        return None, None, None

    filename = secure_filename(file.filename)
    if not allowed_file(filename):
        raise ValueError('Неподдерживаемый тип файла')

    unique_filename = generate_unique_filename(filename)
    folder_path = os.path.join(current_app.config['UPLOAD_FOLDER'], subfolder)
    os.makedirs(folder_path, exist_ok=True)

    file_path = os.path.join(folder_path, unique_filename)
    file.save(file_path)
    file_size = os.path.getsize(file_path)

    return filename, os.path.join(subfolder, unique_filename), file_size

def delete_file(file_path):
    """
    Удаление файла
    :param file_path: путь к файлу
    """
    if not file_path:
        return

    full_path = os.path.join(current_app.config['UPLOAD_FOLDER'], file_path)
    if os.path.exists(full_path):
        os.remove(full_path)

def apply_pagination(query, page=1, per_page=20):
    """
    Применение пагинации к запросу
    :param query: исходный запрос
    :param page: номер страницы
    :param per_page: количество элементов на странице
    :return: объект пагинации
    """
    return query.paginate(page=page, per_page=per_page)

def apply_ordering(query, sort_by=None, order='asc'):
    """
    Применение сортировки к запросу
    :param query: исходный запрос
    :param sort_by: поле для сортировки
    :param order: направление сортировки (asc/desc)
    :return: модифицированный запрос
    """
    if not sort_by:
        return query

    model = query.column_descriptions[0]['entity']
    if not hasattr(model, sort_by):
        return query

    column = getattr(model, sort_by)
    if order == 'desc':
        column = column.desc()

    return query.order_by(column)

def apply_search(query, search_text, search_fields):
    """
    Применение поиска к запросу
    :param query: исходный запрос
    :param search_text: текст для поиска
    :param search_fields: список полей для поиска
    :return: модифицированный запрос
    """
    if not search_text or not search_fields:
        return query

    model = query.column_descriptions[0]['entity']
    search_filters = []

    for field in search_fields:
        if hasattr(model, field):
            column = getattr(model, field)
            search_filters.append(column.ilike(f'%{search_text}%'))

    if search_filters:
        return query.filter(or_(*search_filters))

    return query

def format_datetime(dt):
    """
    Форматирование даты и времени
    :param dt: объект datetime
    :return: отформатированная строка
    """
    if not dt:
        return None
    return dt.strftime('%Y-%m-%d %H:%M:%S')

def parse_datetime(date_str):
    """
    Парсинг строки в datetime
    :param date_str: строка с датой
    :return: объект datetime или None
    """
    if not date_str:
        return None

    formats = [
        '%Y-%m-%d %H:%M:%S',
        '%Y-%m-%d %H:%M',
        '%Y-%m-%d'
    ]

    for fmt in formats:
        try:
            return datetime.strptime(date_str, fmt)
        except ValueError:
            continue

    return None

def calculate_date_range(period):
    """
    Расчет диапазона дат
    :param period: период (today/week/month/year)
    :return: tuple(start_date, end_date)
    """
    now = datetime.now()

    if period == 'today':
        start_date = now.replace(hour=0, minute=0, second=0, microsecond=0)
        end_date = now.replace(hour=23, minute=59, second=59, microsecond=999999)
    elif period == 'week':
        start_date = now - timedelta(days=now.weekday())
        start_date = start_date.replace(hour=0, minute=0, second=0, microsecond=0)
        end_date = start_date + timedelta(days=6, hours=23, minutes=59, seconds=59, microseconds=999999)
    elif period == 'month':
        start_date = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        if now.month == 12:
            end_date = now.replace(year=now.year + 1, month=1, day=1) - timedelta(microseconds=1)
        else:
            end_date = now.replace(month=now.month + 1, day=1) - timedelta(microseconds=1)
    elif period == 'year':
        start_date = now.replace(month=1, day=1, hour=0, minute=0, second=0, microsecond=0)
        end_date = now.replace(month=12, day=31, hour=23, minute=59, second=59, microsecond=999999)
    else:
        raise ValueError('Неподдерживаемый период')

    return start_date, end_date

def generate_access_token(length=32):
    """
    Генерация токена доступа для файлов
    :param length: длина токена
    :return: строка токена
    """
    return secrets.token_hex(length // 2)

def generate_code_from_name(name):
    """
    Генерация кода из названия путем транслитерации
    :param name: исходное название
    :return: транслитерированный код с добавлением 4 уникальных hex символов
    """
    if not name:
        return None

    # Словарь транслитерации
    translit_dict = {
        'а': 'a', 'б': 'b', 'в': 'v', 'г': 'g', 'д': 'd', 'е': 'e', 'ё': 'e',
        'ж': 'zh', 'з': 'z', 'и': 'i', 'й': 'y', 'к': 'k', 'л': 'l', 'м': 'm',
        'н': 'n', 'о': 'o', 'п': 'p', 'р': 'r', 'с': 's', 'т': 't', 'у': 'u',
        'ф': 'f', 'х': 'kh', 'ц': 'ts', 'ч': 'ch', 'ш': 'sh', 'щ': 'sch',
        'ъ': '', 'ы': 'y', 'ь': '', 'э': 'e', 'ю': 'yu', 'я': 'ya',
        'А': 'a', 'Б': 'b', 'В': 'v', 'Г': 'g', 'Д': 'd', 'Е': 'e', 'Ё': 'e',
        'Ж': 'zh', 'З': 'z', 'И': 'i', 'Й': 'y', 'К': 'k', 'Л': 'l', 'М': 'm',
        'Н': 'n', 'О': 'o', 'П': 'p', 'Р': 'r', 'С': 's', 'Т': 't', 'У': 'u',
        'Ф': 'f', 'Х': 'kh', 'Ц': 'ts', 'Ч': 'ch', 'Ш': 'sh', 'Щ': 'sch',
        'Ъ': '', 'Ы': 'y', 'Ь': '', 'Э': 'e', 'Ю': 'yu', 'Я': 'ya',
        ' ': '_', '-': '_'
    }

    # Транслитерация
    result = ''
    for char in name:
        result += translit_dict.get(char, char)

    # Удаление всех символов, кроме a-z, A-Z, 0-9 и _
    result = re.sub(r'[^a-zA-Z0-9_]', '', result)

    # Приведение к нижнему регистру
    result = result.lower()

    # Если результат пустой, возвращаем случайный код
    if not result:
        return f"code_{uuid.uuid4().hex[:8]}"

    # Добавляем 4 уникальных hex символа для обеспечения уникальности
    unique_suffix = uuid.uuid4().hex[:4]
    return f"{result}_{unique_suffix}"

def serialize_value(value):
    """
    Преобразует объекты в сериализуемый формат.
    :param value: объект для сериализации. Может быть типа datetime или другой тип.
    :return: cериализованный объект. datetime преобразуется в строку формата ISO,
    """
    if isinstance(value, datetime):
        return value.isoformat()  # Преобразуем datetime в строку
    return value
