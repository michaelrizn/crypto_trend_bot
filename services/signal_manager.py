from database.db_handler import insert_signal, update_signal, close_signal, get_active_signals, \
    get_active_signal
from services.crypto_api import get_ohlcv, get_current_price
from services.trend_analyzer import analyze_trend, is_trend_still_valid
from utils.time_utils import get_current_time
from database.models import Signal
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
import logging

# Assuming SQLAlchemy is used, initialize the sessionmaker
engine = create_engine('sqlite:///path_to_your_db.sqlite')  # Replace with your actual database URL
Session = sessionmaker(bind=engine)
session = Session()

async def check_and_create_signals(crypto_pairs):
    logging.info("Проверка и создание новых сигналов.")
    new_signals = []
    updated_signals = []
    closed_signals = []

    for pair in crypto_pairs:
        logging.info(f"Проверка пары: {pair}")
        ohlcv = await get_ohlcv(pair)
        if ohlcv:
            trend, accuracy = analyze_trend(ohlcv)
            existing_signal = get_active_signal(pair)
            current_price = await get_current_price(pair)
            current_time = get_current_time()

            if existing_signal:
                if existing_signal.trend == trend:
                    update_signal(pair, current_time, current_price, accuracy)
                    updated_signals.append(existing_signal)
                    logging.info(
                        f"Обновлен существующий сигнал для пары {pair}: {trend} с точностью {accuracy}.")
                else:
                    close_signal(pair, current_time, current_price)
                    closed_signals.append(existing_signal)
                    insert_signal(pair, trend, current_time, current_price, accuracy)
                    new_signal = get_active_signal(pair)
                    new_signals.append(new_signal)
                    logging.info(
                        f"Закрыт старый сигнал и создан новый для пары {pair}: {trend} с точностью {accuracy}.")
            else:
                insert_signal(pair, trend, current_time, current_price, accuracy)
                new_signal = get_active_signal(pair)
                new_signals.append(new_signal)
                logging.info(
                    f"Создан новый сигнал для пары {pair}: {trend} с точностью {accuracy}.")
        else:
            logging.warning(f"Не удалось получить данные OHLCV для пары {pair}. Пропуск.")

    return new_signals, updated_signals, closed_signals


def update_active_signals():
    logging.info("Обновление активных сигналов.")
    active_signals = get_active_signals()
    for signal in active_signals:
        pair = signal.name
        logging.info(f"Актуализация сигнала для пары: {pair}")
        ohlcv = get_ohlcv(pair)
        if ohlcv:
            if is_trend_still_valid(ohlcv, signal.trend):
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
        else:
            logging.warning(f"Не удалось получить данные OHLCV для пары {pair}. Пропуск.")


async def update_signal_in_db(signal):
    try:
        existing_signal = session.query(Signal).get(signal.id)
        if existing_signal:
            existing_signal.trend = signal.trend
            existing_signal.accuracy = signal.accuracy
            existing_signal.close_value = signal.close_value
            session.commit()
        else:
            logging.error(f"Сигнал с ID {signal.id} не найден в базе данных.")
    except Exception as e:
        logging.error(f"Ошибка при обновлении сигнала в базе данных: {e}")