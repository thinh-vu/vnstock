"""
STANDARDIZED INDICES AND MARKET CONSTANTS - USAGE GUIDE

Location: vnstock/common/indices.py

This module provides centralized, standardized reference for indices, sectors,
and market constants used across ALL data sources (VCI, TCBS, MSN, etc.).

Usage by data source wrappers:
- VCI wrapper (explorer/vci/) uses this for consistent index/sector handling
- TCBS wrapper (explorer/tcbs/) uses this for consistent index/sector handling  
- MSN wrapper (explorer/msn/) uses this for consistent index/sector handling
- Any new data source wrapper can use this for standardized lookups

=============================================================================
BASIC USAGE
=============================================================================

1. Get all indices as DataFrame:
   
   from vnstock.common.indices import get_all_indices
   df = get_all_indices()
   # Returns: symbol, name, description, full_name, group, index_id

2. Get indices by group:
   
   from vnstock.common.indices import get_indices_by_group
   hose_df = get_indices_by_group('HOSE Indices')
   sector_df = get_indices_by_group('Sector Indices')
   
3. Get full info for one index:
   
   from vnstock.common.indices import get_index_info
   info = get_index_info('VN30')
   # Returns dict with: name, description, full_name, group, index_id

4. Get just the ID (quick lookup):
   
   from vnstock.common.indices import get_index_id
   idx_id = get_index_id('VN30')  # Returns: 5

5. Get all sectors:
   
   from vnstock.common.indices import get_all_sectors
   sectors_df = get_all_sectors()
   # Returns: sector_id, name

=============================================================================
REFERENCE DATA
=============================================================================

INDICES_INFO (config.py):
- VN30, VNMID, VNSML, VN100, VNALL, VNSI (HOSE Indices)
- VNIT, VNIND, VNCONS, VNCOND, VNHEAL, VNENE, VNUTI, VNREAL, VNFIN, VNMAT
  (Sector Indices)
- VNDIAMOND, VNFINLEAD, VNFINSELECT (Investment Indices)
- VNX50, VNXALL (VNX Indices)

EXCHANGES:
- HOSE: Sở giao dịch Hà Nội (HOSE)
- HNX: Sở giao dịch Hà Nội (HNX)
- UPCOM: Sở giao dịch Hà Nội (UPCOM)

SECTOR_IDS (from HOSE):
- 126: Dịch vụ viễn thông
- 130: Hàng tiêu dùng
- 133: Hàng tiêu dùng thiết yếu
- ... (11 sectors total)

=============================================================================
WHY CENTRALIZED IN common/ ?
=============================================================================

This is NOT part of any specific data source. It's:
- Shared infrastructure used by all data sources
- Standardized reference that all wrappers implement against
- Configuration that applies across the entire library

Location: vnstock/common/ (not vnstock/core/utils/)
Reason: Represents standardized DATA/CONSTANTS, not utilities/helpers
"""
