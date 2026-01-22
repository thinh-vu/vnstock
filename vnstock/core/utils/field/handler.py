"""
Main field handler that integrates all field utilities.

Provides a high-level interface for field validation, normalization,
and mismatch detection.
"""

import logging
from typing import Dict, List, Optional, Tuple
import pandas as pd

from .normalizer import FieldNormalizer, FieldDisplayMode
from .mapper import FieldMapper, KBSFieldMapper
from .validator import FieldValidator, FieldMismatchDetector
from .kbs_complete_mappings import KBS_COMPLETE_MAPPINGS

logger = logging.getLogger(__name__)


class FieldHandler:
    """Main field handler integrating all field utilities."""
    
    def __init__(self, reference_dir: Optional[str] = None, data_source: str = 'KBS'):
        """
        Initialize field handler.
        
        Args:
            reference_dir: Directory containing field reference files
            data_source: Data source type ('KBS', 'VCI', etc.)
        """
        self.data_source = data_source
        self.normalizer = FieldNormalizer()
        
        # Initialize appropriate mapper based on data source
        if data_source == 'KBS':
            self.field_mapper = KBSFieldMapper()
        else:
            self.field_mapper = FieldMapper()
        
        self.validator = FieldValidator(self.field_mapper)
        self.mismatch_detector = FieldMismatchDetector(self.field_mapper)
        
        # Load mappings if available
        if reference_dir:
            self._load_reference_data(reference_dir)
    
    def _load_reference_data(self, reference_dir: str):
        """Load reference data from directory."""
        try:
            if self.data_source == 'KBS':
                # Load KBS mappings from kbs_complete_mappings.py
                self.field_mapper.mappings = KBS_COMPLETE_MAPPINGS.copy()
                self.field_mapper._create_reverse_mappings()
                logger.info(f"Loaded {len(KBS_COMPLETE_MAPPINGS)} KBS field mappings from kbs_complete_mappings.py")
        except Exception as e:
            logger.warning(f"Could not load reference data from {reference_dir}: {e}")
    
    def normalize_field_name(self, field_name: str, language: str = 'auto') -> str:
        """
        Normalize field name to snake_case.
        
        Args:
            field_name: Original field name
            language: Language hint ('vi', 'en', 'auto')
            
        Returns:
            Normalized snake_case name
        """
        return self.normalizer.normalize_field_name(field_name, language)
    
    def get_field_info(self, field_id: str) -> Optional[Dict]:
        """
        Get field information by field ID.
        
        Args:
            field_id: Field identifier
            
        Returns:
            Field information dictionary or None
        """
        return self.field_mapper.get_field_info(field_id)
    
    def get_snake_case(self, field_id: str) -> Optional[str]:
        """
        Get snake_case name for field ID.
        
        Args:
            field_id: Field identifier
            
        Returns:
            Snake_case name or None
        """
        return self.field_mapper.get_snake_case(field_id)
    
    def validate_fields(self, df: pd.DataFrame, report_type: str) -> Dict:
        """
        Validate DataFrame columns against standardized fields.
        
        Args:
            df: DataFrame to validate
            report_type: Type of report
            
        Returns:
            Validation report dictionary
        """
        return self.validator.validate_dataframe_columns(list(df.columns), report_type)
    
    def filter_fields(self, df: pd.DataFrame, mode: FieldDisplayMode = FieldDisplayMode.STANDARDIZED_ONLY,
                     show_warnings: bool = True) -> Tuple[pd.DataFrame, List[str]]:
        """
        Filter DataFrame columns based on display mode.
        
        Args:
            df: DataFrame to filter
            mode: Display mode
            show_warnings: Whether to show warnings
            
        Returns:
            Tuple of (filtered DataFrame, list of warnings)
        """
        warnings = []
        standardized_fields = set(self.field_mapper.reverse_mappings.keys())
        column_set = set(df.columns)
        
        if mode == FieldDisplayMode.STANDARDIZED_ONLY:
            # Keep only standardized fields
            standardized_cols = [col for col in df.columns if col in standardized_fields]
            filtered_df = df[standardized_cols]
            
            # Generate warnings for removed fields
            removed_cols = column_set - set(standardized_cols)
            if removed_cols and show_warnings:
                warnings.append(
                    f"⚠️  Removed {len(removed_cols)} non-standardized fields: "
                    f"{', '.join(sorted(removed_cols)[:5])}"
                    f"{f' and {len(removed_cols)-5} more' if len(removed_cols) > 5 else ''}"
                )
        
        elif mode == FieldDisplayMode.ALL_FIELDS:
            # Keep all fields
            filtered_df = df.copy()
            
        elif mode == FieldDisplayMode.AUTO_CONVERT:
            # Auto-convert non-standardized field names
            renamed_cols = {}
            for col in df.columns:
                if col not in standardized_fields:
                    normalized = self.normalize_field_name(col)
                    renamed_cols[col] = normalized
                    if show_warnings:
                        warnings.append(
                            f"⚠️  Auto-converted field '{col}' → '{normalized}'"
                        )
            
            filtered_df = df.rename(columns=renamed_cols)
        
        else:
            # Default to original DataFrame
            filtered_df = df.copy()
        
        return filtered_df, warnings
    
    def detect_mismatch(self, field_name: str, report_type: str, period_type: str, symbol: str) -> Optional[Dict]:
        """
        Detect field mismatch.
        
        Args:
            field_name: Field name to check
            report_type: Type of report
            period_type: Period type
            symbol: Stock symbol
            
        Returns:
            Mismatch information or None
        """
        return self.mismatch_detector.detect_mismatch(field_name, report_type, period_type, symbol)
    
    def get_mismatch_summary(self) -> Dict:
        """Get summary of all detected mismatches."""
        return self.mismatch_detector.get_mismatch_summary()
    
    def get_statistics(self) -> Dict:
        """Get field handler statistics."""
        return {
            'data_source': self.data_source,
            'total_mappings': len(self.field_mapper.get_all_mappings()),
            'unique_snake_cases': len(self.field_mapper.reverse_mappings),
            'mismatch_count': len(self.mismatch_detector.mismatches)
        }
    
    def create_field_mapping(self, field_id: str, original_vi: str, original_en: str = "", 
                             snake_case: str = "") -> Dict:
        """
        Create a field mapping.
        
        Args:
            field_id: Field identifier
            original_vi: Vietnamese field name
            original_en: English field name
            snake_case: Snake_case name (auto-generated if empty)
            
        Returns:
            Field mapping dictionary
        """
        return self.field_mapper.create_mapping(field_id, original_vi, original_en, snake_case)
    
    def add_field_mapping(self, field_id: str, original_vi: str, original_en: str = "", 
                          snake_case: str = ""):
        """
        Add a field mapping.
        
        Args:
            field_id: Field identifier
            original_vi: Vietnamese field name
            original_en: English field name
            snake_case: Snake_case name (auto-generated if empty)
        """
        self.field_mapper.add_mapping(field_id, original_vi, original_en, snake_case)
    
    def save_mappings(self, output_file: str):
        """
        Save field mappings to file.
        
        Args:
            output_file: Output file path
        """
        self.field_mapper.save_mappings(output_file)
    
    def generate_validation_report(self, validations: List[Dict]) -> str:
        """
        Generate validation report.
        
        Args:
            validations: List of validation dictionaries
            
        Returns:
            Formatted validation report
        """
        return self.validator.generate_validation_report(validations)
    
    def generate_mismatch_report(self) -> str:
        """Generate mismatch report."""
        return self.mismatch_detector.generate_mismatch_report()
    
    def batch_validate(self, dataframes: Dict[str, List[str]]) -> Dict:
        """
        Validate multiple DataFrames.
        
        Args:
            dataframes: Dictionary of {report_type: [column_names]}
            
        Returns:
            Batch validation results
        """
        return self.validator.batch_validate(dataframes)
    
    def suggest_field_name(self, field_name: str) -> Dict:
        """
        Suggest standardized field name.
        
        Args:
            field_name: Field name to standardize
            
        Returns:
            Suggestion dictionary
        """
        return self.validator.suggest_field_name(field_name)
    
    def check_data_integrity(self, field_ids: List[str], expected_fields: Optional[List[str]] = None) -> Dict:
        """
        Check data integrity.
        
        Args:
            field_ids: List of field IDs found
            expected_fields: List of expected field IDs
            
        Returns:
            Integrity check results
        """
        return self.validator.check_data_integrity(field_ids, expected_fields)


