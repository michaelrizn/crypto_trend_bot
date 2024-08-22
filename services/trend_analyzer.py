import numpy as np
from utils.logger import analyze_logger

def analyze_trend(ohlcv_data):
    analyze_logger.info("Начало анализа тренда")
    if not ohlcv_data:
        analyze_logger.warning("Нет данных для анализа")
        return None, 0

    closes = np.array([x[4] for x in ohlcv_data])
    ma_short = np.mean(closes[-24:])  # 24-hour moving average
    ma_long = np.mean(closes)  # Full period moving average

    analyze_logger.info(f"Короткая MA: {ma_short}, Длинная MA: {ma_long}")

    if ma_short > ma_long:
        trend = "long"
    elif ma_short < ma_long:
        trend = "short"
    else:
        trend = None

    # Расчет accuracy
    diff = abs(ma_short - ma_long)
    max_diff = max(closes) - min(closes)
    accuracy = int((1 - diff / max_diff) * 100) if max_diff != 0 else 50
    accuracy = max(1, min(100, accuracy))

    analyze_logger.info(f"Определен тренд: {trend}, Точность: {accuracy}")

    # Здесь можно добавить вызов TinyML анализа
    # tinyml_result = analyze_with_tinyml(ohlcv_data)
    # analyze_logger.info(f"Результат TinyML анализа: {tinyml_result}")

    return trend, accuracy

def is_trend_still_valid(ohlcv_data, current_trend):
    new_trend, _ = analyze_trend(ohlcv_data)
    return new_trend == current_trend