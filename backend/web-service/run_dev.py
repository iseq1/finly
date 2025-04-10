"""
Скрипт запуска приложения в режиме разработки
"""
import os
from app import create_app

if __name__ == '__main__':
    # Установка переменных окружения для режима разработки
    os.environ['FLASK_ENV'] = 'development'
    os.environ['FLASK_DEBUG'] = '1'
    
    # Создание экземпляра приложения
    app = create_app('development')
    
    # Запуск сервера для разработки
    app.run(host='0.0.0.0', port=7020)
