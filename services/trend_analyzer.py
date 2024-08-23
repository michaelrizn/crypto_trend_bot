import pandas as pd
import numpy as np
from utils.logger import analyze_logger
from scipy import stats

def analyze_trend(ohlcv_data):
    analyze_logger.info("Starting trend analysis")

    df = pd.DataFrame(ohlcv_data, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
    df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
    df.set_index('timestamp', inplace=True)

    if len(df) < 48:  # Minimum 2 days of hourly data
        analyze_logger.warning("Insufficient data for analysis")
        return 'neutral', 50, None

    df['MA20'] = df['close'].rolling(window=20).mean()
    df['MA50'] = df['close'].rolling(window=50).mean()
    df['EMA20'] = df['close'].ewm(span=20, adjust=False).mean()
    df['BB_upper'] = df['MA20'] + 2 * df['close'].rolling(window=20).std()
    df['BB_lower'] = df['MA20'] - 2 * df['close'].rolling(window=20).std()

    current_trend = determine_trend(df)
    accuracy = calculate_accuracy(df)
    forecast = generate_forecast(df)

    analyze_logger.info(f"Trend: {current_trend}, Accuracy: {accuracy}%, Forecast: {forecast}")

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
            return 'overbought'
        return 'bullish'
    elif close < ma20 and close < ma50 and close < ema20:
        if close < bb_lower:
            return 'oversold'
        return 'bearish'
    elif ma20 > ma50:
        return 'short_term_bullish'
    elif ma20 < ma50:
        return 'short_term_bearish'
    else:
        return 'sideways'

def calculate_accuracy(df):
    close = df['close'].iloc[-1]
    ma20 = df['MA20'].iloc[-1]
    diff = abs(close - ma20)
    max_diff = max(df['close']) - min(df['close'])
    accuracy = int((1 - diff / max_diff) * 100) if max_diff != 0 else 50
    return max(1, min(100, accuracy))

def generate_forecast(df):
    X = np.arange(len(df)).reshape(-1, 1)
    y = df['close'].values

    model = stats.linregress(X.flatten(), y)
    slope = model.slope
    intercept = model.intercept

    next_day = len(df)
    forecast_price = slope * next_day + intercept

    if forecast_price > df['close'].iloc[-1]:
        return 'upward'
    elif forecast_price < df['close'].iloc[-1]:
        return 'downward'
    else:
        return 'stable'

def is_trend_still_valid(ohlcv_data, trend):
    df = pd.DataFrame(ohlcv_data, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
    df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
    df.set_index('timestamp', inplace=True)

    current_trend = determine_trend(df)
    return current_trend == trend