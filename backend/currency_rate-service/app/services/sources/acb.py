"""
Класс для получения информации о курсе валют посредством CurrencyLayer API (Конгломерат банков Соединенных Штатов Америки)
"""
import requests
from decimal import Decimal, ROUND_HALF_UP
from datetime import datetime
from typing import Optional
from app.services.sources.base import CurrencyRateSource


class ACBSource(CurrencyRateSource):
    """
    Источник данных о курсах валют от сообщества банков Америки
    """

    BASE_URL = "http://api.currencylayer.com/live"
    NAME = "ACB"

    def __init__(self, api_key: str):
        self.api_key = api_key

    def get_rate(self, base_currency: str, target_currency: str) -> Optional[dict]:
        """
        Получить курс валют с АЦБ

        :param base_currency: Валюта, из которой конвертируем (USD)
        :param target_currency: Валюта, в которую конвертируем (например, RUB)
        :return: dict с полями base_currency, target_currency, rate, timestamp, source
        """
        try:
            # CurrencyLayer бесплатный план поддерживает только base=USD
            if base_currency.upper() != "USD":
                print(f"[{self.NAME}] Бесплатный план поддерживает только базу USD")
                return None

            params = {
                "access_key": self.api_key,
                "currencies": target_currency.upper()
            }
            response = requests.get(self.BASE_URL, params=params, timeout=5)
            response.raise_for_status()
            data = response.json()

            if not data.get("success", False):
                print(f"[{self.NAME}] Ошибка API: {data.get('error', {}).get('info')}")
                return None

            rate_key = f"USD{target_currency.upper()}"
            rate = data["quotes"][rate_key]

            return {
                "base_currency": base_currency.upper(),
                "target_currency": target_currency.upper(),
                "rate": Decimal(str(rate)),
                "type": 'fiat',
                "timestamp": datetime.utcnow(),
                "source": self.NAME
            }
        except (requests.RequestException, KeyError, ValueError) as e:
            print(f"[{self.NAME}] Ошибка получения курса: {e}")
            return None
