"""
Расширения Flask приложения
"""
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
from flask_jwt_extended import JWTManager
from flask_restx import Api
from flask_cors import CORS

# Инициализация расширений
db = SQLAlchemy()
ma = Marshmallow()
jwt = JWTManager()

# API будет инициализирован позже
api = None

def init_extensions(app):
    """
    Инициализация всех расширений Flask
    :param app: экземпляр Flask приложения
    """
    global api

    # Инициализация CORS с поддержкой localhost:7018
    CORS(app, resources={r"/*": {"origins": "*"}})

    db.init_app(app)
    ma.init_app(app)
    jwt.init_app(app)

    @jwt.unauthorized_loader
    def missing_token_callback(error):
        return {'message': 'Не авторизован', 'error': 'authorization_required'}, 401

    # Создание всех таблиц при запуске
    with app.app_context():
        db.create_all()

    # Инициализация API
    api = Api(
        app,
        title='DataLens API',
        version='1.0',
        description='API для визуализации и анализа данных',
        prefix='/analyze',
        doc='/analyze/docs',
        authorizations={
            'jwt': {
                'type': 'apiKey',
                'in': 'header',
                'name': 'Authorization',
                'description': 'Добавьте JWT токен в формате: Bearer JWT'
            }
        }
    )
