"""
API для управления базовыми вещами в системе ERP
"""
from datetime import datetime
from flask import request, jsonify
from flask_restx import Namespace, Resource, fields
from app.extensions import db
from app.models.base import BaseModel as BaseModelDB, HistoryModel
from app.schemas.base import BaseSchema, HistorySchema, PaginationSchema, DateRangeSchema, ErrorSchema, SuccessSchema

api = Namespace('base', description='Базовые реализации системы')

# Модели для Swagger документации
base_model = api.model('BaseModel', {
    'id': fields.Integer(readonly=True, description='Уникальный идентификатор'),
    'created_at': fields.DateTime(readonly=True, description='Дата создания'),
    'updated_at': fields.DateTime(readonly=True, description='Дата обновления'),
    'deleted': fields.Boolean(readonly=True, description='Флаг удаления')
})

history_model = api.model('HistoryModel', {
    'id': fields.Integer(readonly=True, description='Уникальный идентификатор'),
    'created_at': fields.DateTime(readonly=True, description='Дата создания'),
    'updated_at': fields.DateTime(readonly=True, description='Дата обновления'),
    'deleted': fields.Boolean(readonly=True, description='Флаг удаления'),
    'action': fields.String(required=True, description='Тип действия (create/update/delete)'),
    'changed_by_id': fields.Integer(required=True, description='ID пользователя, внесшего изменения'),
    'timestamp': fields.DateTime(readonly=True, description='Время изменения'),
    'changes': fields.Raw(description='Изменения в формате JSON')
})

pagination_model = api.model('PaginationModel', {
    'page': fields.Integer(description='Текущая страница'),
    'per_page': fields.Integer(description='Количество элементов на странице'),
    'total': fields.Integer(description='Общее количество элементов'),
    'pages': fields.Integer(description='Общее количество страниц'),
    'has_next': fields.Boolean(description='Есть ли следующая страница'),
    'has_prev': fields.Boolean(description='Есть ли предыдущая страница'),
    'items': fields.List(fields.Nested(base_model), description='Список элементов')
})

date_range_model = api.model('DateRangeModel', {
    'start_date': fields.DateTime(description='Начальная дата'),
    'end_date': fields.DateTime(description='Конечная дата')
})

error_model = api.model('ErrorModel', {
    'message': fields.String(required=True, description='Сообщение об ошибке'),
    'errors': fields.Raw(description='Детали ошибок'),
    'status_code': fields.Integer(description='Код статуса HTTP')
})

success_model = api.model('SuccessModel', {
    'message': fields.String(description='Сообщение об успешном выполнении'),
    'data': fields.Raw(description='Данные ответа')
})

@api.route('/model')
class BaseModelResource(Resource):
    """Базовая модель системы"""
    
    @api.doc('get_base_model')
    @api.marshal_with(base_model)
    def get(self):
        """Получение информации о базовой модели"""
        # Это демонстрационный эндпоинт для отображения базовой модели в Swagger
        # Возвращаем пример базовой модели
        example = {
            'id': 1,
            'created_at': datetime.now(),
            'updated_at': datetime.now(),
            'deleted': False
        }
        return example

@api.route('/history')
class HistoryModelResource(Resource):
    """История изменений"""
    
    @api.doc('get_history_model')
    @api.marshal_with(history_model)
    def get(self):
        """Получение информации о модели истории изменений"""
        # Это демонстрационный эндпоинт для отображения модели истории в Swagger
        example = {
            'id': 1,
            'created_at': datetime.now(),
            'updated_at': datetime.now(),
            'deleted': False,
            'action': 'update',
            'changed_by_id': 1,
            'timestamp': datetime.now(),
            'changes': {'field': 'old_value', 'new_field': 'new_value'}
        }
        return example

@api.route('/pagination')
class PaginationModelResource(Resource):
    """Пагинация"""
    
    @api.doc('get_pagination_model')
    @api.marshal_with(pagination_model)
    def get(self):
        """Получение информации о модели пагинации"""
        # Это демонстрационный эндпоинт для отображения модели пагинации в Swagger
        example = {
            'page': 1,
            'per_page': 20,
            'total': 100,
            'pages': 5,
            'has_next': True,
            'has_prev': False,
            'items': [
                {
                    'id': 1,
                    'created_at': datetime.now(),
                    'updated_at': datetime.now(),
                    'deleted': False
                },
                {
                    'id': 2,
                    'created_at': datetime.now(),
                    'updated_at': datetime.now(),
                    'deleted': False
                }
            ]
        }
        return example

@api.route('/date-range')
class DateRangeModelResource(Resource):
    """Диапазон дат"""
    
    @api.doc('get_date_range_model')
    @api.marshal_with(date_range_model)
    def get(self):
        """Получение информации о модели диапазона дат"""
        # Это демонстрационный эндпоинт для отображения модели диапазона дат в Swagger
        example = {
            'start_date': datetime.now(),
            'end_date': datetime.now()
        }
        return example

@api.route('/error')
class ErrorModelResource(Resource):
    """Модель ошибки"""
    
    @api.doc('get_error_model')
    @api.response(400, 'Ошибка запроса', error_model)
    def get(self):
        """Получение информации о модели ошибки"""
        # Это демонстрационный эндпоинт для отображения модели ошибки в Swagger
        # Используем abort вместо return для гарантированного возврата ошибки
        from flask_restx import abort
        abort(400, message='Произошла ошибка', 
              errors={'field': ['Некорректное значение']}, 
              status_code=400)

@api.route('/success')
class SuccessModelResource(Resource):
    """Модель успешного ответа"""
    
    @api.doc('get_success_model')
    @api.marshal_with(success_model)
    def get(self):
        """Получение информации о модели успешного ответа"""
        # Это демонстрационный эндпоинт для отображения модели успешного ответа в Swagger
        example = {
            'message': 'Операция выполнена успешно',
            'data': {'id': 1, 'name': 'Пример'}
        }
        return example
