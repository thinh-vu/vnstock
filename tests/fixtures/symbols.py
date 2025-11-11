"""
Generate random sample symbols for comprehensive testing.

This module fetches real symbols from HOSE, HNX, UPCOM, derivatives,
covered warrants, and bonds to ensure diverse test coverage.
"""

import random
from typing import List, Dict
import pytest


@pytest.fixture(scope="session")
def real_symbols_dataset():
    """
    Fetch real symbols from exchanges for testing.
    Returns dict with symbol lists for each category.
    """
    try:
        from vnstock.api.listing import Listing
        
        listing = Listing(source='VCI', show_log=False)
        
        # Get all symbols
        all_df = listing.all_symbols(show_log=False, to_df=True)
        
        if all_df.empty:
            return _fallback_symbols()
        
        # Filter by exchange
        hose_symbols = []
        hnx_symbols = []
        upcom_symbols = []
        
        if 'exchange' in all_df.columns and 'symbol' in all_df.columns:
            hose_df = all_df[all_df['exchange'] == 'HOSE']
            hnx_df = all_df[all_df['exchange'] == 'HNX']
            upcom_df = all_df[all_df['exchange'] == 'UPCOM']
            
            hose_symbols = hose_df['symbol'].tolist()
            hnx_symbols = hnx_df['symbol'].tolist()
            upcom_symbols = upcom_df['symbol'].tolist()
        
        # Get derivatives
        derivatives = []
        try:
            futures_df = listing.all_future_indices(show_log=False)
            if not futures_df.empty and 'symbol' in futures_df.columns:
                derivatives = futures_df['symbol'].tolist()
        except Exception:
            derivatives = ['VN30F1M', 'VN30F2M', 'VN30F3M']
        
        # Get covered warrants
        covered_warrants = []
        try:
            cw_df = listing.all_covered_warrant(show_log=False)
            if not cw_df.empty and 'symbol' in cw_df.columns:
                covered_warrants = cw_df['symbol'].tolist()[:50]
        except Exception:
            covered_warrants = []
        
        # Get bonds
        bonds = []
        try:
            bonds_df = listing.all_government_bonds(show_log=False)
            if not bonds_df.empty and 'symbol' in bonds_df.columns:
                bonds = bonds_df['symbol'].tolist()[:30]
        except Exception:
            bonds = []
        
        return {
            'hose': hose_symbols,
            'hnx': hnx_symbols,
            'upcom': upcom_symbols,
            'derivatives': derivatives,
            'covered_warrants': covered_warrants,
            'bonds': bonds,
        }
    
    except Exception as e:
        print(f"Failed to fetch real symbols: {e}")
        return _fallback_symbols()


def _fallback_symbols() -> Dict[str, List[str]]:
    """Fallback symbols if API fetch fails."""
    return {
        'hose': [
            'VCB', 'VHM', 'VIC', 'VNM', 'ACB', 'MSN', 'HPG', 'TCB',
            'VPB', 'GAS', 'BID', 'CTG', 'MWG', 'VRE', 'FPT', 'POW',
            'PLX', 'SAB', 'SSI', 'HDB', 'MBB', 'STB', 'GVR', 'BCM',
            'VJC', 'PDR', 'PNJ', 'DPM', 'DGC', 'HT1'
        ],
        'hnx': [
            'PVS', 'SHS', 'NVB', 'CEO', 'VCS', 'PVI', 'PVX', 'VC3',
            'IDV', 'TNG', 'PLC', 'VCG', 'SHB', 'PVT', 'BVS', 'DTD',
            'VIG', 'HUT', 'TVC', 'MBS'
        ],
        'upcom': [
            'BST', 'ADC', 'ABI', 'APS', 'MCH', 'SVN', 'CQT', 'DHT',
            'FTS', 'HTP', 'KSK', 'LTG', 'NHP', 'PAN', 'QBS', 'SFG',
            'TIG', 'UNI', 'VHG', 'VOS'
        ],
        'derivatives': ['VN30F1M', 'VN30F2M', 'VN30F3M'],
        'covered_warrants': [],
        'bonds': [],
    }


@pytest.fixture
def random_hose_symbols(real_symbols_dataset):
    """Get 100 random HOSE symbols."""
    symbols = real_symbols_dataset['hose']
    count = min(100, len(symbols))
    return random.sample(symbols, count) if symbols else []


@pytest.fixture
def random_hnx_symbols(real_symbols_dataset):
    """Get 100 random HNX symbols."""
    symbols = real_symbols_dataset['hnx']
    count = min(100, len(symbols))
    return random.sample(symbols, count) if symbols else []


@pytest.fixture
def random_upcom_symbols(real_symbols_dataset):
    """Get 100 random UPCOM symbols."""
    symbols = real_symbols_dataset['upcom']
    count = min(100, len(symbols))
    return random.sample(symbols, count) if symbols else []


@pytest.fixture
def derivative_symbols(real_symbols_dataset):
    """Get all derivative symbols."""
    return real_symbols_dataset['derivatives']


@pytest.fixture
def sample_covered_warrants(real_symbols_dataset):
    """Get sample covered warrant symbols."""
    symbols = real_symbols_dataset['covered_warrants']
    return symbols[:20] if symbols else []


@pytest.fixture
def sample_bonds(real_symbols_dataset):
    """Get sample bond symbols."""
    symbols = real_symbols_dataset['bonds']
    return symbols[:20] if symbols else []


@pytest.fixture
def diverse_test_symbols(
    random_hose_symbols,
    random_hnx_symbols,
    random_upcom_symbols
):
    """
    Get diverse test symbols from all exchanges.
    Returns 30 symbols total (10 from each exchange).
    """
    hose_sample = random_hose_symbols[:10]
    hnx_sample = random_hnx_symbols[:10]
    upcom_sample = random_upcom_symbols[:10]
    
    return {
        'hose': hose_sample,
        'hnx': hnx_sample,
        'upcom': upcom_sample,
        'all': hose_sample + hnx_sample + upcom_sample
    }


@pytest.fixture
def all_test_symbols(
    random_hose_symbols,
    random_hnx_symbols,
    random_upcom_symbols,
    derivative_symbols,
    sample_covered_warrants,
    sample_bonds
):
    """Get all test symbols for comprehensive testing."""
    return {
        'hose': random_hose_symbols,
        'hnx': random_hnx_symbols,
        'upcom': random_upcom_symbols,
        'derivatives': derivative_symbols,
        'covered_warrants': sample_covered_warrants,
        'bonds': sample_bonds,
    }


@pytest.fixture
def test_intervals():
    """All supported time intervals."""
    return ['1m', '5m', '15m', '30m', '1h', '1D', '1W', '1M']


@pytest.fixture
def test_date_ranges():
    """Common date ranges for testing."""
    return {
        'recent': {'start': '2024-11-01', 'end': '2024-11-11'},
        'month': {'start': '2024-10-01', 'end': '2024-10-31'},
        'quarter': {'start': '2024-07-01', 'end': '2024-09-30'},
        'year': {'start': '2024-01-01', 'end': '2024-12-31'},
    }
