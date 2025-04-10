"""
Модели для системы авторизации и управления пользователями
"""
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Table, JSON, Float
from sqlalchemy.orm import relationship
from app.extensions import db
from app.models.base import BaseModel, HistoryModel

# Глобальный реестр всех разрешений в системе
PERMISSIONS = set()

def register_permission(permission):
    """
    Регистрация разрешения в глобальном реестре
    :param permission: строка разрешения
    """
    PERMISSIONS.add(permission)


def get_all_permissions():
    """Получение всех зарегистрированных разрешений"""
    # Убедимся, что возвращаем список строк, а не какие-либо объекты
    return sorted([str(p) for p in PERMISSIONS])


class Role(BaseModel):
    """Модель ролей"""
    __tablename__ = 'role'

    name = Column(String(100), unique=True, nullable=False)
    description = Column(String(255))
    level = Column(Integer, default=0)  # Уровень роли для иерархии
    permissions = Column(JSON, default=list)  # Массив строк разрешений
    
    def add_permission(self, permission):
        """Добавление разрешения к роли"""
        if permission not in self.permissions:
            self.permissions.append(permission)
    
    def remove_permission(self, permission):
        """Удаление разрешения из роли"""
        if permission in self.permissions:
            self.permissions.remove(permission)
    
    def has_permission(self, permission):
        """Проверка наличия разрешения у роли"""
        return permission in self.permissions


class RoleHistory(HistoryModel):
    """История изменений ролей"""
    __tablename__ = 'role_history'
    
    role_id = Column(Integer, ForeignKey('role.id'), nullable=False)
    role = relationship('Role')


class User(BaseModel):
    """Модель пользователя"""
    __tablename__ = 'user'

    username = Column(String(64), unique=True, nullable=True)
    email = Column(String(120), unique=True, nullable=False)
    password_hash = Column(String(128))
    first_name = Column(String(64))
    last_name = Column(String(64))
    patronymic = Column(String(64))
    phone_number = Column(String(20))
    birthday = Column(DateTime, nullable=True)
    is_active = Column(Boolean, default=True)
    last_login = Column(DateTime)

    roles = relationship('Role', secondary='user_role', backref='users')
    user_cashboxes = relationship("UserCashbox", back_populates="user")

    def set_password(self, password):
        """Установка хэша пароля"""
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        """Проверка пароля"""
        return check_password_hash(self.password_hash, password)

    def has_permission(self, permission):
        """
        Проверка наличия разрешения у пользователя
        :param permission: строка разрешения
        :return: bool
        """
        return any(role.has_permission(permission) for role in self.roles)


class UserHistory(HistoryModel):
    """История изменений пользователя"""
    __tablename__ = 'user_history'
    
    user_id = Column(Integer, ForeignKey('user.id'), nullable=False)
    user = relationship('User', foreign_keys=[user_id])


class UserRole(BaseModel):
    """Модель связи пользователя и роли"""
    __tablename__ = 'user_role'
    
    user_id = Column(Integer, ForeignKey('user.id'), nullable=False)
    role_id = Column(Integer, ForeignKey('role.id'), nullable=False)
    
    user = relationship('User', viewonly=True, overlaps="roles,users")
    role = relationship('Role', viewonly=True, overlaps="roles,users")
    
    __table_args__ = (
        db.UniqueConstraint('user_id', 'role_id', name='uq_user_role'),
    )


class UserAvatar(BaseModel):
    """Модель аватара пользователя"""
    __tablename__ = 'user_avatar'
    
    user_id = Column(Integer, ForeignKey('user.id'), nullable=False, unique=True)
    file_path = Column(String(255), nullable=False)
    
    user = relationship('User', backref=db.backref('avatar', uselist=False))
    
    @property
    def url(self):
        """Получение URL аватара"""
        from flask import url_for
        return url_for('static', filename=f'uploads/{self.file_path}', _external=True)


class UserSession(BaseModel):
    """Модель сессии пользователя"""
    __tablename__ = 'user_session'

    user_id = Column(Integer, ForeignKey('user.id'), nullable=False)
    refresh_token = Column(String(255), unique=True)
    user_agent = Column(String(255))  # Информация о браузере/устройстве
    ip_address = Column(String(45))
    expires_at = Column(DateTime, nullable=False)
    is_active = Column(Boolean, default=True)
    
    user = relationship('User', backref='sessions')


class UserCashbox(BaseModel):
    """
    Модель кэш-бокса пользователя
    """
    __tablename__ = "user_cashbox"

    user_id = Column(Integer, ForeignKey('user.id'), nullable=False)  # ID пользователя
    cashbox_id = Column(Integer, ForeignKey('cashbox.id'), nullable=False)  # ID кэш-бокса

    balance = Column(Float, default=0.0)  # Текущий баланс
    is_auto_update = Column(Boolean, default=False)  # Включена ли автосинхронизация
    last_synced_at = Column(DateTime, default=datetime.utcnow)  # Дата последнего автоматического обновления

    # Доп. поля:
    custom_name = Column(String(99), nullable=True)  # Кастомное имя кэш-бокса
    note = Column(String(99), nullable=True)  # Заметка от пользователя

    # Связи
    user = relationship("User", back_populates="user_cashboxes")
    cashbox = relationship("Cashbox", back_populates="user_cashboxes")
    incomes = relationship('Income', back_populates='user_cashbox')
    expenses = relationship('Expense', back_populates='user_cashbox')

    def __repr__(self):
        return f"UserCashbox: {self.user.__repr__()}, {self.cashbox.__repr__()}"


class UserCashboxHistory(HistoryModel):
    """Модель изменений кэш-боксов пользователя"""
    __tablename__ = 'user_cashbox_history'

    user_cashbox_id = Column(Integer, ForeignKey('user_cashbox.id'), nullable=False)
    user_cashbox = relationship('UserCashbox')