from .config import *

## MARKET WATCH

def market_top_mover (report_name='Value', exchange='All', filter= 'NetBuyVol', report_range='ThreeMonths', rate='OnePointFive', lang='vi', headers=ssi_headers): #Value, Losers, Gainers, Volume, ForeignTrading, NewLow, Breakout, NewHigh
    """
    This function returns the list of Top Stocks by one of criteria: 'Value', 'Losers', 'Gainers', 'Volume', 'ForeignTrading', 'NewLow', 'Breakout', 'NewHigh'.
    Args:
        report_name(:obj:`str`, required): name of the report including 'Value', 'Losers', 'Gainers', 'Volume', 'ForeignTrading', 'NewLow', 'Breakout', 'NewHigh'
        exchange(:obj:`str`, required): choose one of these exchanges: 'All', 'HOSE', 'HNX', 'UPCOM'
        filter (:obj:`str`, optional): choose one of these filters: 'NetBuyVol', 'NetBuyVal', 'NetSellVol', 'NetSellVal'
        report_range(:obj:`str`, optional): choose one of these ranges: 'OneWeek' for 5 days, 'TwoWeek' for 10 days, 'OneMonth', 'ThreeMonths', 'SixMonths', 'OneYear'
        rate(:obj:`str`, optional): choose one of these rates: 'OnePointTwo', 'OnePointFive', 'Two', 'Five', 'Ten'
        lang(:obj:`str`, optional): choose one of these languages: 'vi', 'en'
    """
    ls1 = ['Gainers', 'Losers', 'Value', 'Volume']
    # ls2 = ['ForeignTrading', 'NewLow', 'Breakout', 'NewHigh']
    if report_name in ls1:
        url = f'https://fiin-market.ssi.com.vn/TopMover/GetTop{report_name}?language={lang}&ComGroupCode={exchange}'
    elif report_name == 'ForeignTrading':
        url = f'https://fiin-market.ssi.com.vn/TopMover/GetTop{report_name}?language={lang}&ComGroupCode={exchange}&Option={filter}'
    elif report_name == 'NewLow':
        url = f'https://fiin-market.ssi.com.vn/TopMover/GetTop{report_name}?language={lang}&ComGroupCode={exchange}&TimeRange={report_range}'
    elif report_name == 'Breakout':
        url = f'https://fiin-market.ssi.com.vn/TopMover/GetTop{report_name}?language={lang}&ComGroupCode={exchange}&TimeRange={report_range}&Rate={rate}'
    elif report_name == 'NewHigh':
        url = f'https://fiin-market.ssi.com.vn/TopMover/GetTop{report_name}?language={lang}&ComGroupCode={exchange}&TimeRange={report_range}'
    # request get to the url as global variable
    response = requests.get(url, headers=headers)
    status = response.status_code
    if status == 200:
        data = response.json()
        df = pd.DataFrame(data['items'])
        return df
    else:
        print(f'Error: {status} when getting data. Details: {response.text}')


def fr_trade_heatmap (symbol='HOSE', report_type='FrBuyVal', headers=ssi_headers): 
    """
    This function returns the foreign investors trading insights which is being rendered as the heatmap on SSI iBoard
    Args:
        exchange (:obj:`str`, required): Choose HOSE, HNX, or UPCOM. Or you can input any index: VN30, HNX30, VN100, etc
        report_type (:obj:`str`, required): choose one of these report types: FrBuyVal, FrSellVal, FrBuyVol, FrSellVol, Volume, Value, MarketCap
    """
    # if symbol in the list of 'All, HOSE, HNX, UPCOM then url use exchange such as https://iboard-query.ssi.com.vn/stock/exchange/hose, else use group such as https://iboard-query.ssi.com.vn/stock/group/hnx30
    if symbol in ['All', 'HOSE', 'HNX', 'UPCOM']:
        url = 'https://iboard-query.ssi.com.vn/stock/exchange/{}'.format(symbol)
    else:
        url = 'https://iboard-query.ssi.com.vn/stock/group/{}'.format(symbol)
    # url = 'https://fiin-market.ssi.com.vn/HeatMap/GetHeatMap?language=vi&Exchange={}&Criteria={}'.format(exchange, report_type)
    response = requests.get(url, headers=headers)
    status = response.status_code
    if status == 200:
        data = response.json()
        df = json_normalize(data['data'])
        return df
    else:
        print(f'Error: {status} when getting data. Details: {response.text}')