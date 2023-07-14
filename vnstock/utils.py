from datetime import datetime, timedelta

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

# def countBack (start_date, end_date):
#   fd_value = datetime.strptime(start_date, '%Y-%m-%d')
#   td_value = datetime.strptime(end_date, '%Y-%m-%d')
#   diff = td_value - fd_value # Calculate the difference
#   seconds = diff.total_seconds() # Get the total number of seconds
#   # Define the number of seconds in each scenario
#   minute = 60
#   quarter_hour = 15 * minute
#   hour = 60 * minute
#   day = 60 * 6 * minute # trading time from 9AM to 3PM which is 6 hours
#   week = 6 * day
#   month = 23 * day # maximum of 23 working days in a month
#   # Calculate the diff in each scenario
#   diff_minute = round(seconds / minute)
#   diff_quarter_hour = round(seconds / quarter_hour)
#   diff_hour = round(seconds / hour)
#   diff_week = round(seconds / week)
#   diff_month = round(seconds / month)
#   return diff_minute, diff_quarter_hour, diff_hour, diff_week, diff_month


# # API request config for SSI API endpoints
# headers = {
#         'Connection': 'keep-alive',
#         'sec-ch-ua': '"Not A;Brand";v="99", "Chromium";v="98", "Google Chrome";v="98"',
#         'DNT': '1',
#         'sec-ch-ua-mobile': '?0',
#         'X-Fiin-Key': 'KEY',
#         'Content-Type': 'application/json',
#         'Accept': 'application/json',
#         'X-Fiin-User-ID': 'ID',
#         'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/98.0.4758.102 Safari/537.36',
#         'X-Fiin-Seed': 'SEED',
#         'sec-ch-ua-platform': 'Windows',
#         'Origin': 'https://iboard.ssi.com.vn',
#         'Sec-Fetch-Site': 'same-site',
#         'Sec-Fetch-Mode': 'cors',
#         'Sec-Fetch-Dest': 'empty',
#         'Referer': 'https://iboard.ssi.com.vn/',
#         'Accept-Language': 'en-US,en;q=0.9,vi-VN;q=0.8,vi;q=0.7'
#         }

# def api_request(url, headers=headers):
#     r = requests.get(url, headers).json()
#     return r