"""
Утилиты для аутентификации и авторизации
"""
import os
from functools import wraps
from datetime import datetime, timezone
from flask import request, current_app, jsonify
from flask_jwt_extended import (
    verify_jwt_in_request, get_jwt_identity,
    create_access_token, create_refresh_token,
    set_access_cookies, set_refresh_cookies,
    unset_jwt_cookies
)
from app.models.auth import User, UserSession
from app.extensions import db

def get_user_by_identity(identity):
    """
    Получение пользователя по идентификатору из JWT
    :param identity: идентификатор пользователя
    :return: объект пользователя или None
    """
    return User.query.get(identity)

def create_tokens(user_id, remember_me=False):
    """
    Создание пары токенов (access + refresh)
    :param user_id: ID пользователя
    :param remember_me: флаг "запомнить меня"
    :return: tuple(access_token, refresh_token)
    """
    access_token = create_access_token(identity=str(user_id))
    refresh_token = create_refresh_token(identity=str(user_id))
    
    # Создание записи о сессии
    session = UserSession(
        user_id=user_id,
        refresh_token=refresh_token,
        user_agent=request.user_agent.string,
        ip_address=request.remote_addr,
        expires_at=datetime.now(timezone.utc) + current_app.config['JWT_REFRESH_TOKEN_EXPIRES'],
        is_active=True
    )
    db.session.add(session)
    db.session.commit()
    
    return access_token, refresh_token

def set_auth_cookies(response, access_token, refresh_token):
    """
    Установка JWT токенов в куки
    :param response: объект ответа Flask
    :param access_token: access token
    :param refresh_token: refresh token
    :return: модифицированный ответ
    """
    set_access_cookies(response, access_token)
    set_refresh_cookies(response, refresh_token)
    return response

def clear_auth_cookies(response):
    """
    Очистка JWT токенов из кук
    :param response: объект ответа Flask
    :return: модифицированный ответ
    """
    unset_jwt_cookies(response)
    return response

def permission_required(permission):
    """
    Декоратор для проверки наличия разрешения у пользователя
    :param permission: строка разрешения
    """
    # Регистрируем разрешение в глобальном реестре
    from app.models.auth import register_permission
    register_permission(permission)
    
    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            verify_jwt_in_request()
            user = get_user_by_identity(get_jwt_identity())
            
            if not user:
                return {
                    'message': 'Пользователь не найден',
                    'status_code': 401
                }, 401
            
            if not user.is_active:
                return {
                    'message': 'Пользователь деактивирован',
                    'status_code': 403
                }, 403
            
            if not user.has_permission(permission):
                return {
                    'message': 'Недостаточно прав для выполнения операции',
                    'status_code': 403
                }, 403
            
            return fn(*args, **kwargs)
        return wrapper
    return decorator

def role_required(role_name):
    """
    Декоратор для проверки наличия роли у пользователя
    :param role_name: название роли
    """
    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            verify_jwt_in_request()
            user = get_user_by_identity(get_jwt_identity())
            
            if not user:
                return {
                    'message': 'Пользователь не найден',
                    'status_code': 401
                }, 401
            
            if not user.is_active:
                return {
                    'message': 'Пользователь деактивирован',
                    'status_code': 403
                }, 403
            
            if not any(role.name == role_name for role in user.roles):
                return {
                    'message': 'Недостаточно прав для выполнения операции',
                    'status_code': 403
                }, 403
            
            return fn(*args, **kwargs)
        return wrapper
    return decorator

def log_action(action_type):
    """
    Декоратор для логирования действий пользователя
    :param action_type: тип действия (create/update/delete)
    """
    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            verify_jwt_in_request()
            user_id = get_jwt_identity()
            
            # Выполнение оригинальной функции
            result = fn(*args, **kwargs)
            
            # Если функция вернула кортеж (response, status_code)
            if isinstance(result, tuple):
                response, status_code = result
            else:
                response, status_code = result, 200
            
            # Логирование только успешных операций
            if 200 <= status_code < 300:
                # Здесь можно добавить логику логирования
                pass
            
            return result
        return wrapper
    return decorator

def make_default_user(id):
    """

    """
    DEFAULT_TG_USER = {
        'username': os.getenv('DEFAULT_TG_USERNAME', 'tguser')+f'{id}',
        'email': f'{id}' + os.getenv('DEFAULT_TG_EMAIL', 'tguser@example.com'),
        'first_name': 'Telegram',
        'last_name': 'User',
        'patronymic': '',
        'phone_number': '00000000000',
        'birthday': '2000-01-01 00:00:00.000001',
        'password': os.getenv('DEFAULT_TG_PASSWORD', 'Telegram1!'),
        'confirm_password': os.getenv('DEFAULT_TG_PASSWORD', 'Telegram1!')
    }
    return DEFAULT_TG_USER