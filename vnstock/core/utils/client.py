"""
API client utilities for vnstock data sources.

This module provides utilities to send requests to vnstock data sources,
supporting multiple modes of sending (direct, via proxy) and multiple proxy
selection modes (try, rotate, random, single).

Functions:
- send_request: interface for all modes of sending requests
- send_request_direct: send request directly
- send_proxy_request: send request via standard proxy
"""

import requests
import json
import random
from typing import Dict, Any, Optional, Union, List
from enum import Enum
from pydantic import BaseModel
from vnstock.core.utils.logger import get_logger
from vnstock.core.utils.proxy_manager import proxy_manager

# Initialize logger for module
logger = get_logger(__name__)


# Proxy configuration model for use across the project
class ProxyConfig(BaseModel):
    """
    Configuration for proxy usage in API requests.
    Use for classes/modules that need to pass proxy settings.
    """
    proxy_list: Optional[List[str]] = None
    proxy_mode: 'ProxyMode' = 'try'
    request_mode: 'RequestMode' = 'direct'


logger = get_logger(__name__)


class ProxyMode(Enum):
    """
    Proxy usage modes for sending requests:
    - TRY: Try each proxy sequentially until successful
    - ROTATE: Rotate proxy after each call
    - RANDOM: Select random proxy for each call
    - SINGLE: Always use first proxy
    - AUTO: Auto-fetch proxies if none provided
    """
    TRY = "try"
    ROTATE = "rotate"
    RANDOM = "random"
    SINGLE = "single"
    AUTO = "auto"


class RequestMode(Enum):
    """
    Request sending modes:
    - DIRECT: Send directly without proxy
    - PROXY: Send via standard proxy
    """
    DIRECT = "direct"
    PROXY = "proxy"


# Global variable to track current proxy index for ROTATE mode
_current_proxy_index = 0


def build_proxy_dict(proxy_url: str) -> Dict[str, str]:
    """
    Convert proxy URL to dict format for requests library.
    
    Args:
        proxy_url (str): URL of the proxy
        
    Returns:
        Dict[str, str]: Proxy configuration dict for requests
    """
    return {"http": proxy_url, "https": proxy_url}

def get_proxy_by_mode(proxy_list: List[str], mode: ProxyMode) -> str:
    """
    Get proxy from the list by selected mode.
    
    Args:
        proxy_list (List[str]): List of proxy URLs
        mode (ProxyMode): Proxy selection mode
        
    Returns:
        str: Selected proxy URL
    """
    global _current_proxy_index
    # Check proxy list
    if not proxy_list:
        raise ValueError("Proxy list is empty")
    # Select proxy by mode
    if mode == ProxyMode.SINGLE:
        return proxy_list[0]
    elif mode == ProxyMode.RANDOM:
        return random.choice(proxy_list)
    elif mode == ProxyMode.ROTATE:
        proxy = proxy_list[_current_proxy_index % len(proxy_list)]
        _current_proxy_index += 1
        return proxy
    else:  # TRY mode
        return proxy_list[0]



def send_request(
    url: str,
    headers: Dict[str, str],
    method: str = "GET",
    params: Optional[Dict] = None,
    payload: Optional[Union[Dict, str]] = None,
    show_log: bool = False,
    timeout: int = 30,
    proxy_list: Optional[List[str]] = None,
    proxy_mode: Union[ProxyMode, str] = ProxyMode.TRY,
    request_mode: Union[RequestMode, str] = RequestMode.DIRECT,
) -> Dict[str, Any]:
    """
    Central interface for all request sending modes.
    
    Based on request_mode and proxy_mode, selects appropriate
    request sending method.
    
    Args:
        url (str): Endpoint address
        headers (Dict[str, str]): Headers for request
        method (str): "GET" or "POST". Default "GET"
        params (Optional[Dict]): Query parameters for GET
        payload (Optional[Union[Dict, str]]): Data to send (POST)
        show_log (bool): Enable detailed logging
        timeout (int): Timeout in seconds
        proxy_list (Optional[List[str]]): List of proxy URLs
          (for PROXY mode)
        proxy_mode (Union[ProxyMode, str]): Proxy usage mode
        request_mode (Union[RequestMode, str]): Request sending mode
        
    Returns:
        Dict[str, Any]: Returned JSON data
        
    Raises:
        ConnectionError: Nếu tất cả proxy đều thất bại hoặc request lỗi
    """
    # Chuyển đổi string thành enum nếu cần
    if isinstance(proxy_mode, str):
        try:
            proxy_mode = ProxyMode(proxy_mode)
        except ValueError:
            raise ValueError(f"Invalid proxy_mode: {proxy_mode}")
    if isinstance(request_mode, str):
        try:
            request_mode = RequestMode(request_mode)
        except ValueError:
            raise ValueError(f"Invalid request_mode: {request_mode}")
    # Log thông tin request nếu cần
    if show_log:
        logger.info(f"{method.upper()} request to {url} (mode: {request_mode.value})")
        if params:
            logger.info(f"Params: {params}")
        if payload:
            logger.info(f"Payload: {payload}")
    # Handle different request modes
    if request_mode == RequestMode.PROXY:
        # Send via standard proxy
        if proxy_mode == ProxyMode.AUTO and not proxy_list:
            # Auto-fetch proxies if none provided
            if show_log:
                logger.info("Auto-fetching proxies via ProxyManager...")
            proxy_list = proxy_manager.get_fresh_proxies(use_cache=True)
            if not proxy_list:
                # If auto-fetch failed, fallback to direct or error? 
                # For now let's error to be explicit, or fallback to direct if user prefers?
                # Sticking to error to match "PROXY mode" intent.
                raise ConnectionError("Failed to auto-fetch valid proxies.")

        if not proxy_list:
            raise ValueError(
                "proxy_list is required for PROXY mode"
            )
        if proxy_mode == ProxyMode.TRY:
            # Try each proxy sequentially until successful
            last_exception = None
            for proxy_url in proxy_list:
                try:
                    if show_log:
                        logger.info(f"Trying proxy: {proxy_url}")
                    proxies = build_proxy_dict(proxy_url)
                    return send_request_direct(
                        url, headers, method, params, payload,
                        timeout, proxies
                    )
                except ConnectionError as e:
                    last_exception = e
                    if show_log:
                        logger.warning(
                            f"Proxy {proxy_url} failed: {e}"
                        )
                    continue
            msg = (
                f"All proxies failed. "
                f"Last error: {last_exception}"
            )
            raise ConnectionError(msg)
        else:
            # Select proxy by mode
            selected_proxy = get_proxy_by_mode(
                proxy_list, proxy_mode
            )
            proxies = build_proxy_dict(selected_proxy)
            if show_log:
                msg = (
                    f"Using proxy ({proxy_mode.value} mode): "
                    f"{selected_proxy}"
                )
                logger.info(msg)
            return send_request_direct(
                url, headers, method, params, payload, timeout,
                proxies
            )
    else:  # RequestMode.DIRECT
        # Send direct request without proxy
        if show_log:
            logger.info("Sending direct request (no proxy)")
        return send_request_direct(
            url, headers, method, params, payload, timeout,
            proxies=None
        )


