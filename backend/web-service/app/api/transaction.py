"""
API для управления транзакциями
"""
from collections import defaultdict
from flask import request
from flask_restx import Resource, fields, Namespace
from flask_jwt_extended import jwt_required, get_jwt_identity
from marshmallow import ValidationError
from app.models.transaction import Income, Expense
from app.schemas.transaction import IncomeSchema, ExpenseSchema
from app.utils.auth import permission_required
from app.utils.helpers import serialize_value, apply_pagination
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
    @api.doc(security='jwt',
             params={
                 'cashbox': 'ID кэш-бокса (опционально)',
                 'limit': 'Количество последних записей (опционально)',
                 'start_date': "Дата начала периода (YYYY-MM-DD)",
                 'end_date': "Дата конца периода (YYYY-MM-DD)",
                 'page': 'Номер страницы',
                 'per_page': 'Кол-во элементов на странице',
                 'sort_by': 'Поле для сортировки',
                 'sort_dir': 'Направление сортировки',
             }
             )
    def get(self):
        """Получение списка всех доходов пользователя"""
        user_id = get_jwt_identity()

        # Получаем все user_cashbox пользователя
        from app.models.auth import UserCashbox
        user_cashboxes = UserCashbox.query.filter_by(user_id=user_id, deleted=False).all()
        user_cashbox_ids = [cashbox.id for cashbox in user_cashboxes]

        from datetime import datetime, timedelta
        def_start_date = datetime.utcnow().replace(day=1).strftime('%Y-%m-%d')
        def_end_date = ((datetime.utcnow().replace(day=28) + timedelta(days=4)).replace(day=1) - timedelta(
            seconds=1)).strftime('%Y-%m-%d')

        # Получаем параметры из запроса
        limit = request.args.get('limit', type=int)
        cashbox_id = request.args.get('cashbox', type=int)
        start_date = request.args.get('start_date', default=def_start_date) + 'T00:00:00.000Z'  # Начало диапазона временного интервала
        end_date = request.args.get('end_date', default=def_end_date) + 'T23:59:59.999Z'  # Конец диапазона временного интервала
        page = request.args.get('page', default=1, type=int)
        per_page = request.args.get('per_page', default=10, type=int)
        sort_by = request.args.get('sort_by', 'transacted_at')
        sort_dir = request.args.get('sort_dir', 'asc')

        # Валидация данных
        from app.schemas.base import DateRangeSchema
        DateRangeSchema().load({'start_date': start_date, 'end_date': end_date})

        # Базовый запрос
        query = Income.query.filter(
            Income.user_cashbox_id.in_(user_cashbox_ids),
            Income.deleted == False
        )

        # Фильтрация по дате, если передана
        if start_date:
            query = query.filter(Income.transacted_at >= start_date)

        if end_date:
            query = query.filter(Income.transacted_at <= end_date)


        # Сортировка
        sortable_fields = {
            'transacted_at': Income.transacted_at,
            'category_id': Income.category_id,
            'subcategory_id': Income.subcategory_id,
            'user_cashbox_id': Income.user_cashbox_id,
            'amount': Income.amount,
            'comment': Income.comment,
            'source': Income.source,
        }

        sort_column = sortable_fields.get(sort_by, Income.transacted_at)
        if sort_dir == 'desc':
            query = query.order_by(sort_column.desc())
        else:
            query = query.order_by(sort_column.asc())

        if cashbox_id:
            query = query.filter(Income.user_cashbox_id == cashbox_id)

        # Применяем пагинацию
        pagination = apply_pagination(query, page, per_page)

        items = pagination.items[:limit] if limit else pagination.items

        incomes_data = IncomeSchema(many=True).dump(items)

        return {
            'items': incomes_data,
            'total': pagination.total,
            'pages': pagination.pages,
            'page': pagination.page,
            'per_page': pagination.per_page,
            'has_next': pagination.has_next,
            'has_prev': pagination.has_prev
        }

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
    # @permission_required('transaction.manage')
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
    # @permission_required('transaction.manage')
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


