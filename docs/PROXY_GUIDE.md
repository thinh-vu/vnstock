# Proxy Management Guide

Complete guide for using the ProxyManager utility to handle network restrictions, ISP blocks, rate limiting, and IP rotation for web scraping and API access (research/personal usages).

## Table of Contents

- [Overview](#overview)
- [Quick Start](#quick-start)
- [ProxyManager Class](#proxymanager-class)
- [Usage Patterns](#usage-patterns)
- [Advanced Configuration](#advanced-configuration)
- [Troubleshooting](#troubleshooting)
- [Examples](#examples)

## Overview

The `ProxyManager` utility provides a comprehensive solution for:

1. **Automatic proxy fetching** from free proxy APIs (proxyscrape)
2. **Proxy validation and testing** for availability and performance
3. **Smart proxy management** with speed sorting and filtering
4. **Easy integration** with any HTTP client or web scraping library
5. **Error handling and fallback** mechanisms

### Key Features

- **Free proxy fetching**: Automatically fetch fresh proxies from proxyscrape API
- **Multi-protocol support**: HTTP, HTTPS, and SOCKS5 proxies
- **Performance testing**: Automatic speed testing and ranking
- **Proxy validation**: Connection testing and health checking
- **Flexible integration**: Works with requests, aiohttp, scrapy, etc.
- **Batch processing**: Handle multiple proxies efficiently
- **Error resilience**: Graceful handling of network issues

### When to Use Proxies

- **Network restrictions**: ISP or corporate firewall blocks target websites
- **Geographic restrictions**: Bypass region-based content blocking
- **Rate limiting**: Distribute requests across multiple IPs to avoid bans
- **IP rotation**: Maintain anonymity for large-scale data collection
- **Load balancing**: Distribute traffic across multiple endpoints
- **Testing**: Simulate different geographic locations

### How It Works

1. **Fetch**: Get fresh proxy lists from free proxy APIs
2. **Test**: Validate proxy connectivity and measure response times
3. **Select**: Choose optimal proxies based on speed and reliability
4. **Use**: Integrate with your HTTP client or scraping framework
5. **Rotate**: Switch proxies automatically for load balancing

### Supported Proxy Sources

- **Proxyscrape API v4**: Primary free proxy source
- **Custom proxy lists**: Add your own proxy servers
- **Premium proxy services**: Extensible for paid proxy APIs

## Quick Start

### Basic Proxy Fetching

```python
from vnstock.core.utils.proxy_manager import ProxyManager

# Initialize manager
manager = ProxyManager(timeout=10)

# Fetch 5 free proxies
proxies = manager.fetch_proxies(limit=5)

# View available proxies
manager.print_proxies(proxies)
```

### Using a Proxy

```python
import requests

# Get a proxy
manager = ProxyManager()
proxies_list = manager.fetch_proxies(limit=1)

if proxies_list:
    proxy = proxies_list[0]
    proxy_config = proxy.dict_format  # {'http': '...', 'https': '...'}
    
    # Use with requests
    response = requests.get('https://api.example.com', proxies=proxy_config)
```

### Finding the Best Proxy

```python
# Fetch and test proxies
manager = ProxyManager()
proxies = manager.fetch_proxies(limit=10)

# Get fastest proxy (tests and sorts by speed)
best_proxy = manager.get_best_proxy(proxies)

if best_proxy:
    print(f"Using proxy: {best_proxy.address}")
    print(f"Speed: {best_proxy.speed}ms")
    print(f"Country: {best_proxy.country}")
```

### Proxy Rotation Example

```python
# Fetch proxies for rotation
manager = ProxyManager()
proxies = manager.fetch_proxies(limit=3)

# Rotate through proxies
urls = ['https://api1.example.com', 'https://api2.example.com', 'https://api3.example.com']

for i, url in enumerate(urls):
    proxy = proxies[i % len(proxies)]
    print(f"Requesting {url} with {proxy.address}")
    
    response = requests.get(url, proxies=proxy.dict_format, timeout=10)
    print(f"Status: {response.status_code}")
```

## ProxyManager Class

### Initialization

```python
from vnstock.core.utils.proxy_manager import ProxyManager

# Default initialization
manager = ProxyManager()

# With custom timeout
manager = ProxyManager(timeout=15)

# With custom API parameters
manager = ProxyManager(
    timeout=10,
    api_key=None  # Optional: for proxyscrape premium
)
```

### Methods

#### `fetch_proxies(limit=15, skip=0)`

Fetch free proxies from proxyscrape API.

**Parameters:**
- `limit` (int): Number of proxies to fetch (default: 15, max: 100)
- `skip` (int): Number of proxies to skip (for pagination)

**Returns:** `List[Proxy]`

**Example:**
```python
proxies = manager.fetch_proxies(limit=10)
print(f"Fetched {len(proxies)} proxies")
```

#### `test_proxy(proxy, test_url=None, timeout=None)`

Test a single proxy for connectivity.

**Parameters:**
- `proxy` (Proxy): Proxy to test
- `test_url` (str): URL to test against (default: httpbin.org/ip)
- `timeout` (int): Connection timeout in seconds

**Returns:** `bool` - True if proxy works, False otherwise

**Example:**
```python
proxy = proxies[0]
if manager.test_proxy(proxy):
    print(f"✓ {proxy.address} works")
else:
    print(f"✗ {proxy.address} failed")
```

#### `test_proxies(proxies, test_url=None, timeout=None)`

Test multiple proxies in parallel.

**Parameters:**
- `proxies` (List[Proxy]): Proxies to test
- `test_url` (str): URL to test against
- `timeout` (int): Connection timeout

**Returns:** `Tuple[List[Proxy], List[Proxy]]` - (working_proxies, failed_proxies)

**Example:**
```python
working, failed = manager.test_proxies(proxies)
print(f"Working: {len(working)}, Failed: {len(failed)}")
```

#### `get_best_proxy(proxies)`

Get the fastest proxy from a list.

**Parameters:**
- `proxies` (List[Proxy]): Proxies to choose from

**Returns:** `Optional[Proxy]` - Fastest proxy or None

**Example:**
```python
best = manager.get_best_proxy(proxies)
if best:
    print(f"Fastest: {best.address} ({best.speed}ms)")
```

#### `print_proxies(proxies)`

Display proxies in formatted table.

**Parameters:**
- `proxies` (List[Proxy]): Proxies to display

**Example:**
```python
manager.print_proxies(proxies)
# Output:
# Protocol | IP Address      | Port | Country | Speed (ms)
# ---------|-----------------|------|---------|----------
# http     | 1.2.3.4         | 8080 | Vietnam | 45.2
# https    | 5.6.7.8         | 3128 | USA     | 123.5
```

### Proxy Class

```python
from vnstock.core.utils.proxy_manager import Proxy

# Create proxy
proxy = Proxy(
    protocol='http',      # http, https, socks5
    ip='1.2.3.4',         # IP address
    port=8080,            # Port number
    country='Vietnam',    # Optional: country name
    speed=45.2            # Optional: speed in ms
)

# Access properties
print(proxy.address)      # http://1.2.3.4:8080
print(proxy.dict_format)  # {'http': 'http://...', 'https': 'http://...'}
print(str(proxy))         # http://1.2.3.4:8080 (Vietnam)
```

## Usage Patterns

### Pattern 1: Basic Proxy Fetching

```python
from vnstock.core.utils.proxy_manager import ProxyManager

# Initialize manager
manager = ProxyManager(timeout=10)

# Fetch free proxies
proxies = manager.fetch_proxies(limit=5, skip=0)

if proxies:
    print(f"✓ Fetched {len(proxies)} proxies")
    manager.print_proxies(proxies)
else:
    print("✗ Failed to fetch proxies")
```

### Pattern 2: Proxy Testing and Validation

```python
# Fetch proxies
manager = ProxyManager()
proxies = manager.fetch_proxies(limit=5)

if not proxies:
    print("No proxies to test")
    exit()

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
```

### Pattern 3: Get Fastest Proxy

```python
# Fetch proxies
manager = ProxyManager()
proxies = manager.fetch_proxies(limit=5)

if not proxies:
    print("No proxies available")
    exit()

# Get fastest proxy
best = manager.get_best_proxy(proxies)

if best:
    print(f"✓ Fastest proxy: {best.address}")
    print(f"  Speed: {best.speed}ms")
    print(f"  Country: {best.country}")
else:
    print("✗ No suitable proxy found")
```

### Pattern 4: Custom Proxy Creation

```python
from vnstock.core.utils.proxy_manager import Proxy

# Create custom proxies
custom_proxies = [
    Proxy(
        protocol='http',
        ip='192.168.1.100',
        port=8080,
        country='Local Network'
    ),
    Proxy(
        protocol='https',
        ip='10.0.0.1',
        port=3128,
        country='Corporate'
    ),
    Proxy(
        protocol='socks5',
        ip='172.16.0.1',
        port=1080,
        country='VPN'
    ),
]

print("Custom Proxies:")
for proxy in custom_proxies:
    print(f"  {proxy.address} ({proxy.country})")
```

### Pattern 5: Proxy Rotation for Multiple Requests

```python
import requests

# Fetch proxies for rotation
manager = ProxyManager()
proxies = manager.fetch_proxies(limit=3)

if not proxies:
    print("No proxies available for rotation")
    exit()

# Simulate multiple API calls with proxy rotation
api_endpoints = [
    'https://api.example.com/data1',
    'https://api.example.com/data2',
    'https://api.example.com/data3',
    'https://api.example.com/data4',
    'https://api.example.com/data5'
]

print(f"Using {len(proxies)} proxies for {len(api_endpoints)} requests")

for i, endpoint in enumerate(api_endpoints):
    proxy = proxies[i % len(proxies)]
    print(f"  {endpoint} -> {proxy.address} ({proxy.country})")

    try:
        response = requests.get(
            endpoint,
            proxies=proxy.dict_format,
            timeout=10
        )
        print(f"    Status: {response.status_code}")
    except Exception as e:
        print(f"    Error: {e}")
```

### Pattern 6: Complete Workflow

```python
# Initialize manager
manager = ProxyManager(timeout=10)

# Step 1: Fetch proxies
print("Step 1: Fetching proxies...")
proxies = manager.fetch_proxies(limit=5)

if not proxies:
    print("✗ No proxies fetched")
    exit()

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
```

### Pattern 7: Error Handling and Fallback

```python
def make_request_with_proxy(url, max_retries=3):
    """Make HTTP request with proxy fallback."""
    manager = ProxyManager(timeout=5)

    for attempt in range(max_retries):
        try:
            print(f"Attempt {attempt + 1}/{max_retries}")
            proxies = manager.fetch_proxies(limit=1)

            if proxies:
                proxy = proxies[0]
                print(f"Using proxy: {proxy.address}")

                response = requests.get(
                    url,
                    proxies=proxy.dict_format,
                    timeout=10
                )
                return response
            else:
                print("No proxies available")

        except Exception as e:
            print(f"Attempt {attempt + 1} failed: {e}")
            continue

    # Fallback: direct connection
    print("Using direct connection (no proxy)")
    return requests.get(url, timeout=10)

# Usage
try:
    response = make_request_with_proxy('https://api.example.com/data')
    print(f"Success: {response.status_code}")
except Exception as e:
    print(f"Final failure: {e}")
```

## Advanced Configuration

### Setting API Key

For proxyscrape premium access:

```python
manager = ProxyManager(api_key='YOUR_API_KEY')
proxies = manager.fetch_proxies(limit=100)  # Higher limit available
```

### Custom Test URL

```python
# Test with specific endpoint
working, failed = manager.test_proxies(
    proxies,
    test_url='https://quote.vcbs.com.vn/api/Quote/Overview/ACB',
    timeout=15
)
```

### Filtering Proxies

```python
# Get only HTTP proxies
http_only = [p for p in proxies if p.protocol == 'http']

# Get only proxies under 100ms
fast_proxies = [p for p in proxies if p.speed < 100]

# Get specific country
vietnam_proxies = [p for p in proxies if 'Vietnam' in p.country]
```

### Proxy Persistence

```python
import json

def save_proxies(proxies, filename='proxies.json'):
    data = [
        {
            'protocol': p.protocol,
            'ip': p.ip,
            'port': p.port,
            'country': p.country,
            'speed': p.speed
        }
        for p in proxies
    ]
    with open(filename, 'w') as f:
        json.dump(data, f)

def load_proxies(filename='proxies.json'):
    from vnstock.core.utils.proxy_manager import Proxy
    
    with open(filename) as f:
        data = json.load(f)
    
    return [Proxy(**item) for item in data]

# Usage
proxies = manager.fetch_proxies(limit=10)
save_proxies(proxies)

# Later...
proxies = load_proxies()
working, _ = manager.test_proxies(proxies)
```

## Troubleshooting

### No Proxies Available

**Problem:** `fetch_proxies()` returns empty list

**Solutions:**
1. Check internet connection
2. Verify proxyscrape API is accessible
3. Check rate limits (free tier: limited requests)
4. Use fallback proxy list
5. Retry after delay

```python
import time

proxies = manager.fetch_proxies(limit=5)
if not proxies:
    print("Rate limited, retrying in 60s...")
    time.sleep(60)
    proxies = manager.fetch_proxies(limit=5)
```

### Proxy Connection Timeout

**Problem:** Proxy responds too slowly

**Solutions:**
1. Increase timeout value
2. Test proxies before use
3. Use faster proxies (lower speed metric)
4. Get additional proxies

```python
# Increase timeout
working, _ = manager.test_proxies(proxies, timeout=20)

# Use fastest proxies
proxies.sort(key=lambda p: p.speed)
fast_proxies = proxies[:5]
```

### API Errors

**Problem:** Error fetching from proxyscrape

**Solutions:**
1. Check network connectivity
2. Verify API endpoint is accessible
3. Check rate limits
4. Use custom proxy list as fallback

```python
try:
    proxies = manager.fetch_proxies(limit=10)
except Exception as e:
    print(f"API error: {e}")
    # Use custom proxies
    proxies = [
        Proxy('http', 'proxy1.example.com', 8080),
        Proxy('http', 'proxy2.example.com', 3128),
    ]
```

### Proxy Not Working with VCI

**Problem:** VCI Quote fails with proxy

**Solutions:**
1. Test proxy with httpbin before using with VCI
2. Verify proxy supports HTTPS (for most APIs)
3. Check timeout is sufficient
4. Try different proxy

```python
# Test proxy first
test_url = 'https://httpbin.org/ip'
if manager.test_proxy(proxy, test_url=test_url):
    # Safe to use with VCI
    print("Proxy works, using with VCI...")
else:
    print("Proxy failed test, trying another...")
```

## Examples

See `tests/examples/proxy_examples.py` for complete working examples with 8 different usage patterns:

```bash
# Run all examples
python tests/examples/proxy_examples.py
```

### Example 1: Basic Proxy Fetching

```python
from vnstock.core.utils.proxy_manager import ProxyManager

# Initialize manager
manager = ProxyManager(timeout=10)

# Fetch 5 free proxies
proxies = manager.fetch_proxies(limit=5, skip=0)

if proxies:
    print(f"✓ Fetched {len(proxies)} proxies")
    manager.print_proxies(proxies)
else:
    print("✗ Failed to fetch proxies")
```

### Example 2: Proxy Testing

```python
# Fetch and test proxies
manager = ProxyManager()
proxies = manager.fetch_proxies(limit=5)

if proxies:
    print(f"Testing {len(proxies)} proxies...")

    # Test all proxies
    working, failed = manager.test_proxies(proxies, timeout=5)

    print(f"✓ Working: {len(working)} proxies")
    print(f"✗ Failed: {len(failed)} proxies")

    if working:
        manager.print_proxies(working)
```

### Example 3: Get Fastest Proxy

```python
# Get the fastest proxy
proxies = manager.fetch_proxies(limit=10)
best = manager.get_best_proxy(proxies)

if best:
    print(f"✓ Fastest proxy: {best.address}")
    print(f"  Speed: {best.speed}ms")
    print(f"  Country: {best.country}")
```

### Example 4: Proxy Rotation

```python
# Rotate through proxies for multiple requests
proxies = manager.fetch_proxies(limit=3)
urls = ['https://api1.example.com', 'https://api2.example.com', 'https://api3.example.com']

for i, url in enumerate(urls):
    proxy = proxies[i % len(proxies)]
    print(f"Requesting {url} with {proxy.address}")

    response = requests.get(url, proxies=proxy.dict_format, timeout=10)
    print(f"Status: {response.status_code}")
```

### Example 5: Custom Proxies

```python
from vnstock.core.utils.proxy_manager import Proxy

# Create custom proxy list
custom_proxies = [
    Proxy('http', '192.168.1.100', 8080, 'Local'),
    Proxy('https', '10.0.0.1', 3128, 'Office'),
    Proxy('socks5', '172.16.0.1', 1080, 'VPN'),
]

print("Custom Proxies:")
for proxy in custom_proxies:
    print(f"  {proxy.address} ({proxy.country})")
```

### Example 6: Complete Workflow

```python
# Complete proxy management workflow
manager = ProxyManager(timeout=10)

# 1. Fetch proxies
proxies = manager.fetch_proxies(limit=5)
print(f"Fetched {len(proxies)} proxies")

# 2. Test proxies
working, failed = manager.test_proxies(proxies)
print(f"Working: {len(working)}, Failed: {len(failed)}")

# 3. Get best proxy
best = manager.get_best_proxy(working)
if best:
    print(f"Best proxy: {best.address} ({best.speed}ms)")

# 4. Use proxy
response = requests.get('https://httpbin.org/ip', proxies=best.dict_format)
print(f"Response: {response.json()}")
```

### Example 7: Error Handling

```python
def safe_request(url, max_retries=3):
    manager = ProxyManager(timeout=5)

    for attempt in range(max_retries):
        try:
            proxies = manager.fetch_proxies(limit=1)
            if proxies:
                proxy = proxies[0]
                response = requests.get(url, proxies=proxy.dict_format, timeout=10)
                return response
        except Exception as e:
            print(f"Attempt {attempt + 1} failed: {e}")
            continue

    # Fallback to direct connection
    return requests.get(url, timeout=10)

# Usage
response = safe_request('https://api.example.com/data')
print(f"Final status: {response.status_code}")
```

### Example 8: Batch Processing

```python
# Process multiple URLs with proxy rotation
manager = ProxyManager()
proxies = manager.fetch_proxies(limit=3)

urls = [
    'https://api.github.com/user',
    'https://api.github.com/repos',
    'https://api.github.com/issues',
    'https://api.github.com/pulls'
]

results = []
for i, url in enumerate(urls):
    proxy = proxies[i % len(proxies)]
    try:
        response = requests.get(url, proxies=proxy.dict_format, timeout=10)
        results.append({
            'url': url,
            'proxy': proxy.address,
            'status': response.status_code,
            'success': True
        })
    except Exception as e:
        results.append({
            'url': url,
            'proxy': proxy.address,
            'error': str(e),
            'success': False
        })

# Display results
for result in results:
    status = f"Status: {result['status']}" if result['success'] else f"Error: {result['error']}"
    print(f"{result['url']} -> {result['proxy']} | {status}")
```

## Integration with HTTP Clients

### Using with requests

```python
import requests
from vnstock.core.utils.proxy_manager import ProxyManager

manager = ProxyManager()
proxies = manager.fetch_proxies(limit=1)

if proxies:
    proxy = proxies[0]

    # Standard requests usage
    response = requests.get(
        'https://api.example.com/data',
        proxies=proxy.dict_format,
        timeout=10
    )
```

### Using with aiohttp

```python
import aiohttp
import asyncio
from vnstock.core.utils.proxy_manager import ProxyManager

async def fetch_with_proxy(url, proxy):
    connector = aiohttp.TCPConnector()
    proxy_url = proxy.address  # http://ip:port

    async with aiohttp.ClientSession(connector=connector) as session:
        async with session.get(url, proxy=proxy_url) as response:
            return await response.text()

# Usage
manager = ProxyManager()
proxies = manager.fetch_proxies(limit=1)

if proxies:
    proxy = proxies[0]
    result = asyncio.run(fetch_with_proxy('https://api.example.com', proxy))
```

### Using with urllib

```python
import urllib.request
from vnstock.core.utils.proxy_manager import ProxyManager

manager = ProxyManager()
proxies = manager.fetch_proxies(limit=1)

if proxies:
    proxy = proxies[0]

    # Setup proxy handler
    proxy_handler = urllib.request.ProxyHandler(proxy.dict_format)
    opener = urllib.request.build_opener(proxy_handler)

    # Make request
    response = opener.open('https://api.example.com')
    data = response.read()
```
   response = requests.get(url, proxies=proxy_config)
   ```

4. **Handle in your code:**
   ```python
   # Modify VCI Quote to accept proxies if needed
   # or pass proxies at requests level in connector
   ```

## Performance Considerations

- **Proxy fetching:** 1-5 seconds (includes API call to proxyscrape)
- **Proxy testing:** 5-30 seconds per batch (depends on timeout and network)
- **Speed metric:** Response time in milliseconds, updated during testing
- **Cache proxies:** Store working proxies to avoid repeated API calls
- **Timeout values:** Balance between accuracy (higher timeout) and speed (lower timeout)
- **Batch processing:** Test proxies in parallel for better performance

## Best Practices

### Proxy Management
- **Test before use:** Always test proxies before relying on them
- **Monitor performance:** Track proxy speed and reliability over time
- **Rotate regularly:** Switch proxies to avoid IP blocking
- **Handle failures:** Implement fallback to direct connections

### Error Handling
- **Network timeouts:** Set appropriate timeout values for your use case
- **Connection errors:** Retry with different proxies on failure
- **Rate limiting:** Respect API limits and implement delays between requests
- **Fallback strategy:** Always have a direct connection fallback

### Security Considerations
- **HTTPS proxies:** Prefer HTTPS proxies for secure connections
- **Proxy trust:** Be aware that free proxies may log your traffic
- **Data sensitivity:** Avoid sending sensitive data through untrusted proxies
- **VPN alternative:** Consider VPNs for high-security requirements

## Troubleshooting

### Common Issues

#### No Proxies Available
**Problem:** `fetch_proxies()` returns empty list

**Solutions:**
- Check internet connection
- Verify proxyscrape API accessibility
- Check rate limits (free tier limitations)
- Retry after delay
- Use custom proxy list as fallback

#### Proxy Connection Timeout
**Problem:** Proxy responds too slowly or times out

**Solutions:**
- Increase timeout value in ProxyManager
- Test proxies before use with `test_proxies()`
- Use faster proxies (check speed metric)
- Get additional proxies with higher limit

#### API Errors
**Problem:** Error fetching from proxyscrape API

**Solutions:**
- Check network connectivity
- Verify API endpoint accessibility
- Implement retry logic with exponential backoff
- Use cached proxy list as fallback

### Debug Mode

Enable detailed logging for troubleshooting:

```python
import logging

logging.basicConfig(level=logging.DEBUG)

manager = ProxyManager()
proxies = manager.fetch_proxies(limit=5)  # Will show debug logs
```

## Related Documentation

- [ProxyManager API Reference](../vnstock/core/utils/proxy_manager.py)
- [Complete Examples](../tests/examples/proxy_examples.py)
- [Proxy Unit Tests](../tests/unit/core/test_proxy_manager.py)
- [Proxyscrape API Documentation](https://www.proxyscrape.com/docs)

## Contributing

To contribute to the proxy system:

1. **Add new proxy sources:** Extend ProxyManager for additional APIs
2. **Improve testing:** Enhance proxy validation and performance metrics
3. **Add protocols:** Support additional proxy protocols (SOCKS4, etc.)
4. **Performance optimization:** Improve batch testing and caching

## License

This proxy management system is part of the vnstock project and follows the same license terms.
