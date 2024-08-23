import mplfinance as mpf
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
import io
from services.trend_analyzer import determine_trend, generate_forecast

def generate_chart(ohlcv_data, trend, signal_start_date=None, signal_end_date=None):
    df = pd.DataFrame(ohlcv_data, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
    df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
    df.set_index('timestamp', inplace=True)

    if len(df) < 48:
        raise ValueError("Insufficient data to compute indicators")

    df['MA20'] = df['close'].rolling(window=20).mean()
    df['MA50'] = df['close'].rolling(window=50).mean()
    df['EMA20'] = df['close'].ewm(span=20, adjust=False).mean()
    df['BB_upper'] = df['MA20'] + 2 * df['close'].rolling(window=20).std()
    df['BB_lower'] = df['MA20'] - 2 * df['close'].rolling(window=20).std()

    trend = determine_trend(df)
    forecast = generate_forecast(df)

    mc = mpf.make_marketcolors(up='g', down='r', inherit=True)
    s = mpf.make_mpf_style(marketcolors=mc)

    apds = []

    if not df['MA20'].isnull().all():
        apds.append(mpf.make_addplot(df['MA20'], color='blue', width=1))
    if not df['MA50'].isnull().all():
        apds.append(mpf.make_addplot(df['MA50'], color='red', width=1))
    if not df['EMA20'].isnull().all():
        apds.append(mpf.make_addplot(df['EMA20'], color='purple', width=1))
    if not df['BB_upper'].isnull().all():
        apds.append(mpf.make_addplot(df['BB_upper'], color='green', linestyle='--'))
    if not df['BB_lower'].isnull().all():
        apds.append(mpf.make_addplot(df['BB_lower'], color='green', linestyle='--'))

    if signal_start_date:
        signal_start = datetime.fromisoformat(signal_start_date)
        if signal_start.tzinfo is not None:
            signal_start = signal_start.replace(tzinfo=None)
        signal_start_index = df.index.get_indexer([signal_start], method='nearest')[0]
        signal_start_series = pd.Series([np.nan] * len(df), index=df.index)
        signal_start_series.iloc[signal_start_index] = df['high'].max() * 1.02
        marker = get_trend_marker(trend)
        apds.append(mpf.make_addplot(signal_start_series, type='scatter', markersize=100, marker=marker['shape'], color=marker['color']))

    # Add forecast arrow
    forecast_arrow = pd.Series([np.nan] * len(df), index=df.index)
    forecast_arrow.iloc[-1] = df['close'].iloc[-1]
    forecast_color = 'g' if forecast == 'upward' else 'r' if forecast == 'downward' else 'gray'
    apds.append(mpf.make_addplot(forecast_arrow, type='scatter', markersize=200, marker='$→$', color=forecast_color))

    fig, axes = mpf.plot(df, type='candle', style=s, addplot=apds,
                         title=f'Trend: {trend.capitalize()}, Forecast: {forecast.capitalize()}',
                         ylabel='Price',
                         datetime_format='%Y-%m-%d %H:%M',
                         figsize=(12, 8),
                         returnfig=True)

    buf = io.BytesIO()
    plt.savefig(buf, format='png', dpi=100, bbox_inches='tight')
    buf.seek(0)
    plt.close(fig)

    return buf

def get_trend_marker(trend):
    markers = {
        'bullish': {'shape': '^', 'color': 'g'},
        'bearish': {'shape': 'v', 'color': 'r'},
        'sideways': {'shape': 'o', 'color': 'gray'},
        'overbought': {'shape': 'd', 'color': 'purple'},
        'oversold': {'shape': 'd', 'color': 'orange'},
        'short_term_bullish': {'shape': '>', 'color': 'lime'},
        'short_term_bearish': {'shape': '<', 'color': 'pink'}
    }
    return markers.get(trend.lower(), {'shape': 'o', 'color': 'gray'})