
"""
API client utilities for vnstock data sources.

This module provides utilities to send requests to vnstock data sources, supporting multiple modes of sending (direct, via proxy) and multiple proxy selection modes (try, rotate, random, single).

Functions:
- send_request: interface for all modes of sending requests
- send_request_direct: send request directly
- send_request_hf_proxy: send request via Hugging Face proxy
- send_proxy_request: gửi request qua proxy thông thường
"""

import requests
import json
import random
from typing import Dict, Any, Optional, Union, List
from enum import Enum
from pydantic import BaseModel
from vnstock.core.utils.logger import get_logger

# Khởi tạo logger cho module
logger = get_logger(__name__)

# Model cấu hình proxy dùng chung cho toàn bộ dự án
class ProxyConfig(BaseModel):
    """
    Cấu hình proxy cho các request API.
    Sử dụng cho các class/module cần truyền proxy.
    """
    proxy_list: Optional[List[str]] = None
    proxy_mode: 'ProxyMode' = 'try'
    request_mode: 'RequestMode' = 'direct'
    hf_proxy_url: Optional[str] = None

# Khởi tạo logger cho module
logger = get_logger(__name__)

class ProxyMode(Enum):
    """
    Các chế độ sử dụng proxy khi gửi request:
    - TRY: Thử lần lượt từng proxy cho đến khi thành công
    - ROTATE: Luân phiên proxy sau mỗi lần gọi
    - RANDOM: Chọn ngẫu nhiên proxy cho mỗi lần gọi
    - SINGLE: Luôn dùng proxy đầu tiên
    """
    TRY = "try"
    ROTATE = "rotate"
    RANDOM = "random"
    SINGLE = "single"

class RequestMode(Enum):
    """
    Các chế độ gửi request:
    - DIRECT: Gửi trực tiếp không qua proxy
    - PROXY: Gửi qua proxy thông thường
    - HF_PROXY: Gửi qua Hugging Face proxy
    """
    DIRECT = "direct"
    PROXY = "proxy"
    HF_PROXY = "hf_proxy"

# Biến toàn cục để theo dõi index proxy hiện tại cho chế độ ROTATE
_current_proxy_index = 0

# Danh sách các Hugging Face proxy URL (có thể mở rộng)
HF_PROXY_URLS = [
    "https://YOUR_SPACE_NAME.hf.space/proxy",
    # Thêm các HF proxy khác nếu cần
]

def build_proxy_dict(proxy_url: str) -> Dict[str, str]:
    """
    Chuyển đổi proxy URL thành dict format cho requests.
    Args:
        proxy_url (str): URL của proxy
    Returns:
        Dict[str, str]: Dict cấu hình proxy cho requests
    """
    return {"http": proxy_url, "https": proxy_url}

def get_proxy_by_mode(proxy_list: List[str], mode: ProxyMode) -> str:
    """
    Lấy proxy từ danh sách proxy theo chế độ đã chọn.
    Args:
        proxy_list (List[str]): Danh sách proxy URL
        mode (ProxyMode): Chế độ chọn proxy
    Returns:
        str: Proxy URL được chọn
    """
    global _current_proxy_index
    # Kiểm tra danh sách proxy
    if not proxy_list:
        raise ValueError("Proxy list is empty")
    # Chọn proxy theo từng mode
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

