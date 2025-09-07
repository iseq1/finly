"""
Схемы для курса валют
"""
import re
from marshmallow import Schema, fields, validates, ValidationError, validates_schema, post_load
from app.schemas.base import BaseSchema, HistorySchema, PaginationSchema
from app.models.currency_rate import CurrencyRateHourly, CurrencyRateDaily


class CurrencyRateHourlySchema(BaseSchema):
    """
    Схема курса валют в течение дня (с периодичностью в один час)
    """

    class Meta:
        model = CurrencyRateHourly
        load_instance = True

    base_currency = fields.String(required=True)  # ISO-код исходной валюты (USD)
    target_currency = fields.String(required=True)  # ISO-код таргетной валюты
    type = fields.String(required=True) # Тип валюты - фиат или крипто
    rate = fields.Decimal(required=True, as_string=True, places=6) # Сам курс (например, 90.123456)
    timestamp = fields.DateTime(required=True) # Время, когда курс был актуален
    source = fields.String(required=True) # Наименование источника информации о курсе

    @validates("base_currency")
    def validate_base_currency(self, value):
        """Проверка корректности исходной валюты"""
        if len(value) == 0 or len(value) > 5:
            raise ValidationError("Некорректное наименование исходной валюты")
        if not bool(re.match(r'^[A-Za-z\s]+$', value)):
            raise ValidationError("Использование недопустимых символов в наименовании исходной валюты запрещено")

    @validates("target_currency")
    def validate_target_currency(self, value):
        """Проверка корректности таргетной валюты"""
        if len(value) == 0 or len(value) > 5:
            raise ValidationError("Некорректное наименование таргетной валюты")
        if not bool(re.match(r'^[A-Za-z\s]+$', value)):
            raise ValidationError("Использование недопустимых символов в наименовании таргетной валюты запрещено")

    @validates("source")
    def validate_source(self, value):
        """Проверка корректности наименование источника информации о курсе"""
        if len(value) == 0 or len(value) > 256:
            raise ValidationError("Некорректное наименование источника информации о курсе")

    @validates("type")
    def validate_type(self, value):
        """Проверка корректности наименование типа валюты"""
        if value not in ('fiat', 'crypto'):
            raise ValidationError("Некорректное наименование типа валюты")

    @validates_schema
    def validate_currency_pair(self, data, **kwargs):
        if data.get('base_currency') == data.get('target_currency'):
            raise ValidationError("Базовая и таргетная валюта не могут совпадать.")


class CurrencyRateDailySchema(BaseSchema):
    """
    Схема курса валют за день (avg значение за день)
    """

    class Meta:
        model = CurrencyRateDaily
        load_instance = True

    base_currency = fields.String(required=True)  # ISO-код исходной валюты (USD)
    target_currency = fields.String(required=True)  # ISO-код таргетной валюты
    avg_rate = fields.Decimal(required=True, as_string=True, places=6) # Сам курс (например, 90.123456)
    type = fields.String(required=True) # Тип валюты - фиат или крипто
    date = fields.Date(required=True) # Дата актуальности курса
    source = fields.String(required=True) # Наименование источника информации о курсе

    @validates("base_currency")
    def validate_base_currency(self, value):
        """Проверка корректности исходной валюты"""
        if len(value) == 0 or len(value) > 5:
            raise ValidationError("Некорректное наименование исходной валюты")
        if not bool(re.match(r'^[A-Za-z\s]+$', value)):
            raise ValidationError("Использование недопустимых символов в наименовании исходной валюты запрещено")

    @validates("target_currency")
    def validate_target_currency(self, value):
        """Проверка корректности таргетной валюты"""
        if len(value) == 0 or len(value) > 5:
            raise ValidationError("Некорректное наименование таргетной валюты")
        if not bool(re.match(r'^[A-Za-z\s]+$', value)):
            raise ValidationError("Использование недопустимых символов в наименовании таргетной валюты запрещено")

    @validates("source")
    def validate_source(self, value):
        """Проверка корректности наименование источника информации о курсе"""
        if len(value) == 0 or len(value) > 256:
            raise ValidationError("Некорректное наименование источника информации о курсе")

    @validates("type")
    def validate_type(self, value):
        """Проверка корректности наименование типа валюты"""
        if value not in ('fiat', 'crypto'):
            raise ValidationError("Некорректное наименование типа валюты")

    @validates_schema
    def validate_currency_pair(self, data, **kwargs):
        if data.get('base_currency') == data.get('target_currency'):
            raise ValidationError("Базовая и таргетная валюта не могут совпадать.")

class CurrencyRateFilterSchema(BaseSchema, PaginationSchema):
    """Схема для фильтрации инвесторов"""
    base = fields.String(required=False, description="Базовая валюта")
    target = fields.String(required=False, description="Таргетная валюта")
    type = fields.String(required=False, description="Тип валюты: fiat/crypto")
    timestamp = fields.String(required=False, description="Дата и время актуального курса")
    date = fields.Date(required=False, description="Дата актуального курса")
    latest = fields.Bool(required=False, missing=False)

