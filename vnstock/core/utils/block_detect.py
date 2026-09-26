"""
Recognise the marks of a CDN or web application firewall refusing access.

Everything here is a pure function: nothing sends a request and nothing reads
network configuration, so it can be tested apart from the calling layer.

The single most important design rule: **not blocked is the default**. A 403
carrying no CDN marker is treated as an ordinary authentication failure from the
source itself, and behaviour stays exactly as it was. Mistaking an auth failure
for a block would make the library stop calling for minutes on end with no good
reason - far more damaging than missing one real block.
"""

import re
from dataclasses import dataclass
from email.utils import parsedate_to_datetime
from urllib.parse import urlsplit

from vnstock.config import Config
from vnstock.core.exceptions import (
    AccessDeniedError,
    ChallengeRequiredError,
    RateLimitedError,
)

__all__ = [
    "BlockSignal",
    "build_block_error",
    "describe_cooldown",
    "detect_block",
    "host_of",
    "parse_retry_after",
]

# Only these statuses are worth suspecting. Anything else leaves immediately
# without touching the response body - the success path must cost nothing extra.
_BLOCKABLE_STATUS = frozenset({403, 429, 451, 503})

# Content types that may carry a block page. CDN block pages are nearly always HTML.
_SNIFFABLE_PREFIXES = ("text/html", "text/plain", "application/xhtml")

# Vendor fingerprints read from headers. Each entry: (header name, substring the
# value must contain or None when mere presence is enough, vendor name).
_VENDOR_HEADERS: tuple[tuple[str, str | None, str], ...] = (
    ("cf-mitigated", None, "cloudflare"),
    ("cf-ray", None, "cloudflare"),
    ("server", "cloudflare", "cloudflare"),
    ("server", "akamaighost", "akamai"),
    ("server", "akamainetstorage", "akamai"),
    ("akamai-grn", None, "akamai"),
    ("x-akamai-transformed", None, "akamai"),
    ("x-iinfo", None, "imperva"),
    ("x-cdn", "imperva", "imperva"),
    ("x-cdn", "incapsula", "imperva"),
    ("x-sucuri-id", None, "sucuri"),
    ("x-amzn-waf-action", None, "aws"),
)

# Body markers, evaluated in exactly this order.
# Each entry: (substrings - matching one is enough, kind, internal code, vendor).
_BODY_MARKERS: tuple[tuple[tuple[str, ...], str, str, str | None], ...] = (
    (("error code: 1015", "error 1015"), "rate_limit", "cf_1015", "cloudflare"),
    (
        (
            "just a moment",
            "checking your browser",
            "cdn-cgi/challenge-platform",
            "__cf_chl",
            "enable javascript and cookies to continue",
        ),
        "challenge",
        "cf_js_challenge",
        "cloudflare",
    ),
    (
        ("cf-turnstile", "g-recaptcha", "hcaptcha", "captcha"),
        "challenge",
        "captcha",
        None,
    ),
    (
        (
            "error code: 1020",
            "error code: 1006",
            "error code: 1007",
            "error code: 1008",
            "error code: 1010",
        ),
        "denied",
        "cf_firewall",
        "cloudflare",
    ),
    (("errors.edgesuite.net",), "denied", "akamai_denied", "akamai"),
    (
        ("incapsula incident id", "_incapsula_resource"),
        "denied",
        "imperva_denied",
        "imperva",
    ),
)

# Generic firewall markers, applied only to 403 and only once an authentication
# failure from the source itself has been ruled out.
_GENERIC_DENY_MARKERS = (
    "attention required",
    "access to this page has been denied",
    "your request has been blocked",
    "bot detection",
    "unusual traffic",
)

# Marks of an authentication or authorisation failure from the source, not a CDN
# block. Hitting any of these stops the check: do not conclude "blocked".
# The Vietnamese entries below are page content to match, not prose.
_AUTH_MARKERS = (
    "unauthorized",
    "invalid token",
    "access token",
    "api key",
    "apikey",
    "expired",
    "chưa đăng nhập",
    "quyền truy cập",
)

