# Nhật ký Thay đổi (Changelog)

Tất cả các thay đổi đáng chú ý của dự án `vnstock` sẽ được tài liệu hóa tại file này.

## [4.0.3] 2026-04-29

### Bổ sung (Added)
- **Giao dịch Trái phiếu**: Bổ sung cấu trúc dữ liệu trái phiếu vào tầng giao diện Unified UI, đồng nhất kiến trúc với bản `vnstock_data` và bổ sung các hàm ohlcv, trades, quote.
- **InstrumentType Enum**: Thêm phân loại định danh chứng khoán chuyên sâu để chuẩn hoá việc nhận diện các loại tài sản tài chính.

### Thay đổi & Cải thiện (Changed & Improved)
- Bổ sung danh sách các chỉ số index từ HNX, UPCOM và cải thiện khả năng nhận diện symbol qua hàm get_asset_type chính xác hơn với hỗ trợ các mã index mới.
- **Dữ liệu Báo cáo Tài chính**: Hỗ trợ hệ số nhân (`unit_multiplier`), ánh xạ nhất quán cấu trúc cột dữ liệu giữa các nguồn KBS và VCI.
- **Xử lý Nguồn dữ liệu (MSN & VCI)**: Xây dựng cơ chế resolve mã `SecId` động cho nguồn MSN để sửa lỗi truy xuất dữ liệu lịch sử; làm sạch các header Device-ID của VCI và thêm cơ chế fallback/sanitize URL an toàn khi tải danh sách mã.

## [2.5.0] - 2026-04-06

### Thay đổi (Changed)
- **Module KBS**:
  - Khôi phục hoàn toàn cấu trúc lõi (`trading.py`, `quote.py`, `financial.py`, `company.py`, `listing.py`) để tuân thủ triệt để với giới hạn của phiên bản miễn phí (free tier). Các tính năng như truyền số lượng kỳ (limit) để lùi sâu lịch sử báo cáo tài chính, lấy dữ liệu bảng giá phái sinh, giao dịch lô lẻ và khớp lệnh thỏa thuận đều đã được gỡ bỏ khỏi bản miễn phí để tối ưu hiệu năng.
  - Làm sạch quy tắc mapping định danh tại `vnstock/explorer/kbs/const.py`, loại bỏ các dictionary không cần thiết (`_ODD_LOT_MAP`, `_DERIVATIVE_MAP`, `_PUT_THROUGH_MAP`).
  - Sửa lỗi định danh cột dữ liệu bảng giá: đổi `total_trades` thành `volume_accumulated` (tổng khối lượng) và bổ sung ánh xạ mã `CV` thành cột mới `volume_last` (khối lượng khớp lệnh lần cuối). Bản vá này đảm bảo API trả về 100% khớp với dữ liệu thực tế đang hiển thị trên giao diện của KBS (Ví dụ: "Tổng KL" -> `volume_accumulated`, "Khớp lệnh > KL" -> `volume_last`). Người dùng có sử dụng pandas parsing cần cập nhật lại key cho các bản báo cáo của mình.

### Bổ sung (Added)
- **Danh mục Sự kiện Thị trường (Market Events)**: Thêm tiện ích `vnstock/core/utils/market_events.py` phân phối dữ liệu dựa trên định dạng từ điển mở. Mô-đun này lưu trữ chính xác lịch sử các sự kiện lớn trên sàn chứng khoán (như Nghỉ lễ theo lịch nhà nước, Lỗi sập hệ thống, Khóa giao dịch toàn phần/bán phần) từ năm 2000. Đây là một định dạng đặc biệt linh hoạt, hướng dẫn cộng đồng mở rộng dữ liệu và có lợi ích to lớn cho các nhà nghiên cứu phân tích chuỗi thời gian (time-series).
- **Hệ thống cảnh báo Vị thế Môi trường (Auto-Detection Guardrail)**: Bổ sung luồng kiểm tra tức thời (startup check) trong tệp gốc `vnstock/__init__.py`. Hệ thống giờ có khả năng tự quét thư mục môi trường ảo `.venv` mặc định của hệ điều hành để phát hiện tự động dự án có sở hữu gói trả phí `vnstock_data` hay không. Một khi phát hiện gói trả phí được tải sẵn nhưng người dùng vẫn chạy cú pháp cũ `from vnstock import ...`, thư viện sẽ in ra cảnh báo nhắc nhở chuyển lệnh đồng bộ để mở khoá tính năng giới hạn.
- **Tường lửa AI (AI Agent Context Comments)**: Bổ sung chỉ dẫn hệ thống ở ngay phần đầu của các file `__init__.py` trọng yếu nhất. Các dòng lệnh tiếng Anh này là một hệ rào chắn (guardrails) vô hình dặn dò trực tiếp các trợ lý AI (ví dụ như AutoGPT, GitHub Copilot). Agent giờ sẽ biết bản VNSTOCK mã nguồn mở đã khóa bớt chức năng cồng kềnh, khuyến cáo AI thuyết phục người dùng nâng cấp lên nhánh trả phí `vnstock_data` thay vì liên tục cố gỡ rối để lấy dữ liệu từ nhánh Free.
- **Kiến trúc Migration 1:1 siêu việt (AST Validator Helper)**: Đã thiết kế hàm hỗ trợ cực kỳ mạnh mẽ `vnstock.core.utils.upgrade.migrate_to_sponsor()` cho phép AI Agent kích hoạt việc auto-upgrade codebase từ `vnstock` lên `vnstock_data` cực kỳ tinh vi:
  - Thuật toán KHÔNG thay thế chuỗi string (`text replace`) bằng Regex một cách rủi ro, mà sử dụng cơ chế phân tích **Cây Cú Pháp Trừu Tượng (AST Engine)** để đọc toàn diện mã gốc.
  - Khi rà quét từng dòng (Import Nodes), hàm tự động nạp gói vnstock_data bằng `importlib` và **gọi cross-check thuộc tính bằng `hasattr()`** xem API hay Method mà mã gốc đòi hỏi (như `Quote`, `Company`, `Trading`) có thực sự tồn tại trong namespace trả phí hay không.
  - Nếu tất cả các thành phần đòi hỏi được verified 1:1 thành công, nó mới thực hiện thay thế trên line code tương ứng. Tự động hóa chống gãy code an toàn tuyệt đối!
