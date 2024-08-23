import ccxt.async_support as ccxt
from config import EXCHANGE_API_KEY, EXCHANGE_SECRET
from utils.logger import general_logger

exchange = ccxt.binance({
    'apiKey': EXCHANGE_API_KEY,
    'secret': EXCHANGE_SECRET,
})

async def get_ohlcv(symbol, timeframe='1h', limit=48):
    try:
        ohlcv = await exchange.fetch_ohlcv(symbol, timeframe, limit=limit)
        await exchange.close()
        return ohlcv
    except Exception as e:
        general_logger.error(f"Error fetching OHLCV data: {e}")
        await exchange.close()
        return None

async def get_current_price(symbol):
    try:
        ticker = await exchange.fetch_ticker(symbol)
        await exchange.close()
        return ticker['last']
    except Exception as e:
        general_logger.error(f"Error fetching current price: {e}")
        await exchange.close()
        return None