_AKAMAI_REFERENCE = re.compile(r"reference\s*#")
_BLOCKED_BY_SECURITY = re.compile(r"blocked by[^<]{0,40}(security|firewall|waf)")


@dataclass(frozen=True)
class BlockSignal:
    """What was recognised in a response bearing the marks of a block.

    Attributes:
        kind: "rate_limit", "challenge" or "denied".
        vendor: Protection layer identified, "unknown" when unclear.
        status_code: HTTP status of the response.
        reason: Stable internal code, for logging and for writing tests against.
        retry_after: Seconds the server asked us to wait, None when it did not.
        evidence: The exact marker that matched. Always present, so a false
            positive can be diagnosed.
    """

    kind: str
    vendor: str
    status_code: int
    reason: str
    retry_after: float | None
    evidence: str


def parse_retry_after(value: str | None) -> float | None:
    """Read a Retry-After header, accepting both a seconds count and a date.

    Never raises: an unreadable value returns None. Unlike urllib3's function of
    the same name, which raises InvalidHeader - here a malformed header must not
    be allowed to derail the error-handling path.
    """
    if not value:
        return None
    text = str(value).strip()
    if not text:
        return None
    try:
        return max(0.0, float(text))
    except (TypeError, ValueError):
        pass
    try:
        import datetime as _dt

        moment = parsedate_to_datetime(text)
        if moment is None:
            return None
        if moment.tzinfo is None:
            moment = moment.replace(tzinfo=_dt.timezone.utc)
        delta = (moment - _dt.datetime.now(_dt.timezone.utc)).total_seconds()
        return max(0.0, delta)
    except Exception:
        return None


def _vendor_from_headers(headers) -> tuple[str, str]:
    """Look for a vendor fingerprint in the headers. Returns (name, evidence)."""
    for name, needle, vendor in _VENDOR_HEADERS:
        raw = headers.get(name)
        if raw is None:
            continue
        if needle is None:
            return vendor, f"{name}: {raw}"
        if needle in str(raw).lower():
            return vendor, f"{name}: {raw}"
    return "unknown", ""


def _sniff_body(response) -> str | None:
    """Read the head of the response body to sniff for markers, guarded throughout."""
    headers = response.headers
    ctype = str(headers.get("Content-Type") or "").lower()

    # Only sniff textual content, or content whose type the server left unstated.
    if ctype and not ctype.startswith(_SNIFFABLE_PREFIXES):
        return None

    # Leave a streaming response alone: reading .content would consume the stream.
    if getattr(response, "_content_consumed", True) is False:
        return None

    # Slice bytes first, decode second. Using .text would force a decode of the
    # whole body, possibly megabytes, just to find one short substring.
    raw = response.content
    if not raw:
        return None
    return raw[: Config.BODY_SNIFF_LIMIT].decode("utf-8", errors="replace").lower()


def _match_body(
    body: str, status: int, vendor: str, header_hit: str
) -> BlockSignal | None:
    """Match the response body against the known markers."""
    for needles, kind, reason, marker_vendor in _BODY_MARKERS:
        for needle in needles:
            if needle in body:
                return BlockSignal(
                    kind=kind,
                    vendor=marker_vendor or vendor,
                    status_code=status,
                    reason=reason,
                    retry_after=None,
                    evidence=f"body: {needle}",
                )

    if "access denied" in body and _AKAMAI_REFERENCE.search(body):
        return BlockSignal(
            kind="denied",
            vendor="akamai" if vendor == "unknown" else vendor,
            status_code=status,
            reason="akamai_denied",
            retry_after=None,
            evidence="body: access denied + reference #",
        )

    # The generic fallback rules apply to 403 only, and only when nothing
    # suggests an authentication failure from the source itself.
    if status == 403 and not header_hit:
        if any(marker in body for marker in _AUTH_MARKERS):
            return None
    if status == 403:
        for marker in _GENERIC_DENY_MARKERS:
            if marker in body:
                return BlockSignal(
                    kind="denied",
                    vendor=vendor,
                    status_code=status,
                    reason="waf_generic",
                    retry_after=None,
                    evidence=f"body: {marker}",
                )
        found = _BLOCKED_BY_SECURITY.search(body)
        if found:
            return BlockSignal(
                kind="denied",
                vendor=vendor,
                status_code=status,
                reason="waf_generic",
                retry_after=None,
                evidence=f"body: {found.group(0)}",
            )
    return None