def create_hf_proxy_payload(url: str, headers: dict, method: str = "GET", payload=None) -> dict:
    """
    Tạo payload để gửi qua Hugging Face proxy.
    Args:
        url (str): URL endpoint cần truy cập
        headers (dict): Header cho request
        method (str): Phương thức HTTP
        payload: Dữ liệu gửi đi
    Returns:
        dict: Payload gửi tới HF proxy
    """
    return {
        "url": url,
        "headers": headers,
        "method": method,
        "payload": payload
    }

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
    hf_proxy_url: Optional[str] = None
) -> Dict[str, Any]:
    """
    Interface trung tâm cho tất cả các mode gửi request.
    Tùy theo request_mode và proxy_mode sẽ chọn cách gửi request phù hợp.
    Args:
        url (str): Địa chỉ endpoint
        headers (Dict[str, str]): Header cho request
        method (str): "GET" hoặc "POST". Mặc định "GET"
        params (Optional[Dict]): Tham số query cho GET
        payload (Optional[Union[Dict, str]]): Dữ liệu gửi đi (POST)
        show_log (bool): Bật log chi tiết
        timeout (int): Timeout (giây)
        proxy_list (Optional[List[str]]): Danh sách proxy URLs (cho PROXY mode)
        proxy_mode (Union[ProxyMode, str]): Chế độ sử dụng proxy
        request_mode (Union[RequestMode, str]): Chế độ gửi request
        hf_proxy_url (Optional[str]): URL của Hugging Face proxy
    Returns:
        Dict[str, Any]: Dữ liệu JSON trả về
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
    # Xử lý theo từng chế độ gửi request
    if request_mode == RequestMode.HF_PROXY:
        # Gửi qua Hugging Face proxy
        if proxy_mode == ProxyMode.TRY and len(HF_PROXY_URLS) > 1:
            # Thử lần lượt các HF proxy cho đến khi thành công
            last_exception = None
            for hf_url in HF_PROXY_URLS:
                try:
                    if show_log:
                        logger.info(f"Trying HF proxy: {hf_url}")
                    return send_request_hf_proxy(
                        url, headers, method, params, payload, timeout, hf_url
                    )
                except ConnectionError as e:
                    last_exception = e
                    if show_log:
                        logger.warning(f"HF proxy {hf_url} failed: {e}")
                    continue
            raise ConnectionError(f"All HF proxies failed. Last error: {last_exception}")
        else:
            # Chọn HF proxy theo mode
            if len(HF_PROXY_URLS) > 1:
                selected_hf_proxy = get_proxy_by_mode(HF_PROXY_URLS, proxy_mode)
            else:
                selected_hf_proxy = hf_proxy_url or HF_PROXY_URLS[0]
            if show_log:
                logger.info(f"Using HF proxy: {selected_hf_proxy}")
            return send_request_hf_proxy(
                url, headers, method, params, payload, timeout, selected_hf_proxy
            )
    elif request_mode == RequestMode.PROXY:
        # Gửi qua proxy thông thường
        if not proxy_list:
            raise ValueError("proxy_list is required for PROXY mode")
        if proxy_mode == ProxyMode.TRY:
            # Thử lần lượt từng proxy cho đến khi thành công
            last_exception = None
            for proxy_url in proxy_list:
                try:
                    if show_log:
                        logger.info(f"Trying proxy: {proxy_url}")
                    proxies = build_proxy_dict(proxy_url)
                    return send_request_direct(
                        url, headers, method, params, payload, timeout, proxies
                    )
                except ConnectionError as e:
                    last_exception = e
                    if show_log:
                        logger.warning(f"Proxy {proxy_url} failed: {e}")
                    continue
            raise ConnectionError(f"All proxies failed. Last error: {last_exception}")
        else:
            # Chọn proxy theo mode
            selected_proxy = get_proxy_by_mode(proxy_list, proxy_mode)
            proxies = build_proxy_dict(selected_proxy)
            if show_log:
                logger.info(f"Using proxy ({proxy_mode.value} mode): {selected_proxy}")
            return send_request_direct(
                url, headers, method, params, payload, timeout, proxies
            )
    else:  # RequestMode.DIRECT
        # Gửi trực tiếp không qua proxy
        if show_log:
            logger.info("Sending direct request (no proxy)")
        return send_request_direct(
            url, headers, method, params, payload, timeout, proxies=None
        )

def send_request_hf_proxy(
    url: str,
    headers: Dict[str, str],
    method: str = "GET",
    params: Optional[Dict] = None,
    payload: Optional[Union[Dict, str]] = None,
    timeout: int = 30,
    hf_proxy_url: str = None
) -> Dict[str, Any]:
    """
    Gửi request qua Hugging Face proxy.
    Args:
        url (str): Endpoint URL cần truy cập
        headers (Dict[str, str]): Header cho request
        method (str): "GET" hoặc "POST"
        params (Optional[Dict]): Tham số query cho GET
        payload (Optional[Union[Dict, str]]): Dữ liệu gửi đi (POST)
        timeout (int): Timeout (giây)
        hf_proxy_url (str): URL của Hugging Face proxy
    Returns:
        Dict[str, Any]: Dữ liệu JSON trả về
    """
    if not hf_proxy_url:
        hf_proxy_url = HF_PROXY_URLS[0]
    # Xử lý query parameters cho GET
    target_url = url
    if params and method.upper() == "GET":
        query_string = "&".join([f"{k}={v}" for k, v in params.items()])
        target_url = f"{url}?{query_string}"
    # Tạo payload cho HF proxy
    hf_payload = create_hf_proxy_payload(
        url=target_url,
        headers=headers,
        method=method,
        payload=payload
    )
    # Headers cho request tới HF proxy
    hf_headers = {
        "Content-Type": "application/json",
        "Accept": "application/json"
    }
    # Gửi request qua HF proxy bằng POST
    return send_request_direct(
        url=hf_proxy_url,
        headers=hf_headers,
        method="POST",
        payload=hf_payload,
        timeout=timeout
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
    Gửi request trực tiếp tới endpoint, không qua proxy đặc biệt.
    Args:
        url (str): Endpoint URL
        headers (Dict[str, str]): Header cho request
        method (str): "GET" hoặc "POST"
        params (Optional[Dict]): Tham số query cho GET
        payload (Optional[Union[Dict, str]]): Dữ liệu gửi đi (POST)
        timeout (int): Timeout (giây)
        proxies (Optional[Dict[str, str]]): Dict proxy nếu có
    Returns:
        Dict[str, Any]: Dữ liệu JSON trả về
    Raises:
        ConnectionError: Nếu request thất bại hoặc trả về mã lỗi
    """
    try:
        # Xử lý GET/POST
        if method.upper() == "GET":
            response = requests.get(
                url, headers=headers, params=params, timeout=timeout, proxies=proxies
            )
        else:  # POST
            if payload is not None:
                if isinstance(payload, dict):
                    data_arg = json.dumps(payload)
                elif isinstance(payload, str):
                    data_arg = payload
                else:
                    raise ValueError("Payload must be either a dictionary or a raw string.")
            else:
                data_arg = None
            response = requests.post(
                url, headers=headers, data=data_arg, timeout=timeout, proxies=proxies
            )
        # Kiểm tra mã trả về
        if response.status_code != 200:
            raise ConnectionError(
                f"Failed to fetch data: {response.status_code} - {response.reason}"
            )
        return response.json()
    except requests.exceptions.RequestException as e:
        error_msg = f"API request failed: {str(e)}"
        logger.error(error_msg)
        raise ConnectionError(error_msg)

