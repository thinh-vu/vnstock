"""API client utilities for vnstock data sources."""

import requests
import json
from typing import Dict, Any, Optional
from vnstock.core.utils.logger import get_logger

logger = get_logger(__name__)

def send_request(url: str, headers: Dict[str, str], method: str = "GET", 
                    params: Optional[Dict] = None, payload: Optional[Dict] = None,
                    show_log: bool = False, timeout: int = 30) -> Dict[str, Any]:
    """Centralized function for making API requests with consistent error handling."""
    if show_log:
        logger.info(f"{method} request to {url}")
        if params:
            logger.info(f"Params: {params}")
        if payload:
            logger.info(f"Payload: {payload}")

    try:
        if method.upper() == "GET":
            response = requests.get(url, headers=headers, params=params, timeout=timeout)
        else:  # POST
            response = requests.post(
                url, 
                headers=headers, 
                data=json.dumps(payload) if payload else None,
                timeout=timeout
            )
            
        if response.status_code != 200:
            raise ConnectionError(f"Failed to fetch data: {response.status_code} - {response.reason}")
            
        data = response.json()
        
        if show_log:
            logger.info(f"Response status: {response.status_code}")
            
        return data
    except requests.exceptions.RequestException as e:
        error_msg = f"API request failed: {str(e)}"
        logger.error(error_msg)
        raise ConnectionError(error_msg)
