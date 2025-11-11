"""
Proxy manager for vnstock - fetches and manages free proxies.

Provides functionality to:
- Fetch free proxies from proxyscrape API
- Parse and validate proxy data
- Test proxy connectivity
- Configure proxies for vnstock requests
"""

import requests
import json
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


@dataclass
class Proxy:
    """Represents a single proxy."""
    protocol: str  # http, https, socks5
    ip: str
    port: int
    country: str = ""
    speed: float = 0.0  # milliseconds
    last_checked: Optional[datetime] = None

    @property
    def address(self) -> str:
        """Return proxy address as protocol://ip:port."""
        return f"{self.protocol}://{self.ip}:{self.port}"

    @property
    def dict_format(self) -> Dict[str, str]:
        """Return proxy in dict format for requests library."""
        return {
            'http': self.address,
            'https': self.address,
        }

    def __str__(self) -> str:
        return self.address


class ProxyManager:
    """Manages proxy fetching, validation, and configuration."""

    PROXYSCRAPE_API = (
        "https://api.proxyscrape.com/v4/free-proxy-list/get"
    )

    HEADERS = {
        'accept': 'application/json, text/plain, */*',
        'accept-language': 'en-US,en;q=0.9,vi;q=0.8',
        'dnt': '1',
        'origin': 'https://vi.proxyscrape.com',
        'priority': 'u=1, i',
        'referer': 'https://vi.proxyscrape.com/',
        'sec-ch-ua': (
            '"Chromium";v="142", "Google Chrome";v="142", '
            '"Not_A Brand";v="99"'
        ),
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"macOS"',
        'sec-fetch-dest': 'empty',
        'sec-fetch-mode': 'cors',
        'sec-fetch-site': 'same-site',
        'user-agent': (
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) '
            'AppleWebKit/537.36 (KHTML, like Gecko) '
            'Chrome/142.0.0.0 Safari/537.36'
        )
    }

    def __init__(self, timeout: int = 10):
        """Initialize ProxyManager.
        
        Args:
            timeout: Request timeout in seconds
        """
        self.timeout = timeout
        self.proxies: List[Proxy] = []
        self.last_fetch: Optional[datetime] = None

    def fetch_proxies(
        self,
        limit: int = 15,
        skip: int = 0,
        protocol: str = 'protocolipport'
    ) -> List[Proxy]:
        """Fetch free proxies from proxyscrape API.
        
        Args:
            limit: Number of proxies to fetch (max 100)
            skip: Number of proxies to skip
            protocol: Proxy format (protocolipport, ipport, ip_port)
        
        Returns:
            List of Proxy objects
        """
        params = {
            'request': 'get_proxies',
            'skip': skip,
            'proxy_format': protocol,
            'format': 'json',
            'limit': min(limit, 100)  # API limit is 100
        }

        try:
            logger.info(
                f"Fetching {limit} proxies from proxyscrape API..."
            )
            response = requests.get(
                self.PROXYSCRAPE_API,
                params=params,
                headers=self.HEADERS,
                timeout=self.timeout
            )
            response.raise_for_status()

            data = response.json()

            # Check for successful response - API doesn't return 'status' field
            # Instead check if we have proxies data
            if (not data.get('proxies') or
                    not isinstance(data.get('proxies'), list)):
                logger.warning(
                    "API returned invalid data: no proxies list"
                )
                return []

            proxies = self._parse_proxy_data(data.get('proxies', []))
            self.proxies = proxies
            self.last_fetch = datetime.now()

            logger.info(f"Successfully fetched {len(proxies)} proxies")
            return proxies

        except requests.RequestException as e:
            logger.error(f"Failed to fetch proxies: {e}")
            return []
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse proxy response: {e}")
            return []

    def _parse_proxy_data(self, proxy_list: List[Dict]) -> List[Proxy]:
        """Parse proxy data from API response.
        
        Args:
            proxy_list: List of proxy data dictionaries
        
        Returns:
            List of Proxy objects
        """
        proxies = []

        for proxy_data in proxy_list:
            try:
                # Handle different possible field names
                protocol = proxy_data.get(
                    'protocol',
                    proxy_data.get('Protocol', 'http')
                ).lower()

                # Parse IP and port from different formats
                # First try direct ip/port fields (newer API format)
                if 'ip' in proxy_data and 'port' in proxy_data:
                    ip = proxy_data.get('ip')
                    port = int(proxy_data.get('port', 80))
                # Then try ip_data format (older API format)
                elif 'ip_data' in proxy_data:
                    ip_data = proxy_data.get('ip_data', {})
                    ip = ip_data.get('ip')
                    port = int(ip_data.get('port', 80))
                elif 'ipport' in proxy_data:
                    # Format: ip:port
                    ip_port = proxy_data.get('ipport', ':')
                    ip, port = ip_port.split(':')
                    port = int(port)
                else:
                    # Try to extract from protocolipport format
                    full_proxy = proxy_data.get(
                        'proxy',
                        ''
                    )
                    if '://' in full_proxy:
                        protocol, rest = full_proxy.split('://', 1)
                        ip, port = rest.split(':')
                        port = int(port)
                    else:
                        continue

                # Validate required fields
                if not ip:
                    continue

                country = proxy_data.get('country', '')
                speed = float(proxy_data.get('speed', 0))

                proxy = Proxy(
                    protocol=protocol,
                    ip=ip,
                    port=port,
                    country=country,
                    speed=speed,
                    last_checked=datetime.now()
                )

                proxies.append(proxy)
                logger.debug(f"Parsed proxy: {proxy}")

            except (ValueError, KeyError, AttributeError) as e:
                logger.warning(
                    f"Failed to parse proxy data {proxy_data}: {e}"
                )
                continue

        return proxies

    def test_proxy(
        self,
        proxy: Proxy,
        test_url: str = 'https://httpbin.org/ip',
        timeout: int = 5
    ) -> bool:
        """Test if proxy is working.
        
        Args:
            proxy: Proxy object to test
            test_url: URL to test proxy against
            timeout: Request timeout in seconds
        
        Returns:
            True if proxy works, False otherwise
        """
        try:
            response = requests.get(
                test_url,
                proxies=proxy.dict_format,
                timeout=timeout
            )
            works = response.status_code == 200
            if works:
                logger.debug(f"Proxy {proxy} is working")
            return works

        except requests.RequestException as e:
            logger.debug(f"Proxy {proxy} test failed: {e}")
            return False

    def test_proxies(
        self,
        proxies: Optional[List[Proxy]] = None,
        test_url: str = 'https://httpbin.org/ip',
        timeout: int = 5
    ) -> Tuple[List[Proxy], List[Proxy]]:
        """Test multiple proxies.
        
        Args:
            proxies: List of proxies to test (uses self.proxies if None)
            test_url: URL to test against
            timeout: Request timeout per proxy
        
        Returns:
            Tuple of (working_proxies, failed_proxies)
        """
        if proxies is None:
            proxies = self.proxies

        working = []
        failed = []

        for proxy in proxies:
            if self.test_proxy(proxy, test_url, timeout):
                working.append(proxy)
            else:
                failed.append(proxy)

        logger.info(
            f"Proxy test results: {len(working)} working, "
            f"{len(failed)} failed"
        )

        return working, failed

    def get_best_proxy(
        self,
        proxies: Optional[List[Proxy]] = None
    ) -> Optional[Proxy]:
        """Get fastest proxy from list.
        
        Args:
            proxies: List of proxies (uses self.proxies if None)
        
        Returns:
            Fastest Proxy or None if no proxies available
        """
        if proxies is None:
            proxies = self.proxies

        if not proxies:
            return None

        return min(proxies, key=lambda p: p.speed)

    def print_proxies(self, proxies: Optional[List[Proxy]] = None):
        """Print proxies in readable format.
        
        Args:
            proxies: List of proxies to print (uses self.proxies if None)
        """
        if proxies is None:
            proxies = self.proxies

        if not proxies:
            print("No proxies available")
            return

        header = (
            f"{'Protocol':<10} {'IP':<15} {'Port':<6} "
            f"{'Country':<15} {'Speed (ms)':<10}"
        )
        print(f"\n{header}")
        print("-" * 60)

        for proxy in proxies:
            print(
                f"{proxy.protocol:<10} {proxy.ip:<15} {proxy.port:<6} "
                f"{proxy.country:<15} {proxy.speed:<10.2f}"
            )

        print()
