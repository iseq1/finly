"""
Скрипт для инициализации базы данных
"""
from app import create_app
from app.extensions import db

def init_db():
    """Инициализация базы данных"""
    app = create_app('development')
    with app.app_context():
        # Создание всех таблиц
        db.create_all()
        print("База данных успешно инициализирована")


if __name__ == '__main__':
    init_db()
