"""
Класс для получения информации о курсе валют посредством Binance
"""
import requests
from decimal import Decimal
from datetime import datetime
from app.services.sources.base import CurrencyRateSource


class BinanceSource(CurrencyRateSource):
    """
    Источник данных о курсах криптовалют с сайта Binance
    """

    BASE_URL = "https://api.binance.com/api/v3/ticker/price"
    NAME = "Binance"

    def get_rate(self, base_currency: str, target_currency: str) -> dict[str, str | Decimal | datetime] | None:
        """
        Получить курс валют с Binance

        :param base_currency: Валюта, из которой конвертируем (например, BTC)
        :param target_currency: Валюта, в которую конвертируем (например, USDT)
        :return: Словарь с полями base_currency, target_currency, rate, timestamp, source
        """
        try:
            base = base_currency.upper().strip()
            target = target_currency.upper().strip()
            symbol = f"{base}{target}"
            response = requests.get(f'{self.BASE_URL}?symbol={symbol}', timeout=5)
            response.raise_for_status()
            data = response.json()

            if "code" in data:
                print(f"[{self.NAME}] Неверный символ {symbol}: {data.get('msg')}")
                return None

            return {
                "base_currency": base,
                "target_currency": target,
                "rate": Decimal(str(data["price"])),
                "type": 'crypto',
                "timestamp": datetime.utcnow(),
                "source": self.NAME
            }

        except (requests.RequestException, KeyError, ValueError) as e:
            # Тут ты можешь логировать ошибку
            print(f"[{self.NAME}] Ошибка получения курса: {e}")
            return None