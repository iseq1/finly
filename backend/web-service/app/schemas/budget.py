"""
Схемы для бюджета
"""
import re
from marshmallow import Schema, fields, validates, ValidationError, validates_schema, post_load
from app.schemas.base import BaseSchema, HistorySchema
from app.models.budget import BalanceSnapshot, BalanceSnapshotHistory


class SnapshotSchema(Schema):
    name = fields.String(required=True)
    currency = fields.String(required=True)
    balance = fields.Float(required=True)

    @validates("currency")
    def validate_currency(self, value):
        """Проверка корректности валюты"""
        if len(value) == 0 or len(value) > 5:
            raise ValidationError("Некорректное наименование валюты")
        if not bool(re.match(r'^[A-Za-z\s]+$', value)):
            raise ValidationError("Использование недопустимых символов запрещено")


class BalanceSnapshotSchema(BaseSchema):
    """Схема для снимка баланса"""

    class Meta:
        model = BalanceSnapshot
        load_instance = True

    user_id = fields.Integer(required=True)
    month = fields.Integer(required=True)
    year = fields.Integer(required=True)
    snapshot = fields.Dict(keys=fields.Integer, values=fields.Nested(SnapshotSchema), required=True)
    base_currency = fields.String(required=True)
    is_static = fields.Boolean(required=True)

    @validates("month")
    def validate_month(self, value):
        """Проверка корректности месяца"""
        if not (1 <= value <= 12):
            raise ValidationError('Некорректное значение месяца')

    @validates("year")
    def validate_year(self, value):
        """Проверка корректности года"""
        if not (1900 <= value <= 2100):
            raise ValidationError('Некорректное значение года')

    @validates("base_currency")
    def validate_base_currency(self, value):
        """Проверка корректности базовой валюты"""
        if len(value) == 0 or len(value) > 5:
            raise ValidationError("Некорректное наименование валюты")
        if not bool(re.match(r'^[A-Za-z\s]+$', value)):
            raise ValidationError("Использование недопустимых символов запрещено")


class BalanceSnapshotHistorySchema(HistorySchema):
    """Схема изменений снимка баланса"""
    balance_snapshot_id = fields.Integer(required=True)