"""
Конфигурационный файл приложения.
Содержит различные настройки для разных окружений (development, testing, production).
"""
import os
from datetime import timedelta
from dotenv import load_dotenv
load_dotenv()

class Config:
    """Базовый класс конфигурации"""
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'hard-to-guess-string'
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY') or 'jwt-secret-string'
    JWT_TOKEN_LOCATION = ['headers', 'cookies']
    JWT_COOKIE_CSRF_PROTECT = False
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=1)
    JWT_REFRESH_TOKEN_EXPIRES = timedelta(days=30)
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'uploads')
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB макс размер файла
    ALLOWED_EXTENSIONS = {'pdf', 'doc', 'docx', 'png', 'jpg', 'jpeg', 'txt', 'xls', 'xlsx'}

class DevelopmentConfig(Config):
    """Конфигурация для разработки"""
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = os.environ.get('DEV_DATABASE_URL') or \
        'sqlite:///' + os.path.join(os.path.dirname(os.path.abspath(__file__)), 'dev.db')

class TestingConfig(Config):
    """Конфигурация для тестирования"""
    TESTING = True
    SQLALCHEMY_DATABASE_URI = os.environ.get('TEST_DATABASE_URL') or \
        'sqlite:///' + os.path.join(os.path.dirname(os.path.abspath(__file__)), 'test.db')

class ProductionConfig(Config):
    """Конфигурация для продакшена"""
    import urllib.parse

    password = "ycns_sDLjMe/2/QyAGcR2t]r>@wpauw]tPF5"
    encoded_password = urllib.parse.quote(password)
    print(encoded_password)

    SQLALCHEMY_DATABASE_URI = (
        f"postgresql+psycopg2://yegor:{encoded_password}@"
        "rc1a-bb556tungla99a1m.mdb.yandexcloud.net,rc1d-q003ru2blltomcc3.mdb.yandexcloud.net:6432/prod_db"
        "?sslmode=verify-full&sslrootcert=C:/Users/GAMER/.postgresql/root.crt"
    )


config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}
