from datetime import datetime, timedelta
import os
import platform

def get_date(n, unit):
    """
    Return YYYY-mm-dd value from today to n days, months or years in the past
    Parameters:
        n: number of days, months or years
        unit: 'day', 'month' or 'year'
    """
    if unit == 'day':
        return (datetime.now() - timedelta(days=n)).strftime('%Y-%m-%d')
    elif unit == 'month':
        return (datetime.now() - relativedelta(months=n)).strftime('%Y-%m-%d')
    elif unit == 'year':
        return (datetime.now() - relativedelta(years=n)).strftime('%Y-%m-%d')

def get_username():
    try:
        username = os.getlogin()
        return username
    except OSError as e:
        print(f"Error: {e}")
        return None
    
def get_os():
    try:
        os = platform.system()
        return os
    except OSError as e:
        print(f"Error: {e}")
        return None

# def previous_weekday (date):
#   date_value = datetime.strptime(date, '%Y-%m-%d')
#   weekday_name = date_value.strftime('%a')
#   if weekday_name == 'Sun':
#     prev_weekday_date = date_value - timedelta(days=2)
#   elif weekday_name == 'Mon':
#     prev_weekday_date = date_value - timedelta(days=3)
#   else:
#     prev_weekday_date = date_value - timedelta(days=1)
#   return prev_weekday_date

