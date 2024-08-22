import mplfinance as mpf
import pandas as pd
import numpy as np
from datetime import datetime
import matplotlib.pyplot as plt
from scipy.interpolate import make_interp_spline
import io

def find_nearest_index(df, target_time):
    nearest_idx = df.index.get_indexer([target_time], method='nearest')[0]
    return df.index[nearest_idx]

def generate_chart(ohlcv_data, trend, signal_start_date=None, signal_end_date=None):
    df = pd.DataFrame(ohlcv_data, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
    df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
    df.set_index('timestamp', inplace=True)

    # Расчет плавной линии тренда
    x = np.arange(len(df))
    y = df['close'].values

    if len(x) > 3:  # Проверка, что достаточно точек для сглаживания
        x_smooth = np.linspace(x.min(), x.max(), len(x))  # Делаем сглаживание с тем же количеством точек
        spl = make_interp_spline(x, y, k=3)
        y_smooth = spl(x_smooth)
    else:
        x_smooth = x
        y_smooth = y

    # Настройка стиля графика
    mc = mpf.make_marketcolors(up='g', down='r', inherit=True)
    s = mpf.make_mpf_style(marketcolors=mc)

    # Подготовка дополнительных графиков
    apds = [mpf.make_addplot(y_smooth, color='blue', width=1)]

    if signal_start_date:
        signal_start = datetime.fromisoformat(signal_start_date)
        if signal_start.tzinfo is not None:
            signal_start = signal_start.replace(tzinfo=None)
        signal_start_index = df.index.get_indexer([signal_start], method='nearest')[0]
        signal_start_series = pd.Series([np.nan] * len(df), index=df.index)
        signal_start_series.iloc[signal_start_index] = df['close'].iloc[signal_start_index]
        apds.append(mpf.make_addplot(signal_start_series, type='scatter', markersize=100, marker='^', color='g' if trend.lower() == 'long' else 'r'))

    if signal_end_date:
        signal_end = datetime.fromisoformat(signal_end_date)
        if signal_end.tzinfo is not None:
            signal_end = signal_end.replace(tzinfo=None)
        signal_end_index = df.index.get_indexer([signal_end], method='nearest')[0]
        signal_end_series = pd.Series([np.nan] * len(df), index=df.index)
        signal_end_series.iloc[signal_end_index] = df['close'].iloc[signal_end_index]
        apds.append(mpf.make_addplot(signal_end_series, type='scatter', markersize=100, marker='v', color='r'))

    # Создание графика
    fig, axes = mpf.plot(df, type='candle', style=s, addplot=apds,
                         title=f'Тренд: {trend.capitalize()}',
                         ylabel='Цена',
                         datetime_format='%Y-%m-%d %H:%M',
                         figsize=(12, 8),
                         returnfig=True)

    axes[0].legend(['Линия тренда', 'Начало сигнала', 'Конец сигнала'])

    buf = io.BytesIO()
    plt.savefig(buf, format='png', dpi=100, bbox_inches='tight')
    buf.seek(0)
    plt.close(fig)

    return buf