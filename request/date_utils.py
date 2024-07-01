from datetime import datetime, timedelta


def get_date_from_weekday(year, month, day_of_week):
    first_day_of_month = datetime(year, month, 1)
    first_day_weekday = first_day_of_month.weekday()
    delta_days = (day_of_week - first_day_weekday) % 7
    target_date = first_day_of_month + timedelta(days=delta_days)
    return target_date.date()

def get_date_times_from_json(schedule, year, month):
    date_times = []
    for day, times in schedule.items():
        target_date = get_date_from_weekday(year, month, int(day))
        for time_range in times:
            start_time, end_time = time_range.split('-')
            start_datetime = datetime.combine(target_date, datetime.strptime(start_time, '%H:%M').time())
            end_datetime = datetime.combine(target_date, datetime.strptime(end_time, '%H:%M').time())
            date_times.append((start_datetime, end_datetime))
    return date_times

def filter_out_busy_times(date_times, busy_times):
    filtered_times = []
    for available_start, available_end in date_times:
        is_available = True
        for busy_start, busy_end in busy_times:
            if (available_start < busy_end and available_end > busy_start):
                is_available = False
                break
        if is_available:
            filtered_times.append((available_start, available_end))
    return filtered_times
