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
        # Import complete mappings from separate file
        from .kbs_complete_mappings import KBS_COMPLETE_MAPPINGS
        
        # Load built-in mappings
        self.mappings = KBS_COMPLETE_MAPPINGS
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
                    self.mappings = json.load(f)
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
            Snake case field name or None
        """
        mapping = self.mappings.get(field_id)
        return mapping.get('snake_case') if mapping else None
    
    def get_field_id(self, snake_case: str) -> Optional[str]:
        """
        Get field_id for snake_case name.
        
        Args:
            snake_case: Snake case field name
            
        Returns:
            Field identifier or None
        """
        return self.reverse_mappings.get(snake_case)
    
    def get_field_info(self, field_id: str) -> Optional[Dict]:
        """
        Get complete field information.
        
        Args:
            field_id: Field identifier
            
        Returns:
            Field information dictionary or None
        """
        return self.mappings.get(field_id)
    
    def normalize_field(self, field_name: str) -> str:
        """
        Normalize field name using field normalizer.
        
        Args:
            field_name: Field name to normalize
            
        Returns:
            Normalized field name
        """
        return self.normalizer.normalize_field_name(field_name)
    
    def create_mapping(self, field_id: str, item_vi: str, item_en: str = "") -> Dict:
        """
        Create field mapping dictionary.
        
        Args:
            field_id: Field identifier
            item_vi: Vietnamese field name
            item_en: English field name
            
        Returns:
            Field mapping dictionary
        """
        snake_case = self.normalize_field(item_vi if item_vi else item_en)
        
        mapping = {
            'original_vi': item_vi,
            'original_en': item_en,
            'snake_case': snake_case,
            'base_name': snake_case,
            'was_conflict': False,
            'was_standardized': False
        }
        
        return mapping
    
    def validate_mappings(self) -> List[str]:
        """
        Validate field mappings for consistency.
        
        Returns:
            List of validation warnings
        """
        warnings = []
        
        # Check for duplicate snake_case names
        snake_case_counts = {}
        for field_id, mapping in self.mappings.items():
            snake_case = mapping.get('snake_case')
            if snake_case:
                snake_case_counts[snake_case] = snake_case_counts.get(snake_case, 0) + 1
        
        for snake_case, count in snake_case_counts.items():
            if count > 1:
                warnings.append(f"Duplicate snake_case '{snake_case}' found {count} times")
        
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
        # Import complete mappings from separate file
        from .kbs_complete_mappings import KBS_COMPLETE_MAPPINGS
        
        # Load built-in mappings
        self.mappings = KBS_COMPLETE_MAPPINGS
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
        Get list of standardized field names.
        
        Args:
            report_type: Optional report type filter
            
        Returns:
            List of standardized field names
        """
        return list(self.reverse_mappings.keys())