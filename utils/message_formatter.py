from datetime import datetime
from utils.time_utils import format_date, calculate_time_difference


def format_new_signal_message(signal, is_new=False):
    status = "Новый сигнал" if is_new else "Актуально"
    trend_emoji = "🟢" if signal.trend.lower() == "long" else "🔴"
    return f"✅{status}: {signal.name} {trend_emoji} {signal.trend.upper()} Точность: {signal.accuracy}\n" \
           f"Начало: {format_date(signal.date_start)} Цена: {signal.price_start}\n" \
           f"Актуально на: {format_date(signal.date_last)} Цена: {signal.price_last}"


def format_closed_signal_message(signal):
    trend_emoji = "🟢" if signal.trend.lower() == "long" else "🔴"
    price_change = ((signal.price_end - signal.price_start) / signal.price_start) * 100
    price_change_str = f"+{price_change:.2f}%" if price_change >= 0 else f"{price_change:.2f}%"

    return f"❌Сигнал закрыт: {signal.name} {trend_emoji} {signal.trend.upper()}\n" \
           f"Начало: {format_date(signal.date_start)} Цена: {signal.price_start}\n" \
           f"Конец: {format_date(signal.date_end)} Цена: {signal.price_end}\n" \
           f"Изменение цены: {price_change_str}\n" \
           f"Общая длительность: {calculate_time_difference(signal.date_start, signal.date_end)}"


def format_signals_table(signals):
    formatted_signals = []

    for signal in signals:
        formatted_signal = (
            f"ID: {signal[0]}\n"
            f"Name: {signal[1]}\n"
            f"Trend: {signal[2]}\n"
            f"Start Date: {signal[3]}\n"
            f"Last Date: {signal[4]}\n"
            f"Accuracy: {signal[5]}\n"
            f"End Date: {signal[6]}\n"
            f"Start Price: {signal[7]}\n"
            f"Last Price: {signal[8]}\n"
            f"End Price: {signal[9]}\n"
            f"Count Sends: {signal[10]}\n"
            f"Reported: {signal[11]}\n"
            "----------------------"
        )
        formatted_signals.append(formatted_signal)

    return "\n".join(formatted_signals)