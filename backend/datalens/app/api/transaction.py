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
from app.utils.helpers import serialize_value
from app.extensions import db

api = Namespace('transactions', description='Операции получения транзакций пользователя')


@api.route('/income/by_cashbox')
class IncomeList(Resource):
    """Управление записями дохода"""

    @jwt_required()
    @api.doc(security='jwt',
             params={
                 'start_date': "Дата начала периода (YYYY-MM-DD)",
                 'end_date': "Дата конца периода (YYYY-MM-DD)",
             })
    def get(self):
        """Получение списка всех доходов пользователя по кэш-боксам"""
        from datetime import datetime, timedelta
        def_start_date = datetime.utcnow().replace(day=1).strftime('%Y-%m-%d')
        def_end_date = ((datetime.utcnow().replace(day=28) + timedelta(days=4)).replace(day=1) - timedelta(
            seconds=1)).strftime('%Y-%m-%d')

        # Получение данных из запроса
        start_date = request.args.get('start_date',
                                      default=def_start_date) + 'T00:00:00.000Z'  # Начало диапазона временного интервала
        end_date = request.args.get('end_date',
                                    default=def_end_date) + 'T23:59:59.999Z'  # Конец диапазона временного интервала

        from app.schemas.base import DateRangeSchema
        DateRangeSchema().load({'start_date': start_date, 'end_date': end_date})


        user_id = get_jwt_identity()

        from app.models.auth import UserCashbox
        from app.schemas.auth import UserCashboxSchema

        cashboxes = UserCashbox.query.filter_by(user_id=user_id, deleted=False).all()

        result = []
        for cashbox in cashboxes:
            incomes = Income.query.filter(
                Income.user_cashbox_id == cashbox.id,
                Income.deleted == False,
                Income.transacted_at >= start_date,
                Income.transacted_at <= end_date
            ).order_by(Income.transacted_at.desc()).all()

            result.append({
                "cashbox": UserCashboxSchema().dump(cashbox),
                "incomes": IncomeSchema(many=True).dump(incomes)
            })

        return result


@api.route('/income/by_category')
class IncomeByCategory(Resource):
    """Получение доходов пользователя, сгруппированных по категориям"""

    @jwt_required()
    @api.doc(security='jwt', params={
        'start_date': 'Дата начала периода (YYYY-MM-DD)',
        'end_date': 'Дата конца периода (YYYY-MM-DD)',
    })
    def get(self):
        """Получение списка доходов пользователя, сгруппированных по категориям"""
        from datetime import datetime, timedelta

        user_id = get_jwt_identity()

        # Даты по умолчанию — текущий месяц
        def_start_date = datetime.utcnow().replace(day=1).strftime('%Y-%m-%d')
        def_end_date = ((datetime.utcnow().replace(day=28) + timedelta(days=4)).replace(day=1) - timedelta(seconds=1)).strftime('%Y-%m-%d')

        start_date = request.args.get('start_date', default=def_start_date) + 'T00:00:00.000Z'
        end_date = request.args.get('end_date', default=def_end_date) + 'T23:59:59.999Z'

        from app.schemas.base import DateRangeSchema
        DateRangeSchema().load({'start_date': start_date, 'end_date': end_date})

        # Импорты моделей и схем
        from app.models.auth import UserCashbox
        from app.schemas.settings.categories import CategorySchema

        # Получаем все user_cashbox пользователя
        cashbox_ids = [
            cb.id for cb in UserCashbox.query.filter_by(user_id=user_id, deleted=False).all()
        ]

        # Получаем все доходы за период
        incomes = Income.query.filter(
            Income.user_cashbox_id.in_(cashbox_ids),
            Income.deleted == False,
            Income.transacted_at >= start_date,
            Income.transacted_at <= end_date
        ).order_by(Income.transacted_at.desc()).all()

        # Группируем по категориям
        grouped = {}
        for income in incomes:
            category = income.category
            category_data = CategorySchema().dump(category)
            if category.id not in grouped:
                grouped[category.id] = {
                    "category": category_data,
                    "incomes": []
                }
            grouped[category.id]["incomes"].append(IncomeSchema().dump(income))

        return list(grouped.values())


