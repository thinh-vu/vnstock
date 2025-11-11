"""
Tests for proxy manager functionality.

Tests cover:
- Fetching proxies from proxyscrape API
- Parsing proxy data correctly
- Testing proxy connectivity
- Configuring proxies for VCI requests
"""

import pytest
import requests
from unittest.mock import Mock, patch
from vnstock.core.utils.proxy_manager import (
    Proxy, ProxyManager
)


@pytest.mark.unit
class TestProxyClass:
    """Test Proxy data class."""

    def test_proxy_creation(self):
        """Test creating a Proxy object."""
        proxy = Proxy(
            protocol='http',
            ip='192.168.1.1',
            port=8080,
            country='US',
            speed=50.0
        )

        assert proxy.protocol == 'http'
        assert proxy.ip == '192.168.1.1'
        assert proxy.port == 8080
        assert proxy.country == 'US'

    def test_proxy_address_property(self):
        """Test proxy address formatting."""
        proxy = Proxy(
            protocol='https',
            ip='10.0.0.1',
            port=3128
        )

        assert proxy.address == 'https://10.0.0.1:3128'

    def test_proxy_dict_format(self):
        """Test proxy dict format for requests."""
        proxy = Proxy(
            protocol='http',
            ip='192.168.1.1',
            port=8080
        )

        proxy_dict = proxy.dict_format
        assert 'http' in proxy_dict
        assert 'https' in proxy_dict
        assert proxy_dict['http'] == 'http://192.168.1.1:8080'

    def test_proxy_str(self):
        """Test proxy string representation."""
        proxy = Proxy(
            protocol='socks5',
            ip='1.2.3.4',
            port=1080
        )

        assert str(proxy) == 'socks5://1.2.3.4:1080'


