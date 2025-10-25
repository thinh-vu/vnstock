"""
Main entry point and orchestrator for vnstock library.

This module provides the Vnstock class which acts as the primary interface
for accessing stock, forex, crypto, index, and fund data from various sources.
"""

import logging
from typing import Optional

from vnstock.core.utils.logger import get_logger
from vnstock.common.data import (
    StockComponents,
    MSNComponents,
    Fund,
)
from vnstock.explorer.msn.const import (
    _CURRENCY_ID_MAP,
    _GLOBAL_INDICES,
    _CRYPTO_ID_MAP,
)

logger = get_logger(__name__)


class Vnstock:
    """
    Main entry point for the vnstock library.
    
    Provides unified access to stock data, forex quotes, crypto prices,
    world indices, and fund information from multiple data sources.
    
    Attributes:
        SUPPORTED_SOURCES (list): List of supported data sources.
        msn_symbol_map (dict): Mapping of MSN symbols.
    
    Example:
        >>> stock = Vnstock()
        >>> acb = stock.stock('ACB')  # Vietnamese stock
        >>> btc = stock.crypto('BTC')  # Bitcoin price
        >>> djia = stock.world_index('DJI')  # Dow Jones
    """
    
    SUPPORTED_SOURCES = ["VCI", "TCBS", "MSN"]
    msn_symbol_map = {
        **_CURRENCY_ID_MAP,
        **_GLOBAL_INDICES,
        **_CRYPTO_ID_MAP,
    }

    def __init__(self, symbol: Optional[str] = None, source: str = "VCI",
                 show_log: bool = True):
        """
        Initialize Vnstock client.
        
        Args:
            symbol (str, optional): Default symbol for stock queries.
                Defaults to None.
            source (str): Default data source. One of VCI, TCBS, MSN.
                Defaults to "VCI".
            show_log (bool): Whether to display log messages.
                Defaults to True.
        
        Raises:
            ValueError: If source is not in SUPPORTED_SOURCES.
        """
        self.symbol = symbol
        self.source = source.upper()
        self.show_log = show_log
        
        if self.source not in self.SUPPORTED_SOURCES:
            raise ValueError(
                f"Supported sources: {', '.join(self.SUPPORTED_SOURCES)}. "
                f"Got: {source}"
            )
        
        if not show_log:
            logger.setLevel(logging.CRITICAL)

    def stock(self, symbol: Optional[str] = None,
              source: Optional[str] = None) -> StockComponents:
        """
        Get stock data components for a symbol.
        
        Args:
            symbol (str, optional): Stock symbol (e.g., 'ACB', 'VNM').
                Defaults to 'VN30F1M' if not specified.
            source (str, optional): Data source override.
                Defaults to instance source if not specified.
        
        Returns:
            StockComponents: Object with quote, company, finance, etc.
        
        Example:
            >>> acb = stock.stock('ACB')
            >>> history = acb.quote.history('2023-01-01', '2023-12-31')
            >>> profile = acb.company.profile()
        """
        if symbol is None:
            symbol = 'VN30F1M'
            logger.info(
                "Symbol not specified, using default: VN30F1M"
            )
        else:
            self.symbol = symbol

        if source is None:
            source = self.source

        return StockComponents(
            self.symbol,
            source,
            show_log=self.show_log
        )

    def fx(self, symbol: Optional[str] = 'EURUSD',
            source: Optional[str] = "MSN") -> MSNComponents:
        """
        Get forex (currency) data.
        
        Args:
            symbol (str): Currency pair (e.g., 'EURUSD', 'GBPUSD').
                Defaults to 'EURUSD'.
            source (str): Data source. Only MSN is supported.
                Defaults to "MSN".
        
        Returns:
            MSNComponents: Object with quote and listing data.
        
        Example:
            >>> eurusd = stock.fx('EURUSD')
            >>> history = eurusd.quote.history('2023-01-01', '2023-12-31')
        """
        if symbol:
            mapped_symbol = self.msn_symbol_map.get(symbol, symbol)
            logger.debug(f"Mapped {symbol} -> {mapped_symbol}")
        else:
            mapped_symbol = symbol

        return MSNComponents(mapped_symbol, source)

    def crypto(self, symbol: Optional[str] = 'BTC',
               source: Optional[str] = "MSN") -> MSNComponents:
        """
        Get cryptocurrency data.
        
        Args:
            symbol (str): Crypto symbol (e.g., 'BTC', 'ETH').
                Defaults to 'BTC'.
            source (str): Data source. Only MSN is supported.
                Defaults to "MSN".
        
        Returns:
            MSNComponents: Object with quote and listing data.
        
        Example:
            >>> btc = stock.crypto('BTC')
            >>> history = btc.quote.history('2023-01-01', '2023-12-31')
        """
        if symbol:
            mapped_symbol = self.msn_symbol_map.get(symbol, symbol)
            logger.debug(f"Mapped {symbol} -> {mapped_symbol}")
        else:
            mapped_symbol = symbol

        return MSNComponents(mapped_symbol, source)

    def world_index(self, symbol: Optional[str] = 'DJI',
                    source: Optional[str] = "MSN") -> MSNComponents:
        """
        Get world market index data.
        
        Args:
            symbol (str): Index symbol (e.g., 'DJI', 'IXIC').
                Defaults to 'DJI' (Dow Jones).
            source (str): Data source. Only MSN is supported.
                Defaults to "MSN".
        
        Returns:
            MSNComponents: Object with quote and listing data.
        
        Example:
            >>> djia = stock.world_index('DJI')
            >>> history = djia.quote.history('2023-01-01', '2023-12-31')
        """
        if symbol:
            mapped_symbol = self.msn_symbol_map.get(symbol, symbol)
            logger.debug(f"Mapped {symbol} -> {mapped_symbol}")
        else:
            mapped_symbol = symbol

        return MSNComponents(mapped_symbol, source)

    def fund(self, source: str = "FMARKET") -> Fund:
        """
        Get fund/mutual fund data.
        
        Args:
            source (str): Data source. Only FMARKET is currently supported.
                Defaults to "FMARKET".
        
        Returns:
            Fund: Object with fund data and methods.
        
        Example:
            >>> funds = stock.fund()
            >>> all_funds = funds.listing()
        """
        return Fund(source)