@api.route('/income/by_subcategory')
class IncomeBySubcategory(Resource):
    """Получение доходов пользователя, сгруппированных по подкатегориям"""

    @jwt_required()
    @api.doc(security='jwt', params={
        'start_date': 'Дата начала периода (YYYY-MM-DD)',
        'end_date': 'Дата конца периода (YYYY-MM-DD)',
    })
    def get(self):
        from datetime import datetime, timedelta

        user_id = get_jwt_identity()

        # Даты по умолчанию — текущий месяц
        def_start_date = datetime.utcnow().replace(day=1).strftime('%Y-%m-%d')
        def_end_date = ((datetime.utcnow().replace(day=28) + timedelta(days=4)).replace(day=1) - timedelta(seconds=1)).strftime('%Y-%m-%d')

        start_date = request.args.get('start_date', default=def_start_date) + 'T00:00:00.000Z'
        end_date = request.args.get('end_date', default=def_end_date) + 'T23:59:59.999Z'

        from app.schemas.base import DateRangeSchema
        DateRangeSchema().load({'start_date': start_date, 'end_date': end_date})

        # Импорты
        from app.models.auth import UserCashbox
        from app.schemas.settings.categories import SubcategorySchema

        # Получаем user_cashbox текущего пользователя
        cashbox_ids = [
            cb.id for cb in UserCashbox.query.filter_by(user_id=user_id, deleted=False).all()
        ]

        # Доходы за указанный период
        incomes = Income.query.filter(
            Income.user_cashbox_id.in_(cashbox_ids),
            Income.deleted == False,
            Income.transacted_at >= start_date,
            Income.transacted_at <= end_date
        ).order_by(Income.transacted_at.desc()).all()

        # Группировка по подкатегориям
        grouped = {}
        for income in incomes:
            subcategory = income.subcategory
            if not subcategory:
                continue  # на случай, если subcategory_id = None
            subcategory_data = SubcategorySchema().dump(subcategory)
            if subcategory.id not in grouped:
                grouped[subcategory.id] = {
                    "subcategory": subcategory_data,
                    "incomes": []
                }
            grouped[subcategory.id]["incomes"].append(IncomeSchema().dump(income))

        return list(grouped.values())


@api.route('/income/by_category_and_cashbox')
class IncomeByCategoryAndCashbox(Resource):
    """Группировка доходов по категориям и кэш-боксам"""

    @jwt_required()
    @api.doc(security='jwt', params={
        'start_date': 'Дата начала периода (YYYY-MM-DD)',
        'end_date': 'Дата конца периода (YYYY-MM-DD)',
    })
    def get(self):
        """Группировка доходов по категориям и кэш-боксам"""

        from datetime import datetime, timedelta

        user_id = get_jwt_identity()

        # Даты по умолчанию — текущий месяц
        def_start_date = datetime.utcnow().replace(day=1).strftime('%Y-%m-%d')
        def_end_date = ((datetime.utcnow().replace(day=28) + timedelta(days=4)).replace(day=1) - timedelta(
            seconds=1)).strftime('%Y-%m-%d')

        start_date = request.args.get('start_date', default=def_start_date) + 'T00:00:00.000Z'
        end_date = request.args.get('end_date', default=def_end_date) + 'T23:59:59.999Z'

        from app.schemas.base import DateRangeSchema
        DateRangeSchema().load({'start_date': start_date, 'end_date': end_date})

        # Импорты
        from app.models.auth import UserCashbox
        from app.schemas.auth import UserCashboxSchema
        from app.schemas.settings.categories import CategorySchema

        # Получаем кэш-боксы пользователя
        user_cashboxes = UserCashbox.query.filter_by(user_id=user_id, deleted=False).all()
        cashbox_ids = [cb.id for cb in user_cashboxes]

        incomes = Income.query.filter(
            Income.user_cashbox_id.in_(cashbox_ids),
            Income.deleted == False,
            Income.transacted_at >= start_date,
            Income.transacted_at <= end_date
        ).all()

        # Структура: category_id -> {cashbox_id -> сумма}
        from collections import defaultdict

        grouped = defaultdict(lambda: defaultdict(float))
        category_map = {}
        cashbox_map = {cb.id: cb for cb in user_cashboxes}

        for inc in incomes:
            if not inc.category_id or not inc.user_cashbox_id:
                continue
            grouped[inc.category_id][inc.user_cashbox_id] += inc.amount
            category_map[inc.category_id] = inc.category

        result = []
        for cat_id, cashbox_data in grouped.items():
            cat_obj = category_map.get(cat_id)
            result.append({
                "category": CategorySchema().dump(cat_obj),
                "cashboxes": [
                    {
                        "cashbox": UserCashboxSchema().dump(cashbox_map[cid]),
                        "total_amount": round(amount, 2)
                    }
                    for cid, amount in cashbox_data.items()
                ]
            })

        return result


