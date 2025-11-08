"""
Standardized market constants for the vnstock library.

This module contains centralized reference data for indices, sectors,
and exchanges used across all data sources (VCI, TCBS, MSN, etc.).
These are shared constants, not system configuration.
"""

# =============================================================================
# STANDARDIZED INDICES METADATA
# =============================================================================
# Comprehensive index information: symbol -> full details
INDICES_INFO = {
    # HOSE Indices - Blue Chip and Large Cap
    'VN30': {
        'name': 'VN30',
        'description': '30 cổ phiếu vốn hóa lớn nhất & thanh khoản tốt nhất HOSE',
        'full_name': 'VN30 Index',
        'group': 'HOSE Indices',
        'index_id': 5,
    },
    'VNMID': {
        'name': 'VNMID',
        'description': 'Mid-Cap Index - nhóm cổ phiếu vốn hóa trung bình',
        'full_name': 'VNMidCap Index',
        'group': 'HOSE Indices',
        'index_id': 6,
    },
    'VNSML': {
        'name': 'VNSML',
        'description': 'Small-Cap Index - nhóm cổ phiếu vốn hóa nhỏ',
        'full_name': 'VNSmallCap Index',
        'group': 'HOSE Indices',
        'index_id': 7,
    },
    'VN100': {
        'name': 'VN100',
        'description': '100 cổ phiếu có vốn hoá lớn nhất HOSE',
        'full_name': 'VN100 Index',
        'group': 'HOSE Indices',
        'index_id': 8,
    },
    'VNALL': {
        'name': 'VNALL',
        'description': 'Tất cả cổ phiếu trên HOSE và HNX',
        'full_name': 'VNAll Index',
        'group': 'HOSE Indices',
        'index_id': 9,
    },
    'VNSI': {
        'name': 'VNSI',
        'description': 'Vietnam Small-Cap Index',
        'full_name': 'VNSI Index',
        'group': 'HOSE Indices',
        'index_id': 21,
    },

    # Sector Indices (Bộ chỉ số ngành - Mapped to ICB sector_id)
    'VNIT': {
        'name': 'VNIT',
        'description': 'Công nghệ thông tin',
        'full_name': 'Information Technology Sector Index',
        'group': 'Sector Indices',
        'index_id': 10,
        'sector_id': 159,
    },
    'VNIND': {
        'name': 'VNIND',
        'description': 'Công nghiệp',
        'full_name': 'Industrials Sector Index',
        'group': 'Sector Indices',
        'index_id': 11,
        'sector_id': 155,
    },
    'VNCONS': {
        'name': 'VNCONS',
        'description': 'Hàng tiêu dùng',
        'full_name': 'Consumer Staples Index',
        'group': 'Sector Indices',
        'index_id': 12,
        'sector_id': 130,
    },
    'VNCOND': {
        'name': 'VNCOND',
        'description': 'Hàng tiêu dùng thiết yếu',
        'full_name': 'Consumer Discretionary Sector Index',
        'group': 'Sector Indices',
        'index_id': 13,
        'sector_id': 133,
    },
    'VNHEAL': {
        'name': 'VNHEAL',
        'description': 'Chăm sóc sức khoẻ',
        'full_name': 'Health Care Sector Index',
        'group': 'Sector Indices',
        'index_id': 14,
        'sector_id': 135,
    },
    'VNENE': {
        'name': 'VNENE',
        'description': 'Năng lượng',
        'full_name': 'Energy Sector Index',
        'group': 'Sector Indices',
        'index_id': 15,
        'sector_id': 154,
    },
    'VNUTI': {
        'name': 'VNUTI',
        'description': 'Dịch vụ tiện ích',
        'full_name': 'Utilities Sector Index',
        'group': 'Sector Indices',
        'index_id': 16,
        'sector_id': 150,
    },
    'VNREAL': {
        'name': 'VNREAL',
        'description': 'Bất động sản',
        'full_name': 'Real Estate Sector Index',
        'group': 'Sector Indices',
        'index_id': 17,
        'sector_id': 166,
    },
    'VNFIN': {
        'name': 'VNFIN',
        'description': 'Tài chính',
        'full_name': 'Financials Sector Index',
        'group': 'Sector Indices',
        'index_id': 18,
        'sector_id': 138,
    },
    'VNMAT': {
        'name': 'VNMAT',
        'description': 'Nguyên vật liệu',
        'full_name': 'Materials Sector Index',
        'group': 'Sector Indices',
        'index_id': 19,
        'sector_id': 143,
    },

    # Investment Indices (Bộ chỉ số đầu tư)
    'VNDIAMOND': {
        'name': 'VNDIAMOND',
        'description': (
            'Chỉ số các cổ phiếu có triển vọng lớn của doanh '
            'nghiệp đầu ngành thuộc các lĩnh vực khác nhau'
        ),
        'full_name': 'Vietnam Diamond Index',
        'group': 'Investment Indices',
        'index_id': 2,
    },
    'VNFINLEAD': {
        'name': 'VNFINLEAD',
        'description': (
            'Chỉ số của các cổ phiếu thuộc nhóm ngành tài chính '
            'đầu ngành (ngân hàng, chứng khoán, bảo hiểm)'
        ),
        'full_name': 'Vietnam Leading Financial Index',
        'group': 'Investment Indices',
        'index_id': 3,
    },
    'VNFINSELECT': {
        'name': 'VNFINSELECT',
        'description': (
            'Chỉ số của các cổ phiếu đại diện cho ngành tài '
            'chính, đến từ những công ty chứng khoán, bảo hiểm'
        ),
        'full_name': 'Vietnam Financial Select Sector Index',
        'group': 'Investment Indices',
        'index_id': 4,
    },

    # VNX Indices (HNX)
    'VNX50': {
        'name': 'VNX50',
        'description': (
            '50 cổ phiếu vốn hóa lớn nhất trên toàn bộ thị '
            'trường HOSE và HNX'
        ),
        'full_name': 'VNX50 Index',
        'group': 'VNX Indices',
        'index_id': 4,
    },
    'VNXALL': {
        'name': 'VNXALL',
        'description': 'Tất cả cổ phiếu trên toàn bộ thị trường HOSE và HNX',
        'full_name': 'VNX All Index',
        'group': 'VNX Indices',
        'index_id': 1,
    },
}

