import ccxt
from config import EXCHANGE_API_KEY, EXCHANGE_SECRET
import numpy as np

exchange = ccxt.binance({
    'apiKey': EXCHANGE_API_KEY,
    'secret': EXCHANGE_SECRET
})

async def get_ohlcv(pair):
    try:
        ohlcv = exchange.fetch_ohlcv(pair, timeframe='1h', limit=48)
        ohlcv_array = np.array(ohlcv)
        return {
            'timestamp': ohlcv_array[:, 0],
            'open': ohlcv_array[:, 1],
            'high': ohlcv_array[:, 2],
            'low': ohlcv_array[:, 3],
            'close': ohlcv_array[:, 4],
            'volume': ohlcv_array[:, 5]
        }
    except Exception as e:
        print(f"Ошибка при получении данных OHLCV для пары {pair}: {e}")
        return None

async def get_current_price(pair):
    try:
        ticker = exchange.fetch_ticker(pair)
        return ticker['close']
    except Exception as e:
        print(f"Ошибка при получении текущей цены для пары {pair}: {e}")
        return None