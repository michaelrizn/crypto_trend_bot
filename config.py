import os
from dotenv import load_dotenv

# Загружаем переменные из .env
load_dotenv()

BOT_TOKEN = os.getenv('BOT_TOKEN')
CHANNEL_ID = os.getenv('CHANNEL_ID')
CRYPTO_PAIRS = os.getenv('CRYPTO_PAIRS').split(',')
EXCHANGE_API_KEY = os.getenv('EXCHANGE_API_KEY')
EXCHANGE_SECRET = os.getenv('EXCHANGE_SECRET')
DB_NAME = os.getenv('DB_NAME')
CHECK_INTERVAL = int(os.getenv('CHECK_INTERVAL'))
TIMEZONE = os.getenv('TIMEZONE')

_SEND_ACTUAL_SIGNALS = True

def toggle_actual_signals():
    global _SEND_ACTUAL_SIGNALS
    _SEND_ACTUAL_SIGNALS = not _SEND_ACTUAL_SIGNALS
    return _SEND_ACTUAL_SIGNALS

def get_actual_signals_status():
    return _SEND_ACTUAL_SIGNALS