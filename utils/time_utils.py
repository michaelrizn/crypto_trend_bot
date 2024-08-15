from datetime import datetime

def get_current_time():
    return datetime.now().isoformat()

def calculate_time_difference(start_time, end_time):
    start = datetime.fromisoformat(start_time)
    end = datetime.fromisoformat(end_time)
    diff = end - start
    days = diff.days
    hours = diff.seconds // 3600
    return f"{days} days and {hours} hours"