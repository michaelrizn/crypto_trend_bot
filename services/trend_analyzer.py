import numpy as np

def analyze_trend(ohlcv_data):
    if not ohlcv_data:
        return None, 0

    closes = np.array([x[4] for x in ohlcv_data])
    ma_short = np.mean(closes[-12:])  # 12-hour moving average
    ma_long = np.mean(closes)  # 48-hour moving average

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
    accuracy = max(1, min(100, accuracy))  # Убедимся, что accuracy в пределах от 1 до 100

    return trend, accuracy

def is_trend_still_valid(ohlcv_data, current_trend):
    new_trend, _ = analyze_trend(ohlcv_data)
    return new_trend == current_trend