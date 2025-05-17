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
    CORS(app, resources={
        r"/*": {
            "origins": ["http://localhost:7018", "http://localhost:7020", "https://finly.ru"],
            "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
            "allow_headers": ["Content-Type", "Authorization"],
            "expose_headers": ["Content-Type", "Authorization"],
            "supports_credentials": True,
            "send_wildcard": False
        }
    })
    
    db.init_app(app)
    ma.init_app(app)
    jwt.init_app(app)
    
    # Регистрация обработчиков ошибок JWT
    @jwt.expired_token_loader
    def expired_token_callback(jwt_header, jwt_payload):
        """Обработчик для истекших JWT токенов"""
        return {
            'message': 'Срок действия токена истек',
            'error': 'token_expired',
            'status_code': 401
        }, 401
    
    @jwt.invalid_token_loader
    def invalid_token_callback(error):
        """Обработчик для невалидных JWT токенов"""
        return {
            'message': 'Недействительный токен',
            'error': 'invalid_token',
            'status_code': 401
        }, 401
    
    @jwt.unauthorized_loader
    def missing_token_callback(error):
        """Обработчик для отсутствующих JWT токенов"""
        return {
            'message': 'Отсутствует токен авторизации',
            'error': 'authorization_required',
            'status_code': 401
        }, 401
    
    @jwt.needs_fresh_token_loader
    def token_not_fresh_callback(jwt_header, jwt_payload):
        """Обработчик для случаев, когда требуется свежий токен"""
        return {
            'message': 'Требуется свежий токен авторизации',
            'error': 'fresh_token_required',
            'status_code': 401
        }, 401
    
    @jwt.revoked_token_loader
    def revoked_token_callback(jwt_header, jwt_payload):
        """Обработчик для отозванных токенов"""
        return {
            'message': 'Токен был отозван',
            'error': 'token_revoked',
            'status_code': 401
        }, 401
    
    # Создание всех таблиц при запуске
    with app.app_context():
        db.create_all()
    
    # Инициализация API
    api = Api(
        app,
        title='Web-service API',
        version='1.0',
        description='API для web-service системы \n\n\n **Все модели основаны на BaseModel, с.м раздел Models** \n\n Любые данные о формате времени, структуре ошибок, ответов, пагинации, поиске и прочем представлены в `/base`',
        prefix='/api',
        doc='/api/docs',
        authorizations={
            'jwt': {
                'type': 'apiKey',
                'in': 'header',
                'name': 'Authorization',
                'description': 'Добавьте JWT токен в формате: Bearer JWT'
            }
        }
    )
