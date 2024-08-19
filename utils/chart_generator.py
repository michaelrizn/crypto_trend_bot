import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib.patches import Arrow
import numpy as np
from datetime import datetime
import io
import logging
from pytz import UTC

def generate_chart(ohlcv_data, trend, signal_start_date=None, signal_end_date=None):
    dates = [datetime.fromtimestamp(x[0] / 1000, tz=UTC) for x in ohlcv_data]
    closes = [x[4] for x in ohlcv_data]

    fig, ax = plt.subplots(figsize=(10, 6))
    ax.plot(dates, closes, label='Цена закрытия')

    ax.set_title(f'Тренд: {trend.capitalize()}')
    ax.set_xlabel('Время')
    ax.set_ylabel('Цена')
    ax.legend()

    # Форматирование оси X для отображения дат
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d %H:%M', tz=UTC))
    plt.xticks(rotation=45)

    # Отметка начала сигнала
    if signal_start_date:
        signal_start = datetime.fromisoformat(signal_start_date).replace(tzinfo=UTC)
        start_index = dates.index(min(dates, key=lambda d: abs(d - signal_start)))
        ax.axvline(x=dates[start_index], color='g' if trend.lower() == 'long' else 'r', linestyle='--', label='Начало сигнала')

    # Отметка конца сигнала, если есть
    if signal_end_date:
        signal_end = datetime.fromisoformat(signal_end_date).replace(tzinfo=UTC)
        end_index = dates.index(min(dates, key=lambda d: abs(d - signal_end)))
        ax.axvline(x=dates[end_index], color='black', linestyle='--', label='Конец сигнала')

    plt.tight_layout()

    # Сохранение графика в байтовый поток
    buf = io.BytesIO()
    plt.savefig(buf, format='png')
    buf.seek(0)
    plt.close(fig)

    return buf