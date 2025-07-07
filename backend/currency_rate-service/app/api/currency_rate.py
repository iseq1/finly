"""
API для управления курсом валют
"""
from collections import defaultdict
from flask import request, jsonify
from flask_restx import Resource, fields, Namespace
from flask_jwt_extended import jwt_required, get_jwt_identity
from marshmallow import ValidationError
from app.models.currency_rate import CurrencyRateDaily, CurrencyRateHourly
from app.schemas.currency_rate import CurrencyRateDailySchema, CurrencyRateHourlySchema
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
