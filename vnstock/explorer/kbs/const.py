"""Constants for KB Securities (KBS) data source."""

# Base URLs
_IIS_BASE_URL = 'https://kbbuddywts.kbsec.com.vn/iis-server/investment'
_SAS_BASE_URL = 'https://kbbuddywts.kbsec.com.vn/sas'

# IIS Server Endpoints - Listing & Market Data
_SEARCH_URL = f'{_IIS_BASE_URL}/stock/search/data'
_SECTOR_ALL_URL = f'{_IIS_BASE_URL}/sector/all'
_SECTOR_STOCK_URL = f'{_IIS_BASE_URL}/sector/stock'
_INDEX_URL = f'{_IIS_BASE_URL}/index'

# IIS Server Endpoints - Stock Data
_STOCK_DATA_URL = f'{_IIS_BASE_URL}/stocks'
_STOCK_INFO_URL = f'{_IIS_BASE_URL}/stockinfo'
_STOCK_TRADE_HISTORY_URL = f'{_IIS_BASE_URL}/trade/history'
_STOCK_MATCHED_BY_PRICE_URL = f'{_IIS_BASE_URL}/stock/matched-by-price'

# IIS Server Endpoints - Price Board (ISS)
_STOCK_ISS_URL = f'{_IIS_BASE_URL}/stock/iss'

# IIS Server Endpoints - Rankings
_RANKING_VOLUME_URL = f'{_IIS_BASE_URL}/rtranking/volume'
_RANKING_FOREIGN_URL = f'{_IIS_BASE_URL}/rtranking/foreignTotal'

# SAS Endpoints - Stock Data Store
_SAS_STOCK_URL = f'{_SAS_BASE_URL}/kbsv-stock-data-store/stock'
_SAS_HISTORICAL_QUOTES_URL = f'{_SAS_STOCK_URL}/{{symbol}}/historical-quotes'
_SAS_FINANCE_INFO_URL = f'{_SAS_STOCK_URL}/finance-info'
_SAS_TRADING_MARGIN_URL = f'{_SAS_STOCK_URL}/trading-margin'
_SAS_CTKH_INFO_URL = f'{_SAS_STOCK_URL}/ctkh-info'

# SAS Endpoints - News
_SAS_NEWS_URL = f'{_SAS_BASE_URL}/kbsv-news/api/v2/news'

# Group codes mapping
_GROUP_CODE = {
    'HOSE': 'HOSE',
    'HNX': 'HNX',
    'UPCOM': 'UPCOM',
    'VN30': '30',
    'VN100': '100',
    'VNMidCap': 'MID',
    'VNSmallCap': 'SML',
    'VNSI': 'SI',
    'VNX50': 'X50',
    'VNXALL': 'XALL',
    'VNALL': 'ALL',
    'HNX30': 'HNX30',
    'ETF': 'FUND',
    'CW': 'CW',
    'BOND': 'BOND',
    'FU_INDEX': 'DER',
}

# Exchange mapping for standardization
_EXCHANGE_MAP = {
    'HOSE': 'HOSE',
    'HNX': 'HNX',
    'UPCOM': 'UPCOM',
}

# Industry codes mapping (from KBS API response)
_INDUSTRY_CODE = {
    1: 'Bán buôn',
    2: 'Bảo hiểm',
    3: 'Bất động sản',
    5: 'Chứng khoán',
    6: 'Công nghệ và thông tin',
    7: 'Bán lẻ',
    8: 'Chăm sóc sức khỏe',
    10: 'Khai khoáng',
    11: 'Ngân hàng',
    12: 'Nông - Lâm - Ngư',
    15: 'SX Thiết bị, máy móc',
    16: 'SX Hàng gia dụng',
    17: 'Sản phẩm cao su',
    18: 'SX Nhựa - Hóa chất',
    19: 'Thực phẩm - Đồ uống',
    20: 'Chế biến Thủy sản',
    21: 'Vật liệu xây dựng',
    22: 'Tiện ích',
    23: 'Vận tải - kho bãi',
    24: 'Xây dựng',
    25: 'Dịch vụ lưu trú, ăn uống, giải trí',
    26: 'SX Phụ trợ',
    27: 'Thiết bị điện',
    28: 'Dịch vụ tư vấn, hỗ trợ',
    29: 'Tài chính khác',
}

