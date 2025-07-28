"""
API для управления курсом валют
"""
from collections import defaultdict
from datetime import datetime, timedelta

from flask import request, jsonify
from flask_restx import Resource, fields, Namespace
from flask_jwt_extended import jwt_required, get_jwt_identity
from marshmallow import ValidationError
from app.models.currency_rate import CurrencyRateDaily, CurrencyRateHourly
from app.schemas.currency_rate import CurrencyRateDailySchema, CurrencyRateHourlySchema, CurrencyRateFilterSchema
from app.utils.auth import permission_required
from app.utils.helpers import serialize_value
from app.extensions import db
from app.tasks.fetch_tasks import get_rate


api = Namespace('rate', description='Операции получения транзакций пользователя')

snapshot_model = api.model('Snapshot', {
    'base': fields.String(required=True, description='BASE кэш-бокса'),
    'target': fields.String(required=True, description='Валюта кэш-бокса'),
    'type': fields.String(required=True, description='Валюта кэш-бокса'),
})

@api.route('/test-fetch-rate')
class IncomeList(Resource):
    """Управление записями дохода"""

    # @jwt_required()
    # @api.doc(security='jwt')
    @api.expect(snapshot_model)
    def post(self):
        """Получение списка всех доходов пользователя по кэш-боксам"""
        data = request.json or {}
        base = data.get("base", "USD")
        target = data.get("target", "RUB")
        type = data.get("type", "fiat")

        # Запускаем таску асинхронно
        task = get_rate.delay(base, target, type)

        return jsonify({"message": "Задача отправлена в очередь", "task_id": task.id})


def convert_through_bridge(base, target, type_, model):
    """
    Конвертация через общую таргет-валюту (USD или USDT).
    Ожидается, что в БД все валюты сведены к target = USD/USDT.
    """
    if base == target:
        return None  # Или rate=1.0, если хочешь

    if base == 'USD':
        target_to_usd = model.query.filter_by(
            base_currency=target,
            target_currency='USD',
            type=type_,
            deleted=False
        ).order_by(model.timestamp.desc() if hasattr(model, 'timestamp') else model.date.desc()).first()

        target_time = getattr(target_to_usd, 'timestamp', None) or getattr(target_to_usd, 'date')

        return {
            "base_currency": base,
            "target_currency": target,
            "type": type_,
            "rate": str(round(1/target_to_usd.rate, 6)),
            "timestamp": target_time.isoformat()
        }

    bridge_currency = 'USD' if type_ == 'fiat' else 'USDT'

    # Получаем курс base → USD
    base_to_usd = model.query.filter_by(
        base_currency=base,
        target_currency=bridge_currency,
        type=type_,
        deleted=False
    ).order_by(model.timestamp.desc() if hasattr(model, 'timestamp') else model.date.desc()).first()

    # Получаем курс target → USD
    target_to_usd = model.query.filter_by(
        base_currency=target,
        target_currency=bridge_currency,
        type=type_,
        deleted=False
    ).order_by(model.timestamp.desc() if hasattr(model, 'timestamp') else model.date.desc()).first()

    if base_to_usd and target_to_usd:
        # Вычисляем через отношение к USD
        base_rate = getattr(base_to_usd, 'rate', None) or getattr(base_to_usd, 'avg_rate', None)
        target_rate = getattr(target_to_usd, 'rate', None) or getattr(target_to_usd, 'avg_rate', None)

        rate = base_rate / target_rate
        base_time = getattr(base_to_usd, 'timestamp', None) or getattr(base_to_usd, 'date')
        target_time = getattr(target_to_usd, 'timestamp', None) or getattr(target_to_usd, 'date')
        timestamp = max(base_time, target_time)

        return {
            "base_currency": base,
            "target_currency": target,
            "type": type_,
            "rate": str(round(rate, 6)),
            "timestamp": timestamp.isoformat()
        }

    return None


