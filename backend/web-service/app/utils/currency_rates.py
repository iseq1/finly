import aiohttp
import asyncio
import json
from datetime import datetime, timedelta

class CurrencyRateProvider:
    def __init__(self):
        self._cache = {}
        self._cache_expiry = None
        self._main_fiat_currencies = ['USD', 'EUR', 'GBP', 'CHF', 'CNY', 'JPY', 'KZT', 'BYN', 'UAH']
        self._crypto_pairs = {
            'BTC': 'BTCUSDT',
            'ETH': 'ETHUSDT',
            'TON': 'TONUSDT',
            'SOL': 'SOLUSDT',
            'LTC': 'LTCUSDT',
            'XRP': 'XRPUSDT',
            'DOGE': 'DOGEUSDT',
            'ADA': 'ADAUSDT',
            'DOT': 'DOTUSDT',
            'TRX': 'TRXUSDT',
        }

    async def get_rates(self):
        if self._cache and self._cache_expiry and datetime.now() < self._cache_expiry:
            return self._cache

        rates = {'RUB': 1.0}

        try:
            async with aiohttp.ClientSession() as session:
                # --- ЦБ РФ: Фиат ---
                async with session.get("https://www.cbr-xml-daily.ru/daily_json.js") as resp:
                    text = await resp.text()
                    data = json.loads(text)
                    valutes = data.get("Valute", {})

                    for code in self._main_fiat_currencies:
                        if code in valutes:
                            rates[code] = valutes[code]['Value']

                usd_to_rub = rates.get('USD', 90)

                # --- Binance: Криптовалюты ---
                binance_url = "https://api.binance.com/api/v3/ticker/price"

                for symbol, pair in self._crypto_pairs.items():
                    async with session.get(f"{binance_url}?symbol={pair}") as resp:
                        if resp.status != 200:
                            print(f"[Binance] Error {resp.status} for {pair}")
                            continue

                        crypto_data = await resp.json()
                        if 'price' not in crypto_data:
                            print(f"[Binance] No 'price' for {symbol} ({pair}): {crypto_data}")
                            continue
                        usdt_price = float(crypto_data['price'])  # цена в USDT
                        rub_price = usdt_price * usd_to_rub
                        rates[symbol] = rub_price


                # --- Специальные валюты ---
                rates['USDT'] = usd_to_rub
                rates['SBRS'] = 1.0

            # Кэшируем на 1 час
            self._cache = rates
            self._cache_expiry = datetime.now() + timedelta(hours=1)

        except Exception as e:
            print(f"[CurrencyRateProvider] Error fetching rates: {e}")
            rates.update({
                'USD': 90, 'EUR': 98, 'GBP': 115, 'CHF': 105, 'CNY': 12.5,
                'JPY': 0.6, 'KZT': 0.2, 'BYN': 28, 'UAH': 2.4,
                'SBRS': 1, 'BTC': 5000000, 'ETH': 300000,
                'TON': 200, 'SOL': 9000, 'LTC': 7000, 'XRP': 50,
                'DOGE': 10, 'ADA': 40, 'DOT': 500, 'TRX': 8
            })

        return rates
