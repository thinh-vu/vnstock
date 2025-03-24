# _BASE_URL = 'https://mt.vietcap.com.vn/api/'
_TRADING_URL = 'https://trading.vietcap.com.vn/api/'
_CHART_URL = 'chart/OHLCChart/gap'
_INTRADAY_URL = 'market-watch'
_GRAPHQL_URL = 'https://trading.vietcap.com.vn/data-mt/graphql'

_INTERVAL_MAP = {'1m' : 'ONE_MINUTE',
            '5m' : 'ONE_MINUTE',
            '15m' : 'ONE_MINUTE',
            '30m' : 'ONE_MINUTE',
            '1H' : 'ONE_HOUR',
            '1D' : 'ONE_DAY',
            '1W' : 'ONE_DAY',
            '1M' : 'ONE_DAY'
            }

_RESAMPLE_MAP = {
            '5m' : '5min',
            '15m' : '15min',
            '30m' : '30min',
            '1W' : '1W',
            '1M' : 'M'
            }

_OHLC_MAP = {
    't': 'time',
    'o': 'open',
    'h': 'high',
    'l': 'low',
    'c': 'close',
    'v': 'volume',
}

# Pandas data type mapping for history price data
_OHLC_DTYPE = {
    "time": "datetime64[ns]",  # Convert timestamps to datetime
    "open": "float64",
    "high": "float64",
    "low": "float64",
    "close": "float64",
    "volume": "int64",
}

_GROUP_CODE = ['HOSE', 'VN30', 'VNMidCap', 'VNSmallCap', 'VNAllShare', 'VN100', 'ETF', 'HNX', 'HNX30', 'HNXCon', 'HNXFin', 'HNXLCap', 'HNXMSCap', 'HNXMan', 'UPCOM', 'FU_INDEX', 'FU_BOND', 'BOND', 'CW']

_INTRADAY_MAP = {
                'truncTime':'time',
                'matchPrice':'price',
                'matchVol':'volume',
                'matchType':'match_type',
                'id':'id'
                }

_INTRADAY_DTYPE = {
                    "time": "datetime64[ns]",
                    "price": "float64",
                    "volume": "int64",
                    "match_type": "str",
                    "id": "str"
                }

_PRICE_DEPTH_MAP = {
                    'priceStep':'price',
                    'accumulatedVolume': 'acc_volume',
                    'accumulatedBuyVolume' : 'acc_buy_volume',
                    'accumulatedSellVolume' : 'acc_sell_volume',
                    'accumulatedUndefinedVolume': 'acc_undefined_volume',
                    }

_FINANCIAL_REPORT_MAP = {'balance_sheet': 'balancesheet',
                            'income_statement': 'incomestatement',
                            'cash_flow': 'cashflow'}

_FINANCIAL_REPORT_PERIOD_MAP = {'year': 'Y', 'quarter': 'Q'}

_UNIT_MAP = {'BILLION':'tỷ', 'PERCENT':'%', 'INDEX':'index', 'MILLION':'triệu'}

SUPPORTED_LANGUAGES = ['vi', 'en']

_INDEX_MAPPING = {'VNINDEX': 'VNINDEX', 'HNXINDEX': 'HNXIndex', 'UPCOMINDEX': 'HNXUpcomIndex'}

_PRICE_INFO_MAP = {
    'ev': 'ev', # Enterprise Value
    'ticker': 'symbol',
    # Price-related columns
    'open_price': 'open',
    'ceiling_price': 'ceiling',
    'floor_price': 'floor',
    'reference_price': 'ref_price',
    'highest_price': 'high',
    'lowest_price': 'low',
    'price_change': 'price_change',
    'percent_price_change': 'price_change_pct',
    
    # Year-based metrics
    'highest_price1_year': 'high_price_1y',
    'lowest_price1_year': 'low_price_1y',
    'percent_lowest_price_change1_year': 'pct_low_change_1y',
    'percent_highest_price_change1_year': 'pct_high_change_1y',
    
    # Foreign ownership related
    'foreign_total_volume': 'foreign_volume',
    'foreign_total_room': 'foreign_room',
    'foreign_holding_room': 'foreign_holding_room',
    
    # Other metrics
    'average_match_volume2_week': 'avg_match_volume_2w',
}


