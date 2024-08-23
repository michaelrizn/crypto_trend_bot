from datetime import datetime
from utils.time_utils import format_date, calculate_time_difference
from config import TIMEZONE
from pytz import timezone
from utils.logger import general_logger

def add_timestamp_and_separator(message):
    current_time = datetime.now(timezone(TIMEZONE)).strftime("%Y-%m-%d %H:%M")
    separator = "-" * 40
    return f"{current_time}\n{separator}\n{message}"

def format_new_signal_message(signal, is_new=False):
    status = "New signal" if signal.count_sends == 0 else "Actual"

    trend_emoji = get_trend_emoji(signal.trend)
    forecast_emoji = get_forecast_emoji(signal.forecast)

    price_change = ((signal.price_last - signal.price_start) / signal.price_start) * 100
    price_change_str = f"{'+' if price_change > 0 else '-'}{abs(price_change):.2f}%"

    general_logger.info(
        f"Formatting signal: {signal.name}, Count Sends: {signal.count_sends}, Status: {status}"
    )

    return (
        f"{trend_emoji} {status}: {signal.name} {signal.trend.upper()} Accuracy: {signal.accuracy}\n"
        f"Start: {format_date(signal.date_start)} Price: {signal.price_start}\n"
        f"Current: {format_date(signal.date_last)} Price: {signal.price_last}\n"
        f"Price change: {price_change_str}\n"
        f"Forecast: {forecast_emoji} {signal.forecast.capitalize()}"
    )

def format_closed_signal_message(signal):
    trend_emoji = get_trend_emoji(signal.trend)

    price_change = ((signal.price_end - signal.price_start) / signal.price_start) * 100
    price_change_str = f"{'+' if price_change > 0 else '-'}{abs(price_change):.2f}%"

    return (
        f"❌ Closed signal: {signal.name} {trend_emoji} {signal.trend.upper()}\n"
        f"Start: {format_date(signal.date_start)} Price: {signal.price_start}\n"
        f"End: {format_date(signal.date_end)} Price: {signal.price_end}\n"
        f"Price change: {price_change_str}\n"
        f"Total duration: {calculate_time_difference(signal.date_start, signal.date_end)}"
    )

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
            f"Forecast: {signal[12]}\n"
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