@api.route('/income/by_subcategory_and_cashbox')
class IncomeBySubcategoryAndCashbox(Resource):
    """Группировка доходов по подкатегориям и кэш-боксам"""

    @jwt_required()
    @api.doc(security='jwt', params={
        'start_date': 'Дата начала периода (YYYY-MM-DD)',
        'end_date': 'Дата конца периода (YYYY-MM-DD)',
    })
    def get(self):
        """Группировка доходов по подкатегориям и кэш-боксам"""
        from collections import defaultdict
        from datetime import datetime, timedelta

        user_id = get_jwt_identity()

        # Даты по умолчанию — текущий месяц
        def_start_date = datetime.utcnow().replace(day=1).strftime('%Y-%m-%d')
        def_end_date = ((datetime.utcnow().replace(day=28) + timedelta(days=4)).replace(day=1) - timedelta(
            seconds=1)).strftime('%Y-%m-%d')

        start_date = request.args.get('start_date', default=def_start_date) + 'T00:00:00.000Z'
        end_date = request.args.get('end_date', default=def_end_date) + 'T23:59:59.999Z'

        from app.schemas.base import DateRangeSchema
        DateRangeSchema().load({'start_date': start_date, 'end_date': end_date})

        # Импорты
        from app.models.auth import UserCashbox
        from app.schemas.auth import UserCashboxSchema
        from app.schemas.settings.categories import SubcategorySchema

        # Все кэш-боксы пользователя
        user_cashboxes = UserCashbox.query.filter_by(user_id=user_id, deleted=False).all()
        cashbox_ids = [cb.id for cb in user_cashboxes]

        # Все доходы пользователя в выбранный период
        incomes = Income.query.filter(
            Income.user_cashbox_id.in_(cashbox_ids),
            Income.deleted == False,
            Income.transacted_at >= start_date,
            Income.transacted_at <= end_date
        ).all()

        grouped = defaultdict(lambda: defaultdict(float))
        subcategory_map = {}
        cashbox_map = {cb.id: cb for cb in user_cashboxes}

        for inc in incomes:
            if not inc.subcategory_id or not inc.user_cashbox_id:
                continue
            grouped[inc.subcategory_id][inc.user_cashbox_id] += inc.amount
            subcategory_map[inc.subcategory_id] = inc.subcategory

        result = []
        for subcat_id, cashbox_data in grouped.items():
            subcat_obj = subcategory_map.get(subcat_id)
            result.append({
                "subcategory": SubcategorySchema().dump(subcat_obj),
                "cashboxes": [
                    {
                        "cashbox": UserCashboxSchema().dump(cashbox_map[cid]),
                        "total_amount": round(amount, 2)
                    }
                    for cid, amount in cashbox_data.items()
                ]
            })

        return result


