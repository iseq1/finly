"""
Схемы для категорий
"""
import re
from marshmallow import Schema, fields, validates, ValidationError, validates_schema, post_load
from app.schemas.base import BaseSchema, HistorySchema
from app.models.settings.categories import Category, CategoryHistory, Subcategory, SubcategoryHistory


class CategorySchema(BaseSchema):
    """Схема для категории"""

    class Meta:
        model = Category
        load_instance = True

    name = fields.String(required=True)
    code = fields.Integer(required=True)
    color = fields.String(required=True)
    logo_url = fields.String(required=True)

    subcategories = fields.List(fields.Nested('SubcategorySchema', dump_only=True))

    @validates("color")
    def validate_color(self, value):
        """Проверка корректности ввода цвета"""
        if len(value) != 7:
            raise ValidationError("Цвет должен быть указан в формате hex #xxxxxx")
        if not bool(re.match(r'^[A-Z0-9#]+$', value)):
            raise ValidationError("Цвет категории указан неверно, используйте hex-формат записи")

    @validates("name")
    def validate_name(self, value):
        """Проверка корректности наименования категории"""
        if len(value) >= 100 or len(value) == 0:
            raise ValidationError("Некорректное наименование категории")
        if not bool(re.match(r'^[А-ЯЁа-яё\s]+$', value)):
            raise ValidationError("Использование недопустимых символов запрещено")


class CategoryHistorySchema(HistorySchema):
    """Схема истории изменения категории"""
    category_id = fields.Integer(required=True)


class SubcategorySchema(BaseSchema):
    """Схема для подкатегорий"""
    class Meta:
        model = Subcategory
        load_instance = True

    name = fields.String(required=True)
    code = fields.Integer(required=True)
    logo_url = fields.String(required=True)
    category_id = fields.Integer(required=True)

    category = fields.Nested('CategorySchema', only=('name', 'code', 'logo_url', 'color'), dump_only=True)

    @validates("name")
    def validate_name(self, value):
        """Проверка корректности наименования подкатегории"""
        if len(value) >= 100 or len(value) == 0:
            raise ValidationError("Некорректное наименование подкатегории")
        if not bool(re.match(r'^[А-ЯЁа-яё\s]+$', value)):
            raise ValidationError("Использование недопустимых символов запрещено")


class SubcategoryHistorySchema(HistorySchema):
    """Схема истории изменения подкатегории"""
    subcategory_id = fields.Integer(required=True)