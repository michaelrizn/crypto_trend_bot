import ccxt
from config import EXCHANGE_API_KEY, EXCHANGE_SECRET

exchange = ccxt.binance({
    'apiKey': EXCHANGE_API_KEY,
    'secret': EXCHANGE_SECRET,
})

def get_ohlcv(symbol, timeframe='1h', limit=48):
    try:
        ohlcv = exchange.fetch_ohlcv(symbol, timeframe, limit=limit)
        return ohlcv
    except Exception as e:
        print(f"Error fetching OHLCV data: {e}")
        return None

def get_current_price(symbol):
    try:
        ticker = exchange.fetch_ticker(symbol)
        return ticker['last']
    except Exception as e:
        print(f"Error fetching current price: {e}")
        return None