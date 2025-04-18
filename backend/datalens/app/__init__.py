# datalens/app/__init__.py

import os
from flask import Flask, jsonify
from marshmallow import ValidationError
from config import config
from app.extensions import init_extensions
from app.schemas.base import ErrorSchema

def create_app(config_name=None):
    if not config_name:
        config_name = os.environ.get('FLASK_ENV', 'development')

    app = Flask(__name__)
    app.config.from_object(config[config_name])

    # Инициализация расширений
    init_extensions(app)

    # Регистрация ошибок
    register_error_handlers(app)

    # Регистрация API роутов
    register_api_routes(app)

    return app

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
    from app.extensions import api

    # Импорт API namespaces после инициализации api
    from app.api.base import api as base_api
    from app.api.auth import api as auth_api
    from app.api.settings import api as settings_api
    from app.api.transaction import api as transactions_api
    from app.api.budget import api as budget_api

    # Регистрация namespaces без префикса /api, так как он уже добавлен в Api
    api.add_namespace(auth_api, path='/auth')
    api.add_namespace(transactions_api, path='/transactions')
    api.add_namespace(budget_api, path='/budget')