# Column mapping for historical data (data_day)
_OHLC_MAP = {
    't': 'time',
    'o': 'open',
    'h': 'high',
    'l': 'low',
    'c': 'close',
    'v': 'volume',
}

# Data type mapping for OHLC data
_OHLC_DTYPE = {
    'time': 'datetime64[ns]',
    'open': 'float64',
    'high': 'float64',
    'low': 'float64',
    'close': 'float64',
    'volume': 'int64',
}

# Column mapping for stock profile
_PROFILE_MAP = {
    'SM': 'business_model',
    'SB': 'symbol',
    'FD': 'founded_date',
    'CC': 'charter_capital',
    'HM': 'num_employees',
    'LD': 'listing_date',
    'FV': 'par_value',
    'EX': 'exchange',
    'LP': 'listing_price',
    'VL': 'listed_volume',
    'CTP': 'ceo_name',
    'CTPP': 'ceo_position',
    'IS': 'inspector_name',
    'ISP': 'inspector_position',
    'FP': 'license_number',
    'BP': 'business_code',
    'TC': 'tax_code',
    'KT': 'auditor',
    'TY': 'company_type',
    'ADD': 'address',
    'PHONE': 'phone',
    'FAX': 'fax',
    'EMAIL': 'email',
    'URL': 'website',
    'HS': 'history',
}

# Event type IDs
_EVENT_TYPE = {
    1: 'Đại hội cổ đông',
    2: 'Trả cổ tức',
    3: 'Phát hành',
    4: 'Giao dịch cổ đông nội bộ',
    5: 'Sự kiện khác',
}

# Interval mapping for technical chart data (KBS API)
# Maps user-friendly intervals to KBS API endpoint suffixes
_INTERVAL_MAP = {
    # Minute intervals
    '1m': '1P',      # 1 minute
    '5m': '5P',      # 5 minutes
    '15m': '15P',    # 15 minutes (not in sample but likely supported)
    '30m': '30P',    # 30 minutes
    # Hour intervals
    '1h': '60P',     # 1 hour (60 minutes)
    '1H': '60P',     # 1 hour (60 minutes) - uppercase alias
    '60m': '60P',    # 60 minutes
    # Daily intervals
    '1d': 'day',     # 1 day
    '1D': 'day',     # 1 day - uppercase alias
    'd': 'day',      # 1 day - short alias
    'D': 'day',      # 1 day - uppercase short alias
    'daily': 'day',  # 1 day - word alias
    # Weekly intervals
    '1w': 'week',    # 1 week
    '1W': 'week',    # 1 week - uppercase alias
    'w': 'week',     # 1 week - short alias
    'W': 'week',     # 1 week - uppercase short alias
    'weekly': 'week', # 1 week - word alias
    # Monthly intervals
    '1M': 'month',   # 1 month
    'm': 'month',    # 1 month - short alias
    'M': 'month',    # 1 month - uppercase short alias
    'monthly': 'month', # 1 month - word alias
}

# Resample mapping for data standardization
# Maps intervals to pandas resample frequency strings
_RESAMPLE_MAP = {
    # Minute intervals
    '1m': '1min',
    '5m': '5min',
    '15m': '15min',
    '30m': '30min',
    # Hour intervals
    '1h': '1H',
    '1H': '1H',
    '60m': '1H',
    # Daily intervals
    '1d': '1D',
    '1D': '1D',
    'd': '1D',
    'D': '1D',
    'daily': '1D',
    # Weekly intervals
    '1w': '1W',
    '1W': '1W',
    'w': '1W',
    'W': '1W',
    'weekly': '1W',
    # Monthly intervals
    '1M': '1MS',
    'm': '1MS',
    'M': '1MS',
    'monthly': '1MS',
}

