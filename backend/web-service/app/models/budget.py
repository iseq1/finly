"""
Модели для бюджета
"""
from sqlalchemy import Column, Integer, String, ForeignKey, Boolean, Float, DateTime, JSON
from sqlalchemy.orm import relationship
from app.models.base import BaseModel, HistoryModel
from datetime import datetime


class BalanceSnapshot(BaseModel):
    """
    Модель снимка баланса
    """
    __tablename__ = 'balance_snapshot'

    user_id = Column(Integer, ForeignKey('user.id'), nullable=False)  # ID пользователя
    month = Column(Integer)  # Месяц снимка
    year = Column(Integer)  # Год снимка
    snapshot = Column(JSON)  # Снимок баланса в формате {user_cashbox: {balance: x, currency: y}}
    base_currency = Column(String(5), default='RUB')  # Базовая валюта
    is_static = Column(Boolean, default=False)  # Статичная ли запись

    def __repr__(self):
        return f"<BalanceSnapshot {self.month}/{self.year}, {self.is_static}>"

    @staticmethod
    def make_balance_snapshot(user_id, month, year, snapshot, is_static):
        new_bs = {
            'user_id': user_id,
            'month': month,
            'year': year,
            'snapshot': snapshot,
            'base_currency': 'RUB',
            'is_static': is_static,
        }
        return new_bs

class BalanceSnapshotHistory(HistoryModel):
    """
    Модель для изменения снимка баланса
    """
    __tablename__ = 'balance_snapshot_history'

    balance_snapshot_id = Column(Integer, ForeignKey('balance_snapshot.id'), nullable=False)
    balance_snapshot = relationship('BalanceSnapshot')