"""
Инициализация Flask приложения
"""
import os
from flask import Flask, jsonify
from marshmallow import ValidationError
from app.extensions import init_extensions
from app.schemas.base import ErrorSchema
from config import config


def create_app(config_name=None):
    """
    Фабрика создания Flask приложения
    :param config_name: имя конфигурации (development/testing/production)
    :return: экземпляр Flask приложения
    """
    if not config_name:
        config_name = os.environ.get('FLASK_ENV', 'development')

    app = Flask(__name__)
    app.config.from_object(config[config_name])

    # Инициализация расширений
    init_extensions(app)

    # Настройка JWT
    app.config['JWT_TOKEN_LOCATION'] = ['headers', 'cookies']
    app.config['JWT_ACCESS_TOKEN_EXPIRES'] = 3600  # 1 hour
    app.config['JWT_REFRESH_TOKEN_EXPIRES'] = 2592000  # 30 days
    app.config['JWT_COOKIE_CSRF_PROTECT'] = False  # Отключаем CSRF защиту для куки

    # Регистрация базовых разрешений
    register_base_permissions()

    # Регистрация обработчиков ошибок
    register_error_handlers(app)

    # Регистрация маршрутов API
    register_api_routes(app)

    return app


def register_base_permissions():
    """
    Регистрация базовых разрешений при запуске приложения
    """
    from app.models.auth import register_permission

    # Разрешения для просмотра
    register_permission('permission.view')
    register_permission('role.view')
    register_permission('user.view')
    register_permission('settings.view')
    register_permission('transaction.view')

    # Разрешения для создания
    register_permission('role.create')
    register_permission('user.create')
    register_permission('settings.create')
    register_permission('transaction.create')

    # Разрешения для обновления
    register_permission('role.update')
    register_permission('user.update')
    register_permission('settings.update')
    register_permission('transaction.update')

    # Разрешения для удаления
    register_permission('role.delete')
    register_permission('user.delete')
    register_permission('settings.delete')
    register_permission('transaction.delete')


def register_error_handlers(app):
    """
    Регистрация обработчиков ошибок
    :param app: экземпляр Flask приложения
    """

    @app.errorhandler(ValidationError)
    def handle_validation_error(error):
        """Обработка ошибок валидации схем"""
        response = ErrorSchema().dump({
            'message': 'Ошибка валидации данных',
            'errors': error.messages,
            'status_code': 400
        })
        return jsonify(response), 400

    @app.errorhandler(401)
    def handle_unauthorized_error(error):
        """Обработка ошибок авторизации"""
        response = ErrorSchema().dump({
            'message': 'Необходима авторизация',
            'status_code': 401
        })
        return jsonify(response), 401

    @app.errorhandler(403)
    def handle_forbidden_error(error):
        """Обработка ошибок доступа"""
        response = ErrorSchema().dump({
            'message': 'Недостаточно прав для выполнения операции',
            'status_code': 403
        })
        return jsonify(response), 403

    @app.errorhandler(404)
    def handle_not_found_error(error):
        """Обработка ошибок отсутствия ресурса"""
        response = ErrorSchema().dump({
            'message': 'Запрашиваемый ресурс не найден',
            'status_code': 404
        })
        return jsonify(response), 404

    @app.errorhandler(405)
    def handle_method_not_allowed_error(error):
        """Обработка ошибок недоступности метода"""
        response = ErrorSchema().dump({
            'message': 'Метод не поддерживается для данного ресурса',
            'status_code': 405
        })
        return jsonify(response), 405

    @app.errorhandler(500)
    def handle_internal_server_error(error):
        """Обработка внутренних ошибок сервера"""
        response = ErrorSchema().dump({
            'message': 'Внутренняя ошибка сервера',
            'status_code': 500
        })
        return jsonify(response), 500


def register_api_routes(app):
    """
    Регистрация маршрутов API
    :param app: экземпляр Flask приложения
    """
    from app.extensions import api

    # Импорт API namespaces после инициализации api
    from app.api.base import api as base_api
    from app.api.auth import api as auth_api
    from app.api.settings import api as settings_api
    from app.api.transaction import api as transactions_api

    # Регистрация namespaces без префикса /api, так как он уже добавлен в Api
    api.add_namespace(base_api, path='/base')
    api.add_namespace(auth_api, path='/auth')
    api.add_namespace(settings_api, path='/settings')
    api.add_namespace(transactions_api, path='/transactions')

    # Создание папки для загрузки файлов
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