# Column mapping for price board (ISS endpoint)
# Maps KBS API fields to schema-aligned field names (PriceBoardCore/Extended)
_PRICE_BOARD_MAP = {
    'TT': 'total_trades',
    'PP': 'price_points',
    'HI': 'high_price',
    'TV': 'total_value',
    'LO': 'low_price',
    'LS': 'listed_shares',
    'CHP': 'percent_change',
    'V1': 'bid_vol_1',
    'V2': 'bid_vol_2',
    'V3': 'bid_vol_3',
    'B1': 'bid_price_1',
    'AP': 'average_price',
    'B2': 'bid_price_2',
    'B3': 'bid_price_3',
    'RE': 'reference_price',
    'EX': 'exchange',
    'FB': 'foreign_buy_volume',
    'FC': 'foreign_buy_count',
    'S1': 'ask_price_1',
    'S2': 'ask_price_2',
    'S3': 'ask_price_3',
    'FL': 'floor_price',
    'FO': 'foreign_ownership_ratio',
    'FR': 'foreign_sell_volume',
    'PTQ': 'put_through_qty',
    'FS': 'foreign_sell_count',
    'SB': 'symbol',
    'PTV': 'put_through_value',
    'TLQ': 'total_listed_qty',
    'OP': 'open_price',
    'CH': 'price_change',
    'CL': 'ceiling_price',
    'CP': 'close_price',
    'TB': 'total_buy_vol',
    'PMP': 'previous_match_price',
    'CV': 'current_vol',
    't': 'time',
    'PMQ': 'previous_match_qty',
    'TO': 'total_offer_vol',
    'U1': 'ask_vol_1',
    'U2': 'ask_vol_2',
    'U3': 'ask_vol_3',
    'MS': 'market_status',
}

# Column mapping for intraday trade history (real-time matching data)
# Maps KBS API fields to standardized column names
_INTRADAY_MAP = {
    't': 'timestamp',           # Full timestamp (YYYY-MM-DD HH:MM:SS:MS)
    'TD': 'trading_date',       # Trading date (DD/MM/YYYY)
    'SB': 'symbol',             # Stock symbol
    'FT': 'time',               # Trade time (HH:MM:SS)
    'LC': 'side',               # Trade side: 'B' (buy) or 'S' (sell)
    'FMP': 'price',             # Match price
    'FCV': 'price_change',      # Price change from previous
    'FV': 'match_volume',       # Match volume
    'AVO': 'accumulated_volume', # Accumulated volume
    'AVA': 'accumulated_value',  # Accumulated value
}

# Data type mapping for intraday data
_INTRADAY_DTYPE = {
    'timestamp': 'object',
    'trading_date': 'object',
    'symbol': 'object',
    'time': 'object',
    'side': 'object',
    'price': 'float64',
    'price_change': 'float64',
    'match_volume': 'int64',
    'accumulated_volume': 'int64',
    'accumulated_value': 'float64',
}

# VCI-equivalent core columns for intraday (standardized output)
# Matches VCI's core intraday columns: time, price, volume, match_type, id
_INTRADAY_CORE_COLUMNS = ['time', 'price', 'volume', 'match_type', 'id']

# Column mapping for trade history
_TRADE_HISTORY_MAP = {
    't': 'timestamp',
    'TD': 'trading_date',
    'SB': 'symbol',
    'FT': 'time',
    'LC': 'side',  # 'B' for buy, 'S' for sell
    'FMP': 'price',
    'FCV': 'volume',
    'FV': 'match_volume',
    'AVO': 'accumulated_volume',
    'AVA': 'accumulated_value',
}

# Column mapping for matched by price
_MATCHED_BY_PRICE_MAP = {
    'price': 'price',
    'buy_vol': 'buy_volume',
    'sell_vol': 'sell_volume',
    'unknown_vol': 'unknown_volume',
    'total_vol': 'total_volume',
}

# Standard columns for price board output
# Mapped to the trading.PriceBoardCore/Extended schema
# Includes bid/ask prices and volumes as CORE fields (standard for price boards)
# Note: KBS API provides close_price as current match price, total_trades as volume
_PRICE_BOARD_STANDARD_COLUMNS = [
    'symbol',               # Mã CK
    'time',                 # Thời điểm
    'exchange',             # Sàn
    'ceiling_price',        # Giá trần
    'floor_price',          # Giá sàn
    'reference_price',      # Giá tham chiếu
    'open_price',           # Mở cửa
    'high_price',           # Cao nhất
    'low_price',            # Thấp nhất
    'close_price',          # Đóng cửa / Giá khớp hiện tại
    'average_price',        # Giá trung bình
    'total_trades',         # Tổng KL giao dịch
    'total_value',          # Tổng GT giao dịch
    'price_change',         # Thay đổi giá
    'percent_change',       # % Thay đổi
    'bid_price_1',          # Giá mua 1 (CORE)
    'bid_vol_1',            # KL mua 1 (CORE)
    'bid_price_2',          # Giá mua 2 (CORE)
    'bid_vol_2',            # KL mua 2 (CORE)
    'bid_price_3',          # Giá mua 3 (CORE)
    'bid_vol_3',            # KL mua 3 (CORE)
    'ask_price_1',          # Giá bán 1 (CORE)
    'ask_vol_1',            # KL bán 1 (CORE)
    'ask_price_2',          # Giá bán 2 (CORE)
    'ask_vol_2',            # KL bán 2 (CORE)
    'ask_price_3',          # Giá bán 3 (CORE)
    'ask_vol_3',            # KL bán 3 (CORE)
    'foreign_buy_volume',   # KL NN mua
    'foreign_sell_volume',  # KL NN bán
]

