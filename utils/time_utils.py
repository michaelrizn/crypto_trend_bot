from datetime import datetime
from pytz import timezone
from config import TIMEZONE

def get_current_time():
    return datetime.now(timezone(TIMEZONE)).isoformat()

def format_date(date_string):
    date = datetime.fromisoformat(date_string)
    return date.astimezone(timezone(TIMEZONE)).strftime("%Y-%m-%d %H:%M")

def calculate_time_difference(start_time, end_time):
    start = datetime.fromisoformat(start_time)
    end = datetime.fromisoformat(end_time)
    diff = end - start
    days = diff.days
    hours = diff.seconds // 3600
    return f"{days} дней и {hours} часов"