"""
Comprehensive guide for using ProxyManager with vnstock.

This guide demonstrates how to fetch proxies, test them,
and integrate with vnstock's VCI data source.

Location: tests/examples/proxy_examples.py (Demo code, not core utils)
Usage: python -m tests.examples.proxy_examples
"""

from vnstock.core.utils.proxy_manager import ProxyManager, Proxy
from vnstock.explorer.vci.quote import Quote


def example_1_basic_proxy_fetch():
    """Example 1: Fetch free proxies from proxyscrape."""
    print("\n=== Example 1: Fetch Free Proxies ===")

    manager = ProxyManager(timeout=10)

    # Fetch 5 free proxies
    proxies = manager.fetch_proxies(limit=5, skip=0)

    if proxies:
        print(f"✓ Fetched {len(proxies)} proxies")
        manager.print_proxies(proxies)
        return proxies
    else:
        print("✗ Failed to fetch proxies")
        return []


def example_2_test_proxies():
    """Example 2: Test proxies for connectivity."""
    print("\n=== Example 2: Test Proxy Connectivity ===")

    manager = ProxyManager()
    proxies = manager.fetch_proxies(limit=5)

    if not proxies:
        print("No proxies to test")
        return

    print(f"Testing {len(proxies)} proxies...")

    # Test each proxy
    working, failed = manager.test_proxies(
        proxies,
        test_url='https://httpbin.org/ip',
        timeout=5
    )

    print(f"✓ Working: {len(working)} proxies")
    print(f"✗ Failed: {len(failed)} proxies")

    if working:
        manager.print_proxies(working)


def example_3_get_best_proxy():
    """Example 3: Get fastest proxy."""
    print("\n=== Example 3: Get Fastest Proxy ===")

    manager = ProxyManager()
    proxies = manager.fetch_proxies(limit=5)

    if not proxies:
        print("No proxies available")
        return

    best = manager.get_best_proxy(proxies)

    if best:
        print(f"✓ Fastest proxy: {best.address}")
        print(f"  Speed: {best.speed}ms")
        print(f"  Country: {best.country}")
    else:
        print("No proxies available")


def example_4_create_custom_proxy():
    """Example 4: Create custom proxy."""
    print("\n=== Example 4: Custom Proxy ===")

    # Create custom proxies
    proxies = [
        Proxy(
            protocol='http',
            ip='192.168.1.100',
            port=8080,
            country='Vietnam'
        ),
        Proxy(
            protocol='https',
            ip='10.0.0.1',
            port=3128,
            country='USA'
        ),
        Proxy(
            protocol='socks5',
            ip='172.16.0.1',
            port=1080,
            country='UK'
        ),
    ]

    print("Custom Proxies:")
    for proxy in proxies:
        print(f"  {proxy.address} ({proxy.country})")


def example_5_proxy_with_vci_quote():
    """Example 5: Use proxy with VCI Quote (demonstration)."""
    print("\n=== Example 5: Proxy with VCI Quote ===")

    # Create a proxy
    proxy = Proxy(
        protocol='http',
        ip='127.0.0.1',
        port=3128,
        country='Local'
    )

    print(f"Proxy configuration: {proxy.address}")
    print(f"Proxy dict format: {proxy.dict_format}")

    # Create VCI Quote instance
    try:
        quote = Quote(
            symbol='ACB',
            random_agent=False,
            show_log=False
        )
        print(f"✓ VCI Quote initialized for symbol: {quote.symbol}")

        # Note: To actually use the proxy, you would need to
        # pass it to the requests calls in VCI Quote
        # This depends on vnstock's implementation

    except Exception as e:
        print(f"✗ Error: {e}")


def example_6_batch_proxy_processing():
    """Example 6: Process multiple symbols with proxy rotation."""
    print("\n=== Example 6: Proxy Rotation Example ===")

    symbols = ['ACB', 'VCB', 'TCB']
    manager = ProxyManager()

    # Fetch proxies for rotation
    proxies = manager.fetch_proxies(limit=3)

    if not proxies:
        print("No proxies available for rotation")
        return

    print(f"Using {len(proxies)} proxies for {len(symbols)} symbols")

    # Simulate proxy rotation
    for i, symbol in enumerate(symbols):
        proxy = proxies[i % len(proxies)]
        print(f"  {symbol} -> {proxy.address} ({proxy.country})")


def example_7_proxy_manager_workflow():
    """Example 7: Complete ProxyManager workflow."""
    print("\n=== Example 7: Complete Workflow ===")

    manager = ProxyManager(timeout=10)

    # Step 1: Fetch proxies
    print("Step 1: Fetching proxies...")
    proxies = manager.fetch_proxies(limit=5)

    if not proxies:
        print("✗ No proxies fetched")
        return

    print(f"✓ Fetched {len(proxies)} proxies")

    # Step 2: Get best proxy
    print("\nStep 2: Getting best proxy...")
    best = manager.get_best_proxy(proxies)

    if best:
        print(f"✓ Best proxy: {best.address}")
        print(f"  Speed: {best.speed}ms")

        # Step 3: Test best proxy
        print("\nStep 3: Testing best proxy...")
        works = manager.test_proxy(best)
        status = 'works' if works else 'failed'
        symbol = '✓' if works else '✗'
        print(f"{symbol} Proxy {status}")

        # Step 4: Display all proxies
        print("\nStep 4: All available proxies:")
        manager.print_proxies(proxies)

    else:
        print("✗ No suitable proxy found")


def example_8_proxy_error_handling():
    """Example 8: Error handling and fallback."""
    print("\n=== Example 8: Error Handling ===")

    manager = ProxyManager(timeout=5)

    try:
        print("Attempting to fetch proxies...")
        proxies = manager.fetch_proxies(limit=3)

        if proxies:
            print(f"✓ Got {len(proxies)} proxies")
        else:
            print("✓ API returned no proxies (might be rate limited)")

    except Exception as e:
        print(f"✗ Error: {e}")
        print("  Using fallback approach...")

        # Fallback: Create static proxy list
        fallback_proxies = [
            Proxy('http', 'proxy1.example.com', 8080),
            Proxy('http', 'proxy2.example.com', 3128),
        ]
        print(f"✓ Created {len(fallback_proxies)} fallback proxies")


if __name__ == '__main__':
    print("\n" + "="*60)
    print("ProxyManager Examples for vnstock")
    print("="*60)

    # Run examples (comment out as needed)
    example_1_basic_proxy_fetch()
    # example_2_test_proxies()  # Slow - uncomment to test
    example_3_get_best_proxy()
    example_4_create_custom_proxy()
    example_5_proxy_with_vci_quote()
    example_6_batch_proxy_processing()
    # example_7_proxy_manager_workflow()  # Comprehensive
    example_8_proxy_error_handling()

    print("\n" + "="*60)
    print("Examples complete!")
    print("="*60)
