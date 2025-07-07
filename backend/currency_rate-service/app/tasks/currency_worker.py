from celery_app import celery
from app.services.currency_rate_service import CurrencyRatesService
from celery.utils.log import get_task_logger
from dotenv import load_dotenv
import os

load_dotenv()
logger = get_task_logger(__name__)


@celery.task(name='fetch_currency_rate')
def fetch_currency_rate(base: str, target: str, type: str):
    try:
        logger.info(f"Запуск задачи получения курса: {base} -> {target} ({type})")
        result = CurrencyRatesService(acb_api_key=os.getenv("EXCHANGE_RATES_SECRET_KEY"), ecb_api_key=os.getenv("CURRENCY_LAYER_SECRET_KEY")).get_rate(base, target, type)

        if result:
            logger.info(f"Курс успешно сохранён: {result}")
            return result
        else:
            logger.warning("Не удалось получить курс из всех источников.")
            return {"error": "No available rate"}

    except Exception as e:
        logger.exception(f"Ошибка при выполнении задачи: {e}")
        return {"error": str(e)}
