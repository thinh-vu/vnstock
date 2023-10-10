---
title: Biểu diễn dữ liệu
sections:
    - Sử dụng tính năng vẽ biểu đồ
    - Gỡ lỗi thư viện phụ thuộc
---

### Sử dụng tính năng vẽ biểu đồ

Hiện tại, vnstock cung cấp tính năng vẽ biểu đồ trong mã nguồn nhánh beta trước khi phân phối chính thức qua PyPI, sau thời gian ngắn thử nghiệm và nhận phản hồi từ người dùng, mã nguồn nguồn sẽ được cập nhật vào nhánh ổn định. Để sử dụng tính năng này, bạn cần cài đặt vnstock từ nhánh beta.

vnstock sử dụng thư viện [plotly](https://plotly.com/python/candlestick-charts/) làm thư viện biểu diễn dữ liệu trực quan. Để có thể sử dụng được tính năng vẽ đồ thị, bạn cần đảm bảo plotly đã được cài đặt thành công.

Plotly là thư việc biểu diễn dữ liệu mạnh mẽ trong Python, cung cấp đa dạng các loại biểu đồ được hỗ trợ và tất cả đồ thị đều hỗ trợ tương tác trực quan (interactive). Hàm **candlestick_chart** dưới đây được xây dựng trên nền **Plotly graph object**, hỗ trợ đầy đủ tính năng của Plotly.

Do tính năng vẽ biểu đồ không phải ai cũng cần thiết dùng, do đó để tối ưu thời gian cài đặt thư viện vnstock và cài đặt gói phụ thuộc, **plotly** được tách khỏi tiến trình cài đặt tự động. Bạn cần sử dụng câu lệnh cài đặt plotly thủ công như sau: 

```shell
pip install plotly
```

Cú pháp câu lệnh vẽ biểu đồ đầy đủ như sau:

```python
from vnstock import * #import all functions

fig = candlestick_chart(symbol='TCB', start_date='2022-01-01', end_date='2023-10-10', resolution='1D', type='stock', 
                  title='Candlestick Chart with MA and Volume', x_label='Date', y_label='Price', ma_periods=[50,200], 
                  show_volume=True, figure_size=(12, 8), reference_period=300, up_color='#00F4B0', down_color='#FF3747')
fig.show()
```

<div class="vic_candlestick">
  <a href="assets/images/VIC_candlestick.png?raw=true" data-title="Minh họa đồ thị nến cho mã cổ phiếu VIC" data-toggle="lightbox"><img class="img-responsive" src="assets/images/VIC_candlestick.png?raw=true" alt="screenshot" /></a>
  <a class="mask" href="assets/images/VIC_candlestick.png?raw=true" data-title="Minh họa đồ thị nến cho mã cổ phiếu VIC" data-toggle="lightbox"><i class="icon fa fa-search-plus"></i></a>
</div>
Bạn có thể tùy chọn bỏ qua bước gán đồ thị với biến fig nếu chỉ muốn xem đồ thị trực tiếp trên Jupyter Notebook mà không thao tác tiếp theo như lưu file.
Để vẽ biểu đồ cho mã chỉ số (index) hoặc mã phái sinh (derivative), bạn cần thay đổi tham số **type** thành **index** hoặc **derivative**. 

```python
from vnstock import * #import all functions
fig = candlestick_chart(symbol='VNINDEX', start_date='2022-01-01', end_date='2023-10-10', resolution='1D', type='index', 
                  title='Candlestick Chart with MA and Volume', x_label='Date', y_label='Price', ma_periods=[50,200], 
                  show_volume=False, figure_size=(15, 8), reference_period=300, up_color='#00F4B0', down_color='#FF3747')
fig.show()
```

Bạn có thể điều chỉnh lại các thông số của hàm cho phù hợp, loại bỏ các thông số không cần thiết khi gọi hàm sẽ cho phép hàm sử dụng giá trị cài đặt mặc định, hoặc bạn điều chỉnh bằng cách cung cấp tham số mới vào.

Các tham số của hàm bao gồm:

- symbol: Mã cổ phiếu
- start_date: Ngày bắt đầu, sử dụng định dạng YYYY-mm-dd, ví dụ '2022-01-01'.
- end_date: Ngày kết thúc, sử dụng định dạng YYYY-mm-dd, ví dụ '2023-10-10'
- resolution: Khung thời gian lấy dữ liệu ví dụ '1D' cho dữ liệu ngày. Các giá trị khác là: 1, 15, 30, 60 . Tham khảo hàm lấy giá lịch sử để biết thêm chi tiết.
- type: Loại dữ liệu. Mặc định là cổ phiếu (stock). Có thể sử dụng để lấy dữ liệu phái sinh, mã chỉ số. Tham khảo hàm lấy giá lịch sử để biết thêm chi tiết.
- title: Tên của đồ thị.
- x_label: Nhãn trục x (hoành)
- y_label: Nhãn trục y (tung)
- ma_periods: Các dải MA cần tính toán, nhập vào dưới dạng một danh sách. Ví dụ [10, 50, 200] sẽ cho phép tính MA10, MA50, MA200. Bạn có thể nhập bao nhiêu dải MA tùy thích.
- show_volume: True để hiển thị thông tin khối lượng giao dịch, False để ẩn.
- figure_size: Kích thước đồ thị, nhập dưới dạng tupple (width, height).
- reference_period: Số ngày để tính toán đường tham chiếu đỉnh/đáy của giá Ví dụ 90.

<div class="vin_candlestick">
  <a href="assets/images/VNINDEX_candlestick.png?raw=true" data-title="Minh họa đồ thị nến cho mã chỉ số VNINDEX" data-toggle="lightbox"><img class="img-responsive" src="assets/images/VNINDEX_candlestick.png?raw=true" alt="screenshot" /></a>
  <a class="mask" href="assets/images/VNINDEX_candlestick.png?raw=true" data-title="Minh họa đồ thị nến cho mã chỉ số VNINDEX" data-toggle="lightbox"><i class="icon fa fa-search-plus"></i></a>
</div>

Để lưu đồ thị với câu lệnh, bạn cần cài đặt gói phụ thuộc **kaleido** sau đó thực hiện lưu file như dưới đây. Sau khi cài đặt thì cần phải khởi động lại runtime của Jupyter Notebook. Trên Google Colab chọn Menu **Runtime** -> **Restart runtime**. Sau đó bạn cần chạy lại các lệnh để vẽ đồ thị rồi mới có thể lưu. Việc này khá bất tiện, do đó nếu không có nhu cầu lưu file bằng câu lệnh, bạn có thể thực hiện từ giao diện đồ họa của đồ thị, chọn biểu tượng cái máy ảnh (thanh công cụ phía trên bên phải), click vào và chọn thư mục để lưu file.

```python
!pip install -U kaleido
```
Việc cài đặt chỉ cần thực hiện một lần, cuối cùng dùng câu lệnh sau để lưu file ảnh. Thay đổi đường dẫn thư mục và tên file theo ý bạn để lưu file ảnh vào thư mục mong muốn.

```python
fig.write_image("THƯ_MỤC_CỦA_BẠN/VNINDEX_candlestick.png")
```

### Gỡ lỗi thư viện phụ thuộc

Bạn có thể chạy lệnh cài đặt toàn bộ thư viện phụ thuộc từ file **requirements.txt**. Tải file [requirements.txt](https://github.com/thinh-vu/vnstock/blob/beta/requirements.txt) về máy của bạn. 
Hãy đảm bảo bạn đã **cd** đến đúng thư mục chứa file requirements.txt trước khi chạy lệnh.

```shell
pip install -r requirements.txt
```