"""
API для управления кэш-боксами
"""
from flask import request
from flask_restx import Resource, fields
from flask_jwt_extended import jwt_required, get_jwt_identity
from marshmallow import ValidationError
from app.models.settings.cashboxes import Cashbox, CashboxType, CashboxProvider
from app.schemas.settings.cashboxes import CashboxSchema, CashboxTypeSchema, CashboxProviderSchema
from app.utils.auth import permission_required
from app.utils.helpers import serialize_value
from app.extensions import db
from app.api.settings import api


# Модели для Swagger документации

cashbox_model = api.model('Cashbox', {
    'name': fields.String(required=True, description='Наименование кэш-бокса'),
    'type_id': fields.Integer(required=True, description='ID-типа кэш-бокса'),
    'provider_id': fields.Integer(required=True, description='ID-провайдера кэш-бокса'),
    'currency': fields.String(required=True, description='Валюта кэш-бокса'),
    'description': fields.String(required=True, description='Описание кэш-бокса'),
    'icon': fields.String(required=True, description='Ссылка на иконку кэш-бокса'),
    'is_active': fields.Boolean(required=True, description='Флаг активности кэш-бокса')
})

cashbox_type_model = api.model('CashboxType', {
    'name': fields.String(required=True, descriptions='Наименование типа кэш-бокса'),
    'code': fields.String(required=True, descriptions='Код типа кэш-бокса'),
})

cashbox_provider_model = api.model('CashboxProvider', {
    'name': fields.String(required=True, description='Наименование кэш-бокса'),
    'full_name': fields.String(required=True, description='Полное наименование кэш-бокса'),
    'logo_url': fields.String(required=True, description='Ссылка на логотип кэш-бокса'),
    'alt_logo_url': fields.String(required=True, description='Ссылка на альтернативный логотип кэш-бокса'),
    'color': fields.String(required=True, description='Цвет кэш-бокса'),
    'second_color': fields.String(required=True, description='Запасной цвет кэш-бокса'),
    'alt_color': fields.String(required=True, description='Альтернативный цвет кэш-бокса'),
    'second_alt_color': fields.String(required=True, description='Альтернативный запасной цвет кэш-бокса'),
})


# Кэш-боксы
@api.route('/cashboxes')
class CashboxList(Resource):
    """Управление кэш-боксами"""

    @jwt_required()
    @api.doc(security='jwt')
    def get(self):
        """Получение списка всех кэш-боксов"""
        cashboxes = Cashbox.query.filter_by(deleted=False).all()
        return CashboxSchema(many=True).dump(cashboxes)

    @jwt_required()
    # @permission_required('settings.manage')
    @api.doc(security='jwt')
    @api.expect(cashbox_model)
    def post(self):
        """Создание нового кэш-бокса"""
        try:
            cashbox_data = CashboxSchema().load(request.json)

            # Проверка существования кэш-бокса
            if Cashbox.query.filter_by(name=cashbox_data.name).first():
                return {'message': 'Кэш-бокс с таким наименованием уже существует'}, 400

            db.session.add(cashbox_data)
            db.session.commit()

            # Логирование изменений
            from app.models.settings.cashboxes import CashboxHistory
            user_id = get_jwt_identity()
            CashboxHistory.log_change(cashbox_data, 'create', user_id)

            return {
                'message': 'Новый кэш-бокс успешно создан',
                'cashbox': CashboxSchema().dump(cashbox_data)
            }, 201

        except ValidationError as e:
            return {'message': 'Ошибка валидации', 'errors': e.messages}, 400


@api.route('/cashboxes/<int:id>')
class CashboxDetail(Resource):
    """Управление конкретным кэш-боксом"""

    @jwt_required()
    @api.doc(security='jwt')
    def get(self, id):
        """Получение информации о конкретном кэш-боксе"""
        cashbox = Cashbox.query.get_or_404(id)
        return CashboxSchema().dump(cashbox)
    
    @jwt_required()
    @permission_required('settings.manage')
    @api.doc(security='jwt')
    @api.expect(cashbox_model)
    def put(self, id):
        """Обновление кэш-бокса"""
        try:
            cashbox = Cashbox.query.get_or_404(id)
            cashbox_data = CashboxSchema().load(request.json)
            
            # Сохранение старых данных для истории
            old_data = cashbox.to_dict()
            
            # Проверка уникальности кэш-бокса
            existing_name = Cashbox.query.filter_by(name=cashbox_data.name).first()
            if existing_name and existing_name.id != id:
                return {'message': 'Кэш-бокс с таким наименованием уже существует'}, 400
            
            for field, value in cashbox_data.__dict__.items():
                if field != '_sa_instance_state':
                    setattr(cashbox, field, value)

            db.session.commit()

            # Логирование изменений
            from app.models.settings.cashboxes import CashboxHistory
            user_id = get_jwt_identity()
            changes = {k: serialize_value(v) for k, v in cashbox.to_dict().items() if old_data.get(k) != v}
            CashboxHistory.log_change(cashbox, 'update', user_id, changes)

            return {
                'message': 'Кэш-бокс успешно обновлен',
                'cashbox': CashboxSchema().dump(cashbox)
            }

        except ValidationError as e:
            return {'message': 'Ошибка валидации', 'errors': e.messages}, 400

    @jwt_required()
    @permission_required('settings.manage')
    @api.doc(security='jwt')
    def delete(self, id):
        """Удаление кэш-бокса"""
        cashbox = Cashbox.query.get_or_404(id)

        # Логирование изменений
        from app.models.settings.cashboxes import CashboxHistory
        user_id = get_jwt_identity()
        CashboxHistory.log_change(cashbox, 'delete', user_id)

        cashbox.soft_delete()
        return {'message': f'Кэш-бокс с ID = {cashbox.id} успешно удален'}


