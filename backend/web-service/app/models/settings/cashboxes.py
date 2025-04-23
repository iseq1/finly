"""
Модели для кэш-боксов
"""
from sqlalchemy import Column, Integer, String, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from app.models.base import BaseModel, HistoryModel


class Cashbox(BaseModel):
    """
    Модель кэш-бокса
    """
    __tablename__ = 'cashbox'

    name = Column(String(99), nullable=False)  # Наименование кэш-бокса
    type_id = Column(Integer, ForeignKey('cashbox_type.id'), nullable=False)  # ID-тип кэш-бокса
    provider_id = Column(Integer, ForeignKey('cashbox_provider.id'), nullable=False)  # ID-провайдера кэш-бокса (Банк/Биржа/Сервис)
    currency = Column(String(5), nullable=False)  # Валюта кэш-бокса
    description = Column(String(255))  # Описание кэш-бокса
    icon = Column(String(512), nullable=True)  # Иконка кэш-бокса
    is_active = Column(Boolean(), default=True)  # Активен ли кэш-бокс

    # Связи
    type = relationship('CashboxType', back_populates='cashboxes')
    provider = relationship('CashboxProvider', back_populates='cashboxes')
    user_cashboxes = relationship("UserCashbox", back_populates="cashbox")

    def __repr__(self):
        return f"Cashbox: {self.name}, {self.type.name}, {self.provider.name}"


class CashboxHistory(HistoryModel):
    """
    Модель для изменения кэш-бокса
    """
    __tablename__ = "cashbox_history"

    cashbox_id = Column(Integer, ForeignKey('cashbox.id'), nullable=False)
    cashbox = relationship('Cashbox')


class CashboxType(BaseModel):
    """
    Модель типа кэш-бокса
    """
    __tablename__ = "cashbox_type"

    name = Column(String(99), nullable=False)  # Наименование типа
    code = Column(String(50), unique=True, nullable=False)  # 'debit_card', 'crypto', ...

    # Связи
    cashboxes = relationship('Cashbox', back_populates='type')

    def __repr__(self):
        return f"CashboxType: {self.name}"


class CashboxTypeHistory(HistoryModel):
    """
    Модель изменения типа кэш-бокса
    """
    __tablename__ = "cashbox_type_history"

    cashbox_type_id = Column(Integer, ForeignKey('cashbox_type.id'), nullable=False)
    cashbox_type = relationship('CashboxType')


class CashboxProvider(BaseModel):
    """
    Модель провайдера кэш-бокса
    """
    __tablename__ = "cashbox_provider"

    name = Column(String(99), nullable=False)  # Наименование провайдера (Т-Банк)
    full_name = Column(String(256), nullable=False)  # Полное наименование провайдера
    logo_url = Column(String(512), nullable=False)  # Ссылка на логотип провайдера
    alt_logo_url = Column(String(512), nullable=True)  # Ссылка на альтернативный логотип провайдера
    color = Column(String(7), nullable=False)  # Основной цвет провайдера
    second_color = Column(String(7), nullable=True)  # Второй цвет провайдера
    alt_color = Column(String(7), nullable=False)  # Альтернативный цвет провайдера
    second_alt_color = Column(String(7), nullable=True)  # Второй альтернативный цвет провайдера

    # Связи
    cashboxes = relationship('Cashbox', back_populates='provider')

    def __repr__(self):
        return f"CashboxProvider: {self.name}"


class CashboxProviderHistory(HistoryModel):
    """
    Модель изменения провайдера кэш-бокса
    """
    __tablename__ = 'cashbox_provider_history'

    cashbox_provider_id = Column(Integer, ForeignKey('cashbox_provider.id'), nullable=False)
    cashbox_provider = relationship('CashboxProvider')