def detect_block(response) -> BlockSignal | None:
    """Recognise the marks of a block in an HTTP response.

    Returns None when the response bears no such marks - including the ordinary
    authentication 403 a data source returns on its own account.

    This function never raises: every parsing mishap collapses to None, so that a
    malformed response cannot mask the real error the caller is handling.
    """
    if not Config.BLOCK_DETECTION_ENABLED:
        return None
    try:
        status = response.status_code
        if status not in _BLOCKABLE_STATUS:
            return None

        headers = response.headers
        vendor, header_hit = _vendor_from_headers(headers)

        # An auth challenge means the source is asking who you are, not refusing you.
        if headers.get("WWW-Authenticate") is not None:
            return None

        if status == 429:
            return BlockSignal(
                kind="rate_limit",
                vendor=vendor,
                status_code=429,
                reason="http_429",
                retry_after=parse_retry_after(headers.get("Retry-After")),
                evidence=header_hit or "status=429",
            )

        if status == 451:
            return BlockSignal(
                kind="denied",
                vendor=vendor,
                status_code=451,
                reason="http_451",
                retry_after=None,
                evidence=header_hit or "status=451",
            )

        # A JSON response with no CDN fingerprint is almost certainly a business
        # error from the source itself, not a block page from the edge.
        ctype = str(headers.get("Content-Type") or "").lower()
        if "json" in ctype and not header_hit:
            return None

        body = _sniff_body(response)
        if body:
            signal = _match_body(body, status, vendor, header_hit)
            if signal is not None:
                return signal

        if status == 403 and header_hit:
            return BlockSignal(
                kind="denied",
                vendor=vendor,
                status_code=403,
                reason=f"{vendor}_403",
                retry_after=None,
                evidence=header_hit,
            )

        # A 503 behind a CDN whose body carries no challenge marker: treat it as
        # the origin being briefly unwell and leave it to the ordinary retry layer.
        return None
    except Exception:
        return None


# ---------------------------------------------------------------------------
# Building an error from a recognised signal
#
# This sits in the same module as the detection, and is public API, so that
# vnstock and vnstock_data use one single set of messages. Every extra copy is
# one more chance for the two to say different things about the same event.
#
# The message text itself stays in Vietnamese: it is read by end users, not by
# maintainers.
# ---------------------------------------------------------------------------

_RESET_HINT = "from vnstock.core.utils import reset_circuit; reset_circuit()"


def host_of(url: str) -> str:
    """Take the hostname out of a URL, for use in a message shown to the user."""
    return (urlsplit(url).netloc or url).lower()


def describe_cooldown(
    host: str, remaining: float, reset_hint: str = _RESET_HINT
) -> str:
    """Message for a request stopped early because a cooldown is in force."""
    return (
        f"Đang tạm ngừng gọi tới {host} vì lượt gọi trước bị nguồn dữ liệu chặn. "
        f"Còn {remaining:.0f} giây nữa mới thử lại. Yêu cầu này dừng tại chỗ, "
        "không phát sinh kết nối mạng, để tránh kéo dài thời gian bị chặn. "
        f"Nếu bạn đã đổi mạng hoặc đổi proxy và muốn thử lại ngay: {reset_hint}"
    )


