from database.db_handler import insert_signal, update_signal, close_signal, get_active_signals, get_active_signal
from services.crypto_api import get_ohlcv, get_current_price
from services.trend_analyzer import analyze_trend, is_trend_still_valid
from utils.time_utils import get_current_time
from database.models import Signal
from utils.logger import analyze_logger, general_logger
import asyncio

async def check_and_create_signals(crypto_pairs):
    general_logger.info("Checking and creating new signals.")
    analyze_logger.info("Starting the process of checking and creating signals")
    new_signals = []
    updated_signals = []
    closed_signals = []

    for pair in crypto_pairs:
        analyze_logger.info(f"Analyzing pair: {pair}")
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
                    analyze_logger.info(f"Updated existing signal for pair {pair}: {trend} with accuracy {accuracy}")
                else:
                    close_signal(pair, current_time, current_price)
                    closed_signals.append(existing_signal)
                    insert_signal(pair, trend, current_time, current_price, accuracy, forecast)
                    new_signal = get_active_signal(pair)
                    new_signals.append(new_signal)
                    analyze_logger.info(f"Closed old signal and created new for pair {pair}: {trend} with accuracy {accuracy}")
            else:
                insert_signal(pair, trend, current_time, current_price, accuracy, forecast)
                new_signal = get_active_signal(pair)
                new_signals.append(new_signal)
                analyze_logger.info(f"Created new signal for pair {pair}: {trend} with accuracy {accuracy}")
        else:
            analyze_logger.warning(f"Failed to get OHLCV data for pair {pair}. Skipping.")

    analyze_logger.info("Finished the process of checking and creating signals")
    return new_signals, updated_signals, closed_signals

async def update_active_signals():
    general_logger.info("Updating active signals.")
    analyze_logger.info("Starting update of active signals")
    active_signals = get_active_signals()
    for signal in active_signals:
        pair = signal.name
        analyze_logger.info(f"Updating signal for pair: {pair}")
        ohlcv = await get_ohlcv(pair)
        if ohlcv:
            if is_trend_still_valid(ohlcv, signal.trend):
                analyze_logger.info(f"Signal for pair {pair} is still valid")
                current_price = await get_current_price(pair)
                current_time = get_current_time()
                _, accuracy, forecast = analyze_trend(ohlcv)
                update_signal(pair, current_time, current_price, accuracy, forecast)
            else:
                analyze_logger.info(f"Signal for pair {pair} is no longer valid")
                current_price = await get_current_price(pair)
                current_time = get_current_time()
                close_signal(pair, current_time, current_price)
        else:
            analyze_logger.warning(f"Failed to get OHLCV data for pair {pair}. Skipping.")
    analyze_logger.info("Finished updating active signals")

async def update_signal_in_db(signal):
    try:
        existing_signal = get_active_signal(signal.name)
        if existing_signal:
            update_signal(signal.name, signal.date_last, signal.price_last, signal.accuracy, signal.forecast)
            analyze_logger.info(f"Updated signal in DB: ID {signal.id}, trend {signal.trend}, accuracy {signal.accuracy}")
        else:
            analyze_logger.error(f"Signal with ID {signal.id} not found in database.")
    except Exception as e:
        analyze_logger.error(f"Error updating signal in database: {e}")