@api.route('/expense')
class ExpenseList(Resource):
    """Управление расходами"""

    @jwt_required()
    @api.doc(security='jwt',
             params={
                 'cashbox': 'ID кэш-бокса (опционально)',
                 'limit': 'Количество последних записей (опционально)',
                 'start_date': "Дата начала периода (YYYY-MM-DD)",
                 'end_date': "Дата конца периода (YYYY-MM-DD)",
                 'page': 'Номер страницы',
                 'per_page': 'Кол-во элементов на странице',
                 'sort_by': 'Поле для сортировки',
                 'sort_dir': 'Направление сортировки',
             }
             )
    def get(self):
        """Получение списка всех расходов пользователя"""
        user_id = get_jwt_identity()

        # Получаем все user_cashbox пользователя
        from app.models.auth import UserCashbox
        user_cashboxes = UserCashbox.query.filter_by(user_id=user_id, deleted=False).all()
        user_cashbox_ids = [cashbox.id for cashbox in user_cashboxes]

        from datetime import datetime, timedelta
        def_start_date = datetime.utcnow().replace(day=1).strftime('%Y-%m-%d')
        def_end_date = ((datetime.utcnow().replace(day=28) + timedelta(days=4)).replace(day=1) - timedelta(
            seconds=1)).strftime('%Y-%m-%d')

        # Получаем параметры из запроса
        limit = request.args.get('limit', type=int)
        cashbox_id = request.args.get('cashbox', type=int)
        start_date = request.args.get('start_date',
                                      default=def_start_date) + 'T00:00:00.000Z'  # Начало диапазона временного интервала
        end_date = request.args.get('end_date',
                                    default=def_end_date) + 'T23:59:59.999Z'  # Конец диапазона временного интервала
        page = request.args.get('page', default=1, type=int)
        per_page = request.args.get('per_page', default=10, type=int)
        sort_by = request.args.get('sort_by', 'transacted_at')
        sort_dir = request.args.get('sort_dir', 'asc')

        # Валидация данных
        from app.schemas.base import DateRangeSchema
        DateRangeSchema().load({'start_date': start_date, 'end_date': end_date})

        # Базовый запрос
        query = Expense.query.filter(
            Expense.user_cashbox_id.in_(user_cashbox_ids),
            Expense.deleted == False
        )

        # Фильтрация по дате, если передана
        if start_date:
            query = query.filter(Expense.transacted_at >= start_date)

        if end_date:
            query = query.filter(Expense.transacted_at <= end_date)

        # Сортировка
        sortable_fields = {
            'transacted_at': Expense.transacted_at,
            'category_id': Expense.category_id,
            'subcategory_id': Expense.subcategory_id,
            'user_cashbox_id': Expense.user_cashbox_id,
            'amount': Expense.amount,
            'comment': Expense.comment,
            'vendor': Expense.vendor,
            'location': Expense.location,
        }

        sort_column = sortable_fields.get(sort_by, Income.transacted_at)
        if sort_dir == 'desc':
            query = query.order_by(sort_column.desc())
        else:
            query = query.order_by(sort_column.asc())

        if cashbox_id:
            query = query.filter(Expense.user_cashbox_id == cashbox_id)


        pagination = apply_pagination(query, page, per_page)

        items = pagination.items[:limit] if limit else pagination.items

        expenses_data = ExpenseSchema(many=True).dump(items)

        return {
            'items': expenses_data,
            'total': pagination.total,
            'pages': pagination.pages,
            'page': pagination.page,
            'per_page': pagination.per_page,
            'has_next': pagination.has_next,
            'has_prev': pagination.has_prev
        }

    @jwt_required()
    # @permission_required('transaction.manage')
    @api.doc(security='jwt')
    @api.expect(expense_model)
    def post(self):
        """Создание новой записи расхода"""
        try:
            expense_data = ExpenseSchema().load(request.json)

            # Получение кэш-бокса пользователя
            from app.models.auth import UserCashbox
            user_cashbox = UserCashbox.query.filter_by(id=expense_data.user_cashbox_id).first()

            # Проверка корректности указанного пользовательского кэш-бокса
            if not user_cashbox:
                return {'message': 'Кэш-бокс не найден'}, 404

            # Сохранение старых данных для истории
            old_data = user_cashbox.to_dict()

            # Обновление баланса кэш-бокса
            user_cashbox.balance -= expense_data.amount

            db.session.add(expense_data)
            db.session.commit()

            # Логирование изменений
            from app.models.transaction import ExpenseHistory
            user_id = get_jwt_identity()
            ExpenseHistory.log_change(expense_data, 'create', user_id)

            # Логирование изменений
            from app.models.auth import UserCashboxHistory
            changes = {k: serialize_value(v) for k, v in user_cashbox.to_dict().items() if old_data.get(k) != v}
            UserCashboxHistory.log_change(user_cashbox, 'update', user_id, changes)

            return {
                'message': 'Новая запись расхода успешна создана',
                'second_message': 'Данные пользовательского кэш-бокса обновлены',
                'expense': ExpenseSchema().dump(expense_data)
            }

        except ValidationError as e:
            return {'message': 'Ошибка валидации', 'errors': e.messages}, 400


