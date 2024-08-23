from datetime import datetime
from utils.time_utils import format_date, calculate_time_difference
from config import TIMEZONE
from pytz import timezone
from utils.logger import general_logger

import datetime

def add_timestamp_and_separator(message):
    current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
    separator = "============================"
    return f"{separator}\n{current_time}\n{separator}\n{message}"

def format_new_signal_message(signal, is_new=False):
    status = "Новый сигнал" if signal.count_sends == 0 else "Актуальный"

    trend_emoji = get_trend_emoji(signal.trend)
    forecast_emoji = get_forecast_emoji(signal.forecast)

    price_change = signal.price_last - signal.price_start
    price_change_percent = (price_change / signal.price_start) * 100
    price_change_str = f"{'+' if price_change > 0 else '-'}${abs(price_change):.2f} ({'+' if price_change_percent > 0 else '-'}{abs(price_change_percent):.2f}%)"

    general_logger.info(
        f"Форматирование сигнала: {signal.name}, Количество отправок: {signal.count_sends}, Статус: {status}"
    )

    return (
        f"{trend_emoji} {status}: {signal.name} {translate_trend(signal.trend).upper()} Точность: {signal.accuracy}\n"
        f"Начало: {format_date(signal.date_start)} Цена: ${signal.price_start:.2f}\n"
        f"Текущая: {format_date(signal.date_last)} Цена: ${signal.price_last:.2f}\n"
        f"Изменение цены: {price_change_str}\n"
        f"Прогноз: {forecast_emoji} {translate_forecast(signal.forecast).capitalize()}"
    )

def format_closed_signal_message(signal):
    trend_emoji = get_trend_emoji(signal.trend)

    price_change = signal.price_end - signal.price_start
    price_change_percent = (price_change / signal.price_start) * 100
    price_change_str = f"{'+' if price_change > 0 else '-'}${abs(price_change):.2f} ({'+' if price_change_percent > 0 else '-'}{abs(price_change_percent):.2f}%)"

    return (
        f"❌ Закрытый сигнал: {signal.name} {trend_emoji} {translate_trend(signal.trend).upper()}\n"
        f"Начало: {format_date(signal.date_start)} Цена: ${signal.price_start:.2f}\n"
        f"Окончание: {format_date(signal.date_end)} Цена: ${signal.price_end:.2f}\n"
        f"Изменение цены: {price_change_str}\n"
        f"Общая продолжительность: {calculate_time_difference(signal.date_start, signal.date_end)}"
    )

def format_signals_table(signals):
    formatted_signals = []

    for signal in signals:
        price_end = f"${signal[9]:.2f}" if signal[9] is not None else "N/A"
        formatted_signal = (
            f"ID: {signal[0]}\n"
            f"Название: {signal[1]}\n"
            f"Тренд: {translate_trend(signal[2])}\n"
            f"Дата начала: {signal[3]}\n"
            f"Последняя дата: {signal[4]}\n"
            f"Точность: {signal[5]}\n"
            f"Дата окончания: {signal[6]}\n"
            f"Начальная цена: ${signal[7]:.2f}\n"
            f"Последняя цена: ${signal[8]:.2f}\n"
            f"Цена при закрытии: {price_end}\n"
            f"Количество отправок: {signal[10]}\n"
            f"Отмечено: {signal[11]}\n"
            f"Прогноз: {translate_forecast(signal[12])}\n"
            "----------------------"
        )
        formatted_signals.append(formatted_signal)

    return "\n".join(formatted_signals)

def get_trend_emoji(trend):
    trend_emojis = {
        "bullish": "🐂",
        "bearish": "🐻",
        "neutral": "➡️",
        "sideways": "↔️",
        "overbought": "🔥",
        "oversold": "🧊",
        "short_term_bullish": "📈",
        "short_term_bearish": "📉",
    }
    return trend_emojis.get(trend.lower(), "⚪️")

def get_forecast_emoji(forecast):
    forecast_emojis = {
        "upward": "🚀",
        "downward": "🔻",
        "stable": "➖"
    }
    return forecast_emojis.get(forecast.lower(), "❓")

def translate_trend(trend):
    trend_translations = {
        "bullish": "бычий",
        "bearish": "медвежий",
        "neutral": "нейтральный",
        "sideways": "боковой",
        "overbought": "перекупленность",
        "oversold": "перепроданность",
        "short_term_bullish": "краткосрочный бычий",
        "short_term_bearish": "краткосрочный медвежий",
    }
    return trend_translations.get(trend.lower(), trend)

def translate_forecast(forecast):
    forecast_translations = {
        "upward": "восходящий",
        "downward": "нисходящий",
        "stable": "стабильный"
    }
    return forecast_translations.get(forecast.lower(), forecast)