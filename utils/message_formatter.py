from datetime import datetime

def format_new_signal_message(signal, is_new=False):
    status = "NEW" if is_new else "ACTUAL"
    return f"""{status}
🟩 {signal.name}
Trend: {signal.trend.upper()}
Start: {signal.date_start}
Price: {signal.price_start}
Last check: {signal.date_last}
Current price: {signal.price_last}
Accuracy: {signal.accuracy}%"""

def format_closed_signal_message(signal):
    return f"""CLOSED
{signal.name}
Trend: {signal.trend.upper()}
Start: {signal.date_start}
Start price: {signal.price_start}
End: {signal.date_end}
End price: {signal.price_end}
Total duration: {calculate_duration(signal.date_start, signal.date_end)}"""

def calculate_duration(start_date, end_date):
    start = datetime.fromisoformat(start_date)
    end = datetime.fromisoformat(end_date)
    duration = end - start
    days = duration.days
    hours, remainder = divmod(duration.seconds, 3600)
    minutes, _ = divmod(remainder, 60)
    return f"{days} days, {hours} hours, {minutes} minutes"