@api.route('/expense/<int:id>')
class ExpenseDetail(Resource):
    """Управление конкретной записью расхода пользователя"""

    @jwt_required()
    @api.doc(security='jwt')
    def get(self, id):
        """Получение информации о конкретной записи расхода"""
        expense = Expense.query.get_or_404(id)
        # TODO: need to return full expense information, including all info about cashbox, provider, type and categories

        return ExpenseSchema().dump(expense)

    @jwt_required()
    # @permission_required('transaction.manage')
    @api.doc(security='jwt')
    @api.expect(expense_model)
    def put(self, id):
        """Обновление конкретной записи расхода"""
        try:

            expense = Expense.query.get_or_404(id)
            expense_data = ExpenseSchema().load(request.json)
            user_id = get_jwt_identity()

            # Сохранение старых данных для истории
            old_data = expense.to_dict()
            old_user_cashbox_id = expense.user_cashbox_id
            old_amount = expense.amount

            # Случай когда пользователь изменил кэш-бокс -> изменяется баланс старого и нового кэш-боксов
            if expense_data.user_cashbox_id != old_user_cashbox_id:
                from app.models.auth import UserCashbox
                old_user_cashbox = UserCashbox.query.get_or_404(old_user_cashbox_id)
                new_user_cashbox = UserCashbox.query.get_or_404(expense_data.user_cashbox_id)

                old_user_cashbox.balance += old_amount
                new_user_cashbox.balance -= expense_data.amount

                # Логирование изменений баланса
                from app.models.auth import UserCashboxHistory
                UserCashboxHistory.log_change(old_user_cashbox, 'update', user_id, {'balance': f'{old_user_cashbox.balance}'})
                UserCashboxHistory.log_change(new_user_cashbox, 'update', user_id, {'balance': f'{new_user_cashbox.balance}'})

            # Случай когда пользователь изменил сумму расхода -> изменяется баланс текущего кэш-бокса
            elif expense_data.amount != old_amount:
                from app.models.auth import UserCashbox
                user_cashbox = UserCashbox.query.get_or_404(old_user_cashbox_id)
                user_cashbox.balance += (old_amount - expense_data.amount)

                # Логирование изменений баланса
                from app.models.auth import UserCashboxHistory
                UserCashboxHistory.log_change(user_cashbox, 'update', user_id, {'balance': f'{user_cashbox.balance}'})

            # Обновляем поля
            for field, value in expense_data.__dict__.items():
                if field != '_sa_instance_state':
                    setattr(expense, field, value)

            db.session.commit()

            # Логирование изменений
            from app.models.transaction import ExpenseHistory
            changes = {k: serialize_value(v) for k, v in expense.to_dict().items() if old_data.get(k) != v}
            ExpenseHistory.log_change(expense, 'update', user_id, changes)

            return {
                'message': 'Запись расхода успешно обновлена',
                'expense': ExpenseSchema().dump(expense)
            }

        except ValidationError as e:
            return {'message': 'Ошибка валидации', 'errors': e.messages}, 400

    @jwt_required()
    # @permission_required('transaction.manage')
    @api.doc(security='jwt')
    def delete(self, id):
        """Удаление конкретной записи расхода"""
        expense = Expense.query.get_or_404(id)

        from app.models.auth import UserCashbox
        user_cashbox = UserCashbox.query.get_or_404(expense.user_cashbox_id)

        user_cashbox.balance += expense.amount

        # Логирование изменений
        from app.models.auth import UserCashboxHistory
        user_id = get_jwt_identity()
        UserCashboxHistory.log_change(user_cashbox, 'update', user_id, {'balance': f'{user_cashbox.balance}'})
        from app.models.transaction import ExpenseHistory
        ExpenseHistory.log_change(expense, 'delete', user_id)
        expense.soft_delete()
        return {'message': f'Запись расхода с ID = {id} успешна удалена'}


