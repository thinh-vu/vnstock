"""
Field validation utilities.

Provides tools for validating field names, checking coverage,
and generating validation reports.
"""

import logging
from typing import Dict, List, Optional, Set, Tuple
from .mapper import FieldMapper

logger = logging.getLogger(__name__)


class FieldValidator:
    """Validate field names and coverage."""
    
    def __init__(self, field_mapper: Optional[FieldMapper] = None):
        """
        Initialize field validator.
        
        Args:
            field_mapper: Field mapper instance
        """
        self.field_mapper = field_mapper or FieldMapper()
    
    def validate_dataframe_columns(self, columns: List[str], report_type: str) -> Dict:
        """
        Validate DataFrame columns against standardized fields.
        
        Args:
            columns: List of DataFrame column names
            report_type: Type of report (income_statement, balance_sheet, etc.)
            
        Returns:
            Validation report dictionary
        """
        standardized_fields = set(self.field_mapper.reverse_mappings.keys())
        column_set = set(columns)
        
        # Find standardized and non-standardized fields
        standardized_columns = column_set & standardized_fields
        non_standardized_columns = column_set - standardized_fields
        
        # Calculate coverage
        coverage_pct = (len(standardized_columns) / len(columns) * 100) if columns else 0
        
        validation = {
            'total_columns': len(columns),
            'standardized_columns': len(standardized_columns),
            'non_standardized_columns': len(non_standardized_columns),
            'coverage_pct': coverage_pct,
            'standardized_field_names': list(standardized_columns),
            'non_standardized_field_names': list(non_standardized_columns),
            'report_type': report_type,
            'validation_passed': len(non_standardized_columns) == 0
        }
        
        return validation
    
    def validate_field_name(self, field_name: str) -> Dict:
        """
        Validate a single field name.
        
        Args:
            field_name: Field name to validate
            
        Returns:
            Validation result dictionary
        """
        is_standardized = field_name in self.field_mapper.reverse_mappings
        
        # Try to normalize the field name
        normalized = self.field_mapper.normalize_field_name(field_name)
        
        validation = {
            'field_name': field_name,
            'is_standardized': is_standardized,
            'normalized_name': normalized,
            'field_id': self.field_mapper.get_field_id(field_name) if is_standardized else None,
            'field_info': self.field_mapper.get_field_info(self.field_mapper.get_field_id(field_name)) if is_standardized else None
        }
        
        return validation
    
    def check_field_coverage(self, field_ids: List[str], report_type: str) -> Dict:
        """
        Check coverage of field IDs against standardized fields.
        
        Args:
            field_ids: List of field IDs to check
            report_type: Type of report
            
        Returns:
            Coverage report dictionary
        """
        total_fields = len(field_ids)
        covered_fields = 0
        missing_fields = []
        
        for field_id in field_ids:
            if self.field_mapper.get_snake_case(str(field_id)):
                covered_fields += 1
            else:
                missing_fields.append(field_id)
        
        coverage_pct = (covered_fields / total_fields * 100) if total_fields > 0 else 0
        
        report = {
            'total_field_ids': total_fields,
            'covered_field_ids': covered_fields,
            'missing_field_ids': len(missing_fields),
            'coverage_pct': coverage_pct,
            'missing_field_names': missing_fields,
            'report_type': report_type
        }
        
        return report
    
    def generate_validation_report(self, validations: List[Dict]) -> str:
        """
        Generate comprehensive validation report.
        
        Args:
            validations: List of validation dictionaries
            
        Returns:
            Formatted validation report
        """
        report_lines = []
        report_lines.append("=" * 80)
        report_lines.append("FIELD VALIDATION REPORT")
        report_lines.append("=" * 80)
        
        total_validations = len(validations)
        passed_validations = sum(1 for v in validations if v.get('validation_passed', False))
        
        report_lines.append(f"\nTotal Validations: {total_validations}")
        report_lines.append(f"Passed Validations: {passed_validations}")
        report_lines.append(f"Failed Validations: {total_validations - passed_validations}")
        
        if validations:
            avg_coverage = sum(v.get('coverage_pct', 0) for v in validations) / len(validations)
            report_lines.append(f"Average Coverage: {avg_coverage:.1f}%")
        
        report_lines.append(f"\n--- Validation Details ---")
        
        for i, validation in enumerate(validations, 1):
            report_lines.append(f"\n{i}. {validation.get('report_type', 'Unknown')}")
            report_lines.append(f"   Total Columns: {validation.get('total_columns', 0)}")
            report_lines.append(f"   Standardized: {validation.get('standardized_columns', 0)}")
            report_lines.append(f"   Non-standardized: {validation.get('non_standardized_columns', 0)}")
            report_lines.append(f"   Coverage: {validation.get('coverage_pct', 0):.1f}%")
            report_lines.append(f"   Status: {'✅ PASSED' if validation.get('validation_passed') else '❌ FAILED'}")
            
            if validation.get('non_standardized_field_names'):
                report_lines.append(f"   Non-standardized fields: {validation['non_standardized_field_names'][:5]}")
                if len(validation['non_standardized_field_names']) > 5:
                    report_lines.append(f"     ... and {len(validation['non_standardized_field_names']) - 5} more")
        
        report_lines.append("\n" + "=" * 80)
        
        return "\n".join(report_lines)
    
    def suggest_field_name(self, field_name: str) -> Dict:
        """
        Suggest standardized field name for non-standardized field.
        
        Args:
            field_name: Non-standardized field name
            
        Returns:
            Suggestion dictionary
        """
        normalized = self.field_mapper.normalize_field_name(field_name)
        
        # Check if normalized name conflicts with existing names
        is_conflict = normalized in self.field_mapper.reverse_mappings
        
        # Create unique name if needed
        if is_conflict:
            # Generate a unique name
            used_names = set(self.field_mapper.reverse_mappings.keys())
            unique_name = self.field_mapper.normalizer.create_unique_name(
                normalized, 
                "suggested", 
                used_names
            )
        else:
            unique_name = normalized
        
        suggestion = {
            'original_field': field_name,
            'suggested_name': unique_name,
            'normalized_name': normalized,
            'has_conflict': is_conflict,
            'is_standardized': field_name in self.field_mapper.reverse_mappings
        }
        
        return suggestion
    
    def batch_validate(self, dataframes: Dict[str, List[str]]) -> Dict:
        """
        Validate multiple DataFrames.
        
        Args:
            dataframes: Dictionary of {report_type: [column_names]}
            
        Returns:
            Batch validation results
        """
        results = {}
        
        for report_type, columns in dataframes.items():
            validation = self.validate_dataframe_columns(columns, report_type)
            results[report_type] = validation
        
        # Calculate overall statistics
        total_columns = sum(v['total_columns'] for v in results.values())
        total_standardized = sum(v['standardized_columns'] for v in results.values())
        overall_coverage = (total_standardized / total_columns * 100) if total_columns > 0 else 0
        
        batch_results = {
            'individual_validations': results,
            'overall_statistics': {
                'total_dataframes': len(dataframes),
                'total_columns': total_columns,
                'total_standardized': total_standardized,
                'overall_coverage_pct': overall_coverage
            }
        }
        
        return batch_results
    
    def check_data_integrity(self, field_ids: List[str], expected_fields: Optional[List[str]] = None) -> Dict:
        """
        Check data integrity and completeness.
        
        Args:
            field_ids: List of field IDs found in data
            expected_fields: List of expected field IDs (optional)
            
        Returns:
            Integrity check results
        """
        found_fields = set(str(f) for f in field_ids)
        
        if expected_fields:
            expected_set = set(str(f) for f in expected_fields)
            missing_fields = expected_set - found_fields
            extra_fields = found_fields - expected_set
            completeness = (len(found_fields & expected_set) / len(expected_set) * 100) if expected_set else 0
        else:
            missing_fields = set()
            extra_fields = found_fields
            completeness = 100.0
        
        integrity_check = {
            'found_field_count': len(found_fields),
            'expected_field_count': len(expected_fields) if expected_fields else len(found_fields),
            'missing_field_count': len(missing_fields),
            'extra_field_count': len(extra_fields),
            'completeness_pct': completeness,
            'missing_field_ids': list(missing_fields),
            'extra_field_ids': list(extra_fields),
            'integrity_passed': len(missing_fields) == 0
        }
        
        return integrity_check


