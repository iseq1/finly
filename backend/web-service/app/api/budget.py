"""
API для управления бюджетом
"""
from datetime import datetime
from flask import request
from flask_restx import Resource, fields, Namespace
from flask_jwt_extended import jwt_required, get_jwt_identity
from marshmallow import ValidationError
from app.models.budget import BalanceSnapshot, Budget
from app.schemas.budget import BalanceSnapshotSchema, SnapshotSchema, BudgetSchema
from app.utils.auth import permission_required
from app.utils.helpers import serialize_value
from app.extensions import db

api = Namespace('budget', description='Операции управления бюджетом')

# Модели для Swagger документации

snapshot_model = api.model('Snapshot', {
    'name': fields.String(required=True, description='Название кэш-бокса'),
    'currency': fields.String(required=True, description='Валюта кэш-бокса'),
    'balance': fields.Float(required=True, description='Баланс кэш-бокса'),
})


balance_snapshot_model = api.model('BalanceSnapshot', {
    'user_id': fields.Integer(required=True, description='ID-пользователя'),
    'month': fields.Integer(required=True, description='Месяц снимка'),
    'year': fields.Integer(required=True, description='Год снимка'),
    'snapshot': fields.Raw(required=True, description='Снимок баланса', example={
        1: {'name': 'Карта Тинькофф', 'currency': 'RUB', 'balance': 15400.0},
        2: {'name': 'Binance', 'currency': 'USDT', 'balance': 220.34}
    }),    'base_currency': fields.String(required=True, description='Базовая валюта'),
    'is_static': fields.Boolean(required=True, description='Статичная ли запись')
})


budget_model = api.model('Budget', {
    'user_id': fields.Integer(required=True, description='ID-пользователя'),
    'category_id': fields.Integer(required=True, description='ID-категории'),
    'subcategory_id': fields.Integer(required=True, description='ID-подкатегории'),
    'user_cashbox_id': fields.Integer(required=True, description='ID-пользовательского кэш-бокса'),
    'month': fields.Integer(required=True, description='Месяц'),
    'year': fields.Integer(required=True, description='Год'),
    'amount': fields.Float(required=True, description='Планируемая сумма'),
    'currency': fields.String(required=True, description='Валюта'),
    'comment': fields.String(required=True, description='Комментарий пользователя'),
    'is_recurring': fields.Boolean(required=True, description='Повторяется ли каждый месяц'),
    'is_locked': fields.Boolean(required=True, description='Зафиксирован ли бюджет'),
})

def get_difference(user_id):
    """
    Возвращает суммы доходов и расходов пользователя по его кэш-боксам за текущий месяц.
    :param user_id: идентификатор пользователя
    :return: два словаря — с доходами (to_div) и расходами (to_sum) по user_cashbox_id
    """
    current_year = datetime.now().year
    current_month = datetime.now().month

    from app.models.transaction import Income, Expense
    income_in_current_month = Income.query.filter(Income.user_id == user_id, Income.deleted == False,
                                                  Income.transacted_at >= f'{current_year}-{current_month}-01T00:00:00.000Z')
    expense_in_current_month = Expense.query.filter(Expense.user_id == user_id, Expense.deleted == False,
                                                    Expense.transacted_at >= f'{current_year}-{current_month}-01T00:00:00.000Z')

    to_div = {}
    for income in income_in_current_month:
        if income.user_cashbox_id in to_div:
            to_div[income.user_cashbox_id] += income.amount
        else:
            to_div[income.user_cashbox_id] = income.amount

    to_sum = {}
    for expense in expense_in_current_month:
        if expense.user_cashbox_id in to_sum:
            to_sum[expense.user_cashbox_id] += expense.amount
        else:
            to_sum[expense.user_cashbox_id] = expense.amount

    return to_div, to_sum


def make_snapshot(user_id, difference=False):
    """
    Создает снимок баланса для указанного пользователя.
    :param user_id: идентификатор пользователя
    :param difference: если True, вычисляет разницу в балансе
    :return: словарь с данными о состоянии баланса пользователя
    """
    if difference:
        to_div, to_sum = get_difference(user_id)

    from app.models.auth import UserCashbox
    snapshot_item = {
        user_cashbox.id: SnapshotSchema().load({
            'name': user_cashbox.cashbox.name,
            'currency': user_cashbox.cashbox.currency,
            'balance': user_cashbox.balance - to_div[user_cashbox.id] + to_sum[user_cashbox.id] if difference else user_cashbox.balance,
        })
        for user_cashbox in UserCashbox.query.filter_by(user_id=user_id, deleted=False)
    }

    return snapshot_item