@api.route('/statistics')
class StatisticsList(Resource):
    """Управление статистикой транзакций пользователя"""

    @jwt_required()
    @api.doc(security='jwt',
             params={
                 'start_date': "Дата начала периода (YYYY-MM-DD)",
                 'end_date': "Дата конца периода (YYYY-MM-DD)",
                 'type': "Тип транзакций: income/expense",
                 'include_empty_categories': "Включать категории без транзакций (true/false)",
                 'sort_by': "Поле для сортировки (category)",
                 'order': "Направление сортировки (asc/desc)"
             })
    def get(self):
        """Получение статистики пользователя"""
        try:
            from datetime import datetime, timedelta
            def_start_date = datetime.utcnow().replace(day=1).strftime('%Y-%m-%d')
            def_end_date = ((datetime.utcnow().replace(day=28) + timedelta(days=4)).replace(day=1) - timedelta(seconds=1)).strftime('%Y-%m-%d')

            # Получение данных из запроса
            start_date = request.args.get('start_date',
                                          default=def_start_date) + 'T00:00:00.000Z'  # Начало диапазона временного интервала
            end_date = request.args.get('end_date',
                                        default=def_end_date) + 'T23:59:59.999Z'  # Конец диапазона временного интервала
            include_empty = request.args.get('include_empty_categories', default='true').lower() == 'true' # Учитывать ли пустые ячейки
            transaction_type = request.args.get('type', default='income')  # Тип транзакции
            sort_by = request.args.get('sort_by', default='amount')  # Поле для сортировки (по умолчанию - сумма)
            order = request.args.get('order', default='asc')  # Направление сортировки (по умолчанию - по возрастанию)
            user_id = get_jwt_identity()  # ID-пользователя

            # Валидация данных
            from app.schemas.base import DateRangeSchema
            DateRangeSchema().load({'start_date': start_date, 'end_date': end_date})
            if transaction_type not in ['income', 'expense']:
                raise ValidationError('Некорректно указан type транзакции')

            from app.models.auth import UserCashbox
            from app.models.transaction import Income, Expense
            from app.models.settings.categories import Category

            # Получение всех пользовательских кэш-боксов пользователя
            user_cashboxes = UserCashbox.query.filter_by(user_id=user_id, deleted=False).all()
            user_cashbox_ids = [cb.id for cb in user_cashboxes]

            # Запрос транзакций пользователя
            if transaction_type == 'income':
                query = Income.query.filter(Income.user_cashbox_id.in_(user_cashbox_ids), Income.deleted == False)
            else:
                query = Expense.query.filter(Expense.user_cashbox_id.in_(user_cashbox_ids), Expense.deleted == False)

            if start_date:
                query = query.filter(Income.transacted_at >= start_date if transaction_type == 'income' else Expense.transacted_at >= start_date)
            if end_date:
                query = query.filter(Income.transacted_at <= end_date if transaction_type == 'income' else Expense.transacted_at <= end_date)

            transactions = query.all()

            # Сортировка
            if sort_by == 'category':
                transactions.sort(key=lambda x: x.category.name, reverse=(order == 'desc'))

            statistics = {}

            # Агрегация транзакций по провайдерам
            for transaction in transactions:
                category_name = transaction.category.name
                provider_name = transaction.user_cashbox.cashbox.provider.name
                amount = transaction.amount

                if category_name not in statistics:
                    statistics[category_name] = {
                        'id': transaction.category.id,
                        'code': transaction.category.code,
                        'data': {}
                    }
                if provider_name not in statistics[category_name]['data']:
                    statistics[category_name]['data'][provider_name] = {
                        'id': transaction.user_cashbox.cashbox.provider.id,
                        'sum': 0,
                    }
                statistics[category_name]['data'][provider_name]['sum'] += amount
            # Добавление категорий без транзакций
            if include_empty:
                if transaction_type == 'income':
                    all_categories = [item for item in Category.query.filter_by().all() if item.type == 'income']
                else:
                    all_categories = [item for item in Category.query.filter_by().all() if item.type == 'expense']
                for category in all_categories:
                    category_name = category.name
                    if category_name not in statistics:
                        statistics[category_name] = {
                            'id': category.id,
                            'code': category.code,
                            'data': {},
                        }
                    for cb in user_cashboxes:
                        provider_name = cb.cashbox.provider.name
                        if provider_name not in statistics[category_name]['data']:
                            statistics[category_name]['data'][provider_name] = {
                                'id': cb.cashbox.provider.id,
                                'sum': 0
                            }

            # Подсчет итогов
            category_totals = {}
            provider_totals = {}

            for category, category_data in statistics.items():
                category_totals[category] = sum([provider_data['sum'] for provider, provider_data in category_data['data'].items()])
                for provider, provider_data in category_data['data'].items():
                    provider_totals[provider] = provider_totals.get(provider, 0) + provider_data['sum']

            return {
                'message': 'Статистика успешно получена',
                'statistics': statistics,
                'category_totals': category_totals,
                'provider_totals': provider_totals  # Используем итог по провайдерам
            }, 200

        except ValidationError as e:
            return {'message': 'Ошибка валидации', 'errors': e.messages}, 400


