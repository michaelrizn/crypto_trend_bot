import mplfinance as mpf
import pandas as pd
import numpy as np
from datetime import datetime
import matplotlib.pyplot as plt
import io

def find_nearest_index(df, target_time):
    nearest_idx = df.index.get_indexer([target_time], method='nearest')[0]
    return df.index[nearest_idx]

def analyze_trend(df, trend):
    if len(df) == 0:
        return trend

    ma20 = df['MA20'].iloc[-1] if 'MA20' in df.columns and not df['MA20'].isnull().all() else np.nan
    ma50 = df['MA50'].iloc[-1] if 'MA50' in df.columns and not df['MA50'].isnull().all() else np.nan
    ema20 = df['EMA20'].iloc[-1] if 'EMA20' in df.columns and not df['EMA20'].isnull().all() else np.nan
    close = df['close'].iloc[-1] if 'close' in df.columns and not df['close'].isnull().all() else np.nan
    bb_upper = df['BB_upper'].iloc[-1] if 'BB_upper' in df.columns and not df['BB_upper'].isnull().all() else np.nan
    bb_lower = df['BB_lower'].iloc[-1] if 'BB_lower' in df.columns and not df['BB_lower'].isnull().all() else np.nan

    trend_signal = None

    if not np.isnan(close) and not np.isnan(ma20) and not np.isnan(ma50) and not np.isnan(ema20):
        if close > ma20 and close > ma50 and close > ema20:
            trend_signal = 'long'
        elif close < ma20 and close < ma50 and close < ema20:
            trend_signal = 'short'
    if not np.isnan(close) and not np.isnan(bb_upper) and close > bb_upper:
        trend_signal = 'overbought'
    elif not np.isnan(close) and not np.isnan(bb_lower) and close < bb_lower:
        trend_signal = 'oversold'

    return trend_signal if trend_signal else trend

def generate_chart(ohlcv_data, trend, signal_start_date=None, signal_end_date=None):
    df = pd.DataFrame(ohlcv_data, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
    df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
    df.set_index('timestamp', inplace=True)

    if len(df) < 20:
        raise ValueError("Insufficient data to compute indicators")

    df['MA20'] = df['close'].rolling(window=20).mean()
    df['MA50'] = df['close'].rolling(window=50).mean()
    df['EMA20'] = df['close'].ewm(span=20, adjust=False).mean()
    df['BB_upper'] = df['MA20'] + 2 * df['close'].rolling(window=20).std()
    df['BB_lower'] = df['MA20'] - 2 * df['close'].rolling(window=20).std()

    trend = analyze_trend(df, trend)

    mc = mpf.make_marketcolors(up='g', down='r', inherit=True)
    s = mpf.make_mpf_style(marketcolors=mc)

    apds = []

    if 'MA20' in df.columns and not df['MA20'].isnull().all():
        apds.append(mpf.make_addplot(df['MA20'], color='blue', width=1))
    if 'MA50' in df.columns and not df['MA50'].isnull().all():
        apds.append(mpf.make_addplot(df['MA50'], color='red', width=1))
    if 'EMA20' in df.columns and not df['EMA20'].isnull().all():
        apds.append(mpf.make_addplot(df['EMA20'], color='purple', width=1))
    if 'BB_upper' in df.columns and not df['BB_upper'].isnull().all():
        apds.append(mpf.make_addplot(df['BB_upper'], color='green', linestyle='--'))
    if 'BB_lower' in df.columns and not df['BB_lower'].isnull().all():
        apds.append(mpf.make_addplot(df['BB_lower'], color='green', linestyle='--'))

    if signal_start_date:
        signal_start = datetime.fromisoformat(signal_start_date)
        if signal_start.tzinfo is not None:
            signal_start = signal_start.replace(tzinfo=None)
        signal_start_index = df.index.get_indexer([signal_start], method='nearest')[0]
        signal_start_series = pd.Series([np.nan] * len(df), index=df.index)
        if trend.lower() == 'long':
            signal_start_series.iloc[signal_start_index] = df['high'].max() * 1.02
            apds.append(mpf.make_addplot(signal_start_series, type='scatter', markersize=100, marker='^', color='g'))
        elif trend.lower() == 'short':
            signal_start_series.iloc[signal_start_index] = df['high'].max() * 1.02
            apds.append(mpf.make_addplot(signal_start_series, type='scatter', markersize=100, marker='v', color='r'))

    fig, axes = mpf.plot(df, type='candle', style=s, addplot=apds,
                         title=f'Trend: {trend.capitalize()}',
                         ylabel='Price',
                         datetime_format='%Y-%m-%d %H:%M',
                         figsize=(12, 8),
                         returnfig=True)

    buf = io.BytesIO()
    plt.savefig(buf, format='png', dpi=100, bbox_inches='tight')
    buf.seek(0)
    plt.close(fig)

    return buf