def reset_proxy_rotation():
    """
    Reset proxy rotation index về 0.
    Dùng khi muốn bắt đầu lại vòng quay proxy ở chế độ ROTATE.
    """
    global _current_proxy_index
    _current_proxy_index = 0

# Các hàm tiện lợi cho từng mode gửi request
def send_direct_request(url: str, headers: Dict[str, str], **kwargs):
    """
    Gửi request trực tiếp không qua proxy.
    Args:
        url (str): Endpoint URL
        headers (Dict[str, str]): Header cho request
        **kwargs: Các tham số bổ sung cho send_request
    Returns:
        Dict[str, Any]: Dữ liệu JSON trả về
    """
    return send_request(url, headers, request_mode=RequestMode.DIRECT, **kwargs)

def send_proxy_request(url: str, headers: Dict[str, str], proxy_list: List[str], **kwargs):
    """
    Gửi request qua proxy thông thường.
    Args:
        url (str): Endpoint URL
        headers (Dict[str, str]): Header cho request
        proxy_list (List[str]): Danh sách proxy URL
        **kwargs: Các tham số bổ sung cho send_request
    Returns:
        Dict[str, Any]: Dữ liệu JSON trả về
    """
    return send_request(url, headers, proxy_list=proxy_list, request_mode=RequestMode.PROXY, **kwargs)

def send_hf_proxy_request(url: str, headers: Dict[str, str], **kwargs):
    """
    Gửi request qua Hugging Face proxy.
    Args:
        url (str): Endpoint URL
        headers (Dict[str, str]): Header cho request
        **kwargs: Các tham số bổ sung cho send_request
    Returns:
        Dict[str, Any]: Dữ liệu JSON trả về
    """
    return send_request(url, headers, request_mode=RequestMode.HF_PROXY, **kwargs)
