"""
Класс для получения информации о курсе валют посредством Центрального банка РФ
"""
import requests
from decimal import Decimal, ROUND_HALF_UP
from datetime import datetime, timezone
from typing import Optional
from app.services.sources.base import CurrencyRateSource


class CBRSource(CurrencyRateSource):
    """
    Источник данных о курсах валют с сайта ЦБ РФ
    """

    BASE_URL = "https://www.cbr-xml-daily.ru/daily_json.js"
    NAME = "CBR"

    def get_rate(self, base_currency: str, target_currency: str) -> Optional[dict]:
        """
        Получить курс валют с ЦБ РФ

        :param base_currency: Валюта, из которой конвертируем (например, USD)
        :param target_currency: Валюта, в которую конвертируем (RUB)
        :return: dict с полями base_currency, target_currency, rate, timestamp, source
        """

        base_currency = base_currency.upper()
        target_currency = target_currency.upper()

        # ЦБ РФ работает только с базой RUB
        if base_currency != "RUB" and target_currency != "RUB" and target_currency != "USD":
            return None

        try:
            response = requests.get(self.BASE_URL, timeout=5)
            response.raise_for_status()
            data = response.json()

            valute = data.get("Valute", {})
            timestamp = datetime.now(timezone.utc).isoformat()

            if base_currency == "RUB":
                # RUB -> другая валюта
                target_data = valute.get(target_currency)
                if not target_data:
                    return None
                rate = Decimal(target_data["Nominal"]) / Decimal(target_data["Value"])
            elif target_currency == "RUB":
                # другая валюта -> RUB
                base_data = valute.get(base_currency)
                if not base_data:
                    return None
                rate = Decimal(base_data["Value"]) / Decimal(base_data["Nominal"])
            elif target_currency == "USD":
                # другая валюта -> RUB -> USD
                base_data = valute.get(base_currency)
                if not base_data:
                    return None
                rate_in_rub = Decimal(base_data["Value"]) / Decimal(base_data["Nominal"]) # другая валюта -> RUB
                rate = rate_in_rub / Decimal(valute.get('USD')["Nominal"]) / Decimal(valute.get('USD')["Value"])
            else:
                raise Exception('Некорректно указаны валюты')

            rate = rate.quantize(Decimal("0.000001"), rounding=ROUND_HALF_UP)

            return {
                "base_currency": base_currency,
                "target_currency": target_currency,
                "rate": rate,
                "type": 'fiat',
                "timestamp": timestamp,
                "source": self.NAME
            }

        except (requests.RequestException, KeyError, ValueError) as e:
            # Тут ты можешь логировать ошибку
            print(f"[CBR] Ошибка получения курса: {e}")
            return None
