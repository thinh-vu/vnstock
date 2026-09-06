# vnstock/core/utils/browser_profiles.py

# User-Agent strings used when a caller explicitly selects a browser/platform via
# `get_headers(browser=..., platform=...)`. The library does NOT rotate between
# these; a given selection yields the same header on every request.
#
# Verified against vendor release channels on 2026-09-06:
#   Chrome 152.0.7977.77 (2026-09-03) · Edge 152.0.4191.62 (2026-09-04)
#   Firefox 155.0 (2026-09-01)        · Safari 26.5 · Opera 133 (Chromium 148)
#   Samsung Internet 30
#
# Maintenance notes:
#   - Chrome and Edge moved to a two-week stable cadence in September 2026, so the
#     major version here will drift quickly. Only the major version is significant;
#     Chromium reports the rest as ".0.0.0" (User-Agent Reduction).
#   - Chromium freezes the mobile token to "Android 10; K" and omits the device
#     model. Apple freezes the desktop token at "Mac OS X 10_15_7". Both are
#     upstream anti-fingerprinting measures, not placeholders to be "corrected".
#   - Brave and Vivaldi send a Chrome-identical User-Agent by default and add no
#     token of their own; they are mapped to the Chrome string deliberately.
#   - Coc Coc is Chromium-based and is mapped to its Chromium base string.

_CHROME_VERSION = "152.0.0.0"
_CHROMIUM_OPERA_BASE = "148.0.0.0"

_CHROME_WINDOWS = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    f"AppleWebKit/537.36 (KHTML, like Gecko) Chrome/{_CHROME_VERSION} Safari/537.36"
)
_CHROME_MACOS = (
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
    f"AppleWebKit/537.36 (KHTML, like Gecko) Chrome/{_CHROME_VERSION} Safari/537.36"
)
_CHROME_LINUX = (
    "Mozilla/5.0 (X11; Linux x86_64) "
    f"AppleWebKit/537.36 (KHTML, like Gecko) Chrome/{_CHROME_VERSION} Safari/537.36"
)

DESKTOP_BROWSERS = {
    "chrome": {
        "windows": _CHROME_WINDOWS,
        "macos": _CHROME_MACOS,
        "linux": _CHROME_LINUX,
    },
    "firefox": {
        "windows": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:155.0) "
            "Gecko/20100101 Firefox/155.0"
        ),
        "macos": (
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:155.0) "
            "Gecko/20100101 Firefox/155.0"
        ),
        "linux": (
            "Mozilla/5.0 (X11; Linux x86_64; rv:155.0) Gecko/20100101 Firefox/155.0"
        ),
    },
    "edge": {
        "windows": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            f"Chrome/{_CHROME_VERSION} Safari/537.36 Edg/{_CHROME_VERSION}"
        ),
        "macos": (
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            f"Chrome/{_CHROME_VERSION} Safari/537.36 Edg/{_CHROME_VERSION}"
        ),
    },
    "opera": {
        "windows": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            f"Chrome/{_CHROMIUM_OPERA_BASE} Safari/537.36 OPR/133.0.0.0"
        ),
        "macos": (
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            f"Chrome/{_CHROMIUM_OPERA_BASE} Safari/537.36 OPR/133.0.0.0"
        ),
    },
    # Brave and Vivaldi ship a Chrome-identical User-Agent by default.
    "brave": {"windows": _CHROME_WINDOWS, "macos": _CHROME_MACOS},
    "vivaldi": {"windows": _CHROME_WINDOWS, "macos": _CHROME_MACOS},
    # Coc Coc is Chromium-based; mapped to its Chromium base string.
    "coccoc": {"windows": _CHROME_WINDOWS, "macos": _CHROME_MACOS},
    "safari": {
        "macos": (
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
            "AppleWebKit/605.1.15 (KHTML, like Gecko) Version/26.5 Safari/605.1.15"
        ),
    },
}

# Chromium-based mobile strings use the reduced form: the platform token is frozen
# to "Android 10; K" and the device model is omitted.
_CHROME_ANDROID = (
    "Mozilla/5.0 (Linux; Android 10; K) "
    f"AppleWebKit/537.36 (KHTML, like Gecko) Chrome/{_CHROME_VERSION} "
    "Mobile Safari/537.36"
)

MOBILE_BROWSERS = {
    "chrome": {"android": _CHROME_ANDROID},
    "safari": {
        "ios": (
            "Mozilla/5.0 (iPhone; CPU iPhone OS 26_5 like Mac OS X) "
            "AppleWebKit/605.1.15 (KHTML, like Gecko) Version/26.5 "
            "Mobile/15E148 Safari/604.1"
        ),
    },
    "samsung": {
        "android": (
            "Mozilla/5.0 (Linux; Android 10; K) "
            "AppleWebKit/537.36 (KHTML, like Gecko) SamsungBrowser/30.0 "
            f"Chrome/{_CHROME_VERSION} Mobile Safari/537.36"
        ),
    },
    "opera": {
        "android": (
            "Mozilla/5.0 (Linux; Android 10; K) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            f"Chrome/{_CHROMIUM_OPERA_BASE} Mobile Safari/537.36 OPR/100.0.0.0"
        ),
    },
    "coccoc": {"android": _CHROME_ANDROID},
    "firefox": {
        "android": "Mozilla/5.0 (Android 15; Mobile; rv:155.0) Gecko/155.0 Firefox/155.0",
    },
}

# Combine all browser profiles
USER_AGENTS = {}

for browser_dict in [DESKTOP_BROWSERS, MOBILE_BROWSERS]:
    for browser, platforms in browser_dict.items():
        if browser not in USER_AGENTS:
            USER_AGENTS[browser] = {}
        USER_AGENTS[browser].update(platforms)


def list_all_profiles():
    print("Available browser/platform combinations:")
    for browser, platforms in USER_AGENTS.items():
        for platform in platforms:
            print(f"- {browser:10} | {platform:10}")