# Quick lookup: symbol -> ID (for backward compatibility)
INDICES_MAP = {sym: info['index_id'] for sym, info in INDICES_INFO.items()}

# Index groupings for reference and iteration
INDEX_GROUPS = {
    'HOSE Indices': [
        'VN30', 'VNMID', 'VNSML', 'VN100', 'VNALL', 'VNSI'
    ],
    'Sector Indices': [
        'VNIT', 'VNIND', 'VNCONS', 'VNCOND', 'VNHEAL', 'VNENE',
        'VNUTI', 'VNREAL', 'VNFIN', 'VNMAT'
    ],
    'Investment Indices': [
        'VNDIAMOND', 'VNFINLEAD', 'VNFINSELECT'
    ],
    'VNX Indices': [
        'VNX50', 'VNXALL'
    ],
}

# =============================================================================
# INDUSTRY CLASSIFICATION (ICB - Bộ phân loại ICB)
# =============================================================================
# Sector IDs for filtering and categorization from HOSE
SECTOR_IDS = {
    126: 'Dịch vụ viễn thông',
    130: 'Hàng tiêu dùng',
    133: 'Hàng tiêu dùng thiết yếu',
    135: 'Chăm sóc sức khoẻ',
    138: 'Tài chính',
    143: 'Nguyên vật liệu',
    150: 'Dịch vụ tiện ích',
    154: 'Năng lượng',
    155: 'Công nghiệp',
    159: 'Công nghệ thông tin',
    166: 'Bất động sản',
}

# =============================================================================
# EXCHANGE INFORMATION
# =============================================================================
# Stock exchange codes and names
EXCHANGES = {
    'HOSE': 'Sở giao dịch Hà Nội (HOSE)',
    'HNX': 'Sở giao dịch Hà Nội (HNX)',
    'UPCOM': 'Sở giao dịch Hà Nội (UPCOM)',
}
