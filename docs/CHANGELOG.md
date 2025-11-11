## 11-11-2025

### 🚀 **Phiên bản v3.3.0**
- **Tương thích hệ thống thư viện Sponsor** sử dụng phương thức xác thực người dùng và quyền sử dụng thông qua Vnstock API key thay cho Github.
- **Hỗ trợ proxy tự động**: Thêm khả năng sử dụng proxy miễn phí để tránh bị chặn IP, phù hợp cho nghiên cứu và sử dụng cá nhân
- **Hệ thống quản lý nguồn dữ liệu**: Tạo hệ thống thống nhất để quản lý tất cả nguồn dữ liệu (VCI, TCBS, FMP, XNO, DNSE)
- **Kết nối FMP & XNO**: Thêm nguồn dữ liệu thị trường quốc tế, cần lấy API key miễn phí từ FMP và XNO
- **Tái tổ chức mã nguồn**: Gộp các module trong core.utils, chuẩn hóa cách đặt tên và cấu trúc trong common
- **Hệ thống kiểm thử đầy đủ**: Thêm bộ test toàn diện cho các module VCI, TCBS, FMP với kiểm thử tích hợp
- **Chuyển sang pyproject.toml**: Thay thế setup.py bằng pyproject.toml, cập nhật các thư viện phụ thuộc
- **Cấu hình Context7**: Thiết lập hệ thống lập chỉ mục tài liệu cho AI
- **Cập nhật tài liệu**: Làm mới notebook hướng dẫn nhanh, định dạng CHANGELOG và hướng dẫn sử dụng

### 🔧 **Cải thiện kỹ thuật**
- Chuẩn hóa hằng số thị trường, chỉ số và định nghĩa kiểu dữ liệu
- Cải thiện xử lý lỗi và thông báo xác thực
- Tối ưu cấu hình proxy với chế độ dự phòng và xử lý lỗi
- Tái cấu trúc mã nguồn để dễ đọc và bảo trì hơn

### 📚 **Tài liệu**
- Thêm PROXY_GUIDE.md với hướng dẫn chi tiết quản lý proxy
- Cập nhật notebook hướng dẫn nhanh cho FMP và XNO
- Đổi change_logs.md thành CHANGELOG.md với định dạng chuẩn
- Thêm script demo và ví dụ sử dụng proxy


## 27-05-2025

- Sửa lỗi nhắn tin qua Lark:
- Cho phép gửi file qua webhook dưới dạng mã hóa base64, cần giải mã khi nhận tin nhắn hoặc platform hỗ trợ parse dữ liệu