def send_request_direct(
    url: str,
    headers: Dict[str, str],
    method: str = "GET",
    params: Optional[Dict] = None,
    payload: Optional[Union[Dict, str]] = None,
    timeout: int = 30,
    proxies: Optional[Dict[str, str]] = None
) -> Dict[str, Any]:
    """
    Send request directly to endpoint without special proxy.
    
    Args:
        url (str): Endpoint URL
        headers (Dict[str, str]): Headers for request
        method (str): "GET" or "POST"
        params (Optional[Dict]): Query parameters for GET
        payload (Optional[Union[Dict, str]]): Data to send (POST)
        timeout (int): Timeout in seconds
        proxies (Optional[Dict[str, str]]): Proxy dict if any
        
    Returns:
        Dict[str, Any]: Returned JSON data
        
    Raises:
        ConnectionError: If request fails or returns error code
    """
    try:
        # Handle GET/POST
        if method.upper() == "GET":
            response = requests.get(
                url, headers=headers, params=params,
                timeout=timeout, proxies=proxies
            )
        else:  # POST
            if payload is not None:
                if isinstance(payload, dict):
                    data_arg = json.dumps(payload)
                elif isinstance(payload, str):
                    data_arg = payload
                else:
                    msg = (
                        "Payload must be either a dict "
                        "or a raw string."
                    )
                    raise ValueError(msg)
            else:
                data_arg = None
            response = requests.post(
                url, headers=headers, data=data_arg,
                timeout=timeout, proxies=proxies
            )
        # Check response status
        if response.status_code != 200:
            msg = (
                f"Failed to fetch data: "
                f"{response.status_code} - {response.reason}"
            )
            raise ConnectionError(msg)
        return response.json()
    except requests.exceptions.RequestException as e:
        error_msg = f"API request failed: {str(e)}"
        logger.error(error_msg)
        raise ConnectionError(error_msg)


def reset_proxy_rotation():
    """
    Reset proxy rotation index to 0.
    
    Use when you want to restart the proxy rotation cycle in ROTATE mode.
    """
    global _current_proxy_index
    _current_proxy_index = 0


def send_direct_request(
    url: str, headers: Dict[str, str], **kwargs
):
    """
    Send request directly without proxy.
    
    Args:
        url (str): Endpoint URL
        headers (Dict[str, str]): Headers for request
        **kwargs: Additional parameters for send_request
        
    Returns:
        Dict[str, Any]: Returned JSON data
    """
    return send_request(
        url, headers, request_mode=RequestMode.DIRECT, **kwargs
    )

def send_proxy_request(
    url: str, headers: Dict[str, str], proxy_list: List[str],
    **kwargs
):
    """
    Send request via standard proxy.
    
    Args:
        url (str): Endpoint URL
        headers (Dict[str, str]): Headers for request
        proxy_list (List[str]): List of proxy URLs
        **kwargs: Additional parameters for send_request
        
    Returns:
        Dict[str, Any]: Returned JSON data
    """
    return send_request(
        url, headers, proxy_list=proxy_list,
        request_mode=RequestMode.PROXY, **kwargs
    )



