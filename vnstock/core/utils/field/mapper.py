"""
Field mapping utilities.

Provides tools for loading and managing field mappings between
different naming conventions and data sources.
"""

import json
import logging
from pathlib import Path
from typing import Dict, Optional, List
from .normalizer import FieldNormalizer

logger = logging.getLogger(__name__)


class FieldMapper:
    """Manage field mappings between different naming conventions."""
    
    def __init__(self, mapping_file: Optional[str] = None):
        """
        Initialize field mapper.
        
        Args:
            mapping_file: Path to field mapping file
        """
        self.normalizer = FieldNormalizer()
        self.mappings = {}
        self.reverse_mappings = {}
        
        if mapping_file:
            self.load_mappings(mapping_file)
        else:
            self._load_builtin_mappings()
    
    def _load_builtin_mappings(self):
        """Load built-in KBS standardized field mappings."""
        # Import built-in mappings from separate file
        from .kbs_mappings import KBS_BUILTIN_MAPPINGS
        
        # Load built-in mappings
        self.mappings = KBS_BUILTIN_MAPPINGS
        self._create_reverse_mappings()
        
        logger.info(f"Loaded {len(self.mappings)} built-in KBS field mappings")
    
    def load_mappings(self, mapping_file: str):
        """
        Load field mappings from JSON file.
        
        Args:
            mapping_file: Path to JSON mapping file
        """
        try:
            mapping_path = Path(mapping_file)
            if mapping_path.exists():
                with open(mapping_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                # Handle different mapping formats
                if isinstance(data, dict):
                    # Format: {field_id: {snake_case: ..., original_vi: ..., original_en: ...}}
                    self.mappings = data
                elif isinstance(data, list):
                    # Format: [{field_id: ..., snake_case: ..., ...}]
                    self.mappings = {str(item['field_id']): item for item in data}
                
                # Create reverse mappings
                self._create_reverse_mappings()
                
                logger.info(f"Loaded {len(self.mappings)} field mappings from {mapping_file}")
            else:
                logger.warning(f"Mapping file not found: {mapping_file}")
        except Exception as e:
            logger.error(f"Error loading mappings from {mapping_file}: {e}")
    
    def _create_reverse_mappings(self):
        """Create reverse mappings from snake_case to field_id."""
        self.reverse_mappings = {}
        for field_id, mapping in self.mappings.items():
            snake_case = mapping.get('snake_case')
            if snake_case:
                self.reverse_mappings[snake_case] = field_id
    
    def get_snake_case(self, field_id: str) -> Optional[str]:
        """
        Get snake_case name for field_id.
        
        Args:
            field_id: Field identifier
            
        Returns:
            Snake_case field name or None
        """
        mapping = self.mappings.get(str(field_id))
        return mapping.get('snake_case') if mapping else None
    
    def get_field_info(self, field_id: str) -> Optional[Dict]:
        """
        Get complete field information.
        
        Args:
            field_id: Field identifier
            
        Returns:
            Field information dictionary or None
        """
        return self.mappings.get(str(field_id))
    
    def get_field_id(self, snake_case: str) -> Optional[str]:
        """
        Get field_id from snake_case name.
        
        Args:
            snake_case: Snake_case field name
            
        Returns:
            Field identifier or None
        """
        return self.reverse_mappings.get(snake_case)
    
    def normalize_field(self, field_name: str, language: str = 'auto') -> str:
        """
        Normalize field name to snake_case.
        
        Args:
            field_name: Original field name
            language: Language hint ('vi', 'en', 'auto')
            
        Returns:
            Normalized snake_case name
        """
        return self.normalizer.normalize_field_name(field_name, language)
    
    def create_mapping(self, field_id: str, original_vi: str, original_en: str = "", 
                      snake_case: str = "") -> Dict:
        """
        Create a field mapping entry.
        
        Args:
            field_id: Field identifier
            original_vi: Vietnamese field name
            original_en: English field name
            snake_case: Snake_case name (auto-generated if empty)
            
        Returns:
            Field mapping dictionary
        """
        if not snake_case:
            # Auto-generate snake_case from Vietnamese name
            snake_case = self.normalizer.normalize_field_name(original_vi, 'vi')
        
        mapping = {
            'field_id': field_id,
            'original_vi': original_vi,
            'original_en': original_en,
            'snake_case': snake_case
        }
        
        return mapping
    
    def add_mapping(self, field_id: str, original_vi: str, original_en: str = "", 
                   snake_case: str = ""):
        """
        Add a field mapping.
        
        Args:
            field_id: Field identifier
            original_vi: Vietnamese field name
            original_en: English field name
            snake_case: Snake_case name (auto-generated if empty)
        """
        mapping = self.create_mapping(field_id, original_vi, original_en, snake_case)
        self.mappings[str(field_id)] = mapping
        self._create_reverse_mappings()
    
    def save_mappings(self, output_file: str):
        """
        Save field mappings to JSON file.
        
        Args:
            output_file: Output file path
        """
        try:
            output_path = Path(output_file)
            output_path.parent.mkdir(parents=True, exist_ok=True)
            
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(self.mappings, f, ensure_ascii=False, indent=2)
            
            logger.info(f"Saved {len(self.mappings)} field mappings to {output_file}")
        except Exception as e:
            logger.error(f"Error saving mappings to {output_file}: {e}")
    
    def get_all_mappings(self) -> Dict:
        """Get all field mappings."""
        return self.mappings.copy()
    
    def filter_by_report_type(self, report_type: str) -> Dict:
        """
        Filter mappings by report type (if available).
        
        Args:
            report_type: Report type to filter by
            
        Returns:
            Filtered mappings
        """
        filtered = {}
        for field_id, mapping in self.mappings.items():
            # This would need report_type information in the mapping
            # For now, return all mappings
            filtered[field_id] = mapping
        
        return filtered
    
    def get_statistics(self) -> Dict:
        """Get mapping statistics."""
        stats = {
            'total_mappings': len(self.mappings),
            'unique_snake_cases': len(self.reverse_mappings),
            'has_vietnamese': 0,
            'has_english': 0,
            'auto_generated': 0
        }
        
        for mapping in self.mappings.values():
            if mapping.get('original_vi'):
                stats['has_vietnamese'] += 1
            if mapping.get('original_en'):
                stats['has_english'] += 1
        
        return stats
    
    def validate_mappings(self) -> List[str]:
        """
        Validate field mappings for consistency.
        
        Returns:
            List of validation warnings
        """
        warnings = []
        
        # Check for duplicate snake_case names
        snake_cases = [m.get('snake_case') for m in self.mappings.values()]
        duplicates = [name for name in snake_cases if snake_cases.count(name) > 1]
        
        if duplicates:
            warnings.append(f"Duplicate snake_case names found: {duplicates}")
        
        # Check for empty field names
        for field_id, mapping in self.mappings.items():
            if not mapping.get('snake_case'):
                warnings.append(f"Empty snake_case for field_id: {field_id}")
        
        return warnings


class KBSFieldMapper(FieldMapper):
    """Specialized field mapper for KBS data source."""
    
    def __init__(self):
        """Initialize KBS field mapper with built-in standardized mappings."""
        # Initialize with built-in mappings
        super().__init__(None)
        self._load_builtin_mappings()
    
    def _load_builtin_mappings(self):
        """Load built-in KBS standardized field mappings."""
        # Import built-in mappings from separate file
        from .kbs_mappings import KBS_BUILTIN_MAPPINGS
        
        # Load built-in mappings
        self.mappings = KBS_BUILTIN_MAPPINGS
        self._create_reverse_mappings()
        
        logger.info(f"Loaded {len(self.mappings)} built-in KBS field mappings")
    
    def load_kbs_mappings(self, mapping_file: Optional[str] = None):
        """Load KBS-specific field mappings."""
        if mapping_file:
            self.load_mappings(mapping_file)
        else:
            # Use built-in mappings without external file dependency
            pass
    
    def get_kbs_field_info(self, field_id: str) -> Optional[Dict]:
        """
        Get KBS field information.
        
        Args:
            field_id: KBS field identifier
            
        Returns:
            Field information or None
        """
        return self.get_field_info(field_id)
    
    def create_kbs_mapping(self, field_id: str, item_vi: str, item_en: str = "") -> Dict:
        """
        Create KBS field mapping.
        
        Args:
            field_id: KBS field identifier
            item_vi: Vietnamese field name
            item_en: English field name
            
        Returns:
            Field mapping dictionary
        """
        return self.create_mapping(field_id, item_vi, item_en)
    
    def get_standardized_fields(self, report_type: Optional[str] = None) -> List[str]:
        """
        Get standardized field names.
        
        Args:
            report_type: Optional report type filter
            
        Returns:
            List of standardized field names
        """
        if report_type:
            # This would need report type filtering logic
            pass
        
        return list(self.reverse_mappings.keys())