@api.route('/expense/by_cashbox')
class ExpenseList(Resource):
    """Управление записями расхода"""

    @jwt_required()
    @api.doc(security='jwt',
             params={
                 'start_date': "Дата начала периода (YYYY-MM-DD)",
                 'end_date': "Дата конца периода (YYYY-MM-DD)",
             })
    def get(self):
        """Получение списка всех расходов пользователя по кэш-боксам"""
        from datetime import datetime, timedelta
        def_start_date = datetime.utcnow().replace(day=1).strftime('%Y-%m-%d')
        def_end_date = ((datetime.utcnow().replace(day=28) + timedelta(days=4)).replace(day=1) - timedelta(
            seconds=1)).strftime('%Y-%m-%d')

        # Получение данных из запроса
        start_date = request.args.get('start_date',
                                      default=def_start_date) + 'T00:00:00.000Z'  # Начало диапазона временного интервала
        end_date = request.args.get('end_date',
                                    default=def_end_date) + 'T23:59:59.999Z'  # Конец диапазона временного интервала

        from app.schemas.base import DateRangeSchema
        DateRangeSchema().load({'start_date': start_date, 'end_date': end_date})


        user_id = get_jwt_identity()

        from app.models.auth import UserCashbox
        from app.schemas.auth import UserCashboxSchema

        cashboxes = UserCashbox.query.filter_by(user_id=user_id, deleted=False).all()

        result = []
        for cashbox in cashboxes:
            expenses = Expense.query.filter(
                Expense.user_cashbox_id == cashbox.id,
                Expense.deleted == False,
                Expense.transacted_at >= start_date,
                Expense.transacted_at <= end_date
            ).order_by(Expense.transacted_at.desc()).all()

            result.append({
                "cashbox": UserCashboxSchema().dump(cashbox),
                "expenses": ExpenseSchema(many=True).dump(expenses)
            })

        return result


@api.route('/expense/by_category')
class ExpenseByCategory(Resource):
    """Получение расходов пользователя, сгруппированных по категориям"""

    @jwt_required()
    @api.doc(security='jwt', params={
        'start_date': 'Дата начала периода (YYYY-MM-DD)',
        'end_date': 'Дата конца периода (YYYY-MM-DD)',
    })
    def get(self):
        """Получение списка расходов пользователя, сгруппированных по категориям"""
        from datetime import datetime, timedelta

        user_id = get_jwt_identity()

        # Даты по умолчанию — текущий месяц
        def_start_date = datetime.utcnow().replace(day=1).strftime('%Y-%m-%d')
        def_end_date = ((datetime.utcnow().replace(day=28) + timedelta(days=4)).replace(day=1) - timedelta(seconds=1)).strftime('%Y-%m-%d')

        start_date = request.args.get('start_date', default=def_start_date) + 'T00:00:00.000Z'
        end_date = request.args.get('end_date', default=def_end_date) + 'T23:59:59.999Z'

        from app.schemas.base import DateRangeSchema
        DateRangeSchema().load({'start_date': start_date, 'end_date': end_date})

        # Импорты моделей и схем
        from app.models.auth import UserCashbox
        from app.schemas.settings.categories import CategorySchema

        # Получаем все user_cashbox пользователя
        cashbox_ids = [
            cb.id for cb in UserCashbox.query.filter_by(user_id=user_id, deleted=False).all()
        ]

        # Получаем все доходы за период
        expenses = Expense.query.filter(
            Expense.user_cashbox_id.in_(cashbox_ids),
            Expense.deleted == False,
            Expense.transacted_at >= start_date,
            Expense.transacted_at <= end_date
        ).order_by(Expense.transacted_at.desc()).all()

        # Группируем по категориям
        grouped = {}
        for expense in expenses:
            category = expense.category
            category_data = CategorySchema().dump(category)
            if category.id not in grouped:
                grouped[category.id] = {
                    "category": category_data,
                    "expenses": []
                }
            grouped[category.id]["expenses"].append(ExpenseSchema().dump(expense))

        return list(grouped.values())