# Типы кэш-боксов
@api.route('/cashboxes-type')
class CashboxTypeList(Resource):
    """Управление типами кэш-боксов"""

    @jwt_required()
    @api.doc(security='jwt')
    def get(self):
        """Получение списка всех типов кэш-боксов"""
        cashbox_types = CashboxType.query.filter_by(deleted=False).all()
        return CashboxTypeSchema(many=True).dump(cashbox_types)

    @jwt_required()
    # @permission_required('settings.manage')
    @api.doc(security='jwt')
    @api.expect(cashbox_type_model)
    def post(self):
        """Создание нового типа кэш-бокса"""
        try:
            cashbox_type_data = CashboxTypeSchema().load(request.json)

            # Проверка существования типа кэш-бокса
            if CashboxType.query.filter_by(name=cashbox_type_data.name).first():
                return {'message': 'Тип кэш-бокса с таким наименованием уже существует'}, 400
            if CashboxType.query.filter_by(code=cashbox_type_data.code).first():
                return {'message': 'Тип кэш-бокса с таким кодом уже существует'}, 400

            db.session.add(cashbox_type_data)
            db.session.commit()

            # Логирование изменений
            from app.models.settings.cashboxes import CashboxTypeHistory
            user_id = get_jwt_identity()
            CashboxTypeHistory.log_change(cashbox_type_data, 'create', user_id)

            return {
                'message': 'Новый тип кэш-бокса успешно создан',
                'cashbox_type': CashboxTypeSchema().dump(cashbox_type_data)
            }, 201

        except ValidationError as e:
            return {'message': 'Ошибка валидации', 'errors': e.messages}, 400


@api.route('/cashboxes-type/<int:id>')
class CashboxTypeDetail(Resource):
    """Управление конкретным типом кэш-бокса"""

    @jwt_required()
    @api.doc(security='jwt')
    def get(self, id):
        """Получение информации о конкретном типе кэш-бокса"""
        cashbox_type = CashboxType.query.get_or_404(id)
        return CashboxTypeSchema().dump(cashbox_type)

    @jwt_required()
    # @permission_required('settings.manage')
    @api.doc(security='jwt')
    @api.expect(cashbox_type_model)
    def put(self, id):
        """Обновление типа кэш-бокса"""
        try:
            cashbox_type = CashboxType.query.get_or_404(id)
            cashbox_type_data = CashboxTypeSchema().load(request.json)

            # Сохранение старых данных для истории
            old_data = cashbox_type.to_dict()

            # Проверка уникальности категории
            existing_name = CashboxType.query.filter_by(name=cashbox_type_data.name).first()
            if existing_name and existing_name.id != id:
                return {'message': 'Тип кэш-бокса с таким наименованием уже существует'}, 400

            existing_code = CashboxType.query.filter_by(code=cashbox_type_data.code).first()
            if existing_code and existing_code.id != id:
                return {'message': 'Тип кэш-бокса с таким кодом уже существует'}, 400

            for field, value in cashbox_type_data.__dict__.items():
                if field != '_sa_instance_state':
                    setattr(cashbox_type, field, value)

            db.session.commit()

            # Логирование изменений
            from app.models.settings.cashboxes import CashboxTypeHistory
            user_id = get_jwt_identity()
            changes = {k: serialize_value(v) for k, v in cashbox_type.to_dict().items() if old_data.get(k != v)}
            CashboxTypeHistory.log_change(cashbox_type, 'update', user_id, changes)

            return {
                'message': 'Тип кэш-бокса успешно обновлен',
                'cashbox_type': CashboxTypeSchema().dump(cashbox_type)
            }

        except ValidationError as e:
            return {'message': 'Ошибка валидации', 'errors': e.messages}, 400

    @jwt_required()
    # @permission_required('settings.manage')
    @api.doc(security='jwt')
    def delete(self, id):
        """Удаление типа кэш-бокса"""
        cashbox_type = CashboxType.query.get_or_404(id)

        # Логирование изменений
        from app.models.settings.cashboxes import CashboxTypeHistory
        user_id = get_jwt_identity()
        CashboxTypeHistory.log_change(cashbox_type, 'delete', user_id)

        # TODO: soft delete for cashboxes by cashbox_type
        cashbox_type.soft_delete()
        return {'message': f'Тип кэш-бокса с ID = {cashbox_type.id} успешно удален'}


