import pandas as pd
import numpy as np
from utils.logger import analyze_logger


def analyze_trend(ohlcv_data):
    analyze_logger.info("Начало анализа тренда")

    df = pd.DataFrame(ohlcv_data, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
    df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
    df.set_index('timestamp', inplace=True)

    if len(df) < 20:
        analyze_logger.warning("Недостаточно данных для анализа")
        return 'neutral', 50

    df['MA20'] = df['close'].rolling(window=20).mean()
    df['MA50'] = df['close'].rolling(window=50).mean()
    df['EMA20'] = df['close'].ewm(span=20, adjust=False).mean()
    df['BB_upper'] = df['MA20'] + 2 * df['close'].rolling(window=20).std()
    df['BB_lower'] = df['MA20'] - 2 * df['close'].rolling(window=20).std()

    trend_signal = 'neutral'
    close = df['close'].iloc[-1]
    ma20 = df['MA20'].iloc[-1]
    ma50 = df['MA50'].iloc[-1]
    ema20 = df['EMA20'].iloc[-1]
    bb_upper = df['BB_upper'].iloc[-1]
    bb_lower = df['BB_lower'].iloc[-1]

    if not np.isnan(close) and not np.isnan(ma20) and not np.isnan(ma50) and not np.isnan(ema20):
        if close > ma20 and close > ma50 and close > ema20:
            trend_signal = 'long'
        elif close < ma20 and close < ma50 and close < ema20:
            trend_signal = 'short'

    if not np.isnan(close) and not np.isnan(bb_upper) and close > bb_upper:
        trend_signal = 'overbought'
    elif not np.isnan(close) and not np.isnan(bb_lower) and close < bb_lower:
        trend_signal = 'oversold'

    diff = abs(close - ma20)
    max_diff = max(df['close']) - min(df['close'])
    accuracy = int((1 - diff / max_diff) * 100) if max_diff != 0 else 50
    accuracy = max(1, min(100, accuracy))

    analyze_logger.info(f"Тренд: {trend_signal}, Точность: {accuracy}%")

    return trend_signal, accuracy


def is_trend_still_valid(ohlcv_data, trend):
    df = pd.DataFrame(ohlcv_data, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
    df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
    df.set_index('timestamp', inplace=True)

    ma20 = df['MA20'].iloc[-1] if 'MA20' in df.columns and not df['MA20'].isnull().all() else np.nan

    if trend == "long" and df['close'].iloc[-1] > ma20:
        return True
    elif trend == "short" and df['close'].iloc[-1] < ma20:
        return True
    return False