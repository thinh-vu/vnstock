from datetime import datetime, timedelta

import requests

from vnstock.core.utils.logger import get_logger
from vnstock.explorer.msn.const import _CRYPTO_ID_MAP, _CURRENCY_ID_MAP, _GLOBAL_INDICES

logger = get_logger(__name__)


def msn_apikey(headers, version="20240430", show_log=False):
    """
    Get MSN apikey to use for data queries.
    Lấy apikey của MSN để sử dụng cho các truy vấn dữ liệu.

    Args:
        - headers (required): Header của request (Request header).
        - version (optional): Phiên bản của apikey, thường là giá trị ngày tháng của hôm đó. Mặc định là None. (API version, usually today's date (e.g., 20240527). Default is None.)
        - show_log (optional): Hiển thị thông tin log giúp debug dễ dàng. Mặc định là False (Show log info for debugging. Default is False).
    """
    scope = """{"audienceMode":"adult",
                        "browser":{"browserType":"chrome","version":"0","ismobile":"false"},
                        "deviceFormFactor":"desktop","domain":"www.msn.com",
                        "locale":{"content":{"language":"vi","market":"vn"},"display":{"language":"vi","market":"vn"}},
                        "ocid":"hpmsn","os":"macos","platform":"web",
                        "pageType":"financestockdetails"}
                        """
    if version is None:
        today = (datetime.now() - timedelta(hours=7)).strftime("%Y%m%d")
        version = today

    url = f"https://assets.msn.com/resolver/api/resolve/v3/config/?expType=AppConfig&expInstance=default&apptype=finance&v={version}.168&targetScope={scope}"
    if show_log:
        logger.info(f"Requesting apikey from {url}")

    try:
        response = requests.request("GET", url, headers=headers, timeout=10)
        response.raise_for_status()  # Raise an exception for bad status codes

        # Check if response is empty
        if not response.text.strip():
            raise ValueError("Empty response from MSN API")

        # Try to parse JSON
        try:
            data = response.json()
        except requests.exceptions.JSONDecodeError as e:
            logger.error(
                f"Failed to parse JSON response. Status: {response.status_code}, Text: {response.text[:200]}..."
            )
            raise ValueError(f"Invalid JSON response from MSN API: {str(e)}")  # noqa: B904

        if show_log:
            logger.info(f"Response: {data}")

        # Check if expected structure exists
        try:
            apikey = data["configs"]["shared/msn-ns/HoroscopeAnswerCardWC/default"][
                "properties"
            ]["horoscopeAnswerServiceClientSettings"]["apikey"]
        except KeyError as e:
            logger.error(f"Expected API key structure not found in response: {str(e)}")
            logger.error(
                f"Available keys in response: {list(data.keys()) if isinstance(data, dict) else 'Not a dict'}"
            )
            raise ValueError(f"API key not found in MSN response structure: {str(e)}")  # noqa: B904

        return apikey

    except requests.exceptions.RequestException as e:
        logger.error(f"Network error when requesting MSN API key: {str(e)}")
        raise ConnectionError(f"Failed to connect to MSN API: {str(e)}")  # noqa: B904
    except Exception as e:
        logger.error(f"Unexpected error in msn_apikey: {str(e)}")
        raise


def get_asset_type(symbol_id):
    symbol_id = symbol_id.upper()
    if symbol_id in _CURRENCY_ID_MAP.values() or symbol_id in _CURRENCY_ID_MAP.keys():
        return "currency"
    elif symbol_id in _CRYPTO_ID_MAP.values() or symbol_id in _CRYPTO_ID_MAP.keys():
        return "crypto"
    elif symbol_id in _GLOBAL_INDICES.values() or symbol_id in _GLOBAL_INDICES.keys():
        return "index"
    else:
        return "Unknown"
