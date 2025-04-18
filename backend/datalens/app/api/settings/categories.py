"""
API для управления категориями
"""
from flask import request
from flask_restx import Resource, fields
from flask_jwt_extended import jwt_required, get_jwt_identity
from marshmallow import ValidationError
from app.models.settings.categories import Category, Subcategory
from app.schemas.settings.categories import CategorySchema, SubcategorySchema
from app.utils.auth import permission_required
from app.utils.helpers import serialize_value
from app.extensions import db
from app.api.settings import api

# Модели для Swagger документации

category_model = api.model('Category', {
    'name': fields.String(required=True, description='Наименование категории'),
    'code': fields.String(required=True, description='Код категории'),
    'logo_url': fields.String(required=True, description='Ссылка на логотип категории'),
    'color': fields.String(required=True, description='Цвет категории формата hex #xxxxxx'),
})

subcategory_model = api.model('Subcategory', {
    'name': fields.String(required=True, description='Наименование подкатегории'),
    'code': fields.String(required=True, description='Код подкатегории'),
    'logo_url': fields.String(required=True, description='Ссылка на логотип подкатегории'),
    'category_id': fields.String(required=True, description='ID-категории'),
})


# Категории
@api.route('/categories')
class CategoryList(Resource):
    """Управление категориями"""

    @jwt_required()
    @api.doc(security='jwt')
    def get(self):
        """Получения списка всех категорий"""
        categories = Category.query.filter_by(deleted=False).all()
        return CategorySchema(many=True).dump(categories)

    @jwt_required()
    # @permission_required('settings.manage')
    @api.doc(security='jwt')
    @api.expect(category_model)
    def post(self):
        """Создание новой категории"""
        try:
            category_data = CategorySchema().load(request.json)

            # Проверка существования категории
            if Category.query.filter_by(name=category_data.name).first():
                return {'message': 'Категория с таким наименованием уже существует'}, 400
            if Category.query.filter_by(code=category_data.code).first():
                return {'message': 'Категория с таким кодом уже существует'}, 400

            db.session.add(category_data)
            db.session.commit()

            # Логирование изменений
            from app.models.settings.categories import CategoryHistory
            user_id = get_jwt_identity()
            CategoryHistory.log_change(category_data, 'create', user_id)

            return {
                'message': 'Новая категория успешно создана',
                'category': CategorySchema().dump(category_data)
            }, 201

        except ValidationError as e:
            return {'message': 'Ошибка валидации', 'errors': e.messages}, 400


@api.route('/categories/<int:id>')
class CategoryDetail(Resource):
    """Управление конкретной категорией"""

    @jwt_required()
    @api.doc(security='jwt')
    def get(self, id):
        """Получение информации о конкретной категории"""
        category = Category.query.get_or_404(id)
        return CategorySchema().dump(category)

    @jwt_required()
    # @permission_required('settings.manage')
    @api.doc(security='jwt')
    @api.expect(category_model)
    def put(self, id):
        """Обновление категории"""
        try:
            category = Category.query.get_or_404(id)
            category_data = CategorySchema().load(request.json)

            # Сохранение старых данных для истории
            old_data = category.to_dict()

            # Проверка уникальности категории
            existing_name = Category.query.filter_by(name=category_data.name).first()
            if existing_name and existing_name.id != id:
                return {'message': 'Категория с таким наименованием уже существует'}, 400

            existing_code = Category.query.filter_by(code=category_data.code).first()
            if existing_code and existing_code.id != id:
                return {'message': 'Категория с таким кодом уже существует'}, 400

            for field, value in category_data.__dict__.items():
                if field != '_sa_instance_state':
                    setattr(category, field, value)

            db.session.commit()

            # Логирование изменений
            from app.models.settings.categories import CategoryHistory
            user_id = get_jwt_identity()
            changes = {k: serialize_value(v) for k, v in category.to_dict().items() if old_data.get(k) != v}
            CategoryHistory.log_change(category, 'update', user_id, changes)

            return {
                'message': 'Категория успешно обновлена',
                'category': CategorySchema().dump(category)
            }

        except ValidationError as e:
            return {'message': 'Ошибка валидации', 'errors': e.messages}, 400

    @jwt_required()
    # @permission_required('settings.manage')
    @api.doc(security='jwt')
    def delete(self, id):
        """Удаление категории"""
        category = Category.query.get_or_404(id)

        # Логирование изменений
        from app.models.settings.categories import CategoryHistory
        user_id = get_jwt_identity()
        CategoryHistory.log_change(category, 'delete', user_id)

        # TODO: soft delete for subcategory by category
        category.soft_delete()
        return {'message': f'Категория c ID = {category.id} успешно удалена'}


