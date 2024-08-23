from database.db_handler import insert_signal, update_signal, close_signal, get_active_signals, get_active_signal
from services.crypto_api import get_ohlcv, get_current_price
from services.trend_analyzer import analyze_trend, is_trend_still_valid
from utils.time_utils import get_current_time
from database.models import Signal
from utils.logger import analyze_logger, general_logger
import asyncio

async def check_and_create_signals(crypto_pairs):
    general_logger.info("Проверка и создание новых сигналов.")
    analyze_logger.info("Начало процесса проверки и создания сигналов")
    new_signals = []
    updated_signals = []
    closed_signals = []

    for pair in crypto_pairs:
        analyze_logger.info(f"Анализ пары: {pair}")
        ohlcv = await get_ohlcv(pair)
        if ohlcv:
            trend, accuracy, forecast = analyze_trend(ohlcv)
            existing_signal = get_active_signal(pair)
            current_price = await get_current_price(pair)
            current_time = get_current_time()

            if existing_signal:
                if existing_signal.trend == trend:
                    update_signal(pair, current_time, current_price, accuracy, forecast)
                    updated_signals.append(existing_signal)
                    analyze_logger.info(f"Обновлен существующий сигнал для пары {pair}: {trend} с точностью {accuracy}")
                else:
                    close_signal(pair, current_time, current_price)
                    closed_signals.append(existing_signal)
                    insert_signal(pair, trend, current_time, current_price, accuracy, forecast)
                    new_signal = get_active_signal(pair)
                    new_signals.append(new_signal)
                    analyze_logger.info(f"Закрыт старый сигнал и создан новый для пары {pair}: {trend} с точностью {accuracy}")
            else:
                insert_signal(pair, trend, current_time, current_price, accuracy, forecast)
                new_signal = get_active_signal(pair)
                new_signals.append(new_signal)
                analyze_logger.info(f"Создан новый сигнал для пары {pair}: {trend} с точностью {accuracy}")
        else:
            analyze_logger.warning(f"Не удалось получить данные OHLCV для пары {pair}. Пропуск.")

    analyze_logger.info("Завершение процесса проверки и создания сигналов")
    return new_signals, updated_signals, closed_signals

async def update_active_signals():
    general_logger.info("Обновление активных сигналов.")
    analyze_logger.info("Начало обновления активных сигналов")
    active_signals = get_active_signals()
    for signal in active_signals:
        pair = signal.name
        analyze_logger.info(f"Обновление сигнала для пары: {pair}")
        ohlcv = await get_ohlcv(pair)
        if ohlcv:
            if is_trend_still_valid(ohlcv, signal.trend):
                analyze_logger.info(f"Сигнал для пары {pair} все еще актуален")
                current_price = await get_current_price(pair)
                current_time = get_current_time()
                _, accuracy, forecast = analyze_trend(ohlcv)
                update_signal(pair, current_time, current_price, accuracy, forecast)
            else:
                analyze_logger.info(f"Сигнал для пары {pair} больше не актуален")
                current_price = await get_current_price(pair)
                current_time = get_current_time()
                close_signal(pair, current_time, current_price)
        else:
            analyze_logger.warning(f"Не удалось получить данные OHLCV для пары {pair}. Пропуск.")
    analyze_logger.info("Завершение обновления активных сигналов")

async def update_signal_in_db(signal):
    try:
        existing_signal = get_active_signal(signal.name)
        if existing_signal:
            update_signal(signal.name, signal.date_last, signal.price_last, signal.accuracy, signal.forecast)
            analyze_logger.info(f"Обновлен сигнал в базе данных: ID {signal.id}, тренд {signal.trend}, точность {signal.accuracy}")
        else:
            analyze_logger.error(f"Сигнал с ID {signal.id} не найден в базе данных.")
    except Exception as e:
        analyze_logger.error(f"Ошибка при обновлении сигнала в базе данных: {e}")