import requests
from io import BytesIO
import pandas as pd
import base64
import datetime
import warnings
from vnai import optimize_execution
warnings.filterwarnings("ignore", message="Workbook contains no default style, apply openpyxl's default")
from vnstock.core.utils.parser import camel_to_snake


@optimize_execution('MISC')
def vcb_exchange_rate(date='2023-12-26'):
    """
    Get exchange rate from Vietcombank for a specific date.
    
    Parameters:
        date (str): Date in format YYYY-MM-DD. If left blank, the current date will be used.
    """
    if date == '':
        date = datetime.datetime.now().strftime('%Y-%m-%d')
    else:
        try:
            datetime.datetime.strptime(date, '%Y-%m-%d')
        except ValueError:
            print("Error: Incorrect date format. Should be YYYY-MM-DD.")

    url = f"https://www.vietcombank.com.vn/api/exchangerates/exportexcel?date={date}"
    response = requests.get(url)
    if response.status_code == 200:
        json_data = response.json()
        excel_data = base64.b64decode(json_data["Data"])  # Decode base64 data
        columns = ['CurrencyCode', 'CurrencyName', 'Buy Cash', 'Buy Transfer', 'Sell' ]
        df = pd.read_excel(BytesIO(excel_data), sheet_name='ExchangeRate')
        df.columns = columns
        df = df.iloc[2:-4]
        df['date'] = date
        df.columns = [camel_to_snake(col) for col in df.columns]
        return df
    else:
        print(f"Error: Unable to fetch data. Details: {response.text}")