@api.route('/statistics/category/<int:id>')
class StatisticsCategoryList(Resource):
    """Управление статистикой транзакций пользователя по категории"""

    @jwt_required()
    @api.doc(security='jwt',
             params={
                 'start_date': "Дата начала периода (YYYY-MM-DD)",
                 'end_date': "Дата конца периода (YYYY-MM-DD)",
                 'type': "Тип транзакций: income/expense",
                 'sort_by': "Поле для сортировки (amount/transacted_at/comment/subcategory/cashbox)",
                 'order': "Направление сортировки (asc/desc)"
             })
    def get(self, id):
        """Получение всех транзакций в категории"""
        try:
            from datetime import datetime, timedelta
            def_start_date = datetime.utcnow().replace(day=1).strftime('%Y-%m-%d')
            def_end_date = ((datetime.utcnow().replace(day=28) + timedelta(days=4)).replace(day=1) - timedelta(seconds=1)).strftime('%Y-%m-%d')

            # Получение данных из запроса
            start_date = request.args.get('start_date',
                                          default=def_start_date) + 'T00:00:00.000Z'  # Начало диапазона временного интервала
            end_date = request.args.get('end_date',
                                        default=def_end_date) + 'T23:59:59.999Z'  # Конец диапазона временного интервала
            transaction_type = request.args.get('type', default='income')  # Тип транзакции
            sort_by = request.args.get('sort_by', default='amount')  # Поле для сортировки (по умолчанию - сумма)
            order = request.args.get('order', default='asc')  # Направление сортировки (по умолчанию - по возрастанию)
            user_id = get_jwt_identity()  # ID-пользователя

            # Валидация данных
            from app.schemas.base import DateRangeSchema
            DateRangeSchema().load({'start_date': start_date, 'end_date': end_date})
            if transaction_type not in ['income', 'expense']:
                raise ValidationError('Некорректно указан type транзакции')

            from app.models.auth import UserCashbox
            from app.models.transaction import Income, Expense
            from app.models.settings.categories import Category, Subcategory

            # Получение всех пользовательских кэш-боксов пользователя
            user_cashboxes = UserCashbox.query.filter_by(user_id=user_id, deleted=False).all()
            user_cashbox_ids = [cb.id for cb in user_cashboxes]

            # Запрос транзакций пользователя
            if transaction_type == 'income':
                query = Income.query.filter(Income.user_cashbox_id.in_(user_cashbox_ids), Income.deleted == False, Income.category_id == id)
            else:
                query = Expense.query.filter(Expense.user_cashbox_id.in_(user_cashbox_ids), Expense.deleted == False, Expense.category_id == id)

            if start_date:
                query = query.filter(
                    Income.transacted_at >= start_date if transaction_type == 'income' else Expense.transacted_at >= start_date)
            if end_date:
                query = query.filter(
                    Income.transacted_at <= end_date if transaction_type == 'income' else Expense.transacted_at <= end_date)

            transactions = query.all()

            # Сортировка
            if sort_by == 'amount':
                transactions.sort(key=lambda x: x.amount, reverse=(order == 'desc'))
            elif sort_by == 'transacted_at':
                transactions.sort(key=lambda x: x.transacted_at, reverse=(order == 'desc'))
            elif sort_by == 'comment':
                transactions.sort(key=lambda x: x.comment, reverse=(order == 'desc'))
            elif sort_by == 'subcategory':
                transactions.sort(key=lambda x: x.subcategory.name, reverse=(order == 'desc'))
            elif sort_by == 'cashbox':
                transactions.sort(key=lambda x: x.user_cashbox.cashbox.name, reverse=(order == 'desc'))

            # Группировка транзакций по подкатегориям
            subcat_data = defaultdict(lambda: {"total": 0, "transactions": []})

            for item in transactions:
                subcategory = item.subcategory
                user_cashbox = item.user_cashbox
                cashbox = user_cashbox.cashbox
                provider = cashbox.provider

                subcat_data[subcategory.id]["subcategory_name"] = subcategory.name
                subcat_data[subcategory.id]["total"] += item.amount

                if transaction_type == 'income':
                    subcat_data[subcategory.id]["transactions"].append({
                        "id": item.id,
                        "amount": item.amount,
                        "comment": item.comment,
                        "transacted_at": item.transacted_at.isoformat(),
                        "source": item.source,
                        "cashbox": {
                            "user_cashbox_id": user_cashbox.id,
                            "cashbox_name": cashbox.name,
                            "provider_name": provider.name
                        }
                    })
                else:
                    subcat_data[subcategory.id]["transactions"].append({
                        "id": item.id,
                        "amount": item.amount,
                        "comment": item.comment,
                        "transacted_at": item.transacted_at.isoformat(),
                        "vendor": item.vendor,
                        "location": item.location,
                        "cashbox": {
                            "user_cashbox_id": user_cashbox.id,
                            "cashbox_name": cashbox.name,
                            "provider_name": provider.name
                        }
                    })

            # Сборка финального списка
            statistics = []
            for subcat_id, data in subcat_data.items():
                statistics.append({
                    "subcategory_id": subcat_id,
                    "subcategory_name": data["subcategory_name"],
                    "total": data["total"],
                    "transactions": data["transactions"]
                })

            # Получение имени категории
            category = Category.query.get(id)

            return {
                "message": "Детализация по категории успешно получена",
                "category_id": id,
                "category_name": category.name if category else None,
                "type": transaction_type,
                "statistics": statistics
            }, 200

        except ValidationError as e:
            return {'message': 'Ошибка валидации', 'errors': e.messages}, 400


