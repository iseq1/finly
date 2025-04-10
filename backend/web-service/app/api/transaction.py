"""
API для управления транзакциями
"""
from flask import request
from flask_restx import Resource, fields, Namespace
from flask_jwt_extended import jwt_required, get_jwt_identity
from marshmallow import ValidationError
from app.models.transaction import Income, IncomeHistory, Expense, ExpenseHistory
from app.schemas.transaction import IncomeSchema, IncomeHistorySchema, ExpenseSchema, ExpenseHistorySchema
from app.utils.auth import permission_required
from app.utils.helpers import serialize_value
from app.extensions import db

api = Namespace('transactions', description='Операции управления транзакциями пользователя')

# Модели для Swagger документации

income_model = api.model('Income', {
    'user_cashbox_id': fields.Integer(required=True, description='ID-пользовательского кэш-бокса'),
    'category_id': fields.Integer(required=True, description='ID-категории'),
    'subcategory_id': fields.Integer(required=True, description='ID-подкатегории'),
    'amount': fields.Float(required=True, description='Сумма транзакции'),
    'comment': fields.String(required=True, description='Комментарий к транзакции'),
    'transacted_at': fields.DateTime(required=True, description='Время и дата проведения транзакции'),
    'source': fields.String(required=True, description='Источник дохода')
})

expense_model = api.model('Expense', {
    'user_cashbox_id': fields.Integer(required=True, description='ID-пользовательского кэш-бокса'),
    'category_id': fields.Integer(required=True, description='ID-категории'),
    'subcategory_id': fields.Integer(required=True, description='ID-подкатегории'),
    'amount': fields.Float(required=True, description='Сумма транзакции'),
    'comment': fields.String(required=True, description='Комментарий к транзакции'),
    'transacted_at': fields.DateTime(required=True, description='Время и дата проведения транзакции'),
    'vendor': fields.String(required=True, description='Причина расхода (Покупка в СпортМастер)'),
    'location': fields.String(required=True, description='Локация совершения расхода (ТЦ KazanMall)')
})


# Доходы
@api.route('/income')
class IncomeList(Resource):
    """Управление доходами"""

    @jwt_required()
    @api.doc(security='jwt')
    def get(self):
        """Получения списка всех доходов пользователя"""
        user_id = get_jwt_identity()

        # Получаем все user_cashbox пользователя
        from app.models.auth import UserCashbox
        user_cashboxes = UserCashbox.query.filter_by(user_id=user_id, deleted=False).all()
        user_cashbox_ids = [cashbox.id for cashbox in user_cashboxes]

        # Получаем все доходы пользователя (по полученным user_cashbox_ids и полю deleted)
        incomes = Income.query.filter(Income.user_cashbox_id.in_(user_cashbox_ids), Income.deleted == False).all()
        return IncomeSchema(many=True).dump(incomes)

    @jwt_required()
    # @permission_required('transaction.manage')
    @api.doc(security='jwt')
    @api.expect(income_model)
    def post(self):
        """Создание новой записи дохода"""
        try:
            income_data = IncomeSchema().load(request.json)

            # Получение кэш-бокса пользователя
            from app.models.auth import UserCashbox
            user_cashbox = UserCashbox.query.filter_by(id=income_data.user_cashbox_id).first()

            # Проверка корректности указанного пользовательского кэш-бокса
            if not user_cashbox:
                return {'message': 'Кэш-бокс не найден'}, 404

            # Сохранение старых данных для истории
            old_data = user_cashbox.to_dict()

            # Обновление баланса кэш-бокса
            user_cashbox.balance += income_data.amount

            db.session.add(income_data)
            db.session.commit()

            # Логирование изменений
            from app.models.transaction import IncomeHistory
            user_id = get_jwt_identity()
            IncomeHistory.log_change(income_data, 'create', user_id)

            # Логирование изменений
            from app.models.auth import UserCashboxHistory
            changes = {k: serialize_value(v) for k, v in user_cashbox.to_dict().items() if old_data.get(k) != v }
            UserCashboxHistory.log_change(user_cashbox, 'update', user_id, changes)

            return {
                'message': 'Новая запись дохода успешна создана',
                'second_message': 'Данные пользовательского кэш-бокса обновлены',
                'income': IncomeSchema().dump(income_data)
            }

        except ValidationError as e:
            return {'message': 'Ошибка валидации', 'errors': e.messages}, 400


