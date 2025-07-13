from celery import Celery
from celery.schedules import crontab
from dotenv import load_dotenv
import os

load_dotenv()

CELERY_ENABLE_UTC = True
CELERY_TIMEZONE = 'Europe/Moscow'  # UTC+3


def make_celery():
    redis_url = os.getenv("REDIS_URL", "redis://localhost:6379/0")
    celery = Celery(
        "currency_rate",
        broker=redis_url,
        backend=redis_url,
        include=["app.tasks.fetch_tasks", "app.tasks.periodic_tasks"],
    )

    celery.conf.timezone = 'Europe/Moscow'  # или 'Europe/Moscow' если нужно
    celery.conf.beat_schedule = {
        # Запускать каждый час, например в 0 минут
        "collect-all-rates-every-hour": {
            "task": "collect_all_rates_task",
            "schedule": crontab(minute=0),
        },
        # Запускать каждый день в 23:55 UTC
        "calculate-daily-average-every-day": {
            "task": "calculate_daily_avg_task",
            "schedule": crontab(hour=23, minute=55),
        },
    }

    return celery


celery = make_celery()