# Mapping from KBS API fields to the schema fields
_KBS_TO_SCHEMA_MAP = {
    # Price Board (stock) mappings
    'SB': 'symbol',
    't': 'time',
    'EX': 'exchange',
    'CL': 'ceiling_price',
    'FL': 'floor_price',
    'RE': 'reference_price',
    'CP': 'match_price',
    'CV': 'match_volume',
    'OP': 'open_price',
    'HI': 'high_price',
    'LO': 'low_price',
    'AP': 'average_price',
    'TV': 'total_value',
    'CH': 'price_change',
    'CHP': 'percent_change',
    'FB': 'foreign_buy_volume',
    'FR': 'foreign_sell_volume',
    'ST': 'trading_status',
    'TT': 'total_trades',
    'TD': 'trading_date',
    
    # Put-through mappings
    'PR': 'match_price',
    'MVL': 'match_volume',
    'TI': 'time',
    'MC': 'exchange',
}

# Columns to exclude from get_all output (unclear/meaningless fields)
# These are KBS API fields that don't have clear meaning or are internal codes
_EXCLUDED_COLUMNS = {
    'ULS',                      # Unknown/unclear field
    'IN',                       # Internal code (e.g., 'ASB', 'VCH')
    'OIC',                      # Unknown/unclear field
    'TSI',                      # Unknown/unclear field
    'EP',                       # Unknown/unclear field (always 0.0)
    'ER',                       # Unknown/unclear field
    'FTY',                      # Unknown/unclear field
    'P1',                       # Unclear price field
    'P2',                       # Unclear price field (duplicate of bid_price_1)
    'price_points',             # Always 0
    'total_buy_vol',            # Always 0
    'total_offer_vol',          # Always 0
    'previous_match_price',     # Not useful for current board
    'previous_match_qty',       # Not useful for current board
    'current_vol',              # Unclear/redundant
    'market_status',            # Single character code (O, C, etc.)
}

# Exchange code normalization mapping
# Normalize exchange codes to HOSE standard (used in API inputs)
_EXCHANGE_CODE_MAP = {
    'HOSE': 'HOSE',             # Ho Chi Minh Stock Exchange
    'HSX': 'HOSE',              # Old VCI code - normalize to HOSE
    'HNX': 'HNX',               # Ha Noi Stock Exchange
    'UPCOM': 'UPCOM',           # Unlisted Public Company Market
}

# Company profile data mapping from API response
# Maps API field codes to standardized column names
_COMPANY_PROFILE_MAP = {
    'SM': 'business_model',
    'SB': 'symbol',
    'FD': 'founded_date',
    'CC': 'charter_capital',
    'HM': 'number_of_employees',
    'LD': 'listing_date',
    'FV': 'par_value',
    'EX': 'exchange',
    'LP': 'listing_price',
    'VL': 'listed_volume',
    'CTP': 'ceo_name',
    'CTPP': 'ceo_position',
    'IS': 'inspector_name',
    'ISP': 'inspector_position',
    'FP': 'establishment_license',
    'BP': 'business_code',
    'TC': 'tax_id',
    'KT': 'auditor',
    'TY': 'company_type',
    'ADD': 'address',
    'PHONE': 'phone',
    'FAX': 'fax',
    'EMAIL': 'email',
    'URL': 'website',
    'BRANCH': 'branches',
    'HS': 'history',
    'KLCPNY': 'free_float_percentage',
    'SFV': 'free_float',
    'KLCPLH': 'outstanding_shares',
    'AD': 'as_of_date',
}

# Subsidiaries data mapping
_SUBSIDIARIES_MAP = {
    'D': 'update_date',
    'NM': 'name',
    'CC': 'charter_capital',
    'OR': 'ownership_percent',
    'CR': 'currency',
}

