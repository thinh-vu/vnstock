"""
vnstock connectors.

Provides connectors to various data sources for financial data.
"""

# Import submodules to trigger provider registration
from . import fmp  # noqa: F401

# For direct imports
from .fmp import Quote as FMPQuote

__all__ = ['fmp', 'FMPQuote']
