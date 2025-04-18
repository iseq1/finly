"""
Схемы для транзакций
"""
import re
from marshmallow import Schema, fields, validates, ValidationError, validates_schema, post_load
from app.schemas.base import BaseSchema, HistorySchema
from app.models.transaction import TransactionBase, Income, IncomeHistory, Expense, ExpenseHistory


class TransactionBaseSchema(BaseSchema):
    """Абстрактная схема для транзакций"""

    class Meta:
        model = TransactionBase
        load_instance = True

    user_cashbox_id = fields.Integer(required=True)
    category_id = fields.Integer(required=True)
    subcategory_id = fields.Integer(required=True)

    amount = fields.Float(required=True)
    comment = fields.String(required=True)
    transacted_at = fields.DateTime(required=True)


class IncomeSchema(TransactionBaseSchema):
    """Схема дохода"""

    class Meta:
        model = Income
        load_instance = True

    source = fields.String()

    # Связи
    user_cashbox = fields.Nested('UserCashboxSchema', only=('id', 'user', 'cashbox'), dump_only=True)
    category = fields.Nested('CategorySchema', only=('name', 'code'), dump_only=True)
    subcategory = fields.Nested('SubcategorySchema', only=('name', 'code'), dump_only=True)


class IncomeHistorySchema(HistorySchema):
    """Схема изменения дохода"""
    income_id = fields.Integer(required=True)


class ExpenseSchema(TransactionBaseSchema):
    """Схема расхода"""

    class Meta:
        model = Expense
        load_instance = True

    vendor = fields.String()
    location = fields.String()

    # Связи
    user_cashbox = fields.Nested('UserCashboxSchema', only=('id', 'user', 'cashbox'), dump_only=True)
    category = fields.Nested('CategorySchema', only=('name', 'code'), dump_only=True)
    subcategory = fields.Nested('SubcategorySchema', only=('name', 'code'), dump_only=True)


class ExpenseHistorySchema(HistorySchema):
    """Схема истории расходов"""
    expense_id = fields.Integer(required=True)