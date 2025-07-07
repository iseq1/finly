"""
Модели для курса валют
"""
from sqlalchemy import Column, Integer, String, ForeignKey, Boolean, Float, DateTime, Numeric, Index, UniqueConstraint, Date
from sqlalchemy.orm import relationship
from app.models.base import BaseModel, HistoryModel

class CurrencyRateHourly(BaseModel):
    """
    Модель курса валют в течение дня (с периодичностью в один час)
    """

    __tablename__ = 'currency_rate_hourly'

    base_currency = Column(String(5), nullable=False)  # ISO-код исходной валюты (USD)
    target_currency = Column(String(5), nullable=False)  # ISO-код таргетной валюты
    rate = Column(Numeric(precision=12, scale=6), nullable=False) # Сам курс (например, 90.123456)
    timestamp = Column(DateTime, nullable=False) # Время, когда курс был актуален
    source = Column(String(128), nullable=False) # Наименование источника информации о курсе

    __table_args__ = (
        UniqueConstraint('base_currency', 'target_currency', 'timestamp', 'source', name='uniq_hourly_rate'),
        Index('ix_rate_hourly_base_target_ts', 'base_currency', 'target_currency', 'timestamp'),
    )

    def __repr__(self):
        return f"<CurrencyRateHourly {self.base_currency}/{self.target_currency} @ {self.timestamp} = {self.rate}>"


class CurrencyRateDaily(BaseModel):
    """
    Модель курса валют за день (avg значение за день)
    """
    __tablename__ = 'currency_rate_daily'

    base_currency = Column(String(5), nullable=False)  # ISO-код исходной валюты (USD)
    target_currency = Column(String(5), nullable=False)  # ISO-код базовой валюты
    avg_rate = Column(Numeric(precision=12, scale=6), nullable=False) # Сам курс (например, 90.123456)
    date = Column(Date, nullable=False, index=True) # Дата актуальности курса
    source = Column(String(128), nullable=False) # Наименование источника информации о курсе

    __table_args__ = (
        UniqueConstraint('base_currency', 'target_currency', 'date', name='uniq_rate_daily'),
        Index('ix_rate_daily_base_target_date', 'base_currency', 'target_currency', 'date'),
    )

    def __repr__(self):
        return f"<CurrencyRateDaily {self.base_currency}/{self.target_currency} @ {self.date} = {self.avg_rate}>"
