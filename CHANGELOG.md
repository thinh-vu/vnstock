# Nhật ký Thay đổi (Changelog)

Tất cả các thay đổi đáng chú ý của dự án `vnstock` sẽ được tài liệu hóa tại file này.

## [Unreleased] - Data-only package refactor

### Added
- **DNSE data provider** (`vnstock/explorer/dnse`): OHLCV history, intraday tick tape, and multi-symbol price board via the public Entrade API (`https://services.entrade.com.vn`). No authentication required. Register with `source="DNSE"` in `Quote`, `Trading`, and `Market.equity` calls. Prices are native VND (not divided by 1000 as with KBS raw values). Provider self-registers at import time via `ProviderRegistry.register("quote"/"trading", "dnse", ...)`.
- **Automatic provider load balancing** (`vnstock/core/router.py`, `vnstock/ui/_pools.py`): `BaseUI._dispatch()` now automatically rotates through available providers using round-robin with per-provider cooldown. When a provider returns a timeout, connection error, or HTTP 5xx/429, the system retries with the next provider in the pool transparently. Callers that pass `source=` explicitly bypass the router. `df.attrs["source_used"]` records the provider that served each request. Pool membership is declared in `vnstock/ui/_pools.py::POOLS`.
- **In-process / persistent cache layer** (`vnstock/core/cache.py`, `vnstock/core/settings.py::CacheConfig`): `BaseUI._dispatch()` now supports an optional response cache. Disabled by default; enable via `VNSTOCK_CACHE_ENABLED=true`. Backends: `memory` (LRU, in-process) and `sqlite` (persistent, WAL). Per-call overrides: `use_cache=False` bypasses the cache; `cache_ttl=<seconds>` sets per-request TTL. Deterministic SHA-256 cache keys; `df.attrs` metadata preserved through cache round-trips. Cache manager accessible via `vnstock.core.cache.get_cache_manager()`.
### Breaking Changes
- **Removed**: `Broker`, `show_api`, `show_doc`, `show_docs` removed from public exports.
- **Removed**: `vnstock.common.viz` charting and pandas `.viz` extension removed; install `vnstock_ezchart` directly in your app if needed.
- **Removed**: `vnstock.bot.notify.Messenger` and all Slack/Telegram/Discord/Lark helpers removed.
- **Removed**: DNSE broker connector (`vnstock.connector.dnse`) removed; login, account, and order execution are no longer available via this package.
- **Removed**: `vnstock_ezchart` removed as a package dependency.

All data extraction APIs (`Reference`, `Market`, `Fundamental`, `Retail`, legacy `Quote`/`Listing`/`Company`/`Finance`/`Trading`/`Fund`) and provider credentials (e.g. FMP `api_key`) are unaffected.

## [4.0.3] 2026-04-29

### Bổ sung (Added)
- **Giao dịch Trái phiếu**: Bổ sung cấu trúc dữ liệu trái phiếu vào tầng giao diện Unified UI và bổ sung các hàm ohlcv, trades, quote.
- **InstrumentType Enum**: Thêm phân loại định danh chứng khoán chuyên sâu để chuẩn hoá việc nhận diện các loại tài sản tài chính.

### Thay đổi & Cải thiện (Changed & Improved)
- Bổ sung danh sách các chỉ số index từ HNX, UPCOM và cải thiện khả năng nhận diện symbol qua hàm get_asset_type chính xác hơn với hỗ trợ các mã index mới.
- **Dữ liệu Báo cáo Tài chính**: Hỗ trợ hệ số nhân (`unit_multiplier`), ánh xạ nhất quán cấu trúc cột dữ liệu giữa các nguồn KBS và VCI.
- **Xử lý Nguồn dữ liệu (MSN & VCI)**: Xây dựng cơ chế resolve mã `SecId` động cho nguồn MSN để sửa lỗi truy xuất dữ liệu lịch sử; làm sạch các header Device-ID của VCI và thêm cơ chế fallback/sanitize URL an toàn khi tải danh sách mã.

## [2.5.0] - 2026-04-06

### Thay đổi (Changed)
- **Module KBS**:
  - Khôi phục hoàn toàn cấu trúc lõi (`trading.py`, `quote.py`, `financial.py`, `company.py`, `listing.py`) theo phạm vi dữ liệu hiện được duy trì trong module. Các tính năng như truyền số lượng kỳ (limit) để lùi sâu lịch sử báo cáo tài chính, lấy dữ liệu bảng giá phái sinh, giao dịch lô lẻ và khớp lệnh thỏa thuận đều đã được loại bỏ khỏi module này để tối ưu hiệu năng.
  - Làm sạch quy tắc mapping định danh tại `vnstock/explorer/kbs/const.py`, loại bỏ các dictionary không cần thiết (`_ODD_LOT_MAP`, `_DERIVATIVE_MAP`, `_PUT_THROUGH_MAP`).
  - Sửa lỗi định danh cột dữ liệu bảng giá: đổi `total_trades` thành `volume_accumulated` (tổng khối lượng) và bổ sung ánh xạ mã `CV` thành cột mới `volume_last` (khối lượng khớp lệnh lần cuối). Bản vá này đảm bảo API trả về 100% khớp với dữ liệu thực tế đang hiển thị trên giao diện của KBS (Ví dụ: "Tổng KL" -> `volume_accumulated`, "Khớp lệnh > KL" -> `volume_last`). Người dùng có sử dụng pandas parsing cần cập nhật lại key cho các bản báo cáo của mình.

### Bổ sung (Added)
- **Danh mục Sự kiện Thị trường (Market Events)**: Thêm tiện ích `vnstock/core/utils/market_events.py` phân phối dữ liệu dựa trên định dạng từ điển mở. Mô-đun này lưu trữ chính xác lịch sử các sự kiện lớn trên sàn chứng khoán (như Nghỉ lễ theo lịch nhà nước, Lỗi sập hệ thống, Khóa giao dịch toàn phần/bán phần) từ năm 2000. Đây là một định dạng đặc biệt linh hoạt, hướng dẫn cộng đồng mở rộng dữ liệu và có lợi ích to lớn cho các nhà nghiên cứu phân tích chuỗi thời gian (time-series).