@api.route('/expense/by_subcategory')
class ExpenseBySubcategory(Resource):
    """Получение расходов пользователя, сгруппированных по подкатегориям"""

    @jwt_required()
    @api.doc(security='jwt', params={
        'start_date': 'Дата начала периода (YYYY-MM-DD)',
        'end_date': 'Дата конца периода (YYYY-MM-DD)',
    })
    def get(self):
        """Получение расходов пользователя, сгруппированных по подкатегориям"""
        from datetime import datetime, timedelta

        user_id = get_jwt_identity()

        # Даты по умолчанию — текущий месяц
        def_start_date = datetime.utcnow().replace(day=1).strftime('%Y-%m-%d')
        def_end_date = ((datetime.utcnow().replace(day=28) + timedelta(days=4)).replace(day=1) - timedelta(seconds=1)).strftime('%Y-%m-%d')

        start_date = request.args.get('start_date', default=def_start_date) + 'T00:00:00.000Z'
        end_date = request.args.get('end_date', default=def_end_date) + 'T23:59:59.999Z'

        from app.schemas.base import DateRangeSchema
        DateRangeSchema().load({'start_date': start_date, 'end_date': end_date})

        # Импорты
        from app.models.auth import UserCashbox
        from app.schemas.settings.categories import SubcategorySchema

        # Получаем user_cashbox текущего пользователя
        cashbox_ids = [
            cb.id for cb in UserCashbox.query.filter_by(user_id=user_id, deleted=False).all()
        ]

        # Доходы за указанный период
        expenses = Expense.query.filter(
            Expense.user_cashbox_id.in_(cashbox_ids),
            Expense.deleted == False,
            Expense.transacted_at >= start_date,
            Expense.transacted_at <= end_date
        ).order_by(Expense.transacted_at.desc()).all()

        # Группировка по подкатегориям
        grouped = {}
        for expense in expenses:
            subcategory = expense.subcategory
            if not subcategory:
                continue  # на случай, если subcategory_id = None
            subcategory_data = SubcategorySchema().dump(subcategory)
            if subcategory.id not in grouped:
                grouped[subcategory.id] = {
                    "subcategory": subcategory_data,
                    "expenses": []
                }
            grouped[subcategory.id]["expenses"].append(ExpenseSchema().dump(expense))

        return list(grouped.values())


@api.route('/expense/by_category_and_cashbox')
class ExpenseByCategoryAndCashbox(Resource):
    """Группировка доходов по категориям и кэш-боксам"""

    @jwt_required()
    @api.doc(security='jwt', params={
        'start_date': 'Дата начала периода (YYYY-MM-DD)',
        'end_date': 'Дата конца периода (YYYY-MM-DD)',
    })
    def get(self):
        """Группировка доходов по категориям и кэш-боксам"""

        from datetime import datetime, timedelta

        user_id = get_jwt_identity()

        # Даты по умолчанию — текущий месяц
        def_start_date = datetime.utcnow().replace(day=1).strftime('%Y-%m-%d')
        def_end_date = ((datetime.utcnow().replace(day=28) + timedelta(days=4)).replace(day=1) - timedelta(
            seconds=1)).strftime('%Y-%m-%d')

        start_date = request.args.get('start_date', default=def_start_date) + 'T00:00:00.000Z'
        end_date = request.args.get('end_date', default=def_end_date) + 'T23:59:59.999Z'

        from app.schemas.base import DateRangeSchema
        DateRangeSchema().load({'start_date': start_date, 'end_date': end_date})

        # Импорты
        from app.models.auth import UserCashbox
        from app.schemas.auth import UserCashboxSchema
        from app.schemas.settings.categories import CategorySchema

        # Получаем кэш-боксы пользователя
        user_cashboxes = UserCashbox.query.filter_by(user_id=user_id, deleted=False).all()
        cashbox_ids = [cb.id for cb in user_cashboxes]

        expenses = Expense.query.filter(
            Expense.user_cashbox_id.in_(cashbox_ids),
            Expense.deleted == False,
            Expense.transacted_at >= start_date,
            Expense.transacted_at <= end_date
        ).all()

        # Структура: category_id -> {cashbox_id -> сумма}
        from collections import defaultdict

        grouped = defaultdict(lambda: defaultdict(float))
        category_map = {}
        cashbox_map = {cb.id: cb for cb in user_cashboxes}

        for exp in expenses:
            if not exp.category_id or not exp.user_cashbox_id:
                continue
            grouped[exp.category_id][exp.user_cashbox_id] += exp.amount
            category_map[exp.category_id] = exp.category

        result = []
        for cat_id, cashbox_data in grouped.items():
            cat_obj = category_map.get(cat_id)
            result.append({
                "category": CategorySchema().dump(cat_obj),
                "cashboxes": [
                    {
                        "cashbox": UserCashboxSchema().dump(cashbox_map[cid]),
                        "total_amount": round(amount, 2)
                    }
                    for cid, amount in cashbox_data.items()
                ]
            })

        return result