@api.route('/statistics/provider/<int:id>')
class StatisticsCashboxList(Resource):
    """Управление статистикой транзакций пользователя по кэш-боксам провайдера"""

    @jwt_required()
    @api.doc(security='jwt',
             params={
                 'start_date': "Дата начала периода (YYYY-MM-DD)",
                 'end_date': "Дата конца периода (YYYY-MM-DD)",
                 'type': "Тип транзакций: income/expense",
                 'sort_by': "Поле для сортировки (name/currency/description/type_name/total)",
                 'order': "Направление сортировки (asc/desc)"
             })
    def get(self, id):
        """Получение всех транзакций в кэш-боксах провайдера"""
        try:
            from datetime import datetime, timedelta
            def_start_date = datetime.utcnow().replace(day=1).strftime('%Y-%m-%d')
            def_end_date = ((datetime.utcnow().replace(day=28) + timedelta(days=4)).replace(day=1) - timedelta(seconds=1)).strftime('%Y-%m-%d')

            # Получение данных из запроса
            start_date = request.args.get('start_date', default=def_start_date) + 'T00:00:00.000Z'  # Начало диапазона временного интервала
            end_date = request.args.get('end_date', default=def_end_date) + 'T23:59:59.999Z'  # Конец диапазона временного интервала
            transaction_type = request.args.get('type', default='income')  # Тип транзакции
            sort_by = request.args.get('sort_by', default='amount')  # Поле для сортировки (по умолчанию - сумма)
            order = request.args.get('order', default='asc')  # Направление сортировки (по умолчанию - по возрастанию)
            user_id = get_jwt_identity()  # ID-пользователя

            # Валидация данных
            from app.schemas.base import DateRangeSchema
            DateRangeSchema().load({'start_date': start_date, 'end_date': end_date})
            if transaction_type not in ['income', 'expense']:
                raise ValidationError('Некорректно указан type транзакции')

            from app.models.auth import UserCashbox
            from app.models.transaction import Income, Expense
            from app.models.settings.cashboxes import Cashbox, CashboxProvider, CashboxType

            # Получение всех пользовательских кэш-боксов пользователя
            user_cashboxes = UserCashbox.query.filter_by(user_id=user_id, deleted=False).all()

            # Получение всех кэш-боксов пользователя, связанных с этим провайдером
            provider_cashbox_ids = [cb.id for cb in user_cashboxes if cb.cashbox.provider_id == id]

            # Запрос транзакций пользователя
            if transaction_type == 'income':
                query = Income.query.filter(Income.user_cashbox_id.in_(provider_cashbox_ids), Income.deleted == False)
            else:
                query = Expense.query.filter(Expense.user_cashbox_id.in_(provider_cashbox_ids), Expense.deleted == False)

            if start_date:
                query = query.filter(
                    Income.transacted_at >= start_date if transaction_type == 'income' else Expense.transacted_at >= start_date)
            if end_date:
                query = query.filter(
                    Income.transacted_at <= end_date if transaction_type == 'income' else Expense.transacted_at <= end_date)

            transactions = query.all()

            # Сортировка
            if sort_by == 'name':
                transactions.sort(key=lambda x: x.user_cashbox.cashbox.name, reverse=(order == 'desc'))
            elif sort_by == 'currency':
                transactions.sort(key=lambda x: x.user_cashbox.cashbox.currency, reverse=(order == 'desc'))
            elif sort_by == 'description':
                transactions.sort(key=lambda x: x.user_cashbox.cashbox.description, reverse=(order == 'desc'))
            elif sort_by == 'type_name':
                transactions.sort(key=lambda x: x.user_cashbox.cashbox.type.name, reverse=(order == 'desc'))
            elif sort_by == 'total':
                transactions.sort(key=lambda x: x.subcategory.name, reverse=(order == 'desc'))

            # Группировка транзакций по кэш-боксам
            subcat_data = defaultdict(lambda: {"total": 0, "transactions": []})

            for item in transactions:
                user_cashbox = item.user_cashbox
                cashbox = user_cashbox.cashbox

                subcat_data[cashbox.id]["cashbox_name"] = cashbox.name
                subcat_data[cashbox.id]["cashbox_type"] = cashbox.type.name
                subcat_data[cashbox.id]["currency"] = cashbox.currency
                subcat_data[cashbox.id]["description"] = cashbox.description
                subcat_data[cashbox.id]["icon"] = cashbox.icon
                subcat_data[cashbox.id]["total"] += item.amount


            # Сборка финального списка
            statistics = []
            for subcat_id, data in subcat_data.items():
                statistics.append({
                    "cashbox_id": subcat_id,
                    "cashbox_name": data["cashbox_name"],
                    "cashbox_type": data["cashbox_type"],
                    "currency": data["currency"],
                    "description": data["description"],
                    "icon": data["icon"],
                    "total": data["total"],
                    # "transactions": data["transactions"]
                })

            # Получение провайдера
            provider = CashboxProvider.query.get_or_404(id)

            return {
                "message": "Детализация по провайдеру успешно получена",
                "provider_id": id,
                "provider_name": provider.name if provider else None,
                "type": transaction_type,
                "statistics": statistics
            }, 200

        except ValidationError as e:
            return {'message': 'Ошибка валидации', 'errors': e.messages}, 400


