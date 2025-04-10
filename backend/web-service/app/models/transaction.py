"""
Модели для транзакций
"""
from sqlalchemy import Column, Integer, String, ForeignKey, Boolean, Float, DateTime
from sqlalchemy.orm import relationship
from app.models.base import BaseModel, HistoryModel
from datetime import datetime


class TransactionBase(BaseModel):
    """
    Абстрактная базовая модель транзакции
    """
    __abstract__ = True

    user_cashbox_id = Column(Integer, ForeignKey('user_cashbox.id'), nullable=False)  # ID-пользовательского кэш-бокса
    category_id = Column(Integer, ForeignKey('category.id'), nullable=False)  # ID-категории
    subcategory_id = Column(Integer, ForeignKey('subcategory.id'), nullable=False)  # ID-подкатегории

    amount = Column(Float, default=0.0)  # Сумма транзакции
    comment = Column(String(256))  # Комментарий к транзакции
    transacted_at = Column(DateTime, default=datetime.utcnow)  # Дата и время совершения транзакции

    def __repr__(self):
        return f"<Transaction {self.id}, {self.amount}, {self.transacted_at.date()}, {self.comment}>"


class Income(TransactionBase):
    """
    Модель дохода
    """
    __tablename__ = 'income'

    source = Column(String(256), nullable=True)  # Источник дохода

    # Связи
    user_cashbox = relationship('UserCashbox', back_populates='incomes')
    category = relationship('Category')
    subcategory = relationship('Subcategory')

    def __repr__(self):
        return f"<Income {self.id}, {self.amount}, '{self.source}', {self.transacted_at.date()}>"


class IncomeHistory(HistoryModel):
    """
    Модель для изменения дохода
    """
    __tablename__ = "income_history"

    income_id = Column(Integer, ForeignKey('income.id'), nullable=False)
    income = relationship('Income')


class Expense(TransactionBase):
    """
    Модель расхода
    """
    __tablename__ = "expense"

    vendor = Column(String(256), nullable=True)  # Кому уходит трата
    location = Column(String(256), nullable=True)  # Локация траты

    # Связи
    user_cashbox = relationship('UserCashbox', back_populates='expenses')
    category = relationship('Category')
    subcategory = relationship('Subcategory')

    def __repr__(self):
        return f"<Expense {self.id}, {self.amount}, {self.vendor}, {self.transacted_at.date()}>"


class ExpenseHistory(HistoryModel):
    """
    Модель для изменения расхода
    """
    __tablename__ = "expense_history"

    expense_id = Column(Integer, ForeignKey('expense.id'), nullable=False)
    expense = relationship('Expense')