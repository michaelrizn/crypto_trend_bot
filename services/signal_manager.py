from database.db_handler import insert_signal, update_signal, close_signal, get_active_signals
from services.crypto_api import get_ohlcv, get_current_price
from services.trend_analyzer import analyze_trend, is_trend_still_valid
from utils.time_utils import get_current_time
import logging

def check_and_create_signals(crypto_pairs):
    logging.info("Проверка и создание новых сигналов.")
    for pair in crypto_pairs:
        logging.info(f"Проверка пары: {pair}")
        ohlcv = get_ohlcv(pair)
        trend, accuracy = analyze_trend(ohlcv)
        if trend:
            logging.info(f"Обнаружен новый тренд для пары {pair}: {trend} с точностью {accuracy}.")
            current_price = get_current_price(pair)
            current_time = get_current_time()
            insert_signal(pair, trend, current_time, current_price, accuracy)

def update_active_signals():
    logging.info("Обновление активных сигналов.")
    active_signals = get_active_signals()
    for signal in active_signals:
        pair = signal[1]
        logging.info(f"Актуализация сигнала для пары: {pair}")
        ohlcv = get_ohlcv(pair)
        if is_trend_still_valid(ohlcv, signal[2]):
            logging.info(f"Сигнал для пары {pair} всё ещё актуален.")
            current_price = get_current_price(pair)
            current_time = get_current_time()
            _, accuracy = analyze_trend(ohlcv)
            update_signal(pair, current_time, current_price, accuracy)
        else:
            logging.info(f"Сигнал для пары {pair} больше не актуален.")
            current_price = get_current_price(pair)
            current_time = get_current_time()
            close_signal(pair, current_time, current_price)