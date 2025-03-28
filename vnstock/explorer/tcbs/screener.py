"""
Stock Screener Module for Vietnamese markets.

This module provides functionality to screen stocks based on various parameters
using TCBS data source.
"""

import json
from typing import Dict, Any, Optional

import pandas as pd

from .const import _BASE_URL, _SCREENER_MAPPING
from vnai import optimize_execution
from vnstock.core.utils.logger import get_logger
from vnstock.core.utils.user_agent import get_headers
from vnstock.core.utils.parser import camel_to_snake
from vnstock.core.utils import client

logger = get_logger(__name__)


class Screener:
    """Class for screening stocks based on various parameters."""

    def __init__(self, random_agent: bool = False, show_log: bool = False):
        """
        Initialize the Screener with configuration parameters.

        Parameters:
            random_agent (bool): Whether to use a random user agent for requests.
            show_log (bool): Whether to display logs during operations.
        """
        self.base_url = _BASE_URL  # Ensure _BASE_URL contains the correct endpoint
        self.data_source = 'TCBS'
        self.headers = get_headers(data_source=self.data_source, random_agent=random_agent)
        self.show_log = show_log

    @optimize_execution("TCBS")
    def stock(self, 
              params: Dict[str, Any] = {"exchangeName": "HOSE,HNX,UPCOM"}, 
              limit: int = 50, 
              id: Optional[str] = None, 
              lang: str = "vi") -> pd.DataFrame:
        """
        Get stock screening insights from TCBS Stock Screener.

        Parameters:
            params (dict): Dictionary of parameters for stock screening. Keys should be filter names,
                           and values can be single values or (min, max) tuples.
            limit (int): Number of data points per page. Default is 50.
            id (str): Optional ID of the stock screener.
            lang (str): Directive language for multi-language fields (e.g., "vi" or "en"). Default is "vi".

        Returns:
            pd.DataFrame: DataFrame containing the screened stock data with standardized column names,
                          and cells processed to show the value for the directive language.
        
        Raises:
            ValueError: If API request fails or response format is unexpected.
        """
        url = f"{self.base_url}/ligo/v1/watchlist/preview"
        
        # Create a list of filters based on the params dictionary
        filters = []
        for key, value in params.items():
            # If value is a tuple (min, max), create two filters
            if isinstance(value, tuple) and len(value) == 2:
                min_value, max_value = value
                filters.append({
                    "key": key,
                    "operator": ">=",
                    "value": min_value
                })
                filters.append({
                    "key": key,
                    "operator": "<=",
                    "value": max_value
                })
            # Exclude "size" from filters as it is handled separately
            elif key != "size":
                filters.append({
                    "key": key,
                    "value": value,
                    "operator": "="
                })
        
        # Use size from params if provided; otherwise, use the limit parameter
        requested_size = params.get("size", limit)
        
        # Prepare payload as a dictionary (it will be serialized within the API client)
        payload = {
            "tcbsID": id,
            "filters": filters,
            "size": requested_size
        }

        if self.show_log:
            logger.info(f"base_url: {url}")
            logger.info(f"Fetching stock data with params: {params}")
            logger.info(f"Headers: {self.headers}")
            logger.info(f"Payload: {payload}")
        
        try:
            # Send request to get response using the API client
            response = client.send_request(
                url=url,
                headers=self.headers,
                method="POST",
                payload=payload,
                show_log=self.show_log
            )
            
            # Validate response structure
            if not response or 'searchData' not in response or 'pageContent' not in response['searchData']:
                raise ValueError("Invalid response format from API")
            
            # Create DataFrame from response data
            df = pd.DataFrame(response['searchData']['pageContent'])
            
            # Skip further processing if DataFrame is empty
            if df.empty:
                logger.warning("No data returned from stock screener API")
                return df
                
            # Drop columns that are entirely NA
            df = df.dropna(axis=1, how="all")

            # Convert column names from camelCase to snake_case
            df.columns = [camel_to_snake(col) for col in df.columns]

            # Rename columns based on _SCREENER_MAPPING if available
            df.rename(columns={col: _SCREENER_MAPPING.get(col, col) for col in df.columns}, inplace=True)

            # List of columns to process for multi-language dictionary extraction
            cols_to_process = [
                "price_vs_sma100",
                "has_financial_report",
                "breakout",
                "rsi14_status",
                "dmi_signal",
                "bolling_band_signal",
                "price_vs_sma10",
                "price_vs_sma50",
                "sar_vs_macd_hist",
                "macd_histogram",
                "tcbs_buy_sell_signal",
                "tcbs_recommend",
                "foreign_transaction",
                "price_vs_sma20",
                "price_vs_sma5",
                "company_name",    
                "industry",   
                "exchange",
                "uptrend",
                "price_break_out52_week",
                "price_wash_out52_week",
                "heating_up"
            ]
            
            # Process the specified columns:
            # If a cell is a dictionary with language keys, extract the value for the directive language.
            for col in cols_to_process:
                if col in df.columns:
                    df[col] = df[col].apply(lambda cell: cell.get(lang) if isinstance(cell, dict) and lang in cell else cell)

            # replace value HOSE to HSX for the column exchange
            try:
                df['exchange'] = df['exchange'].replace('HOSE', 'HSX')
                df = df.drop(columns=['company_name'])
            except Exception as e:
                logger.error(f"Lỗi khi thực hiện chuẩn hoá cột: {str(e)}")
                pass
            
            return df
            
        except Exception as e:
            logger.error(f"Error fetching stock data: {str(e)}")
            raise
