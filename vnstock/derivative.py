from .config import *

# DERIVATIVES

# A function to get derivatives data from livedragon
def derivatives_historical_match (symbol='VN30F2308', date='2023-07-24', cookie=rv_cookie, headers=rv_headers):
    """
    Get derivatives historical price data from Live Dragon website (CK Rong Viet)
    Parameters:
        symbol (str, required): ticker of the stock
        date (str, required): date of the historical price data
        cookie (str, required): cookie of the request. Visit https://livedragon.vdsc.com.vn/all/all.rv. Open Developer Tools (F12 or Ctrl + Shift + I or Cmd + Option + I on macOS) > Navigate to Network > Choose Fetch/XHR > Select any request > Find Cookie in Header > Copy value.
        headers (dict): headers of the request. You can ignore this parameter.
    """
    # add cookie to headers
    headers['Cookie'] = cookie
    url = "https://livedragon.vdsc.com.vn/general/intradaySearch.rv"
    # convert date to dd/mm/yyyy format
    date = datetime.strptime(date, '%Y-%m-%d').strftime('%d/%m/%Y')
    payload = f"stockCode={symbol}&boardDate={date}"
    response = requests.request("POST", url, headers=headers, data=payload).json()
    df = pd.DataFrame(response['list'])
    # move `Code` column to the first column
    df = df[['Code'] + [col for col in df.columns if col != 'Code']]
    return df