# Подкатегории
@api.route('/subcategories')
class SubcategoryList(Resource):
    """Управление подкатегориями"""

    @jwt_required()
    @api.doc(security='jwt')
    def get(self):
        """Получения списка всех подкатегорий"""
        subcategories = Subcategory.query.filter_by(deleted=False).all()
        return SubcategorySchema(many=True).dump(subcategories)

    @jwt_required()
    # @permission_required('settings.manage')
    @api.doc(security='jwt')
    @api.expect(subcategory_model)
    def post(self):
        """Создание новой подкатегории"""
        try:
            subcategory_data = SubcategorySchema().load(request.json)

            # Проверка существования подкатегории
            if Subcategory.query.filter_by(name=subcategory_data.name).first():
                return {'message': 'Подкатегория с таким наименованием уже существует'}, 400
            if Subcategory.query.filter_by(code=subcategory_data.code).first():
                return {'message': 'Подкатегория с таким кодом уже существует'}, 400

            # Проверка существования родительской категории
            if not Category.query.get_or_404(subcategory_data.category_id):
                return {'message': f'Родительская категория с ID = {subcategory_data.category_id} не была найдена'}

            db.session.add(subcategory_data)
            db.session.commit()

            # Логирование изменений
            from app.models.settings.categories import SubcategoryHistory
            user_id = get_jwt_identity()
            SubcategoryHistory.log_change(subcategory_data, 'create', user_id)

            return {
                'message': 'Новая подкатегория успешно создана',
                'category': CategorySchema().dump(subcategory_data)
            }, 201

        except ValidationError as e:
            return {'message': 'Ошибка валидации', 'errors': e.messages}, 400


@api.route('/subcategories/<int:id>')
class SubcategoryDetail(Resource):
    """Управление конкретной подкатегорией"""

    @jwt_required()
    @api.doc(security='jwt')
    def get(self, id):
        """Получение информации о конкретной подкатегории"""
        subcategory = Subcategory.query.get_or_404(id)
        return SubcategorySchema().dump(subcategory)

    @jwt_required()
    # @permission_required('settings.manage')
    @api.doc(security='jwt')
    @api.expect(subcategory_model)
    def put(self, id):
        """Обновление подкатегории"""
        try:
            subcategory = Subcategory.query.get_or_404(id)
            subcategory_data = SubcategorySchema().load(request.json)

            # Сохранение старых данных для истории
            old_data = subcategory.to_dict()

            # Проверка уникальности категории
            existing_name = Subcategory.query.filter_by(name=subcategory_data.name).first()
            if existing_name and existing_name.id != id:
                return {'message': 'Подкатегория с таким наименованием уже существует'}, 400

            existing_code = Subcategory.query.filter_by(code=subcategory_data.code).first()
            if existing_code and existing_code.id != id:
                return {'message': 'Подкатегория с таким кодом уже существует'}, 400

            # Проверка существования родительской категории
            if not Category.query.get_or_404(subcategory_data.category_id):
                return {'message': f'Родительская категория с ID = {subcategory_data.category_id} не была найдена'}

            for field, value in subcategory_data.__dict__.items():
                if field != '_sa_instance_state':
                    setattr(subcategory, field, value)

            db.session.commit()

            # Логирование изменений
            from app.models.settings.categories import SubcategoryHistory
            user_id = get_jwt_identity()
            changes = {k: serialize_value(v) for k, v in subcategory.to_dict().items() if old_data.get(k) != v}
            SubcategoryHistory.log_change(subcategory, 'update', user_id, changes)

            return {
                'message': 'Подкатегория успешно обновлена',
                'category': CategorySchema().dump(subcategory)
            }

        except ValidationError as e:
            return {'message': 'Ошибка валидации', 'errors': e.messages}, 400

    @jwt_required()
    # @permission_required('settings.manage')
    @api.doc(security='jwt')
    def delete(self, id):
        """Удаление подкатегории"""
        subcategory = Subcategory.query.get_or_404(id)

        # Логирование изменений
        from app.models.settings.categories import SubcategoryHistory
        user_id = get_jwt_identity()
        SubcategoryHistory.log_change(subcategory, 'delete', user_id)

        subcategory.soft_delete()
        return {'message': f'Подкатегория c ID = {subcategory.id} успешно удалена'}
