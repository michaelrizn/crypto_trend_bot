from datetime import datetime

def format_date(date_string):
    date = datetime.fromisoformat(date_string)
    return date.strftime("%Y-%m-%d %H:%M")

def format_new_signal_message(signal, is_new=False):
    status = "Новый сигнал" if is_new else "Актуальный сигнал"
    trend_emoji = "🟢" if signal.trend.lower() == "long" else "🔴"
    return f"{status}: {signal.name} {trend_emoji} {signal.trend.upper()} Точность: {signal.accuracy}\n" \
           f"Начало: {format_date(signal.date_start)} Цена: {signal.price_start}\n" \
           f"Актуально на: {format_date(signal.date_last)} Цена: {signal.price_last}"

def format_closed_signal_message(signal):
    trend_emoji = "🟢" if signal.trend.lower() == "long" else "🔴"
    return f"❌ Сигнал закрыт: {signal.name} {trend_emoji} {signal.trend.upper()}\n" \
           f"Начало: {format_date(signal.date_start)} Цена: {signal.price_start}\n" \
           f"Конец: {format_date(signal.date_end)} Цена: {signal.price_end}\n" \
           f"Общая длительность: {calculate_duration(signal.date_start, signal.date_end)}"

def calculate_duration(start_date, end_date):
    start = datetime.fromisoformat(start_date)
    end = datetime.fromisoformat(end_date)
    duration = end - start
    days = duration.days
    hours, remainder = divmod(duration.seconds, 3600)
    minutes, _ = divmod(remainder, 60)
    return f"{days} дней, {hours} часов, {minutes} минут"