_ICB4_COMTYPE_CODE_MAP = {'Bán lẻ phức hợp': 'CT',
 'Bảo hiểm nhân thọ': 'BH',
 'Bảo hiểm phi nhân thọ': 'BH',
 'Bất động sản': 'CT',
 'Chuyển phát nhanh': 'CT',
 'Chăm sóc y tế': 'CT',
 'Chất thải & Môi trường': 'CT',
 'Containers & Đóng gói': 'CT',
 'Công nghiệp phức hợp': 'CT',
 'Công nghệ sinh học': 'CT',
 'Dược phẩm': 'CT',
 'Dịch vụ Máy tính': 'CT',
 'Dịch vụ giải trí': 'CT',
 'Dịch vụ tiêu dùng chuyên ngành': 'CT',
 'Dịch vụ truyền thông': 'CT',
 'Dịch vụ vận tải': 'CT',
 'Dụng cụ y tế': 'CT',
 'Giải trí & Truyền thông': 'CT',
 'Giầy dép': 'CT',
 'Hàng May mặc': 'CT',
 'Hàng cá nhân': 'CT',
 'Hàng không': 'CT',
 'Hàng điện & điện tử': 'CT',
 'Internet': 'CT',
 'Khai khoáng': 'CT',
 'Khai thác Than': 'CT',
 'Khai thác vàng': 'CT',
 'Kho bãi, hậu cần và bảo dưỡng': 'CT',
 'Khách sạn': 'CT',
 'Kim Loại màu': 'CT',
 'Lâm sản và Chế biến gỗ': 'CT',
 'Lốp xe': 'CT',
 'Máy công nghiệp': 'CT',
 'Môi giới chứng khoán': 'CK',
 'Ngân hàng': 'NH',
 'Nhà cung cấp thiết bị': 'CT',
 'Nhà hàng và quán bar': 'CT',
 'Nhôm': 'CT',
 'Nhựa, cao su & sợi': 'CT',
 'Nuôi trồng nông & hải sản': 'CT',
 'Nước': 'CT',
 'Phân phối dược phẩm': 'CT',
 'Phân phối hàng chuyên dụng': 'CT',
 'Phân phối thực phẩm': 'CT',
 'Phân phối xăng dầu & khí đốt': 'CT',
 'Phần cứng': 'CT',
 'Phần mềm': 'CT',
 'Phụ tùng ô tô': 'CT',
 'Quản lý tài sản': 'NH',
 'Sách, ấn bản & sản phẩm văn hóa': 'CT',
 'Sản phẩm hóa dầu, Nông dược & Hóa chất khác': 'CT',
 'Sản xuất & Phân phối Điện': 'CT',
 'Sản xuất bia': 'CT',
 'Sản xuất giấy': 'CT',
 'Sản xuất và Khai thác dầu khí': 'CT',
 'Sản xuất ô tô': 'CT',
 'Thiết bị gia dụng': 'CT',
 'Thiết bị viễn thông': 'CT',
 'Thiết bị và Dịch vụ Dầu khí': 'CT',
 'Thiết bị văn phòng': 'CT',
 'Thiết bị y tế': 'CT',
 'Thiết bị điện': 'CT',
 'Thuốc lá': 'CT',
 'Thép và sản phẩm thép': 'CT',
 'Thực phẩm': 'CT',
 'Tiện ích khác': 'CT',
 'Tài chính cá nhân': 'NH',
 'Tài chính đặc biệt': 'CT',
 'Tái bảo hiểm': 'BH',
 'Tư Vấn, Định giá, Môi giới Bất động sản': 'CT',
 'Tư vấn & Hỗ trợ KD': 'CT',
 'Vang & Rượu mạnh': 'CT',
 'Viễn thông cố định': 'CT',
 'Viễn thông di động': 'CT',
 'Vận tải Thủy': 'CT',
 'Vận tải hành khách & Du lịch': 'CT',
 'Vật liệu xây dựng & Nội thất': 'CT',
 'Xe tải & Đóng tàu': 'CT',
 'Xây dựng': 'CT',
 'Điện tử tiêu dùng': 'CT',
 'Đào tạo & Việc làm': 'CT',
 'Đường sắt': 'CT',
 'Đồ chơi': 'CT',
 'Đồ gia dụng lâu bền': 'CT',
 'Đồ gia dụng một lần': 'CT',
 'Đồ uống & giải khát': 'CT'}
