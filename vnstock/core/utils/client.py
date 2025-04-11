"""API client utilities for vnstock data sources."""

import requests
import json
from typing import Dict, Any, Optional, Union
from vnstock.core.utils.logger import get_logger

logger = get_logger(__name__)

def send_request(
    url: str,
    headers: Dict[str, str],
    method: str = "GET",
    params: Optional[Dict] = None,
    payload: Optional[Union[Dict, str]] = None,
    show_log: bool = False,
    timeout: int = 30
) -> Dict[str, Any]:
    """
    Centralized function for making API requests with consistent error handling.
    
    Supports sending payload as either a raw string or as a JSON object (provided as a dict). 
    For JSON payloads, the function will automatically serialize the dictionary.

    Args:
        url (str): The URL of the API endpoint.
        headers (Dict[str, str]): HTTP request headers.
        method (str, optional): HTTP method ("GET" or "POST"). Defaults to "GET".
        params (Optional[Dict], optional): Query parameters for GET requests. Defaults to None.
        payload (Optional[Union[Dict, str]], optional): 
            The request payload. Can be a dictionary (for JSON payload) or a raw string. Defaults to None.
        show_log (bool, optional): Flag to enable logging for the request details. Defaults to False.
        timeout (int, optional): Timeout in seconds for the HTTP request. Defaults to 30.
    
    Returns:
        Dict[str, Any]: The JSON-decoded response from the API.
    
    Raises:
        ConnectionError: If the API request fails or returns a non-200 status code.
        ValueError: If payload is provided in an unsupported type.
    """
    if show_log:
        logger.info(f"{method.upper()} request to {url}")
        if params:
            logger.info(f"Params: {params}")
        if payload:
            logger.info(f"Payload: {payload}")

    try:
        if method.upper() == "GET":
            response = requests.get(url, headers=headers, params=params, timeout=timeout)
        else:  # POST method
            # If payload is provided, determine if it's a dict (to be serialized as JSON) or a raw string.
            if payload is not None:
                if isinstance(payload, dict):
                    # Serialize dictionary to JSON formatted string.
                    data_arg = json.dumps(payload)
                elif isinstance(payload, str):
                    # Use the raw payload as is.
                    data_arg = payload
                else:
                    raise ValueError("Payload must be either a dictionary or a raw string.")
            else:
                data_arg = None

            response = requests.post(url, headers=headers, data=data_arg, timeout=timeout)

        # Check if the response status code is 200 (OK)
        if response.status_code != 200:
            raise ConnectionError(
                f"Failed to fetch data: {response.status_code} - {response.reason}"
            )

        data = response.json()

        if show_log:
            logger.info(f"Response data: {data}")
            logger.info(f"Response status: {response.status_code}")

        return data
    except requests.exceptions.RequestException as e:
        error_msg = f"API request failed: {str(e)}"
        logger.error(error_msg)
        raise ConnectionError(error_msg)
