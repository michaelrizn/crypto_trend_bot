from database.db_handler import insert_signal, update_signal, close_signal, get_active_signals
from services.crypto_api import get_ohlcv, get_current_price
from services.trend_analyzer import analyze_trend, is_trend_still_valid
from utils.time_utils import get_current_time

def check_and_create_signals(crypto_pairs):
    for pair in crypto_pairs:
        ohlcv = get_ohlcv(pair)
        trend, accuracy = analyze_trend(ohlcv)
        if trend:
            current_price = get_current_price(pair)
            current_time = get_current_time()
            insert_signal(pair, trend, current_time, current_price, accuracy)

def update_active_signals():
    active_signals = get_active_signals()
    for signal in active_signals:
        pair = signal[1]  # Assuming 'name' is the second column
        ohlcv = get_ohlcv(pair)
        if is_trend_still_valid(ohlcv, signal[2]):  # Assuming 'trend' is the third column
            current_price = get_current_price(pair)
            current_time = get_current_time()
            _, accuracy = analyze_trend(ohlcv)
            update_signal(pair, current_time, current_price, accuracy)
        else:
            current_price = get_current_price(pair)
            current_time = get_current_time()
            close_signal(pair, current_time, current_price)

# Добавьте другие необходимые функции для управления сигналами