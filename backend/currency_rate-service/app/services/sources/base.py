"""
Базовый класс для источника информации о курсе валют
"""
from abc import ABC, abstractmethod


class CurrencyRateSource(ABC):
    """
    Интерфейс для всех источников информации о курсе валют
    """
    @abstractmethod
    def get_rate(self, base: str, target: str) -> dict:
        """
        Возвращает словарь вида:
        {
            "rate": Decimal,
            "timestamp": datetime,
            "source": str
        }
        """
        pass
