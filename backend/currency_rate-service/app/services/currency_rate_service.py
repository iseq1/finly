"""
Сервис, собирающий актуальную информацию о крипто- и фиатной валюте
"""
from app.services.sources.binance import BinanceSource
from app.services.sources.coin_gecko import CoinGeckoSource
from app.services.sources.acb import ACBSource
from app.services.sources.ecb import ECBSource
from app.services.sources.cbr import CBRSource
from typing import Optional, Dict, Union
from datetime import datetime
from decimal import Decimal

class CurrencyRatesService:
    """
    Сервис для получения курса валют с цепочкой источников (fallback)
    """

    def __init__(self, acb_api_key=None, ecb_api_key=None):
        self.fiat_sources = []
        self.crypto_sources = []

        # Инициализация источников в порядке приоритета
        self.fiat_sources.append(CBRSource())
        self.crypto_sources.append(BinanceSource())

        if ecb_api_key:
            self.fiat_sources.append(ECBSource(api_key=ecb_api_key))
        else:
            print("[ECBSource] Warning: ECB API key not provided")

        if acb_api_key:
            self.fiat_sources.append(ACBSource(api_key=acb_api_key))
        else:
            print("[ACBSource] Warning: ACB API key not provided")

        self.crypto_sources.append(CoinGeckoSource())

    def get_rate(self, base_currency: str, target_currency: str, type_currency: str) -> Optional[Dict[str, Union[str, Decimal, datetime]]]:
        """
        Пробуем получить курс валюты по цепочке источников.
        Если один источник не отвечает — идем дальше.
        Возвращаем первый успешно полученный курс.

        :param type_currency: Тип валюты (fiat / crypto)
        :param base_currency: Валюта, из которой конвертируем (USD)
        :param target_currency: Валюта, в которую конвертируем (например, RUB)
        :return: dict с полями base_currency, target_currency, rate, timestamp, source

        """

        if type_currency == 'fiat':
            for source in self.fiat_sources:
                try:
                    rate_info = source.get_rate(base_currency, target_currency)
                    if rate_info is not None:
                        return rate_info
                except Exception as e:
                    print(f"[{self.__class__.__name__}] Ошибка в источнике {source.NAME}: {e}")
                    continue
        elif type_currency == 'crypto':
            for source in self.crypto_sources:
                try:
                    rate_info = source.get_rate(base_currency, target_currency)
                    if rate_info is not None:
                        return rate_info
                except Exception as e:
                    print(f"[{self.__class__.__name__}] Ошибка в источнике {source.NAME}: {e}")
                    continue
        else:
            print(f"[{self.__class__.__name__}] Некорректное указание типа валюты")

        # Если ни один источник не вернул курс — возвращаем None
        print(f"[{self.__class__.__name__}] Не удалось получить курс по цепочке источников")
        return None