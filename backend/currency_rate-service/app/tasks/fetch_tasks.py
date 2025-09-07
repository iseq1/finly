from celery_app import celery
from app.services.currency_rate_service import CurrencyRatesService
from dotenv import load_dotenv
import os

load_dotenv()

@celery.task(name="app.tasks.fetch_tasks.get_rate")
def get_rate(base: str, target: str, type: str):
    service = CurrencyRatesService(
        acb_api_key=os.getenv("EXCHANGE_RATES_SECRET_KEY"),
        ecb_api_key=os.getenv("CURRENCY_LAYER_SECRET_KEY")
    )
    rate = service.get_rate(base, target, type)

    if rate:
        # print(f"[get_rate] Успешно получен курс: {rate}")
        return rate
    else:
        print("[get_rate] Не удалось получить курс")
        return {"error": "No rate found"}

