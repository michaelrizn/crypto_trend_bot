import ccxt.async_support as ccxt
from config import EXCHANGE_API_KEY, EXCHANGE_SECRET

exchange = ccxt.binance({
    'apiKey': EXCHANGE_API_KEY,
    'secret': EXCHANGE_SECRET,
})

async def get_ohlcv(symbol, timeframe='1h', limit=48):
    try:
        ohlcv = await exchange.fetch_ohlcv(symbol, timeframe, limit=limit)
        await exchange.close()  # Важно закрыть соединение после использования
        return ohlcv
    except Exception as e:
        print(f"Error fetching OHLCV data: {e}")
        await exchange.close()  # Закрываем соединение даже в случае ошибки
        return None

async def get_current_price(symbol):
    try:
        ticker = await exchange.fetch_ticker(symbol)
        await exchange.close()  # Важно закрыть соединение после использования
        return ticker['last']
    except Exception as e:
        print(f"Error fetching current price: {e}")
        await exchange.close()  # Закрываем соединение даже в случае ошибки
        return None