# Провайдеры кэш-боксов
@api.route('/cashboxes-provider')
class CashboxProviderList(Resource):
    """Управление провайдерами кэш-бокса"""

    @jwt_required()
    @api.doc(security='jwt')
    def get(self):
        """Получения списка всех провайдеров кэш-бокса"""
        cashbox_providers = CashboxProvider.query.filter_by(deleted=False).all()
        return CashboxProviderSchema(many=True).dump(cashbox_providers)

    @jwt_required()
    # @permission_required('settings.manage')
    @api.doc(security='jwt')
    @api.expect(cashbox_provider_model)
    def post(self):
        """Создание нового провайдера кэш-бокса"""
        try:
            cashbox_provider_data = CashboxProviderSchema().load(request.json)

            # Проверка существования провайдера кэш-бокса
            if CashboxProvider.query.filter_by(name=cashbox_provider_data.name).first():
                return {'message': 'Категория с таким наименованием уже существует'}, 400

            db.session.add(cashbox_provider_data)
            db.session.commit()

            # Логирование изменений
            from app.models.settings.cashboxes import CashboxProviderHistory
            user_id = get_jwt_identity()
            CashboxProviderHistory.log_change(cashbox_provider_data, 'create', user_id)

            return {
                'message': 'Новый провайдер кэш-бокса успешно создан',
                'cashbox_provider': CashboxProviderSchema().dump(cashbox_provider_data)
            }, 201

        except ValidationError as e:
            return {'message': 'Ошибка валидации', 'errors': e.messages}, 400


@api.route('/cashboxes-provider/<int:id>')
class CashboxProviderDetail(Resource):
    """Управление конкретным провайдером кэш-бокса"""

    @jwt_required()
    @api.doc(security='jwt')
    def get(self, id):
        """Получение информации о конкретном провайдере кэш-бокса"""
        cashbox_provider = CashboxProvider.query.get_or_404(id)
        return CashboxProviderSchema().dump(cashbox_provider)

    @jwt_required()
    # @permission_required('settings.manage')
    @api.doc(security='jwt')
    @api.expect(cashbox_provider_model)
    def put(self, id):
        """Обновление конкретного провайдера кэш-бокса"""
        try:
            cashbox_provider = CashboxProvider.query.get_or_404(id)
            cashbox_provider_data = CashboxProviderSchema().load(request.json)

            # Сохранение старых данных для истории
            old_data = cashbox_provider.to_dict()

            # Проверка уникальности провайдера кэш-бокса
            existing_name = CashboxProvider.query.filter_by(name=cashbox_provider_data.name).first()
            if existing_name and existing_name.id != id:
                return {'message': 'Провайдер кэш-бокса с таким наименованием уже существует'}, 400

            for field, value in cashbox_provider_data.__dict__.items():
                if field != '_sa_instance_state':
                    setattr(cashbox_provider, field, value)

            db.session.commit()

            # Логирование изменений
            from app.models.settings.cashboxes import CashboxProviderHistory
            user_id = get_jwt_identity()
            changes = {k: serialize_value(v) for k, v in cashbox_provider.to_dict().items() if old_data.get(k) != v}
            CashboxProviderHistory.log_change(cashbox_provider, 'update', user_id, changes)

            return {
                'message': 'Провайдер кэш-бокса успешно обновлен',
                'cashbox_provider': CashboxProviderSchema().dump(cashbox_provider)
            }

        except ValidationError as e:
            return {'message': 'Ошибка валидации', 'errors': e.messages}, 400

    @jwt_required()
    # @permission_required('settings.manage')
    @api.doc(security='jwt')
    def delete(self, id):
        """Удаление конкретного провайдера кэш-бокса"""
        cashbox_provider = CashboxProvider.query.get_or_404(id)

        # Логирование изменений
        from app.models.settings.cashboxes import CashboxProviderHistory
        user_id = get_jwt_identity()
        CashboxProviderHistory.log_change(cashbox_provider, 'delete', user_id)

        # TODO: soft delete for cashboxes by provider
        cashbox_provider.soft_delete()
        return {'message': f'Провайдер кэш-бокса с ID {cashbox_provider.id} успешно удален'}