@pytest.mark.unit
class TestProxyManager:
    """Test ProxyManager class."""

    def test_proxy_manager_initialization(self):
        """Test ProxyManager initialization."""
        manager = ProxyManager(timeout=15)

        assert manager.timeout == 15
        assert manager.proxies == []
        assert manager.last_fetch is None

    @patch('requests.get')
    def test_fetch_proxies_success(self, mock_get):
        """Test successful proxy fetching."""
        mock_response = Mock()
        mock_response.json.return_value = {
            'status': 'ok',
            'proxies': [
                {
                    'protocol': 'http',
                    'ip': '192.168.1.1',
                    'port': '8080',
                    'country': 'US',
                    'speed': 50.5
                },
                {
                    'protocol': 'https',
                    'ip': '10.0.0.1',
                    'port': '3128',
                    'country': 'UK',
                    'speed': 75.2
                }
            ]
        }
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response

        manager = ProxyManager()
        proxies = manager.fetch_proxies(limit=2)

        assert len(proxies) == 2
        assert proxies[0].ip == '192.168.1.1'
        assert proxies[0].port == 8080
        assert proxies[1].country == 'UK'

    @patch('requests.get')
    def test_fetch_proxies_api_error(self, mock_get):
        """Test handling API errors."""
        mock_response = Mock()
        mock_response.json.return_value = {'status': 'error'}
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response

        manager = ProxyManager()
        proxies = manager.fetch_proxies()

        assert proxies == []

    @patch('requests.get')
    def test_fetch_proxies_network_error(self, mock_get):
        """Test handling network errors."""
        mock_get.side_effect = requests.ConnectionError("Network error")

        manager = ProxyManager()
        proxies = manager.fetch_proxies()

        assert proxies == []

    def test_parse_proxy_data_standard_format(self):
        """Test parsing proxy data in standard format."""
        manager = ProxyManager()

        proxy_data = [
            {
                'protocol': 'http',
                'ip': '192.168.1.1',
                'port': '8080',
                'country': 'US',
                'speed': 50.0
            }
        ]

        proxies = manager._parse_proxy_data(proxy_data)

        assert len(proxies) == 1
        assert proxies[0].protocol == 'http'
        assert proxies[0].ip == '192.168.1.1'
        assert proxies[0].port == 8080

    def test_parse_proxy_data_ipport_format(self):
        """Test parsing proxy data with ipport format."""
        manager = ProxyManager()

        proxy_data = [
            {
                'protocol': 'https',
                'ipport': '10.0.0.1:3128',
                'country': 'UK',
                'speed': 75.0
            }
        ]

        proxies = manager._parse_proxy_data(proxy_data)

        assert len(proxies) == 1
        assert proxies[0].ip == '10.0.0.1'
        assert proxies[0].port == 3128

    def test_parse_proxy_data_invalid_port(self):
        """Test handling invalid port."""
        manager = ProxyManager()

        proxy_data = [
            {
                'protocol': 'http',
                'ip': '192.168.1.1',
                'port': 'invalid',
                'country': 'US'
            }
        ]

        proxies = manager._parse_proxy_data(proxy_data)

        # Should skip invalid proxy
        assert len(proxies) == 0

    @patch('requests.get')
    def test_test_proxy_working(self, mock_get):
        """Test proxy connectivity test (working)."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_get.return_value = mock_response

        proxy = Proxy(
            protocol='http',
            ip='192.168.1.1',
            port=8080
        )

        manager = ProxyManager()
        result = manager.test_proxy(proxy)

        assert result is True

    @patch('requests.get')
    def test_test_proxy_not_working(self, mock_get):
        """Test proxy that doesn't work."""
        mock_get.side_effect = requests.ConnectionError("Connection error")

        proxy = Proxy(
            protocol='http',
            ip='192.168.1.1',
            port=8080
        )

        manager = ProxyManager()
        result = manager.test_proxy(proxy)

        assert result is False

    @patch('vnstock.core.utils.proxy_manager.ProxyManager.test_proxy')
    def test_test_proxies_batch(self, mock_test):
        """Test batch proxy testing."""
        mock_test.side_effect = [True, False, True]

        proxies = [
            Proxy('http', '192.168.1.1', 8080),
            Proxy('http', '10.0.0.1', 3128),
            Proxy('https', '172.16.0.1', 9090),
        ]

        manager = ProxyManager()
        working, failed = manager.test_proxies(proxies)

        assert len(working) == 2
        assert len(failed) == 1

    def test_get_best_proxy(self):
        """Test getting fastest proxy."""
        proxies = [
            Proxy('http', '192.168.1.1', 8080, speed=100.0),
            Proxy('http', '10.0.0.1', 3128, speed=50.0),
            Proxy('https', '172.16.0.1', 9090, speed=75.0),
        ]

        manager = ProxyManager()
        best = manager.get_best_proxy(proxies)

        assert best is not None
        assert best.ip == '10.0.0.1'
        assert best.speed == 50.0

    def test_get_best_proxy_empty(self):
        """Test getting best proxy when none available."""
        manager = ProxyManager()
        best = manager.get_best_proxy([])

        assert best is None


@pytest.mark.integration
class TestProxyIntegration:
    """Integration tests with real proxyscrape API."""

    @pytest.mark.slow
    def test_fetch_real_proxies(self):
        """Test fetching real proxies from API."""
        manager = ProxyManager()
        proxies = manager.fetch_proxies(limit=5)

        # May return 0-5 proxies depending on API availability
        assert isinstance(proxies, list)
        assert len(proxies) <= 5

        if proxies:
            proxy = proxies[0]
            assert proxy.protocol in ['http', 'https', 'socks5']
            assert proxy.ip
            assert proxy.port > 0

    @pytest.mark.slow
    def test_proxy_manager_workflow(self):
        """Test complete proxy manager workflow."""
        manager = ProxyManager()

        # Fetch proxies
        proxies = manager.fetch_proxies(limit=3)

        if proxies:
            # Print proxies
            manager.print_proxies(proxies)

            # Get best proxy
            best = manager.get_best_proxy(proxies)
            assert best is not None
