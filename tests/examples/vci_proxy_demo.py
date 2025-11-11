#!/usr/bin/env python3
"""
VCI Proxy Bypass Demo Script

Script demo hoàn chỉnh để test proxy functionality với VCI
Có thể chạy trên Google Colab hoặc local environment

Usage:
    python vci_proxy_demo.py
    # hoặc trong Colab: !python vci_proxy_demo.py
"""

import sys
import time
import logging
from typing import Optional, Dict, Any

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

try:
    from vnstock.core.utils.proxy_manager import ProxyManager, Proxy
    from vnstock.explorer.vci.quote import Quote
    from vnstock.explorer.vci.listing import Listing
    logger.info("✅ Successfully imported vnstock modules")
except ImportError as e:
    logger.error(f"❌ Failed to import vnstock: {e}")
    logger.error("Please install vnstock: pip install vnstock")
    sys.exit(1)


class VCIProxyDemo:
    """Demo class cho VCI proxy bypass functionality."""

    def __init__(self):
        self.proxy_manager = ProxyManager(timeout=20)
        self.working_proxies = []

    def setup_proxies(self, limit: int = 25) -> bool:
        """Setup và test proxy list."""
        print("🚀 Setting up proxy manager...")
        print(f"🔍 Fetching {limit} proxies from proxyscrape...")

        # Fetch proxies
        proxies = self.proxy_manager.fetch_proxies(limit=limit)

        if not proxies:
            print("❌ Failed to fetch proxies")
            return False

        print(f"✅ Found {len(proxies)} proxies")

        # Test proxies
        print("🧪 Testing proxies (this may take 1-2 minutes)...")
        working, failed = self.proxy_manager.test_proxies(
            proxies,
            test_url='https://httpbin.org/ip',
            timeout=15
        )

        print(f"✅ Working proxies: {len(working)}")
        print(f"❌ Failed proxies: {len(failed)}")

        if not working:
            print("❌ No working proxies found")
            return False

        self.working_proxies = working

        # Show best proxy
        best_proxy = self.proxy_manager.get_best_proxy(working)
        if best_proxy:
            print(f"🚀 Best proxy: {best_proxy.address} ({best_proxy.speed:.1f}ms from {best_proxy.country})")

        return True

    def test_vci_quote_with_proxy(self, symbol: str, max_retries: int = 3) -> Optional[Dict[str, Any]]:
        """Test VCI quote với proxy rotation."""
        print(f"\n📈 Testing VCI Quote for {symbol}")

        for attempt in range(max_retries):
            if not self.working_proxies:
                print("❌ No proxies available")
                return None

            # Rotate proxy
            proxy_index = attempt % len(self.working_proxies)
            current_proxy = self.working_proxies[proxy_index]

            print(f"🔄 Attempt {attempt + 1}/{max_retries} with proxy: {current_proxy.address}")

            try:
                # Khởi tạo VCI Quote
                quote = Quote(
                    symbol=symbol,
                    random_agent=True,
                    show_log=False
                )

                # Trong thực tế, đây là nơi bạn sẽ inject proxy vào VCI requests
                # Hiện tại chỉ mô phỏng
                print("🔍 Simulating VCI API call with proxy...")

                # Simulate network delay
                time.sleep(2)

                # Mock successful response
                mock_response = {
                    'symbol': symbol,
                    'timestamp': time.strftime('%Y-%m-%d %H:%M:%S'),
                    'proxy_used': current_proxy.address,
                    'proxy_country': current_proxy.country,
                    'proxy_speed': f"{current_proxy.speed:.1f}ms",
                    'attempt': attempt + 1,
                    'status': 'success',
                    'mock_data': {
                        'price': '45,000 ± 500',
                        'change': '+1.2% ± 0.5%',
                        'volume': '1,234,567 ± 100,000'
                    }
                }

                print("✅ Success!")
                print(f"   📊 Price: {mock_response['mock_data']['price']}")
                print(f"   📈 Change: {mock_response['mock_data']['change']}")
                print(f"   📊 Volume: {mock_response['mock_data']['volume']}")

                return mock_response

            except Exception as e:
                print(f"❌ Attempt {attempt + 1} failed: {e}")

                # Remove failed proxy
                if current_proxy in self.working_proxies:
                    self.working_proxies.remove(current_proxy)
                    print(f"🗑️ Removed failed proxy: {current_proxy.address}")

                continue

        print(f"❌ All {max_retries} attempts failed for {symbol}")
        return None

    def batch_test_symbols(self, symbols: list, delay: float = 3.0):
        """Test nhiều symbol với proxy rotation."""
        print(f"\n🔄 Batch testing {len(symbols)} symbols with proxy rotation")
        print("=" * 60)

        results = {}

        for i, symbol in enumerate(symbols):
            print(f"\n[{i+1}/{len(symbols)}] Processing {symbol}...")

            result = self.test_vci_quote_with_proxy(symbol)
            results[symbol] = result

            if result:
                print(f"✅ {symbol}: Success")
            else:
                print(f"❌ {symbol}: Failed")

            # Delay để tránh rate limit
            if i < len(symbols) - 1:  # Không delay sau symbol cuối
                print(f"⏳ Waiting {delay}s before next symbol...")
                time.sleep(delay)

        return results

    def show_summary(self, results: Dict[str, Any]):
        """Hiển thị summary kết quả."""
        print("\n" + "=" * 60)
        print("📊 BATCH TEST SUMMARY")
        print("=" * 60)

        total = len(results)
        successful = sum(1 for r in results.values() if r is not None)
        failed = total - successful

        print(f"📈 Total symbols tested: {total}")
        print(f"✅ Successful: {successful}")
        print(f"❌ Failed: {failed}")
        print(f"📊 Success rate: {successful/total*100:.1f}%")
        print("\n📋 Detailed Results:")
        print("-" * 60)

        for symbol, result in results.items():
            if result:
                proxy = result['proxy_used']
                speed = result['proxy_speed']
                print(f"✅ {symbol}: {proxy} ({speed})")
            else:
                print(f"❌ {symbol}: Failed")

        print("\n" + "=" * 60)


def detect_environment():
    """Detect if running in Google Colab."""
    try:
        import google.colab
        return "Google Colab"
    except ImportError:
        return "Local environment"


def main():
    """Main demo function."""
    print("🌐 VCI Proxy Bypass Demo")
    print("=" * 50)

    # Detect environment
    env = detect_environment()
    print(f"🖥️ Running in: {env}")

    if env == "Google Colab":
        print("⚠️ Note: Google Colab may block some proxy ports")
        print("💡 Consider using residential proxies for better success rate")

    # Initialize demo
    demo = VCIProxyDemo()

    # Setup proxies
    if not demo.setup_proxies(limit=20):
        print("❌ Failed to setup proxies. Exiting.")
        return

    # Test symbols
    test_symbols = ['VCB', 'ACB', 'TCB', 'BID', 'CTG']

    # Run batch test
    results = demo.batch_test_symbols(test_symbols, delay=2.0)

    # Show summary
    demo.show_summary(results)

    # Final message
    successful = sum(1 for r in results.values() if r is not None)
    if successful > 0:
        print("\n🎉 Demo completed successfully!")
        print("💡 Next: Integrate proxy vào actual VCI API calls")
        print("📖 See: docs/VCI_PROXY_BYPASS_GUIDE.md for full implementation")
    else:
        print("\n❌ Demo completed with failures")
        print("🔧 Try: Increasing proxy limit or using different proxy sources")
        print("📖 See: docs/VCI_PROXY_BYPASS_GUIDE.md for troubleshooting")


if __name__ == "__main__":
    main()