def build_block_error(
    signal: "BlockSignal",
    url: str,
    cooldown: float,
    proxy_hint: str | None = None,
):
    """Build the specific error, with a message saying what to do next.

    Args:
        signal: The block signal that was recognised.
        url: The address that was called.
        cooldown: Seconds this host will be left alone for.
        proxy_hint: A sentence about proxies, added only when the calling library
            actually supports them. vnstock dropped proxy management, so it
            passes nothing: telling users to configure something that does not
            exist is worse than staying quiet.
    """
    host = host_of(url)
    common = {
        "url": url,
        "host": host,
        "status_code": signal.status_code,
        "reason": signal.reason,
        "retry_after": signal.retry_after,
        "vendor": signal.vendor,
        "cooldown": cooldown,
        "details": {"evidence": signal.evidence},
    }
    tail = f"Các lượt gọi tới {host} sẽ dừng tại chỗ trong {cooldown:.0f} giây tới."

    if signal.kind == "rate_limit":
        if signal.retry_after:
            wait_note = f"Máy chủ yêu cầu chờ {signal.retry_after:.0f} giây. "
        else:
            wait_note = "Máy chủ không cho biết thời gian chờ cụ thể. "
        return RateLimitedError(
            "Nguồn dữ liệu tạm thời từ chối vì số lượt gọi quá dày "
            f"(HTTP {signal.status_code}). {wait_note}"
            "Thư viện dừng ngay thay vì thử lại, vì thử lại lúc này chỉ làm kéo dài "
            f"thời gian bị chặn. {tail} "
            "Nên làm, theo thứ tự: (1) thêm khoảng nghỉ giữa các vòng lặp, "
            "ví dụ time.sleep(1); (2) nếu hàm hỗ trợ lấy nhiều mã trong một lần gọi, "
            "hãy gộp lại; (3) nếu đang chạy nhiều luồng song song, hạ số luồng xuống.",
            **common,
        )

    if signal.kind == "challenge":
        remedy = "đổi sang mạng khác (tắt VPN, phát mạng từ điện thoại)"
        if proxy_hint:
            remedy += f", hoặc {proxy_hint}"
        return ChallengeRequiredError(
            "Lớp bảo vệ của nguồn dữ liệu đang yêu cầu trình duyệt vượt qua bước "
            "kiểm tra tự động. Thư viện không tự vượt qua được bước này, và việc "
            "thử lại chỉ làm kéo dài thời gian bị chặn. Nguyên nhân thường gặp: "
            "(1) địa chỉ IP đang dùng bị đánh giá là rủi ro - hay gặp khi chạy trên "
            "máy chủ đám mây, VPN hoặc proxy miễn phí; (2) đã gọi quá nhiều lượt "
            f"trong thời gian ngắn từ cùng một địa chỉ. Nên làm: {remedy}, rồi thử "
            f"lại sau {cooldown:.0f} giây.",
            **common,
        )

    if signal.status_code == 451:
        return AccessDeniedError(
            "Nguồn dữ liệu từ chối phục vụ vì lý do pháp lý hoặc giới hạn vùng địa lý "
            "(HTTP 451). Cần truy cập từ một quốc gia khác, hoặc qua proxy đặt tại "
            f"vùng được phép. {tail}",
            **common,
        )

    return AccessDeniedError(
        "Nguồn dữ liệu đã từ chối yêu cầu ngay tại lớp bảo vệ "
        f"(HTTP {signal.status_code}). Đây không phải sự cố mạng tạm thời nên thư viện "
        "dừng ngay. Nên kiểm tra theo thứ tự: (1) địa chỉ IP hoặc vùng địa lý đang bị "
        "chặn - thử tắt VPN/proxy hoặc đổi mạng; (2) nếu đang chạy trên Google Colab "
        "hay máy chủ đám mây, dải địa chỉ của nhà cung cấp có thể nằm trong danh sách "
        "chặn sẵn của nguồn; (3) tần suất gọi trước đó quá dày khiến địa chỉ bị đưa vào "
        f"danh sách hạn chế. {tail}",
        **common,
    )
