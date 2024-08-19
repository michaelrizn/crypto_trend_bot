import matplotlib.pyplot as plt
import io
import base64
import logging


def generate_chart(ohlcv_data, trend):
    try:
        closes = [x[4] for x in ohlcv_data]
        plt.figure(figsize=(10, 6), dpi=100)
        plt.plot(closes, label='Цена закрытия')
        plt.title(f'Тренд: {trend.capitalize()}')
        plt.xlabel('Время')
        plt.ylabel('Цена')
        plt.legend()

        buffer = io.BytesIO()
        plt.savefig(buffer, format='png', dpi=100)
        buffer.seek(0)
        image_png = buffer.getvalue()
        buffer.close()
        plt.close()

        return image_png
    except Exception as e:
        logging.error(f"Ошибка при генерации графика: {e}")
        return None