@api.route('/statistics/details/<string:id>')
class StatisticsDetailsList(Resource):
    """Управление статистикой транзакций пользователя по конкретной записи"""

    @jwt_required()
    @api.doc(security='jwt',
             params={
                 'start_date': "Дата начала периода (YYYY-MM-DD)",
                 'end_date': "Дата конца периода (YYYY-MM-DD)",
                 'type': "Тип транзакций: income/expense",
                 'sort_by': "Поле для сортировки ()",
                 'order': "Направление сортировки (asc/desc)"
             })
    def get(self, id):
        """Получение дополнительной информации по транзакциям"""
        try:
            from datetime import datetime, timedelta
            def_start_date = datetime.utcnow().replace(day=1).strftime('%Y-%m-%d')
            def_end_date = ((datetime.utcnow().replace(day=28) + timedelta(days=4)).replace(day=1) - timedelta(seconds=1)).strftime('%Y-%m-%d')

            # Получение данных из запроса
            start_date = request.args.get('start_date', default=def_start_date) + 'T00:00:00.000Z'  # Начало диапазона временного интервала
            end_date = request.args.get('end_date', default=def_end_date) + 'T23:59:59.999Z'  # Конец диапазона временного интервала
            transaction_type = request.args.get('type', default='income')  # Тип транзакции
            sort_by = request.args.get('sort_by', default='amount')  # Поле для сортировки (по умолчанию - сумма)
            order = request.args.get('order', default='asc')  # Направление сортировки (по умолчанию - по возрастанию)
            category_id, provider_id = map(int, id.split('-'))
            user_id = get_jwt_identity()  # ID-пользователя

            # Валидация данных
            from app.schemas.base import DateRangeSchema
            DateRangeSchema().load({'start_date': start_date, 'end_date': end_date})
            if transaction_type not in ['income', 'expense']:
                raise ValidationError('Некорректно указан type транзакции')

            from app.models.auth import UserCashbox
            from app.models.transaction import Income, Expense
            from app.models.settings.cashboxes import Cashbox, CashboxProvider, CashboxType
            from app.models.settings.categories import Category, Subcategory

            # Получение всех пользовательских кэш-боксов пользователя
            user_cashboxes = UserCashbox.query.filter_by(user_id=user_id, deleted=False).all()

            # Получение кэш-бокса пользователя
            provider_cashbox_id = [cb.id for cb in user_cashboxes if cb.cashbox.provider_id == provider_id]

            # Получение подкатегорий указанной категории
            subcategory_ids = [s.id for s in Subcategory.query.filter_by(category_id=category_id).all()]

            # Запрос транзакций пользователя
            if transaction_type == 'income':
                query = Income.query.filter(Income.user_cashbox_id.in_(provider_cashbox_id), Income.deleted == False, Income.subcategory_id.in_(subcategory_ids))
            else:
                query = Expense.query.filter(Expense.user_cashbox_id.in_(provider_cashbox_id), Expense.deleted == False, Expense.subcategory_id.in_(subcategory_ids))

            if start_date:
                query = query.filter(
                    Income.transacted_at >= start_date if transaction_type == 'income' else Expense.transacted_at >= start_date)
            if end_date:
                query = query.filter(
                    Income.transacted_at <= end_date if transaction_type == 'income' else Expense.transacted_at <= end_date)

            transactions = query.all()

            print(transactions)

            # Сортировка
            # if sort_by == 'name':
            #     transactions.sort(key=lambda x: x.user_cashbox.cashbox.name, reverse=(order == 'desc'))
            # elif sort_by == 'currency':
            #     transactions.sort(key=lambda x: x.user_cashbox.cashbox.currency, reverse=(order == 'desc'))

            subcat_data = defaultdict(lambda: {
                "subcategory_name": "",
                "total": 0,
                "transactions": []
            })

            for item in transactions:
                subcat = item.subcategory
                cashbox = item.user_cashbox.cashbox

                subcat_data[subcat.id]["subcategory_name"] = subcat.name
                subcat_data[subcat.id]["total"] += item.amount
                subcat_data[subcat.id]["transactions"].append({
                    "amount": item.amount,
                    "date": item.transacted_at.isoformat(),
                    "cashbox_name": cashbox.name,
                    "comment": item.comment
                })

            # Формирование итоговой статистики
            total_sum = sum([data["total"] for data in subcat_data.values()])
            statistics = []
            for subcat_id, data in subcat_data.items():
                percentage = (data["total"] / total_sum * 100) if total_sum > 0 else 0

                statistics.append({
                    "subcategory_id": subcat_id,
                    "subcategory_name": data["subcategory_name"],
                    "total": data["total"],
                    "percentage": round(percentage, 2),
                    "transactions": data["transactions"]
                })


            category = Category.query.get_or_404(category_id)
            provider = CashboxProvider.query.get_or_404(provider_id)

            return {
                "message": "Детализация по провайдеру и категории успешно получена",
                "category_id": category_id,
                "category_name": category.name if category else None,
                "provider_id": provider_id,
                "provider_name": provider.name if provider else None,
                "type": transaction_type,
                "statistics": statistics
            }, 200

        except ValidationError as e:
            return {'message': 'Ошибка валидации', 'errors': e.messages}, 400