@api.route('/expense/by_subcategory_and_cashbox')
class ExpenseBySubcategoryAndCashbox(Resource):
    """Группировка доходов по подкатегориям и кэш-боксам"""

    @jwt_required()
    @api.doc(security='jwt', params={
        'start_date': 'Дата начала периода (YYYY-MM-DD)',
        'end_date': 'Дата конца периода (YYYY-MM-DD)',
    })
    def get(self):
        """Группировка доходов по подкатегориям и кэш-боксам"""
        from collections import defaultdict
        from datetime import datetime, timedelta

        user_id = get_jwt_identity()

        # Даты по умолчанию — текущий месяц
        def_start_date = datetime.utcnow().replace(day=1).strftime('%Y-%m-%d')
        def_end_date = ((datetime.utcnow().replace(day=28) + timedelta(days=4)).replace(day=1) - timedelta(
            seconds=1)).strftime('%Y-%m-%d')

        start_date = request.args.get('start_date', default=def_start_date) + 'T00:00:00.000Z'
        end_date = request.args.get('end_date', default=def_end_date) + 'T23:59:59.999Z'

        from app.schemas.base import DateRangeSchema
        DateRangeSchema().load({'start_date': start_date, 'end_date': end_date})

        # Импорты
        from app.models.auth import UserCashbox
        from app.schemas.auth import UserCashboxSchema
        from app.schemas.settings.categories import SubcategorySchema

        # Все кэш-боксы пользователя
        user_cashboxes = UserCashbox.query.filter_by(user_id=user_id, deleted=False).all()
        cashbox_ids = [cb.id for cb in user_cashboxes]

        # Все доходы пользователя в выбранный период
        expenses = Expense.query.filter(
            Expense.user_cashbox_id.in_(cashbox_ids),
            Expense.deleted == False,
            Expense.transacted_at >= start_date,
            Expense.transacted_at <= end_date
        ).all()

        grouped = defaultdict(lambda: defaultdict(float))
        subcategory_map = {}
        cashbox_map = {cb.id: cb for cb in user_cashboxes}

        for exp in expenses:
            if not exp.subcategory_id or not exp.user_cashbox_id:
                continue
            grouped[exp.subcategory_id][exp.user_cashbox_id] += exp.amount
            subcategory_map[exp.subcategory_id] = exp.subcategory

        result = []
        for subcat_id, cashbox_data in grouped.items():
            subcat_obj = subcategory_map.get(subcat_id)
            result.append({
                "subcategory": SubcategorySchema().dump(subcat_obj),
                "cashboxes": [
                    {
                        "cashbox": UserCashboxSchema().dump(cashbox_map[cid]),
                        "total_amount": round(amount, 2)
                    }
                    for cid, amount in cashbox_data.items()
                ]
            })

        return result