# Leaders data mapping
_LEADERS_MAP = {
    'FD': 'from_date',
    'PN': 'position',
    'NM': 'name',
    'PO': 'position_en',
    'PI': 'owner_code',
}

# Ownership structure mapping
_OWNERSHIP_MAP = {
    'NM': 'owner_type',
    'OR': 'ownership_percentage',
    'SH': 'shares_owned',
    'D': 'update_date',
}

# Major shareholders mapping
_SHAREHOLDERS_MAP = {
    'NM': 'name',
    'D': 'update_date',
    'V': 'shares_owned',
    'OR': 'ownership_percentage',
}

# Charter capital history mapping
_CHARTER_CAPITAL_MAP = {
    'D': 'date',
    'V': 'charter_capital',
    'C': 'currency',
}

# Labor structure mapping
_LABOR_STRUCTURE_MAP = {
    'Name': 'name',
    'NameEn': 'name_en',
    'Value': 'value',
    'Rate': 'rate',
}

# ============================================================================
# FINANCIAL DATA MAPPINGS - Schema Standardization
# ============================================================================

# Income Statement (KQKD) mapping
_INCOME_STATEMENT_MAP = {
    'doanh_thu': 'revenue',
    'doanh_thu_ban_hang': 'revenue',
    'loi_nhuan_gop': 'gross_profit',
    'loi_nhuan_hoat_dong': 'operating_profit',
    'loi_nhuan_truoc_thue': 'profit_before_tax',
    'loi_nhuan_sau_thue': 'net_profit',
    'eps': 'eps',
    'gia_von_hang_ban': 'cost_of_goods_sold',
    'chi_phi_ban_hang': 'selling_expenses',
    'chi_phi_quan_ly': 'admin_expenses',
    'chi_phi_tai_chinh': 'finance_expenses',
    'thu_nhap_khac': 'other_income',
    'chi_phi_khac': 'other_expenses',
}

# Balance Sheet (CDKT) mapping
_BALANCE_SHEET_MAP = {
    'tong_tai_san': 'total_assets',
    'tai_san_hien_hanh': 'current_assets',
    'tai_san_co_dinh': 'fixed_assets',
    'tong_no_phai_tra': 'total_liabilities',
    'no_hien_hanh': 'current_liabilities',
    'no_dai_han': 'long_term_liabilities',
    'von_chu_so_huu': 'equity',
    'von_dieu_le': 'charter_capital',
    'loi_nhuan_chu_so_huu': 'retained_earnings',
}

# Cash Flow (LCTT) mapping
_CASH_FLOW_MAP = {
    'luu_chuy_tien_hoat_dong': 'operating_cash_flow',
    'luu_chuy_tien_dau_tu': 'investing_cash_flow',
    'luu_chuy_tien_tai_chinh': 'financing_cash_flow',
    'thay_doi_tien_mat': 'net_change_in_cash',
    'tien_mat_dau_ky': 'beginning_cash',
    'tien_mat_cuoi_ky': 'ending_cash',
}

# Financial Ratios (CSTC) mapping
_FINANCIAL_RATIOS_MAP = {
    'pe': 'pe_ratio',
    'pb': 'pb_ratio',
    'ps': 'ps_ratio',
    'roe': 'roe',
    'roa': 'roa',
    'bien_loi_nhuan_gop': 'gross_margin',
    'bien_loi_nhuan_rong': 'net_margin',
    'ty_le_thanh_toan_hien_hanh': 'current_ratio',
    'ty_le_thanh_toan_nhanh': 'quick_ratio',
    'ty_le_no_von': 'debt_to_equity',
    'ty_le_no_tai_san': 'debt_to_assets',
    'von_dieu_le_tren_co_phieu': 'book_value_per_share',
    'loi_nhuan_tren_co_phieu': 'earnings_per_share',
}

# Financial report type mapping
_FINANCIAL_REPORT_TYPE_MAP = {
    'CDKT': 'balance_sheet',
    'KQKD': 'income_statement',
    'LCTT': 'cash_flow',
    'CSTC': 'financial_ratios',
    'CTKH': 'planned_indicators',
    'BCTT': 'summary_financial_report',
}

# Financial period type mapping
_FINANCIAL_PERIOD_TYPE_MAP = {
    1: 'year',
    2: 'quarter',
}

