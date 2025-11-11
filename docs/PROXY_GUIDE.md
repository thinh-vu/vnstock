# Proxy Guide for vnstock

Complete guide for using proxies with vnstock to handle network restrictions, ISP blocks, and rate limiting.

## Table of Contents

- [Overview](#overview)
- [Quick Start](#quick-start)
- [ProxyManager Class](#proxymanager-class)
- [Usage Patterns](#usage-patterns)
- [Advanced Configuration](#advanced-configuration)
- [Troubleshooting](#troubleshooting)
- [Examples](#examples)

## Overview

The `ProxyManager` utility helps you:

1. **Fetch free proxies** from the proxyscrape API
2. **Test proxies** for availability and speed
3. **Manage proxy lists** with validation and sorting
4. **Integrate proxies** with vnstock data sources
5. **Handle network errors** gracefully

### Key Features

- Free proxy fetching from proxyscrape API
- Support for HTTP, HTTPS, and SOCKS5 proxies
- Automatic proxy speed testing
- Proxy validation and filtering
- Easy integration with vnstock Quote classes
- Mock-friendly design for testing

### When to Use Proxies

- Your ISP or network blocks Vietnamese stock exchanges
- You need to bypass geographic restrictions
- You want to distribute requests across multiple IPs
- You're facing rate limiting from data sources
- You need anonymity or IP rotation for large-scale scraping

## Quick Start

### Basic Proxy Fetching

```python
from vnstock.core.utils.proxy_manager import ProxyManager

# Initialize manager
manager = ProxyManager(timeout=10)

# Fetch proxies
proxies = manager.fetch_proxies(limit=5)

# View available proxies
manager.print_proxies(proxies)
```

### Using a Proxy

```python
from vnstock.explorer.vci import Quote
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

### Pattern 1: Single Proxy

```python
from vnstock.core.utils.proxy_manager import ProxyManager
import requests

manager = ProxyManager()
proxies = manager.fetch_proxies(limit=1)

if proxies:
    proxy = proxies[0]
    
    # Use with requests
    response = requests.get(
        'https://quote.vcbs.com.vn/api/Quote/Overview',
        proxies=proxy.dict_format,
        timeout=10
    )
```

### Pattern 2: Proxy Rotation

```python
import requests

manager = ProxyManager()
proxies = manager.fetch_proxies(limit=5)

symbols = ['ACB', 'VCB', 'TCB', 'BID', 'HDB']

for i, symbol in enumerate(symbols):
    proxy = proxies[i % len(proxies)]
    
    response = requests.get(
        f'https://quote.vcbs.com.vn/api/Quote/Overview?{symbol}',
        proxies=proxy.dict_format,
        timeout=10
    )
```

### Pattern 3: Fallback with Testing

```python
manager = ProxyManager(timeout=5)

# Fetch and test
proxies = manager.fetch_proxies(limit=10)
working, _ = manager.test_proxies(proxies)

if working:
    proxy = manager.get_best_proxy(working)
    print(f"Using: {proxy.address}")
else:
    print("No working proxies, using direct connection")
```

### Pattern 4: Custom Proxy List

```python
from vnstock.core.utils.proxy_manager import Proxy

# Create custom proxies
my_proxies = [
    Proxy('http', '192.168.1.100', 8080, 'Local'),
    Proxy('https', '10.0.0.1', 3128, 'Office'),
    Proxy('socks5', '172.16.0.1', 1080, 'VPN'),
]

# Test them
working, failed = manager.test_proxies(my_proxies)
```

### Pattern 5: Error Handling

```python
def fetch_with_proxy(url, max_retries=3):
    manager = ProxyManager(timeout=10)
    
    for attempt in range(max_retries):
        try:
            proxies = manager.fetch_proxies(limit=1)
            if proxies:
                proxy = proxies[0]
                response = requests.get(
                    url,
                    proxies=proxy.dict_format,
                    timeout=10
                )
                return response
        except Exception as e:
            print(f"Attempt {attempt + 1} failed: {e}")
            continue
    
    # Fallback: direct connection
    return requests.get(url, timeout=10)
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

See `tests/examples/proxy_examples.py` for complete working examples:

```bash
# Run examples
python -m tests.examples.proxy_examples
```

### Example 1: Basic Fetch

```python
from vnstock.core.utils.proxy_manager import ProxyManager

manager = ProxyManager()
proxies = manager.fetch_proxies(limit=5)
manager.print_proxies(proxies)
```

### Example 2: Find Best Proxy

```python
proxies = manager.fetch_proxies(limit=10)
best = manager.get_best_proxy(proxies)
print(f"Best: {best.address} ({best.speed}ms)")
```

### Example 3: Rotate Through Proxies

```python
symbols = ['ACB', 'VCB', 'TCB', 'BID', 'HDB']
proxies = manager.fetch_proxies(limit=3)

for i, symbol in enumerate(symbols):
    proxy = proxies[i % len(proxies)]
    print(f"{symbol} -> {proxy.address}")
```

### Example 4: Error Handling

```python
try:
    proxies = manager.fetch_proxies(limit=5)
    if proxies:
        best = manager.get_best_proxy(proxies)
        print(f"✓ Using: {best.address}")
    else:
        print("✓ No proxies, using direct")
except Exception as e:
    print(f"✗ Error: {e}")
```

## Integration with vnstock

To integrate proxies with vnstock data sources:

1. **Fetch proxies:**
   ```python
   from vnstock.core.utils.proxy_manager import ProxyManager
   manager = ProxyManager()
   proxies = manager.fetch_proxies(limit=5)
   ```

2. **Test proxies:**
   ```python
   working, failed = manager.test_proxies(proxies)
   ```

3. **Use with requests:**
   ```python
   import requests
   proxy_config = best_proxy.dict_format
   response = requests.get(url, proxies=proxy_config)
   ```

4. **Handle in your code:**
   ```python
   # Modify VCI Quote to accept proxies if needed
   # or pass proxies at requests level in connector
   ```

## Performance Considerations

- **Proxy fetching:** 1-5 seconds (includes API call)
- **Proxy testing:** 5-30 seconds per batch (depends on timeout)
- **Speed metric:** Updated during testing, represents latency
- **Cache proxies:** Store working proxies to avoid repeated API calls
- **Timeout values:** Balance between accuracy and speed

## Related Documentation

- [ProxyManager API](../vnstock/core/utils/proxy_manager.py)
- [Proxy Integration Tests](../tests/unit/explorer/test_vci_quote_with_proxy.py)
- [Proxy Unit Tests](../tests/unit/core/test_proxy_manager.py)
- [proxyscrape API](https://www.proxyscrape.com/docs)
