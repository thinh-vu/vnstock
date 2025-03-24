from fake_useragent import UserAgent

DEFAULT_HEADERS = {
            'Accept': 'application/json, text/plain, */*',
            'Accept-Language': 'en-US,en;q=0.9,vi-VN;q=0.8,vi;q=0.7',
            'Connection': 'keep-alive',
            'Content-Type': 'application/json',
            'Accept-Language': 'vi',
            'Cache-Control': 'no-cache',
            'Sec-Fetch-Dest': 'empty',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Site': 'same-site',
            'DNT': '1',
            'Pragma': 'no-cache',
            'sec-ch-ua-platform': '"Windows"',
            'sec-ch-ua-mobile': '?0',
        }

HEADERS_MAPPING_SOURCE =    {
                            'SSI': {'Referer': 'https://iboard.ssi.com.vn', 'Origin': 'https://iboard.ssi.com.vn'},
                            'VND': {'Referer': 'https://dchart.vndirect.com.vn', 'Origin': 'https://dchart.vndirect.com.vn'},
                            'TCBS': {'Referer': 'https://tcinvest.tcbs.com.vn/', 'Origin': 'https://tcinvest.tcbs.com.vn/'},
                            'VCI': {'Referer': 'https://trading.vietcap.com.vn/', 'Origin': 'https://trading.vietcap.com.vn/'},
                            'MSN': {'Referer': 'https://www.msn.com/', 'Origin': 'https://www.msn.com/'},
                            'FMARKET': {'Referer': 'https://fmarket.vn/', 'Origin': 'https://fmarket.vn/'},
                            'SJC': {'Referer': 'https://sjc.com.vn/bieu-do-gia-vang', 'Origin': 'https://sjc.com.vn'},
                            }


def get_headers(data_source='SSI', random_agent=True):
    """
    Tạo headers cho request theo nguồn dữ liệu.
    """
    data_source = data_source.upper()
    ua = UserAgent(fallback='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/134.0.0.0 Safari/537.36')
    headers = DEFAULT_HEADERS.copy()
    if random_agent:
        headers['User-Agent'] = ua.random
    else:
        headers['User-Agent'] = ua.chrome
    headers.update(HEADERS_MAPPING_SOURCE.get(data_source, {}))
    return headers