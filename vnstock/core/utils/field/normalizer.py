"""
Field name normalization utilities.

Provides tools for converting field names to standardized formats
including snake_case conversion and Vietnamese text handling.
"""

import re
from enum import Enum
from typing import Dict, Optional, Tuple

# Import Vietnamese text normalization functions from parser module for consistency
from vnstock.core.utils.parser import VIETNAMESE_CHAR_MAP, normalize_vietnamese_text_to_snake_case


class FieldDisplayMode(Enum):
    """Field display modes for field filtering."""
    STANDARDIZED_ONLY = "standardized_only"  # Only standardized fields
    ALL_FIELDS = "all_fields"  # All fields including non-standardized
    AUTO_CONVERT = "auto_convert"  # Auto-convert non-standardized to snake_case


class FieldNormalizer:
    """Normalize field names to snake_case format."""
    
    def __init__(self):
        # Use Vietnamese character mapping from parser module for consistency
        self.vietnamese_map = VIETNAMESE_CHAR_MAP
        self.special_mappings = self._create_special_mappings()
    
    def _create_special_mappings(self) -> Dict[str, str]:
        """Create special mappings for common financial terms."""
        return {
            # Income Statement
            'thu_nhap_lai': 'interest_income',
            'chi_phi_lai': 'interest_expense',
            'thu_nhap_lai_thuan': 'net_interest_income',
            'thu_nhap_hoat_dong_dich_vu': 'fee_commission_income',
            'chi_phi_hoat_dong_dich_vu': 'fee_commission_expense',
            'lai_lo_thuan_hoat_dong_dich_vu': 'net_fee_commission_income',
            'lai_lo_thuan_kinh_doanh_ngoai_hoi': 'net_fx_trading_income',
            'lai_lo_thuan_mua_ban_chung_khoan_kinh_doanh': 'net_trading_securities_income',
            'lai_lo_thuan_mua_ban_chung_khoan_dau_tu': 'net_investment_securities_income',
            'thu_nhap_khac': 'other_income',
            'chi_phi_khac': 'other_expenses',
            'lai_lo_thuan_khac': 'net_other_income',
            'thu_nhap_gop_von': 'capital_contribution_income',
            'chi_phi_hoat_dong': 'operating_expenses',
            'loi_nhuan_thuan_hoat_dong_kinh_doanh': 'operating_profit',
            'chi_phi_du_phong_rui_ro_tin_dung': 'credit_loss_provision',
            'loi_nhuan_truoc_thue': 'profit_before_tax',
            'chi_phi_thue_tndn': 'corporate_income_tax',
            'chi_phi_thue_tndn_hien_hanh': 'current_income_tax_expense',
            'chi_phi_thue_tndn_hoan_lai': 'deferred_income_tax_expense',
            'loi_nhuan_sau_thue': 'net_profit_after_tax',
            'loi_ich_co_dong_thieu_so': 'minority_interest',
            'loi_nhuan_sau_thue_co_dong_ngan_hang_me': 'net_profit_attributable_parent',
            'lai_co_ban_tren_co_phieu': 'earnings_per_share',
            
            # Balance Sheet
            'tai_san_co_dinh': 'fixed_assets',
            'tai_san_co_dinh_hinh': 'tangible_fixed_assets',
            'tai_san_co_dinh_vo_hinh': 'intangible_fixed_assets',
            'tai_san_co_dinh_thue_tai_chinh': 'finance_leased_fixed_assets',
            'nguyen_gia_tscd': 'fixed_assets_cost',
            'hao_mon_tscd': 'accumulated_depreciation',
            'dau_tu_dai_han_khac': 'other_long_term_investments',
            'du_phong_giam_gia_dau_tu_dai_han': 'investment_provision',
            'bat_dong_san_dau_tu': 'investment_properties',
            'nguyen_gia_bdsdt': 'investment_properties_cost',
            'hao_mon_bdsdt': 'accumulated_depreciation_investment_properties',
            'tai_san_co_khac': 'other_assets',
            'cac_khoan_phai_thu': 'accounts_receivable',
            'tai_san_thue_tndn_hoan_lai': 'deferred_tax_assets',
            'loi_the_thuong_mai': 'goodwill',
            'du_phong_rui_ro_tai_san_co_khac': 'other_assets_provision',
            'tong_cong_tai_san': 'total_assets',
            
            # Liabilities
            'khoan_no_chinh_phu': 'government_borrowings',
            'vay_cac_tctd_khac': 'other_credit_institution_borrowings',
            'tien_gui_cac_tctd_khac': 'other_credit_institution_deposits',
            'thue_tndn_hoan_lai_phai_tra': 'deferred_tax_liabilities',
            'cac_khoan_no_khac': 'other_liabilities',
            'phat_hanh_giay_to_co_gia': 'valuable_papers_issued',
            'von_tai_trong_uy_thac_dau_tu': 'investment_trust_capital',
            'con_cu_tai_chinh_phai_sinh': 'derivatives',
            'tien_gui_khach_hang': 'customer_deposits',
            'cac_khoan_lai_phi_phai_thu': 'interest_receivable',
            'tong_no_phai_tra': 'total_liabilities',
            
            # Equity
            'von_cua_tctd': 'credit_institution_capital',
            'von_dieu_le': 'charter_capital',
            'von_cac_quy': 'reserves',
            'quy_cua_tctd': 'credit_institution_reserves',
            'von_dau_tu_xdcb': 'construction_investment_reserves',
            'von_khac': 'other_capital',
            'co_phieu_uu_dai': 'preferred_stock',
            'co_phieu_quy': 'treasury_shares',
            'thang_du_von_co_phieu': 'share_premium',
            'loi_nhuan_chua_phan_phoi': 'undistributed_earnings',
            'loi_ich_co_dong_khong_kiem_soat': 'non_controlling_interest',
            'tong_no_phai_tra_va_von_chu_so_huu': 'total_liabilities_equity',
            
            # Cash Flow
            'luu_chuyen_tien_thuan_hoat_dong_kinh_doanh': 'net_cash_from_operations',
            'luu_chuyen_tien_thuan_hoat_dong_dau_tu': 'net_cash_from_investing',
            'luu_chuyen_tien_thuan_hoat_dong_tai_chinh': 'net_cash_from_financing',
            'mua_samp_tai_san_co_dinh': 'purchase_fixed_assets',
            'tien_thu_thanh_ly_nhuong_ban_tscd': 'proceeds_from_sale_fixed_assets',
            'tien_chi_thanh_ly_nhuong_ban_tscd': 'cost_of_sale_fixed_assets',
            'mua_samp_bat_dong_san_dau_tu': 'purchase_investment_properties',
            'tien_thu_ban_thanh_ly_bat_dong_san_dau_tu': 'proceeds_from_sale_investment_properties',
            'tien_chi_ban_thanh_ly_bat_dong_san_dau_tu': 'cost_of_sale_investment_properties',
            'tang_von_co_phieu': 'equity_issuance_proceeds',
            'tang_giam_tien_gui_khach_hang': 'change_customer_deposits',
            'tang_giam_phathanh_giay_to_co_gia': 'change_valuable_papers_issued',
            'tang_giam_von_tai_trong': 'change_investment_trust_capital',
            'tang_giam_con_cu_tai_chinh': 'change_derivatives',
            'tang_giam_con_no_hoat_dong': 'change_other_operating_liabilities',
        }
    
    def normalize_vietnamese_to_snake_case(self, text: str) -> str:
        """
        Convert Vietnamese text to snake_case using parser module for consistency.
        
        Args:
            text: Vietnamese text to normalize
            
        Returns:
            Normalized snake_case string
        """
        if not text:
            return ""
        
        # Use the robust Vietnamese normalization from parser module
        return normalize_vietnamese_text_to_snake_case(
            text, 
            keep_numbers=True, 
            remove_common_words=False,
            preserve_acronyms=False
        )
    
    def normalize_english_to_snake_case(self, text: str) -> str:
        """
        Convert English text to snake_case.
        
        Args:
            text: English text to normalize
            
        Returns:
            Normalized snake_case string
        """
        if not text:
            return ""
        
        # Remove numbering and special characters
        text = re.sub(r'^[\d\.\s]*', '', text.strip())
        
        # Handle parentheses content
        text = re.sub(r'\([^)]*\)', '', text)
        
        # Remove special characters and convert to snake_case
        text = re.sub(r'[^\w\s]', '', text)
        text = re.sub(r'\s+', '_', text.strip())
        text = re.sub(r'_+', '_', text)
        text = text.lower()
        
        return text
    
    def normalize_field_name(self, text: str, language: str = 'auto') -> str:
        """
        Normalize field name to snake_case using parser module for consistency.
        
        Args:
            text: Field name to normalize
            language: Language hint ('vi', 'en', 'auto')
            
        Returns:
            Normalized snake_case string
        """
        if not text:
            return ""
        
        # Try to detect language if auto
        if language == 'auto':
            # Simple heuristic: if contains Vietnamese characters, treat as Vietnamese
            if any(char in self.vietnamese_map for char in text):
                language = 'vi'
            else:
                language = 'en'
        
        # Normalize based on language
        if language == 'vi':
            normalized = self.normalize_vietnamese_to_snake_case(text)
        else:
            normalized = self.normalize_english_to_snake_case(text)
        
        # Check for special mappings
        if normalized in self.special_mappings:
            return self.special_mappings[normalized]
        
        return normalized
    
    def create_unique_name(self, base_name: str, field_id: str, used_names: set) -> str:
        """
        Create unique field name to avoid conflicts.
        
        Args:
            base_name: Base field name
            field_id: Field identifier
            used_names: Set of already used names
            
        Returns:
            Unique field name
        """
        if base_name not in used_names:
            return base_name
        
        # Add field_id suffix to ensure uniqueness
        unique_name = f"{base_name}_{field_id}"
        
        # If still conflict, add counter
        counter = 1
        while unique_name in used_names:
            unique_name = f"{base_name}_{field_id}_{counter}"
            counter += 1
        
        return unique_name
