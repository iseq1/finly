"""
Класс для получения информации о курсе валют посредством CoinGecko
"""
import requests
from decimal import Decimal
from datetime import datetime
from app.services.sources.base import CurrencyRateSource

class CoinGeckoSource(CurrencyRateSource):
    """
    Источник данных о курсах криптовалют с CoinGecko
    """

    BASE_URL = "https://api.coingecko.com/api/v3/simple/price"
    NAME = "CoinGecko"

    def get_rate(self, base_currency: str, target_currency: str) -> dict[str, str | Decimal | datetime] | None:
        """
        Получить курс валют с Binance

        :param base_currency: Валюта, из которой конвертируем (например, BTC)
        :param target_currency: Валюта, в которую конвертируем (например, USDT)
        :return: Словарь с полями base_currency, target_currency, rate, timestamp, source
        """
        try:
            # CoinGecko использует id монеты, например bitcoin → BTC, ethereum → ETH
            base_id = self.map_symbol_to_id(base_currency)
            if not base_id:
                return None
            target_id = self.map_symbol_to_id(target_currency)
            if not target_id:
                return None

            url = f"{self.BASE_URL}?ids={base_id}&vs_currencies={target_id.lower()}"
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            data = response.json()

            rate = data[base_id][target_id.lower()]
            return {
                "base_currency": base_currency,
                "target_currency": target_currency,
                "rate": Decimal(str(rate)),
                "type": 'crypto',
                "timestamp": datetime.utcnow(),
                "source": self.NAME
            }
        except (requests.RequestException, KeyError, ValueError) as e:
            print(f"[{self.NAME}] Ошибка получения курса: {e}")
            return None

    @staticmethod
    def map_symbol_to_id(symbol: str) -> str | None:
        """
        Маппинг тикеров в CoinGecko ID. Можно позже закешировать.
        """
        mapping = {
            "BTC": "bitcoin",
            "ETH": "ethereum",
            "BNB": "binancecoin",
            "USDT": "tether",
            "XRP": "ripple",
            "SOL": "solana",
            "USDC": "usd-coin",
            "TRX": "tron",
            "DOGE": "dogecoin",
            "STETH": "staked-ether",
            "ADA": "cardano",
            "SHIB": "shiba-inu",
            "PEPE": "pepe",
        }
        return mapping.get(symbol.upper())