# Снимок бюджета
@api.route('/balance_snapshot')
class BalanceSnapshotList(Resource):
    """Управление снимком экрана"""

    @jwt_required()
    @api.doc(security='jwt',
             params={
                 'year': "Год снимка баланса",
             })
    def get(self):
        """Получение всех снимком баланса"""
        try:
            year = request.args.get('year', default=datetime.now().year)
            user_id = get_jwt_identity()

            current_year = datetime.now().year
            current_month = datetime.now().month

            # Получаем последнюю динамическую запись для текущего месяца
            last_snapshot = BalanceSnapshot.query.filter_by(user_id=user_id, is_static=False, deleted=False).order_by(
                BalanceSnapshot.year.desc(), BalanceSnapshot.month.desc()).first()

            if last_snapshot:
                # Если есть динамическая запись (не новый пользователь)

                if last_snapshot.month == current_month and last_snapshot.year == current_year:
                    # Случай, когда надо просто обновить балансы динамической записи

                    # Сохранение старых данных для истории
                    old_data = last_snapshot.to_dict()

                    # Обновление снимка баланса
                    last_snapshot.snapshot = make_snapshot(user_id)
                    db.session.commit()

                    message = 'Динамическая запись успешно обновлена'

                    # Логирование изменений
                    if old_data['snapshot'] != last_snapshot.to_dict()['snapshot']:
                        from app.models.budget import BalanceSnapshotHistory
                        changes = {k: serialize_value(v) for k, v in last_snapshot.to_dict().items() if old_data.get(k) != v}
                        BalanceSnapshotHistory.log_change(last_snapshot, 'update', user_id, changes)

                elif (last_snapshot.year == current_year and abs(last_snapshot.month - current_month) == 1) or (abs(last_snapshot.year - current_year) == 1 and abs(last_snapshot.month - current_month) == 11):
                    # Случай, когда надо зафиксировать динамическую запись и создать новую динамическую запись

                    # Сохранение старых данных для истории
                    old_data = last_snapshot.to_dict()

                    last_snapshot.is_static = True
                    dynamic_snapshot_data = BalanceSnapshotSchema().load(BalanceSnapshot.make_balance_snapshot(user_id=user_id, month= current_month, year=current_year, snapshot=make_snapshot(user_id, True), is_static=False))

                    db.session.add(dynamic_snapshot_data)
                    db.session.commit()

                    message = 'Динамическая запись успешно зафиксирована \nНовая динамическая запись успешно создана'

                    # Логирование изменений
                    from app.models.budget import BalanceSnapshotHistory
                    BalanceSnapshotHistory.log_change(dynamic_snapshot_data, 'create', user_id)

                    # Логирование изменений
                    from app.models.budget import BalanceSnapshotHistory
                    changes = {k: serialize_value(v) for k, v in last_snapshot.to_dict().items() if old_data.get(k) != v}
                    BalanceSnapshotHistory.log_change(last_snapshot, 'update', user_id, changes)

                else:
                    # Случай, когда надо зафиксировать динамическую запись, создать n недостающих статических записей и одну динамическую

                    from dateutil.relativedelta import relativedelta
                    from app.models.auth import UserCashbox


                    # Сохранение старых данных для истории
                    old_data = last_snapshot.to_dict()

                    last_snapshot.is_static = True

                    # Генерация недостающих месяцев
                    last_date = datetime(last_snapshot.year, last_snapshot.month, 1)
                    current_date = datetime(current_year, current_month, 1)
                    delta_months = (current_date.year - last_date.year) * 12 + (current_date.month - last_date.month)

                    for i in range(1, delta_months):
                        missing_date = last_date + relativedelta(months=i)

                        static_snapshot_data = BalanceSnapshotSchema().load(
                            BalanceSnapshot.make_balance_snapshot(user_id=user_id, month=missing_date.month,
                                                                  year=missing_date.year,
                                                                  snapshot=last_snapshot.snapshot, is_static=True))

                        db.session.add(static_snapshot_data)

                        # Логирование изменений
                        from app.models.budget import BalanceSnapshotHistory
                        BalanceSnapshotHistory.log_change(static_snapshot_data, 'create', user_id)

                    # Создание новой динамической записи (актуальные балансы)
                    dynamic_snapshot_data = BalanceSnapshotSchema().load(
                        BalanceSnapshot.make_balance_snapshot(user_id=user_id, month=current_month, year=current_year,
                                                              snapshot=make_snapshot(user_id), is_static=False))

                    db.session.add(dynamic_snapshot_data)
                    db.session.commit()

                    message = f'Динамическая запись успешно зафиксирована\n {delta_months} недостающих статических записей успешно созданы\n Динамическая запись успешно создана'

                    # Логирование изменений
                    from app.models.budget import BalanceSnapshotHistory
                    changes = {k: serialize_value(v) for k, v in last_snapshot.to_dict().items() if old_data.get(k) != v}
                    BalanceSnapshotHistory.log_change(last_snapshot, 'update', user_id, changes)

                    # Логирование изменений
                    from app.models.budget import BalanceSnapshotHistory
                    BalanceSnapshotHistory.log_change(dynamic_snapshot_data, 'create', user_id)

            else:
                # Если нет динамической записи (новый пользователь)

                static_snapshot = BalanceSnapshot.make_balance_snapshot(user_id=user_id, month=current_month, year=current_year, snapshot=make_snapshot(user_id), is_static=True)
                static_snapshot_data = BalanceSnapshotSchema().load(static_snapshot)

                dynamic_snapshot = BalanceSnapshot.make_balance_snapshot(user_id=user_id, month=current_month, year=current_year, snapshot=make_snapshot(user_id), is_static=False)
                dynamic_snapshot_data = BalanceSnapshotSchema().load(dynamic_snapshot)

                db.session.add(static_snapshot_data)
                db.session.add(dynamic_snapshot_data)
                db.session.commit()

                message = 'Новые динамическая и статическая записи для нового пользователя успешно созданы'

                # Логирование изменений
                from app.models.budget import BalanceSnapshotHistory
                BalanceSnapshotHistory.log_change(static_snapshot_data, 'create', user_id)
                BalanceSnapshotHistory.log_change(dynamic_snapshot_data, 'create', user_id)


            balance_snapshot = BalanceSnapshot.query.filter_by(user_id=user_id, year = year).all()
            balance_snapshot.sort(key=lambda x: x.month)

            return {
                'message': message,
                'balance_snapshot': BalanceSnapshotSchema(many=True).dump(balance_snapshot)
            }

        except ValidationError as e:
            return {'message': 'Ошибка валидации', 'errors': e.messages}, 400


