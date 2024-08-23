import pandas as pd
import numpy as np
from utils.logger import analyze_logger
from scipy import stats

def analyze_trend(ohlcv_data):
    analyze_logger.info("Начало анализа тренда")

    df = pd.DataFrame(ohlcv_data, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
    df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
    df.set_index('timestamp', inplace=True)

    if len(df) < 48:  # Минимум 2 дня данных с часовыми интервалами
        analyze_logger.warning("Недостаточно данных для анализа")
        return 'neutral', 50, None

    df['MA20'] = df['close'].rolling(window=20).mean()
    df['MA50'] = df['close'].rolling(window=50).mean()
    df['EMA20'] = df['close'].ewm(span=20, adjust=False).mean()
    df['BB_upper'] = df['MA20'] + 2 * df['close'].rolling(window=20).std()
    df['BB_lower'] = df['MA20'] - 2 * df['close'].rolling(window=20).std()

    current_trend = determine_trend(df)
    accuracy = calculate_accuracy(df)
    forecast = generate_forecast(df)

    analyze_logger.info(f"Тренд: {current_trend}, Точность: {accuracy}%, Прогноз: {forecast}")

    return current_trend, accuracy, forecast

def determine_trend(df):
    close = df['close'].iloc[-1]
    ma20 = df['MA20'].iloc[-1]
    ma50 = df['MA50'].iloc[-1]
    ema20 = df['EMA20'].iloc[-1]
    bb_upper = df['BB_upper'].iloc[-1]
    bb_lower = df['BB_lower'].iloc[-1]

    if close > ma20 and close > ma50 and close > ema20:
        if close > bb_upper:
            return 'перекупленность'
        return 'бычий'
    elif close < ma20 and close < ma50 and close < ema20:
        if close < bb_lower:
            return 'перепроданность'
        return 'медвежий'
    elif ma20 > ma50:
        return 'краткосрочный бычий'
    elif ma20 < ma50:
        return 'краткосрочный медвежий'
    else:
        return 'боковой'

def calculate_accuracy(df):
    close = df['close'].iloc[-1]
    ma20 = df['MA20'].iloc[-1]
    diff = abs(close - ma20)
    max_diff = max(df['close']) - min(df['close'])
    accuracy = int((1 - diff / max_diff) * 100)
    return accuracy

def generate_forecast(df):
    slope, intercept, r_value, p_value, std_err = stats.linregress(range(len(df['close'])), df['close'])
    forecast = 'upward' if slope > 0 else 'downward' if slope < 0 else 'neutral'
    return forecast

def is_trend_still_valid(ohlcv_data, current_trend):
    df = pd.DataFrame(ohlcv_data, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
    df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
    df.set_index('timestamp', inplace=True)

    if len(df) < 48:  # Минимум 2 дня данных с часовыми интервалами
        return False

    df['MA20'] = df['close'].rolling(window=20).mean()
    df['MA50'] = df['close'].rolling(window=50).mean()
    df['EMA20'] = df['close'].ewm(span=20, adjust=False).mean()
    df['BB_upper'] = df['MA20'] + 2 * df['close'].rolling(window=20).std()
    df['BB_lower'] = df['MA20'] - 2 * df['close'].rolling(window=20).std()

    detected_trend = determine_trend(df)
    return detected_trend == current_trend