@api.route('/actual')
class ActualRateList(Resource):
    """Управление актуальными курсами валют"""

    @jwt_required()
    @api.doc(security='jwt', params={
        'base': 'Базовая валюта (например, EUR)',
        'target': 'Таргетная валюта (например, RUB)',
        'type': 'Тип валюты: fiat или crypto',
        'timestamp': 'Дата и время (ISO) для запроса почасового курса',
        'date': 'Дата (YYYY-MM-DD) для запроса дневного курса',
        'latest': 'Вернуть последний доступный курс (true/false)'
    })
    def get(self):
        """Получение актуального курса валюты"""
        try:
            filter_schema = CurrencyRateFilterSchema()
            filters = filter_schema.load(request.args)
            base_filter = {
                'deleted': False,
                'base_currency': filters['base'],
                'target_currency': filters['target'],
                'type': filters['type']
            }

            # 1. Если latest=true → просто возвращаем последний hourly → daily
            if filters.get('latest'):
                result = CurrencyRateHourly.query.filter_by(**base_filter) \
                    .order_by(CurrencyRateHourly.timestamp.desc()).first()

                if not result:
                    result = CurrencyRateDaily.query.filter_by(**base_filter) \
                        .order_by(CurrencyRateDaily.date.desc()).first()

                if not result:
                    # fallback через bridge
                    result = convert_through_bridge(filters['base'], filters['target'], filters['type'],
                                                    CurrencyRateHourly)
                    if not result:
                        result = convert_through_bridge(filters['base'], filters['target'], filters['type'],
                                                        CurrencyRateDaily)
                    if not result:
                        return {'message': 'Данные не найдены'}, 404
                    return {'message': 'Получено через промежуточную валюту', 'actual_rate': result}, 200

                schema = CurrencyRateHourlySchema() if isinstance(result,
                                                                  CurrencyRateHourly) else CurrencyRateDailySchema()
                return {
                    "message": 'Актуальный курс успешно получен',
                    "actual_rate": schema.dump(result),
                }, 200

            # 2. timestamp → ищем в пределах часа
            if filters.get('timestamp'):
                if filters.get('date'):
                    raise ValidationError("Укажите либо timestamp, либо date, но не оба.")

                timestamp_dt = datetime.strptime(filters['timestamp'], '%Y-%m-%d %H:%M:%S.%f')
                start_time = timestamp_dt.replace(minute=0, second=0, microsecond=0)
                end_time = start_time + timedelta(hours=1) - timedelta(seconds=1)

                query = CurrencyRateHourly.query.filter_by(**base_filter) \
                    .filter(CurrencyRateHourly.timestamp >= start_time,
                            CurrencyRateHourly.timestamp <= end_time)

                result = query.first()

                # fallback на текущий день
                if not result:
                    result = CurrencyRateHourly.query.filter_by(**base_filter) \
                        .filter(CurrencyRateHourly.timestamp.between(
                            timestamp_dt.replace(hour=0, minute=0, second=0, microsecond=0),
                            timestamp_dt.replace(hour=23, minute=59, second=59, microsecond=999999)
                        )).order_by(CurrencyRateHourly.timestamp.desc()).first()

                # fallback на daily
                if not result:
                    result = CurrencyRateDaily.query.filter_by(**base_filter, date=timestamp_dt.date()).first()

                # fallback через bridge
                if not result:
                    result = convert_through_bridge(filters['base'], filters['target'], filters['type'], CurrencyRateHourly)
                    if not result:
                        result = convert_through_bridge(filters['base'], filters['target'], filters['type'], CurrencyRateDaily)
                    if not result:
                        return {'message': 'Данные по заданному времени не найдены'}, 404
                    return {'message': 'Получено через промежуточную валюту', 'actual_rate': result}, 200

                schema = CurrencyRateHourlySchema() if isinstance(result, CurrencyRateHourly) else CurrencyRateDailySchema()
                return {
                    "message": 'Актуальный курс успешно получен',
                    "actual_rate": schema.dump(result),
                }, 200

            # 3. date → ищем дневной курс
            if filters.get('date'):
                result = CurrencyRateDaily.query.filter_by(**base_filter, date=filters['date']).first()

                # fallback через bridge
                if not result:
                    result = convert_through_bridge(filters['base'], filters['target'], filters['type'],
                                                    CurrencyRateDaily)
                    if not result:
                        return {'message': 'Данные по заданной дате не найдены'}, 404
                    return {'message': 'Получено через промежуточную валюту', 'actual_rate': result}, 200

                return {
                    "message": 'Актуальный курс успешно получен',
                    "actual_rate": CurrencyRateDailySchema().dump(result),
                }, 200

            return {'message': 'Не указано ни latest, ни timestamp, ни date'}, 400


        except ValidationError as e:
            db.session.rollback()
            return {'message': 'Ошибка валидации фильтров', 'errors': e.messages}, 400

        except Exception as e:
            db.session.rollback()
            return {'message': f'Внутренняя ошибка сервера: {str(e)}'}, 500