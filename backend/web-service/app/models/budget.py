"""
Модели для бюджета
"""
from sqlalchemy import Column, Integer, String, ForeignKey, Boolean, Float, DateTime, JSON
from sqlalchemy.orm import relationship
from app.models.base import BaseModel, HistoryModel
from app.utils.currency_rate_service import ExternalCurrencyRateProvider
from datetime import datetime


class BalanceSnapshot(BaseModel):
    """
    Модель снимка баланса
    """
    __tablename__ = 'balance_snapshot'

    user_id = Column(Integer, ForeignKey('user.id'), nullable=False)  # ID-пользователя
    month = Column(Integer, nullable=False)  # Месяц снимка
    year = Column(Integer, nullable=False)  # Год снимка
    snapshot = Column(JSON)  # Снимок баланса в формате {user_cashbox: {balance: x, currency: y}}
    base_currency = Column(String(5), default='RUB')  # Базовая валюта
    is_static = Column(Boolean, default=False)  # Статичная ли запись

    def __repr__(self):
        return f"<BalanceSnapshot {self.month}/{self.year}, {self.is_static}>"

    @staticmethod
    def make_balance_snapshot(user_id, month, year, snapshot, is_static, base_currency='RUB'):
        """
        Создает снимок баланса для указанного пользователя.
        :param user_id: идентификатор пользователя
        :param month: месяц снимка (1-12)
        :param year: год для снимка (2025)
        :param snapshot: словарь со значением баланса
        :param is_static: если True, снимок считается статичным; если False, динамическим
        :param base_currency: базовая валюта баланса, RUB по-умолчанию
        :return: cловарь с данными о снимке баланса
        """
        new_bs = {
            'user_id': user_id,
            'month': month,
            'year': year,
            'snapshot': snapshot,
            'base_currency': base_currency,
            'is_static': is_static,
        }
        return new_bs

    def get_total_balance(self, to_currency='RUB', rate_provider=None) -> float:
        if rate_provider is None:
            rate_provider = ExternalCurrencyRateProvider()

        snapshot = self.snapshot or {}
        total_in_usd = 0.0
        total_in_usdt = 0.0

        for acc in snapshot.values():
            balance = acc.get('balance', 0.0)
            currency = acc.get('currency', 'RUB')
            currency_type = acc.get('type', 'fiat')

            if currency == 'USD' and currency_type != 'crypto':
                total_in_usd += balance
            elif currency == 'USDT' and currency_type == 'crypto':
                total_in_usdt += balance
            else:
                try:
                    if currency_type != 'crypto':
                        rate = rate_provider.get_rate(base=currency, target='USD', type_='fiat', latest=True)
                        total_in_usd += balance * rate
                    elif currency_type == 'crypto':
                        rate = rate_provider.get_rate(base=currency, target='USDT', type_='crypto', latest=True)
                        total_in_usdt += balance * rate
                except Exception as e:
                    print(f"[WARN] Не удалось получить курс {currency} → USD/USDT: {e}")
                    continue

        # Приводим всё к общей целевой валюте
        result = 0.0

        try:
            if total_in_usd:
                usd_to_target = 1.0 if to_currency == 'USD' else rate_provider.get_rate(base='USD', target=to_currency,
                                                                                        type_='fiat', latest=True)
                result += total_in_usd * usd_to_target

            if total_in_usdt:
                usdt_to_target = 1.0 if to_currency == 'USDT' else rate_provider.get_rate(base='USDT',
                                                                                          target=to_currency,
                                                                                          type_='crypto', latest=True)
                result += total_in_usdt * usdt_to_target

        except Exception as e:
            print(f"[ERROR] Не удалось сконвертировать в {to_currency}: {e}")
            return 0.0

        return round(result, 2)


class BalanceSnapshotHistory(HistoryModel):
    """
    Модель для изменения снимка баланса
    """
    __tablename__ = 'balance_snapshot_history'

    balance_snapshot_id = Column(Integer, ForeignKey('balance_snapshot.id'), nullable=False)
    balance_snapshot = relationship('BalanceSnapshot')


class Budget(BaseModel):
    """
    Модель бюджета
    """
    __tablename__ = 'budget'
    # TODO delete user_id
    user_id = Column(Integer, ForeignKey('user.id'), nullable=False)  # ID-пользователя
    category_id = Column(Integer, ForeignKey('category.id'), nullable=True)  # ID-категории
    subcategory_id = Column(Integer, ForeignKey('subcategory.id'), nullable=True)  # ID-подкатегории
    user_cashbox_id = Column(Integer, ForeignKey('user_cashbox.id'), nullable=True)  # ID-пользовательского кэш-бокса
    month = Column(Integer, nullable=False)  # Месяц
    year = Column(Integer, nullable=False)  # Год
    amount = Column(Float)  # Планируемая сумма
    currency = Column(String(5), default='RUB')  # Валюта
    comment = Column(String(256), nullable=True)  # Комментарий пользователя
    is_recurring = Column(Boolean, default=False)  # Повторяется ли каждый месяц
    is_locked = Column(Boolean, default=False)  # Зафиксирован ли бюджет (нельзя редактировать после начала месяца)

    # Связи
    user = relationship("User", back_populates="user_budgets")

    def __repr__(self):
        return f"<Budget {self.month}/{self.year}, {self.user.username}>"

class BudgetHistory(HistoryModel):
    """История изменения бюджета"""
    budget_id = Column(Integer, ForeignKey('budget.id'), nullable=False)
    budget = relationship('Budget')
