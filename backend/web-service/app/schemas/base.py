"""
Базовые схемы для валидации данных
"""
from marshmallow import Schema, fields, validates_schema, ValidationError
from app.extensions import ma

class BaseSchema(ma.SQLAlchemySchema):
    """Базовая схема для всех моделей"""
    
    id = fields.Integer(dump_only=True)
    created_at = fields.DateTime(dump_only=True)
    updated_at = fields.DateTime(dump_only=True)
    deleted = fields.Boolean(dump_only=True)

class HistorySchema(BaseSchema):
    """Базовая схема для истории изменений"""
    
    action = fields.String(required=True)
    changed_by_id = fields.Integer(required=True)
    timestamp = fields.DateTime(dump_only=True)
    changes = fields.Dict(keys=fields.String(), values=fields.Raw())

class PaginationSchema(Schema):
    """Схема для пагинации"""
    
    page = fields.Integer(missing=1, validate=lambda x: x > 0)
    per_page = fields.Integer(missing=20, validate=lambda x: 0 < x <= 100)
    total = fields.Integer(dump_only=True)
    pages = fields.Integer(dump_only=True)
    has_next = fields.Boolean(dump_only=True)
    has_prev = fields.Boolean(dump_only=True)
    items = fields.List(fields.Nested(lambda: BaseSchema()))

class DateRangeSchema(Schema):
    """Схема для фильтрации по датам"""
    
    start_date = fields.DateTime()
    end_date = fields.DateTime()

    @validates_schema
    def validate_dates(self, data, **kwargs):
        """Проверка, что начальная дата меньше конечной"""
        if data.get('start_date') and data.get('end_date'):
            if data['start_date'] > data['end_date']:
                raise ValidationError('start_date должна быть меньше end_date')

class ErrorSchema(Schema):
    """Схема для ошибок"""
    
    message = fields.String(required=True)
    errors = fields.Dict(keys=fields.String(), values=fields.List(fields.String()))
    status_code = fields.Integer()

class SuccessSchema(Schema):
    """Схема для успешных ответов"""
    
    message = fields.String()
    data = fields.Raw()
