"""
API client utilities for vnstock data sources.

This module provides a single, direct way to send requests to vnstock data
sources. Requests are sent from the caller's own network connection; the
library does not manage, rotate or supply network intermediaries.

Functions:
- send_request: send a request to a data source endpoint
"""

import json
import time
from typing import Any, Dict, Optional, Union

import requests

from vnstock.config import Config
from vnstock.core.exceptions import CircuitOpenError
from vnstock.core.utils.block_detect import (
    build_block_error,
    describe_cooldown,
    detect_block,
    host_of,
)
from vnstock.core.utils.circuit import circuit_check, circuit_key, circuit_trip
from vnstock.core.utils.logger import get_logger

# Initialize logger for module
logger = get_logger(__name__)


def send_request(
    url: str,
    headers: Dict[str, str],
    method: str = "GET",
    params: Optional[Dict] = None,
    payload: Optional[Union[Dict, str]] = None,
    show_log: bool = False,
    timeout: int = 30,
) -> Dict[str, Any]:
    """
    Send a request to a data source endpoint and return the JSON response.

    Args:
        url (str): Endpoint address
        headers (Dict[str, str]): Headers for request
        method (str): "GET" or "POST". Default "GET"
        params (Optional[Dict]): Query parameters for GET
        payload (Optional[Union[Dict, str]]): Data to send (POST)
        show_log (bool): Enable detailed logging
        timeout (int): Timeout in seconds

    Returns:
        Dict[str, Any]: Returned JSON data

    Raises:
        ConnectionError: If the request fails or returns an error code
    """
    # --- Google Colab Restriction Check ---
    if url and isinstance(url, str) and "vietcap.com.vn" in url:
        try:
            from vnstock.core.utils.env import is_colab

            if is_colab():
                raise EnvironmentError(
                    "Lỗi môi trường: Nguồn dữ liệu VCI chặn các địa chỉ IP từ Google Cloud. "
                    "Do đó, bạn không thể truy xuất dữ liệu từ nguồn này trên Google Colab. "
                    "Vui lòng cài đặt thư viện trên máy cục bộ (local) để tiếp tục sử dụng.\n"
                    "Environment Error: VCI data source blocks IP addresses from Google Cloud. "
                    "Therefore, you can not retrieve data from this source on Google Colab. "
                    "Please install the package on your local machine to continue using it."
                )
        except ImportError:
            pass
    # --------------------------------------

    if show_log:
        logger.info(f"{method.upper()} request to {url}")
        if params:
            logger.info(f"Params: {params}")
        if payload:
            logger.info(f"Payload: {payload}")

    # Stop inside a cooldown window without opening a connection: a loop over a
    # symbol list must not keep hammering a host that just said to back off.
    key = circuit_key(url)
    remaining = circuit_check(key)
    if remaining is not None:
        host = host_of(url)
        raise CircuitOpenError(
            describe_cooldown(host, remaining),
            remaining=remaining,
            url=url,
            host=host,
        )

    response = _perform_request(url, headers, method, params, payload, timeout)

    # Look for block markers before the status check: a browser-challenge page
    # is routinely served with HTTP 200, so a status-only check lets it through
    # and the caller gets an empty result with no explanation.
    signal = detect_block(response)
    if signal is not None:
        logger.warning(
            "Block markers detected at %s: %s (%s)",
            host_of(url),
            signal.reason,
            signal.evidence,
        )
        # The server named a wait and it is short enough: wait it out exactly once.
        if (
            signal.kind == "rate_limit"
            and signal.retry_after
            and 0 < signal.retry_after <= Config.RETRY_AFTER_MAX_WAIT
        ):
            logger.warning(
                "Source asked for a %.0fs wait; waiting it out and retrying once.",
                signal.retry_after,
            )
            time.sleep(signal.retry_after)
            response = _perform_request(url, headers, method, params, payload, timeout)
            signal = detect_block(response)

        if signal is not None:
            cooldown = circuit_trip(key, signal)
            # No proxy hint here: vnstock does not manage network intermediaries,
            # so pointing at proxy configuration would name something that does
            # not exist in this package.
            raise build_block_error(signal, url, cooldown)

    # Check response status
    if response.status_code != 200:
        msg = f"Failed to fetch data: {response.status_code} - {response.reason}"
        raise ConnectionError(msg)
    return response.json()


def _perform_request(
    url: str,
    headers: Dict[str, str],
    method: str,
    params: Optional[Dict],
    payload: Optional[Union[Dict, str]],
    timeout: int,
) -> requests.Response:
    """Send the request and hand back the raw response.

    Kept apart from the block-handling logic above so the Retry-After path can
    replay exactly the same call without duplicating it.
    """
    try:
        if method.upper() == "GET":
            return requests.get(url, headers=headers, params=params, timeout=timeout)

        if payload is not None:
            if isinstance(payload, dict):
                data_arg = json.dumps(payload)
            elif isinstance(payload, str):
                data_arg = payload
            else:
                msg = "Payload must be either a dict or a raw string."
                raise ValueError(msg)
        else:
            data_arg = None
        return requests.post(url, headers=headers, data=data_arg, timeout=timeout)
    except requests.exceptions.RequestException as e:
        error_msg = f"API request failed: {str(e)}"
        logger.error(error_msg)
        raise ConnectionError(error_msg) from e
