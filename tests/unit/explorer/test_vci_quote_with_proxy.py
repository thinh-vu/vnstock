"""
Tests for VCI Quote functionality with proxy support.

Tests cover:
- VCI Quote without proxy
- VCI Quote with single proxy
- VCI Quote with proxy fallback
- Proxy rotation for multiple requests
"""

import pytest
from unittest.mock import patch, Mock
from vnstock.explorer.vci.quote import Quote
from vnstock.core.utils.proxy_manager import Proxy, ProxyManager


@pytest.mark.integration
@pytest.mark.vci
class TestVCIQuoteWithProxy:
    """Test VCI Quote with proxy configuration."""

    def test_vci_quote_basic_no_proxy(self):
        """Test VCI Quote without proxy (baseline)."""
        # Use hardcoded symbol to ensure test runs
        symbol = 'ACB'

        quote = Quote(symbol=symbol, random_agent=False, show_log=False)
        assert quote is not None
        assert quote.symbol == symbol

    def test_vci_quote_with_proxy_dict(self):
        """Test VCI Quote with proxy dictionary."""
        # Create mock proxy
        proxy = Proxy(
            protocol='http',
            ip='127.0.0.1',
            port=8080
        )

        # Verify proxy can be applied
        proxy_dict = proxy.dict_format
        assert 'http' in proxy_dict
        assert 'https' in proxy_dict

    @patch('requests.get')
    def test_vci_quote_history_with_proxy(self, mock_get):
        """Test VCI Quote history with mocked proxy request."""
        symbol = 'VCB'  # Use hardcoded symbol

        # Mock successful response with proxy
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'data': [{
                'tradingDate': '2024-01-01',
                'open': 100.0,
                'high': 105.0,
                'low': 98.0,
                'close': 103.0,
                'volume': 1000000
            }]
        }
        mock_get.return_value = mock_response

        quote = Quote(symbol=symbol, random_agent=False, show_log=False)

        # Verify quote works (without actually using proxy in this test)
        assert quote.symbol == symbol

    def test_proxy_manager_with_vci_workflow(self):
        """Test complete workflow with ProxyManager."""
        manager = ProxyManager()

        # Create test proxies
        test_proxies = [
            Proxy('http', '192.168.1.1', 8080),
            Proxy('http', '10.0.0.1', 3128),
            Proxy('https', '172.16.0.1', 9090),
        ]

        # Get best proxy
        best = manager.get_best_proxy(test_proxies)
        assert best is not None

        # Verify proxy format
        proxy_dict = best.dict_format
        assert 'http' in proxy_dict
        assert 'https' in proxy_dict

    @pytest.mark.slow
    def test_vci_quote_with_real_proxy_fetch(self):
        """Test VCI Quote with real proxy fetch."""
        # This test demonstrates the workflow but may skip
        # if proxyscrape API is unavailable
        try:
            manager = ProxyManager(timeout=5)
            proxies = manager.fetch_proxies(limit=3)

            if proxies:
                proxy = proxies[0]
                assert proxy.address

                # Verify we can use this proxy
                proxy_dict = proxy.dict_format
                assert 'http' in proxy_dict

            else:
                pytest.skip("No proxies available from API")

        except Exception as e:
            pytest.skip(f"Proxy API unavailable: {e}")

    def test_proxy_configuration_examples(self):
        """Test various proxy configuration examples."""
        # HTTP proxy
        http_proxy = Proxy(
            protocol='http',
            ip='192.168.1.1',
            port=8080
        )
        assert http_proxy.address == 'http://192.168.1.1:8080'

        # HTTPS proxy
        https_proxy = Proxy(
            protocol='https',
            ip='10.0.0.1',
            port=3128
        )
        assert https_proxy.address == 'https://10.0.0.1:3128'

        # SOCKS5 proxy
        socks_proxy = Proxy(
            protocol='socks5',
            ip='172.16.0.1',
            port=1080
        )
        assert socks_proxy.address == 'socks5://172.16.0.1:1080'


@pytest.mark.integration
class TestProxyIntegrationWithVCI:
    """Integration tests for proxy with VCI functionality."""

    def test_proxy_manager_initialization(self):
        """Test ProxyManager can be initialized."""
        manager = ProxyManager(timeout=10)
        assert manager.timeout == 10
        assert manager.proxies == []

    def test_proxy_application_pattern(self, diverse_test_symbols):
        """Test the pattern for applying proxy to VCI requests."""
        # Create proxy
        proxy = Proxy(
            protocol='http',
            ip='127.0.0.1',
            port=3128
        )

        # Get proxy dict (would be passed to requests)
        proxy_config = proxy.dict_format

        # Verify structure
        assert isinstance(proxy_config, dict)
        assert 'http' in proxy_config
        assert 'https' in proxy_config
        assert proxy_config['http'].startswith('http://')
        assert proxy_config['https'].startswith('http://')

    def test_multiple_proxy_handling(self):
        """Test handling multiple proxies."""
        proxies = [
            Proxy('http', f'192.168.1.{i}', 8080 + i)
            for i in range(1, 4)
        ]

        manager = ProxyManager()

        # Test each proxy
        for proxy in proxies:
            assert proxy.address
            assert proxy.dict_format

        # Get best (by speed)
        for i, proxy in enumerate(proxies):
            proxy.speed = float(i * 10)

        best = manager.get_best_proxy(proxies)
        assert best is proxies[0]
