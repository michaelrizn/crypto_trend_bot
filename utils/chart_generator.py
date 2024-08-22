import mplfinance as mpf
import pandas as pd
import numpy as np
from datetime import datetime
import matplotlib.pyplot as plt
import io


def find_nearest_index(df, target_time):
    nearest_idx = df.index.get_indexer([target_time], method='nearest')[0]
    return df.index[nearest_idx]


def generate_chart(ohlcv_data, trend, signal_start_date=None, signal_end_date=None):
    df = pd.DataFrame(ohlcv_data, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
    df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
    df.set_index('timestamp', inplace=True)

    # Рассчитываем линию тренда
    x = np.arange(len(df))
    y = df['close'].values

    # Вывод длины массивов x и y для диагностики
    print(f"Length of x: {len(x)}, Length of y: {len(y)}")

    z = np.polyfit(x, y, 1)
    p = np.poly1d(z)
    trend_line = p(x)

    # Настройка стиля графика
    mc = mpf.make_marketcolors(up='g', down='r', inherit=True)
    s = mpf.make_mpf_style(marketcolors=mc)

    # Подготовка дополнительных графиков
    apds = [mpf.make_addplot(trend_line, color='blue', width=1)]

    if signal_start_date:
        signal_start = datetime.fromisoformat(signal_start_date)
        if signal_start.tzinfo is not None:
            signal_start = signal_start.replace(tzinfo=None)

        # Используем ближайшую временную метку
        signal_start_index = find_nearest_index(df, signal_start)
        print(
            f"Signal start at {signal_start_index}, close value: {df['close'].loc[signal_start_index]}")

        # Создание временного ряда с NaN, кроме одного значения
        signal_start_series = pd.Series([np.nan] * len(df), index=df.index)
        signal_start_series.loc[signal_start_index] = df['close'].loc[signal_start_index]

        apds.append(mpf.make_addplot(signal_start_series, type='scatter',
                                     markersize=100, marker='^',
                                     color='g' if trend.lower() == 'long' else 'r'))

    if signal_end_date:
        signal_end = datetime.fromisoformat(signal_end_date)
        if signal_end.tzinfo is not None:
            signal_end = signal_end.replace(tzinfo=None)

        # Используем ближайшую временную метку
        signal_end_index = find_nearest_index(df, signal_end)
        print(f"Signal end at {signal_end_index}, close value: {df['close'].loc[signal_end_index]}")

        # Создание временного ряда с NaN, кроме одного значения
        signal_end_series = pd.Series([np.nan] * len(df), index=df.index)
        signal_end_series.loc[signal_end_index] = df['close'].loc[signal_end_index]

        apds.append(mpf.make_addplot(signal_end_series, type='scatter',
                                     markersize=100, marker='v', color='r'))

    # Создание графика
    try:
        fig, axes = mpf.plot(df, type='candle', style=s, addplot=apds,
                             title=f'Тренд: {trend.capitalize()}',
                             ylabel='Цена',
                             datetime_format='%Y-%m-%d %H:%M',
                             figsize=(12, 8),
                             returnfig=True)

        # Настройка легенды
        axes[0].legend(['Линия тренда', 'Начало сигнала', 'Конец сигнала'])

        # Сохранение графика в байтовый поток
        buf = io.BytesIO()
        plt.savefig(buf, format='png', dpi=100, bbox_inches='tight')
        buf.seek(0)
        plt.close(fig)

        return buf
    except Exception as e:
        print(f"Ошибка при создании графика: {e}")
        raise