class KBSFieldHandler(FieldHandler):
    """Specialized field handler for KBS data source."""
    
    def __init__(self, reference_dir: Optional[str] = None):
        """
        Initialize KBS field handler.
        
        Args:
            reference_dir: Directory containing KBS field reference files
        """
        super().__init__(reference_dir, data_source='KBS')
    
    def load_kbs_mappings(self):
        """Load KBS-specific field mappings."""
        self.field_mapper.load_kbs_mappings()
    
    def get_kbs_field_info(self, field_id: str) -> Optional[Dict]:
        """
        Get KBS field information.
        
        Args:
            field_id: KBS field identifier
            
        Returns:
            KBS field information or None
        """
        return self.field_mapper.get_kbs_field_info(field_id)
    
    def create_kbs_mapping(self, field_id: str, item_vi: str, item_en: str = "") -> Dict:
        """
        Create KBS field mapping.
        
        Args:
            field_id: KBS field identifier
            item_vi: Vietnamese field name
            item_en: English field name
            
        Returns:
            KBS field mapping dictionary
        """
        return self.field_mapper.create_kbs_mapping(field_id, item_vi, item_en)
    
    def get_standardized_kbs_fields(self, report_type: Optional[str] = None) -> List[str]:
        """
        Get standardized KBS field names.
        
        Args:
            report_type: Optional report type filter
            
        Returns:
            List of standardized field names
        """
        return self.field_mapper.get_standardized_fields(report_type)
