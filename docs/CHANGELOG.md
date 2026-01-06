## 06-01-2026

### 🔧 **Sửa lỗi**
- Khắc phục lỗi nhận diện sai ký hiệu dẫn xuất VN100 (ví dụ: `VN100F1M`) thành Covered Warrants do xung đột độ dài.
- Tinh chỉnh logic `auto_count_back` trong `Quote.history` để phản ánh chính xác giờ giao dịch thị trường Việt Nam (5 giờ/ngày, 255 phút/ngày).

### 🚀 **Thêm mới**
- Tính năng "Smart Lookback" cho `Quote.history` trong [`vnstock/explorer/vci/quote.py`](vnstock/explorer/vci/quote.py ) và [`vnstock/explorer/tcbs/quote.py`](vnstock/explorer/tcbs/quote.py ). Người dùng có thể sử dụng tham số `length` (ví dụ: `'3M'`, `'10W'`, `'100b'`, `150`) thay vì chỉ định ngày bắt đầu/kết thúc.
- Công cụ mới [`vnstock/core/utils/lookback.py`](vnstock/core/utils/lookback.py ) để phân tích khoảng thời gian linh hoạt và tính toán ngày bắt đầu.
- Tài liệu cho tính năng Smart Lookback tại `docs/feature_lookback.md`.
- Cải thiện cơ chế quản lý header trong [`vnstock/core/utils/user_agent.py`](vnstock/core/utils/user_agent.py ), hỗ trợ `Authorization`, `custom_headers` và `override_headers` cho cấu hình yêu cầu động và linh hoạt.
- Nâng cấp `ProxyManager` với `get_fresh_proxies`, hỗ trợ proxy tùy chỉnh và instance singleton.
- Cập nhật `client.py` để hỗ trợ chế độ proxy `AUTO` và tích hợp với `ProxyManager`.
- Tái cấu trúc `TCBS Quote` để sử dụng wrapper yêu cầu trung tâm `client.py`, cho phép hỗ trợ proxy.
- Tái cấu trúc tất cả module VCI (`Quote`, `Company`, `Financial`, `Listing`, `Trading`) để hỗ trợ cấu hình proxy qua tham số `__init__` (`proxy_mode`, `proxy_list`), giải quyết vấn đề chặn IP trên nền tảng đám mây như Google Colab/Kaggle.
- Tài liệu cho hệ thống header và xác thực mới tại `docs/header_management.md`.

### 🔄 **Thay đổi**
- `Quote.history`: Tham số `start` giờ là tùy chọn nếu `length` hoặc `count_back` được cung cấp.
- Cập nhật `get_asset_type` trong [`vnstock/core/utils/parser.py`](vnstock/core/utils/parser.py ) để nhận diện động tất cả chỉ số từ `vnstock.constants.INDICES_INFO`, đảm bảo hỗ trợ tốt hơn cho chỉ số ngành và đầu tư (ví dụ: `VNSI`, `VNFINLEAD`, `VNIND`).

## 11-11-2025

### 🚀 **Phiên bản v3.3.0**
- **Tương thích hệ thống thư viện Sponsor** sử dụng phương thức xác thực người dùng và quyền sử dụng thông qua Vnstock API key thay cho Github.
- **Tăng tốc sử dụng Vnstock trên Google Colab**: Cho phép lưu trữ thư viện & cấu hình vĩnh viễn trong Google Drive để khởi động nhanh thay vì cài đặt lại sau mỗi phiên làm việc.
- **Hỗ trợ proxy tự động**: Thêm khả năng sử dụng proxy miễn phí để tránh bị chặn IP, phù hợp cho nghiên cứu và sử dụng cá nhân
- **Hệ thống quản lý nguồn dữ liệu**: Tạo hệ thống thống nhất để quản lý tất cả nguồn dữ liệu (VCI, TCBS, FMP, XNO, DNSE)
- **Kết nối FMP & XNO**: Thêm nguồn dữ liệu thị trường quốc tế, cần lấy API key miễn phí từ FMP và XNO
- **Tái tổ chức mã nguồn**: Gộp các module trong core.utils, chuẩn hóa cách đặt tên và cấu trúc trong common
- **Hệ thống kiểm thử đầy đủ**: Thêm bộ test toàn diện cho các module VCI, TCBS, FMP với kiểm thử tích hợp
- **Chuyển sang pyproject.toml**: Thay thế setup.py bằng pyproject.toml, cập nhật các thư viện phụ thuộc
- **Cấu hình Context7**: Thiết lập hệ thống lập chỉ mục tài liệu cho AI
- **Cập nhật tài liệu**: Làm mới notebook hướng dẫn nhanh, hướng dẫn sử dụng

### 🔧 **Cải thiện kỹ thuật**
- Chuẩn hóa hằng số thị trường, chỉ số và định nghĩa kiểu dữ liệu
- Cải thiện xử lý lỗi và thông báo xác thực
- Tối ưu cấu hình proxy với chế độ dự phòng và xử lý lỗi
- Tái cấu trúc mã nguồn tiêu chuẩn với tài liệu mô tả bằng tiếng Anh

### 📚 **Tài liệu**
- Cập nhật notebook hướng dẫn nhanh cho FMP và XNO
- Thêm script demo và ví dụ [sử dụng proxy](https://github.com/thinh-vu/vnstock/blob/main/docs/PROXY_GUIDE.md) tại Github


## 27-05-2025

- Sửa lỗi nhắn tin qua Lark:
- Cho phép gửi file qua webhook dưới dạng mã hóa base64, cần giải mã khi nhận tin nhắn hoặc platform hỗ trợ parse dữ liệu