"""
Базовая модель с поддержкой истории изменений и soft delete
"""
from datetime import datetime
from sqlalchemy import JSON, Column, Integer, DateTime, Boolean, String
from sqlalchemy.ext.declarative import declared_attr
from app.extensions import db

class BaseModel(db.Model):
    """
    Базовый класс для всех моделей с поддержкой истории изменений
    """
    __abstract__ = True

    id = Column(Integer, primary_key=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    deleted = Column(Boolean, default=False, nullable=False)

    @declared_attr
    def __tablename__(cls):
        """Автоматически генерирует имя таблицы из имени класса"""
        return cls.__name__.lower()
    
    def hard_delete(self):
        """Жесткое удаление записи"""
        db.session.delete(self)
        db.session.commit()

    def soft_delete(self):
        """Мягкое удаление записи"""
        self.deleted = True
        db.session.commit()

    def to_dict(self):
        """Преобразование модели в словарь"""
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}

class HistoryModel(BaseModel):
    """
    Базовый класс для моделей истории изменений
    """
    __abstract__ = True

    action = Column(String(50), nullable=False)  # create, update, delete
    changed_by_id = Column(Integer, db.ForeignKey('user.id'), nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False)
    changes = Column(JSON)  # Хранит изменения в формате JSON

    @declared_attr
    def changed_by(cls):
        """Связь с пользователем, который внес изменения"""
        return db.relationship('User', foreign_keys=[cls.changed_by_id])

    @classmethod
    def log_change(cls, item, action, changed_by_id, changes=None):
        """
        Логирование изменений
        :param item: измененный объект
        :param action: тип действия (create/update/delete)
        :param changed_by_id: ID пользователя
        :param changes: словарь изменений
        """

        model_name = item.__class__.__name__
        field_name = MODEL_TO_HISTORY_FIELD.get(model_name)

        if not field_name:
            raise ValueError(f"Нет сопоставления полей истории для модели - {model_name}")

        history = cls(
            action=action,
            changed_by_id=changed_by_id,
            changes=changes,
            **{field_name: item.id}
        )
        db.session.add(history)
        db.session.commit()


MODEL_TO_HISTORY_FIELD = {
    "Role": 'role_id',
    "User": 'user_id',
    # "UserRole": 'user_role_id',
    # "UserAvatar": 'user_avatar_id',
    # "UserSession": 'user_session_id',
    "UserCashbox": 'user_cashbox_id',
    "Category": 'category_id',
    "Subcategory": 'subcategory_id',
    "Cashbox": 'cashbox_id',
    "CashboxType": 'cashbox_type_id',
    "CashboxProvider": 'cashbox_provider_id',
    "Income": 'income_id',
    "Expense": 'expense_id',
    "BalanceSnapshot": 'balance_snapshot_id',
}