# Бюджет
@api.route('')
class BudgetList(Resource):
    """Управление бюджетом"""

    @jwt_required()
    @api.doc(security='jwt',
             params={
                 'month': 'Месяц (1-12)',
                 'year': 'Год (например, 2025)',
             })
    def get(self):
        """Получение списка всех заданных бюджетов пользователя"""
        try:
            # Получение данных из запроса
            month = int(request.args.get('month', default=datetime.utcnow().month))
            year = int(request.args.get('year', default=datetime.utcnow().year))

            # Валидация
            if not (1 <= month <= 12):
                return {'message': 'Месяц должен быть от 1 до 12'}, 400
            if not (1900 <= year <= 2100):
                return {'message': 'Некорректный год'}, 400

            user_id = get_jwt_identity()

            budgets = Budget.query.filter_by(user_id=user_id, month=month, year=year).order_by(Budget.category_id).all()
            return BudgetSchema(many=True).dump(budgets)
        except ValidationError as e:
            return {'message': 'Ошибка валидации', 'errors': e.messages}, 400

    @jwt_required()
    # @permission_required('budget.manage')
    @api.doc(security='jwt')
    @api.expect(budget_model)
    def post(self):
        """Создание нового бюджета"""
        try:
            budget_data = BudgetSchema().load(request.json)

            # Проверка существования бюджета
            if Budget.query.filter_by(user_id=budget_data.user_id, category_id=budget_data.category_id, subcategory_id=budget_data.subcategory_id, user_cashbox_id=budget_data.user_cashbox_id, month=budget_data.month, year=budget_data.year).first():
                return {'message': 'Такой бюджет уже существует'}, 400

            db.session.add(budget_data)
            db.session.commit()

            # Логирование изменений
            from app.models.budget import BudgetHistory
            user_id = get_jwt_identity()
            BudgetHistory.log_change(budget_data, 'create', user_id)

            return {
                'message': 'Новый бюджет успешно создан',
                'budget': BudgetSchema().dump(budget_data)
            }, 201

        except ValidationError as e:
            return {'message': 'Ошибка валидации', 'errors': e.messages}, 400


@api.route('/<int:id>')
class BudgetDetails(Resource):
    """Управление конкретной записью бюджета"""

    @jwt_required()
    @api.doc(security='jwt')
    def get(self, id):
        """Получение информации конкретной записи бюджета"""
        pass

    @jwt_required()
    # @permission_required('budget.manage')
    @api.doc(security='jwt')
    @api.expect(budget_model)
    def put(self, id):
        """Обновление конкретной записи бюджета"""
        # TODO: take to attentions field :is_locked:
        pass

    @jwt_required()
    # @permission_required('budget.manage')
    @api.doc(security='jwt')
    def delete(self, id):
        """Удаление конкретной записи бюджета"""
        pass
