"""
Схемы для кэш-боксов
"""
import re
from marshmallow import Schema, fields, validates, ValidationError, validates_schema, post_load
from app.schemas.base import BaseSchema, HistorySchema
from app.models.settings.cashboxes import Cashbox, CashboxType, CashboxProvider, CashboxHistory, CashboxTypeHistory, CashboxProviderHistory


class CashboxSchema(BaseSchema):
    """Схема для кэш-бокса"""

    class Meta:
        model = Cashbox
        load_instance = True

    name = fields.String(required=True)
    type_id = fields.Integer(required=True)
    provider_id = fields.Integer(required=True)
    currency = fields.String(required=True)
    description = fields.String(required=True)
    icon = fields.String(required=True)
    is_active = fields.Boolean(required=True)

    type = fields.Nested('CashboxTypeSchema', only=('name', 'code'), dump_only=True)
    provider = fields.Nested('CashboxProviderSchema', only=('name', 'logo_url', 'color'), dump_only=True)
    user_cashboxes = fields.List(fields.Nested('UserCashboxSchema'), only=('user_id', 'cashbox_id', 'balance'), dump_only=True)

    @validates("name")
    def validate_name(self, value):
        """Проверка корректности наименования кэш-бокса"""
        if len(value) >= 100 or len(value) == 0:
            raise ValidationError("Некорректное наименование кэш-бокса")
        if not bool(re.match(r'^[А-ЯЁа-яёA-Za-z\s]+$', value)):
            raise ValidationError("Использование недопустимых символов запрещено")

    @validates("currency")
    def validate_currency(self, value):
        """Проверка корректности валюты"""
        if len(value) == 0 or len(value) > 5:
            raise ValidationError("Некорректное наименование валюты")
        if not bool(re.match(r'^[A-Za-z\s]+$', value)):
            raise ValidationError("Использование недопустимых символов запрещено")


class CashboxHistorySchema(HistorySchema):
    """
    Схема изменений кэш-бокса
    """
    cashbox_id = fields.Integer(required=True)


class CashboxTypeSchema(BaseSchema):
    """
    Схема типа кэш-бокса
    """

    class Meta:
        model = CashboxType
        load_instance = True

    name = fields.String(required=True)
    code = fields.String(required=True)

    cashboxes = fields.List(fields.Nested('CashboxSchema'), only='name', dump_only=True)

    @validates("name")
    def validate_name(self, value):
        """Проверка корректности наименования кэш-бокса"""
        if len(value) >= 100 or len(value) == 0:
            raise ValidationError("Некорректное наименование типа кэш-бокса")
        if not bool(re.match(r'^[А-ЯЁа-яё\s]+$', value)):
            raise ValidationError("Использование недопустимых символов запрещено")

    @validates("code")
    def validate_name(self, value):
        """Проверка корректности кода кэш-бокса"""
        if len(value) > 50 or len(value) == 0:
            raise ValidationError("Некорректный код типа кэш-бокса")
        if not bool(re.match(r'^[A-Za-z\s]+$', value)):
            raise ValidationError("Использование недопустимых символов запрещено")


class CashboxTypeHistorySchema(HistorySchema):
    """
    Схема изменения типа кэш-бокса
    """
    cashbox_type_id = fields.Integer(required=True)


class CashboxProviderSchema(BaseSchema):
    """
    Схема провайдера кэш-бокса
    """

    class Meta:
        model = CashboxProvider
        load_instance = True

    name = fields.String(required=True)
    full_name = fields.String(required=True)
    logo_url = fields.String(required=True)
    alt_logo_url = fields.String(required=True)
    color = fields.String(required=True)
    second_color = fields.String(required=True)
    alt_color = fields.String(required=True)
    second_alt_color = fields.String(required=True)

    cashboxes = fields.List(fields.Nested('CashboxSchema'), only='name', dump_only=True)

    @validates("name")
    def validate_name(self, value):
        """Проверка корректности наименования провайдера кэш-бокса"""
        if len(value) >= 100 or len(value) == 0:
            raise ValidationError("Некорректное наименование провайдера кэш-бокса")
        if not bool(re.match(r'^[А-ЯЁа-яёA-Za-z\s]+$', value)):
            raise ValidationError("Использование недопустимых символов запрещено")

    @validates("full_name")
    def validate_name(self, value):
        """Проверка корректности полного наименования провайдера кэш-бокса"""
        if len(value) >= 100 or len(value) == 0:
            raise ValidationError("Некорректное полное наименование провайдера кэш-бокса")
        if not bool(re.match(r'^[А-ЯЁа-яёA-Za-z\s\-]+$', value)):
            raise ValidationError("Использование недопустимых символов запрещено")

    @validates("color")
    def validate_color(self, value):
        """Проверка корректности основного цвета провайдера"""
        if len(value) != 7:
            raise ValidationError("Цвет должен быть указан в формате hex #xxxxxx")
        if not bool(re.match(r'^[A-Z0-9#]+$', value)):
            raise ValidationError("Цвет категории указан неверно, используйте hex-формат записи")

    @validates("second_color")
    def validate_second_color(self, value):
        """Проверка корректности запасного цвета провайдера"""
        if len(value) != 7:
            raise ValidationError("Цвет должен быть указан в формате hex #xxxxxx")
        if not bool(re.match(r'^[A-Z0-9#]+$', value)):
            raise ValidationError("Цвет категории указан неверно, используйте hex-формат записи")

    @validates("alt_color")
    def validate_alt_color(self, value):
        """Проверка корректности альтернативного цвета провайдера"""
        if len(value) != 7:
            raise ValidationError("Цвет должен быть указан в формате hex #xxxxxx")
        if not bool(re.match(r'^[A-Z0-9#]+$', value)):
            raise ValidationError("Цвет категории указан неверно, используйте hex-формат записи")

    @validates("second_alt_color")
    def validate_second_alt_color(self, value):
        """Проверка корректности запасного альтернативного цвета провайдера"""
        if len(value) != 7:
            raise ValidationError("Цвет должен быть указан в формате hex #xxxxxx")
        if not bool(re.match(r'^[A-Z0-9#]+$', value)):
            raise ValidationError("Цвет категории указан неверно, используйте hex-формат записи")


class CashboxProviderHistorySchema(HistorySchema):
    """
    Схема изменения провайдера кэш-бокса
    """
    cashbox_provider_id = fields.Integer(required=True)