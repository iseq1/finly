from celery import shared_task
from app.services.currency_rate_service import CurrencyRatesService
from app.models.currency_rate import CurrencyRateDaily, CurrencyRateHourly
from app.schemas.currency_rate import CurrencyRateDailySchema, CurrencyRateHourlySchema
from datetime import datetime, timedelta
from app import create_app
from app.extensions import db
from sqlalchemy import func
import os

app = create_app()

# 1. Собираем список валют и криптовалют
FIAT_PAIRS = [
    ("AUD", "USD"), ("AZN", "USD"), ("GBP", "USD"),
    ("AMD", "USD"), ("BYN", "USD"), ("BGN", "USD"),
    ("BRL", "USD"), ("HUF", "USD"), ("VND", "USD"),
    ("HKD", "USD"), ("GEL", "USD"), ("DKK", "USD"),
    ("AED", "USD"), ("EUR", "USD"), ("RUB", "USD"),
    ("EGP", "USD"), ("INR", "USD"), ("IDR", "USD"),
    ("KZT", "USD"), ("CAD", "USD"), ("QAR", "USD"),
    ("KGS", "USD"), ("CNY", "USD"), ("MDL", "USD"),
    ("NZD", "USD"), ("NOK", "USD"), ("PLN", "USD"),
    ("RON", "USD"), ("XDR", "USD"), ("SGD", "USD"),
    ("TJS", "USD"), ("THB", "USD"), ("TRY", "USD"),
    ("TMT", "USD"), ("UZS", "USD"), ("UAH", "USD"),
    ("CZK", "USD"), ("SEK", "USD"), ("CHF", "USD"),
    ("RSD", "USD"), ("ZAR", "USD"), ("KRW", "USD"),
    ("JPY", "USD"),
]
CRYPTO_PAIRS = [
    ("BTC", "USDT"), ("ETH", "USDT"), ("BNB", "USDT"),
    ("XRP", "USDT"), ("SOL", "USDT"), ("USDC", "USDT"),
    ("TRX", "USDT"), ("DOGE", "USDT"), ("STETH", "USDT"),
    ("ADA", "USDT"), ("SHIB", "USDT"), ("PEPE", "USDT"),
    ("TON", "USDT"),
]


@shared_task(name="collect_all_rates_task")
def collect_all_rates_task():
    """
    Таска, которая раз в час собирает все нужные курсы и сохраняет в БД
    """
    with app.app_context():

        print("[collect_all_rates_task] Старт")
        service = CurrencyRatesService(
            acb_api_key=os.getenv("EXCHANGE_RATES_SECRET_KEY"),
            ecb_api_key=os.getenv("CURRENCY_LAYER_SECRET_KEY")
        )

        for base, target in FIAT_PAIRS:
            rate = service.get_rate(base, target, type_currency="fiat")
            if rate:
                if not isinstance(rate['timestamp'], str):
                    rate['timestamp'] = rate['timestamp'].isoformat()
                rate_data = CurrencyRateHourlySchema().load(rate)
                db.session.add(rate_data)

        for base, target in CRYPTO_PAIRS:
            rate = service.get_rate(base, target, type_currency="crypto")
            if rate:
                if not isinstance(rate['timestamp'], str):
                    rate['timestamp'] = rate['timestamp'].isoformat()
                rate_data = CurrencyRateHourlySchema().load(rate)
                db.session.add(rate_data)

        db.session.commit()
        print("[collect_all_rates_task] Завершено")


@shared_task(name="calculate_daily_avg_task")
def calculate_daily_avg_task():
    """
    Считает средние курсы за день и записывает в отдельную таблицу
    """
    with app.app_context():

        print("[calculate_daily_avg_task] Старт")
        today = datetime.utcnow().date()
        start = datetime.combine(today, datetime.min.time())
        end = datetime.combine(today, datetime.max.time())

        # Группируем по валютной паре
        results = (
            db.session.query(
                CurrencyRateHourly.base_currency,
                CurrencyRateHourly.target_currency,
                func.avg(CurrencyRateHourly.rate).label("avg_rate"),
                CurrencyRateHourly.source,
                CurrencyRateHourly.type,
            )
            .filter(CurrencyRateHourly.timestamp >= start, CurrencyRateHourly.timestamp <= end)
            .group_by(CurrencyRateHourly.base_currency, CurrencyRateHourly.target_currency, CurrencyRateHourly.source, CurrencyRateHourly.type)
            .all()
        )

        for row in results:
            avg_data = CurrencyRateDailySchema().load({
                'base_currency': row.base_currency,
                'target_currency': row.target_currency,
                'avg_rate': row.avg_rate,
                'type': row.type,
                'date': today.isoformat(),
                'source': row.source,
            })

            db.session.add(avg_data)

        db.session.commit()
        print("[calculate_daily_avg_task] Завершено")