class FieldMismatchDetector:
    """Detect and report field mismatches."""
    
    def __init__(self, field_mapper: Optional[FieldMapper] = None):
        """
        Initialize mismatch detector.
        
        Args:
            field_mapper: Field mapper instance
        """
        self.field_mapper = field_mapper or FieldMapper()
        self.mismatches = []
    
    def detect_mismatch(self, field_name: str, report_type: str, period_type: str, symbol: str) -> Optional[Dict]:
        """
        Detect if a field name is a mismatch.
        
        Args:
            field_name: Field name to check
            report_type: Type of report
            period_type: Period type
            symbol: Stock symbol
            
        Returns:
            Mismatch information or None
        """
        if field_name in self.field_mapper.reverse_mappings:
            return None  # No mismatch
        
        # Create mismatch record
        mismatch = {
            'field_name': field_name,
            'report_type': report_type,
            'period_type': period_type,
            'symbol': symbol,
            'suggested_name': self.field_mapper.normalize_field_name(field_name),
            'severity': 'warning'  # Could be 'error', 'warning', 'info'
        }
        
        self.mismatches.append(mismatch)
        return mismatch
    
    def get_mismatch_summary(self) -> Dict:
        """
        Get summary of all detected mismatches.
        
        Returns:
            Mismatch summary dictionary
        """
        if not self.mismatches:
            return {
                'total_mismatches': 0,
                'severity_counts': {},
                'report_type_counts': {},
                'symbol_counts': {}
            }
        
        severity_counts = {}
        report_type_counts = {}
        symbol_counts = {}
        
        for mismatch in self.mismatches:
            # Count by severity
            severity = mismatch['severity']
            severity_counts[severity] = severity_counts.get(severity, 0) + 1
            
            # Count by report type
            report_type = mismatch['report_type']
            report_type_counts[report_type] = report_type_counts.get(report_type, 0) + 1
            
            # Count by symbol
            symbol = mismatch['symbol']
            symbol_counts[symbol] = symbol_counts.get(symbol, 0) + 1
        
        return {
            'total_mismatches': len(self.mismatches),
            'severity_counts': severity_counts,
            'report_type_counts': report_type_counts,
            'symbol_counts': symbol_counts
        }
    
    def generate_mismatch_report(self) -> str:
        """
        Generate mismatch report.
        
        Returns:
            Formatted mismatch report
        """
        if not self.mismatches:
            return "✅ No field mismatches detected!"
        
        summary = self.get_mismatch_summary()
        
        report_lines = []
        report_lines.append("=" * 80)
        report_lines.append("FIELD MISMATCH REPORT")
        report_lines.append("=" * 80)
        
        report_lines.append(f"\nTotal Mismatches: {summary['total_mismatches']}")
        
        if summary['severity_counts']:
            report_lines.append("\n--- Mismatches by Severity ---")
            for severity, count in sorted(summary['severity_counts'].items()):
                report_lines.append(f"  {severity}: {count}")
        
        if summary['report_type_counts']:
            report_lines.append("\n--- Mismatches by Report Type ---")
            for report_type, count in sorted(summary['report_type_counts'].items()):
                report_lines.append(f"  {report_type}: {count}")
        
        report_lines.append(f"\n--- Sample Mismatches (First 10) ---")
        for i, mismatch in enumerate(self.mismatches[:10]):
            report_lines.append(
                f"{i+1}. {mismatch['symbol']} ({mismatch['report_type']}/{mismatch['period_type']}): "
                f"'{mismatch['field_name']}' → '{mismatch['suggested_name']}'"
            )
        
        if len(self.mismatches) > 10:
            report_lines.append(f"... and {len(self.mismatches) - 10} more")
        
        report_lines.append("\n" + "=" * 80)
        
        return "\n".join(report_lines)
