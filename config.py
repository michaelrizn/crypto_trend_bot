# Токен вашего бота
BOT_TOKEN = "7317150884:AAENXygTDLy3KGvLIh5CgxfqRRS69Rd2I1U"

# ID канала Telegram, куда бот будет отправлять сообщения
CHANNEL_ID = "7317150884"

# Список проверяемых пар
CRYPTO_PAIRS = ["BTC/USDT", "ETH/USDT", "ADA/USDT", "TON/USDT"]

# Настройки API биржи
EXCHANGE_API_KEY = "MWpeIx2bRxJW9igMlA4LDb6i7JovQLM9CYYS5AfbD803JyQhWbPAgi2m9LsBE58k"
EXCHANGE_SECRET = "nxQoPTFVJeR1U6etHoKXtIFbvV5s3nSDOY5579PKVTeHZQcHJw5VZDtJ60JslMBh"

# Настройки базы данных
DB_NAME = "price_trend_db.sqlite"

# Настройки планировщика
CHECK_INTERVAL = 15 * 60  # 1 минута в секундах

# Часовой пояс
TIMEZONE = "Europe/Samara"

_SEND_ACTUAL_SIGNALS = True

def toggle_actual_signals():
    global _SEND_ACTUAL_SIGNALS
    _SEND_ACTUAL_SIGNALS = not _SEND_ACTUAL_SIGNALS
    return _SEND_ACTUAL_SIGNALS

def get_actual_signals_status():
    return _SEND_ACTUAL_SIGNALS