@api.route('/income/<int:id>')
class IncomeDetail(Resource):
    """Управление конкретной записью дохода пользователя"""

    @jwt_required()
    @api.doc(security='jwt')
    def get(self, id):
        """Получение информации о конкретной записи дохода"""
        income = Income.query.get_or_404(id)
        # TODO: need to return full income information, including all info about cashbox, provider, type and categories

        return IncomeSchema().dump(income)

    @jwt_required()
    @api.doc(security='jwt')
    @api.expect(income_model)
    def put(self, id):
        """Обновление конкретной записи дохода"""
        try:

            income = Income.query.get_or_404(id)
            income_data = IncomeSchema().load(request.json)
            user_id = get_jwt_identity()

            # Сохранение старых данных для истории
            old_data = income.to_dict()
            old_user_cashbox_id = income.user_cashbox_id
            old_amount = income.amount

            # Случай когда пользователь изменил кэш-бокс -> изменяется баланс старого и нового кэш-боксов
            if income_data.user_cashbox_id != old_user_cashbox_id:
                from app.models.auth import UserCashbox
                old_user_cashbox = UserCashbox.query.get_or_404(old_user_cashbox_id)
                new_user_cashbox = UserCashbox.query.get_or_404(income_data.user_cashbox_id)

                old_user_cashbox.balance -= old_amount
                new_user_cashbox.balance += income_data.amount

                # Логирование изменений баланса
                from app.models.auth import UserCashboxHistory
                UserCashboxHistory.log_change(old_user_cashbox, 'update', user_id, {'balance': f'{old_user_cashbox.balance}'})
                UserCashboxHistory.log_change(new_user_cashbox, 'update', user_id, {'balance': f'{new_user_cashbox.balance}'})

            # Случай когда пользователь изменил сумму дохода -> изменяется баланс текущего кэш-бокса
            elif income_data.amount != old_amount:
                from app.models.auth import UserCashbox
                user_cashbox = UserCashbox.query.get_or_404(old_user_cashbox_id)
                user_cashbox.balance += (income_data.amount - old_amount)

                # Логирование изменений баланса
                from app.models.auth import UserCashboxHistory
                UserCashboxHistory.log_change(user_cashbox, 'update', user_id, {'balance': f'{user_cashbox.balance}'})

            # Обновляем поля
            for field, value in income_data.__dict__.items():
                if field != '_sa_instance_state':
                    setattr(income, field, value)

            db.session.commit()

            # Логирование изменений
            from app.models.transaction import IncomeHistory
            changes = {k: serialize_value(v) for k, v in income.to_dict().items() if old_data.get(k) != v}
            IncomeHistory.log_change(income, 'update', user_id, changes)

            return {
                'message': 'Запись дохода успешно обновлена',
                'income': IncomeSchema().dump(income)
            }

        except ValidationError as e:
            return {'message': 'Ошибка валидации', 'errors': e.messages}, 400

    @jwt_required()
    @api.doc(security='jwt')
    def delete(self, id):
        """Удаление конкретной записи дохода"""
        income = Income.query.get_or_404(id)

        from app.models.auth import UserCashbox
        user_cashbox = UserCashbox.query.get_or_404(income.user_cashbox_id)

        user_cashbox.balance -= income.amount

        # Логирование изменений
        from app.models.auth import UserCashboxHistory
        user_id = get_jwt_identity()
        UserCashboxHistory.log_change(user_cashbox, 'update', user_id, {'balance': f'{user_cashbox.balance}'})
        from app.models.transaction import IncomeHistory
        IncomeHistory.log_change(income, 'delete', user_id)
        income.soft_delete()
        return {'message': f'Запись дохода с ID = {id} успешна удалена'}

