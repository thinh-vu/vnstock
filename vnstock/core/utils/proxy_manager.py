"""
Proxy manager for vnstock - fetches and manages free proxies.

Provides functionality to:
- Fetch free proxies from proxyscrape API
- Parse and validate proxy data
- Test proxy connectivity
- Configure proxies for vnstock requests
"""

import json
import logging
import threading
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass
from datetime import datetime
from typing import Dict, List, Optional, Tuple

import requests

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

    def __init__(
        self,
        timeout: int = 10,
        pool_ttl_seconds: int = 300,
        min_pool_refresh_interval_seconds: int = 30,
        test_max_workers: int = 16,
    ):
        """Initialize ProxyManager.
        
        Args:
            timeout: Request timeout in seconds
        """
        self.timeout = timeout
        self.pool_ttl_seconds = max(pool_ttl_seconds, 0)
        self.min_pool_refresh_interval_seconds = max(
            min_pool_refresh_interval_seconds,
            0,
        )
        self.test_max_workers = max(test_max_workers, 1)
        self.proxies: List[Proxy] = []
        self.last_fetch: Optional[datetime] = None
        self.last_test: Optional[datetime] = None
        self._last_pool_refresh_monotonic: float = 0.0
        self._refresh_lock = threading.Lock()

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
        started = time.perf_counter()
        try:
            response = requests.get(
                test_url,
                proxies=proxy.dict_format,
                timeout=timeout
            )
            works = response.status_code == 200
            if works:
                proxy.speed = (time.perf_counter() - started) * 1000
                proxy.last_checked = datetime.now()
                logger.debug(f"Proxy {proxy} is working")
            return works

        except requests.RequestException as e:
            proxy.last_checked = datetime.now()
            logger.debug(f"Proxy {proxy} test failed: {e}")
            return False

    def test_proxies(
        self,
        proxies: Optional[List[Proxy]] = None,
        test_url: str = 'https://httpbin.org/ip',
        timeout: int = 5,
        max_workers: Optional[int] = None,
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

        if not proxies:
            return [], []

        working = []
        failed = []
        worker_count = min(max_workers or self.test_max_workers, len(proxies))

        if worker_count <= 1:
            for proxy in proxies:
                if self.test_proxy(proxy, test_url, timeout):
                    working.append(proxy)
                else:
                    failed.append(proxy)
        else:
            with ThreadPoolExecutor(max_workers=worker_count) as executor:
                futures = {
                    executor.submit(self.test_proxy, proxy, test_url, timeout): proxy
                    for proxy in proxies
                }
                for future in as_completed(futures):
                    proxy = futures[future]
                    try:
                        if future.result():
                            working.append(proxy)
                        else:
                            failed.append(proxy)
                    except Exception as exc:
                        logger.debug("Proxy %s test raised error: %s", proxy, exc)
                        failed.append(proxy)

        self.last_test = datetime.now()

        logger.info(
            f"Proxy test results: {len(working)} working, "
            f"{len(failed)} failed"
        )

        return working, failed

    def get_fresh_proxies(
        self,
        use_cache: bool = True,
        auto_test: bool = True
    ) -> List[str]:
        """
        Get list of working proxy addresses (protocol://ip:port).
        
        Args:
            use_cache: Use existing proxies if available
            auto_test: Test proxies before returning
            
        Returns:
            List of proxy address strings
        """
        if not self.proxies or not use_cache:
            self.fetch_proxies()
            
        if not self.proxies:
            return []
            
        if auto_test:
            working, _ = self.test_proxies(self.proxies)
            self.proxies = working
            return [str(p) for p in working]
            
        return [str(p) for p in self.proxies]

    def _is_pool_stale(self) -> bool:
        if self.last_test is None:
            return True
        if self.pool_ttl_seconds == 0:
            return True
        age = (datetime.now() - self.last_test).total_seconds()
        return age >= self.pool_ttl_seconds

    def _should_refresh_pool(self, size: int, auto_refresh: bool) -> bool:
        if not auto_refresh:
            return False
        if len(self.proxies) < size:
            return True
        return self._is_pool_stale()

    def _ranked_pool(self, size: int) -> List[str]:
        ranked = sorted(
            self.proxies,
            key=lambda proxy: proxy.speed if proxy.speed > 0 else float('inf'),
        )
        return [str(proxy) for proxy in ranked[:size]]

    def get_proxy_pool(self, size: int = 16, auto_refresh: bool = True) -> List[str]:
        """
        Get a tested proxy pool for parallel requests.

        Args:
            size: Number of proxies to return.
            auto_refresh: Fetch and test new proxies when pool is low.

        Returns:
            List of proxy URLs.
        """
        desired_size = max(size, 1)
        if self._should_refresh_pool(desired_size, auto_refresh):
            with self._refresh_lock:
                now_monotonic = time.monotonic()
                refresh_age = now_monotonic - self._last_pool_refresh_monotonic
                if self._should_refresh_pool(desired_size, auto_refresh) and (
                    self._last_pool_refresh_monotonic == 0.0 or
                    refresh_age >= self.min_pool_refresh_interval_seconds
                ):
                    self.fetch_proxies(limit=max(desired_size * 2, 8))
                    working, _ = self.test_proxies(self.proxies)
                    self.proxies = working
                    self._last_pool_refresh_monotonic = time.monotonic()

        pool = self._ranked_pool(desired_size)
        logger.info(f"Proxy pool: {len(pool)}/{size}")
        return pool

    def set_custom_proxies(self, proxy_list: List[str]):
        """
        Set custom proxies from list of strings.
        
        Args:
            proxy_list: List of proxy strings (e.g. 'http://1.2.3.4:80')
        """
        new_proxies = []
        for p_str in proxy_list:
            try:
                # Basic parsing
                if '://' in p_str:
                    protocol, rest = p_str.split('://', 1)
                else:
                    protocol = 'http'
                    rest = p_str
                    
                if ':' in rest:
                    ip, port = rest.split(':')
                    new_proxies.append(Proxy(
                        protocol=protocol,
                        ip=ip,
                        port=int(port)
                    ))
            except Exception:
                logger.warning(f"Invalid custom proxy format: {p_str}")
                continue
                
        self.proxies = new_proxies
        self.last_test = None
        logger.info(f"Set {len(new_proxies)} custom proxies")

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

        # Sort by speed (0 speed means unchecked or fast, usually we prioritize verified speed)
        # Assuming speed is response time in ms, lower is better.
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

# Global proxy manager instance
proxy_manager = ProxyManager()
