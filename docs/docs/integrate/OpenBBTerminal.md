!!! abstract "Giới thiệu"
	[OpenBB Terminal](https://openbb.co/products/terminal) OpenBB Terminal là một công cụ mã nguồn mở mạnh mẽ dành cho các nhà đầu tư cá nhân, cung cấp cho bạn khả năng tiếp cận và phân tích dữ liệu tài chính toàn diện ngay từ giao diện dòng lệnh. Phần mềm này được viết bằng ngôn ngữ Python cho ứng dụng Desktop.

![Trang chủ OpenBB Terminal](../assets/images/Trang-chu-OpenBBTerminal.png) 

Hiện tại OpenBB Terminal cho phép sử dụng dữ liệu chuỗi thời gian (time series) do bạn tự cung cấp. Bạn có thể sử dụng dữ liệu giá OHLCV hoặc chỉ số thống kê để sử dụng tính năng [Forecast](https://docs.openbb.co/terminal/menus/forecast) hoặc [Econometrics](https://docs.openbb.co/terminal/menus/econometrics) của OpenBB. 

Bạn không thể thay đổi nguồn cấp dữ liệu ngoài danh sách chỉ định sẵn của OpenBB, do đó chưa có cách đẩy trực tiếp dữ liệu từ vnstock ngay bên trong OpenBB.

Để sử dụng tính năng Forecast và Econometrics như đã nêu ở trên, bạn lưu DataFrame tạo ra bởi vnstock với hàm `export_for_openbb()` để xuất file dưới dạng csv trong thư mục làm việc của OpenBB. Tham khảo thông tin từ OpenBB tại [BRING YOUR OWN DATA](https://my.openbb.co/app/terminal/features) mục IMPORT TIME SERIES DATA và Import data tại mục [CUSTOM DATA](https://docs.openbb.co/terminal/usage/data/custom-data)

Cú pháp hàm đơn giản như sau:

```python
export_for_openbb (df, file_name='REE_ohlcv_export')
```

Trong đó:

- `df` là DataFrame chứa dữ liệu bạn muốn xuất file
- `file_name` là tên file bạn muốn đặt, có thể theo tên mã cổ phiếu theo dõi như `REE_ohlcv_export`
- `extension` (tham số tùy chọn) mặc định là csv, không cần thay đổi, định dạng khác là xlsx

Sau khi chạy lệnh xong, file csv tương ứng sẽ được lưu trong thư mục của OpenBB. Bạn có thể đọc file trong giao diện OpenBB từ tính năng `forecast` với cú pháp `load -f REE_ohlcv_export.csv --alias REE` trong đó `REE_ohlcv_export.csv` là file dữ liệu demo còn `--alias REE` giúp đặt tên rút gọn cho file.
Chúc các bạn thành công!

![](../assets/images/tai-du-lieu-gia-vnstock-vao-openbb-terminal.png)