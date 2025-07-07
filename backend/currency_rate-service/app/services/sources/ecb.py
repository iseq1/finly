"""
Класс для получения информации о курсе валют посредством Exchange Rates Data API (Европейский центральный банк)
"""
import requests
from decimal import Decimal, ROUND_HALF_UP
from datetime import datetime
from typing import Optional
from app.services.sources.base import CurrencyRateSource


class ECBSource(CurrencyRateSource):
    """
    Источник данных о курсах валют от Европейского ЦБ
    """

    BASE_URL = "https://api.apilayer.com/exchangerates_data/latest"
    NAME = "ECB"

    def __init__(self, api_key: str):
        self.api_key = api_key

    def get_rate(self, base_currency: str, target_currency: str) -> Optional[dict]:
        """
        Получить курс валют с ЕЦБ

        :param base_currency: Валюта, из которой конвертируем (например, USD)
        :param target_currency: Валюта, в которую конвертируем (например, RUB)
        :return: dict с полями base_currency, target_currency, rate, timestamp, source
        """
        try:
            url = f"{self.BASE_URL}?symbols={target_currency.upper()}&base={base_currency.upper()}"
            headers = {"apikey": self.api_key}
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()
            data = response.json()

            rate = data["rates"][target_currency.upper()]
            return {
                "base_currency": base_currency.upper(),
                "target_currency": target_currency.upper(),
                "rate": Decimal(str(rate)),
                "timestamp": datetime.utcnow(),
                "source": self.NAME
            }
        except (requests.RequestException, KeyError, ValueError) as e:
            print(f"[{self.NAME}] Ошибка получения курса: {e}")
            return None
