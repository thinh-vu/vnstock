# Biểu diễn dữ liệu

!!! tip "Lưu ý"
    vnstock sử dụng thư viện [plotly](https://plotly.com/python/candlestick-charts/) làm thư viện biểu diễn dữ liệu trực quan. Để có thể sử dụng được tính năng vẽ đồ thị, bạn cần đảm bảo plotly đã được cài đặt thành công.

Plotly là thư viện biểu diễn dữ liệu mạnh mẽ trong Python, cung cấp đa dạng các loại biểu đồ được hỗ trợ và tất cả đồ thị đều hỗ trợ tương tác trực quan (interactive). Hàm `candlestick_chart` dưới đây được xây dựng trên nền `Plotly graph object`, hỗ trợ đầy đủ tính năng của Plotly.

Tính năng vẽ biểu đồ không phải ai cũng cần thiết dùng, do đó để tối ưu thời gian cài đặt thư viện vnstock và cài đặt gói phụ thuộc, `plotly` được tách khỏi tiến trình cài đặt tự động. Bạn cần sử dụng câu lệnh cài đặt plotly thủ công như sau: 

```shell
pip install plotly
```

## Đồ thị nến

Cú pháp câu lệnh vẽ biểu đồ đầy đủ như sau:

```python
from vnstock import * #import all functions, including functions that provide OHLC data for charting
from vnstock.chart import * # import chart functions
df = stock_historical_data("VIC", "2022-01-01", "2023-10-10", "1D", "stock")
fig = candlestick_chart(df, ma_periods=[50,200], show_volume=False, reference_period=300, figure_size=(15, 8), 
                        title='VIC - Candlestick Chart with MA and Volume', x_label='Date', y_label='Price', 
                        colors=('lightgray', 'gray'), reference_colors=('black', 'blue'))
fig.show()
```
![candlestick](../assets/images/VIC_candlestick.png?raw=true)

Bạn có thể tùy chọn bỏ qua bước gán đồ thị với biến fig nếu chỉ muốn xem đồ thị trực tiếp trên Jupyter Notebook mà không thao tác tiếp theo như lưu file.
Để vẽ biểu đồ cho mã chỉ số (index) hoặc mã phái sinh (derivative), bạn cần thay đổi tham số `type` thành `index` hoặc `derivative`. 

```python
from vnstock import * #import all functions

df = stock_historical_data(symbol='VNINDEX', start_date='2022-01-01', end_date='2023-10-10', resolution='1D', type='index')
fig = candlestick_chart(df, 
                  title='VNINDEX Candlestick Chart with MA and Volume', x_label='Date', y_label='Price', ma_periods=[50,200], 
                  show_volume=True, figure_size=(15, 8), reference_period=300, 
                  colors=('lightgray', 'gray'), reference_colors=('black', 'blue'))
fig.show()
```

Bạn có thể điều chỉnh lại các thông số của hàm cho phù hợp, loại bỏ các thông số không cần thiết khi gọi hàm sẽ cho phép hàm sử dụng giá trị cài đặt mặc định, hoặc bạn điều chỉnh bằng cách cung cấp tham số mới vào. Ngoài ra bạn có thể tương tác trực tiếp với đồ thị, ví dụ click vào thông tin chú thích tương tứng từng loại dữ liệu để bật/tắt chúng mà không cần can thiệp vào dòng lệnh.

Các tham số của hàm bao gồm:

- `df`: DataFrame chứa dữ liệu giá định dạng OHLC
- `ma_periods`: Các dải MA cần tính toán, nhập vào dưới dạng một danh sách. Ví dụ [10, 50, 200] sẽ cho phép tính MA10, MA50, MA200. Bạn có thể nhập bao nhiêu dải MA tùy thích.
- `show_volume`: True để hiển thị thông tin khối lượng giao dịch, False để ẩn.
- `reference_period`: Số ngày để tính toán đường tham chiếu đỉnh/đáy của giá Ví dụ 90.
- `figure_size`: Kích thước đồ thị, nhập dưới dạng tupple ví dụ (15, 8) thể hiện 1500 x 800px.
- `title`: Tên của đồ thị.
- `x_label`: Nhãn trục x (hoành)
- `y_label`: Nhãn trục y (tung)
- `colors`: Mã màu thể hiện cho khối lượng giao dịch trong những ngày giá cổ phiếu tăng/giảm, được nhập dưới dạng tupple. Ví dụ ('#00F4B0', '#FF3747').
- `reference_color`: Cặp mã màu cho đường hỗ trợ (lowest low), kháng cự (highest high) được nhập vào dưới dạng tupple. Ví dụ ('black', 'blue')

![vnindex candlestick](../assets/images/VNINDEX_candlestick.png?raw=true)

## Đồ thị Bollinger Bands

Cú pháp câu lệnh vẽ biểu đồ đầy đủ như sau:

```python
from vnstock import * #import all functions
df = stock_historical_data(symbol='VNINDEX', start_date='2022-01-01', end_date='2023-10-10', resolution='1D', type='index')
bollinger_df = bollinger_bands(df, window=20, num_std_dev=2)
fig = bollinger_bands_chart(bollinger_df, use_candlestick=True, show_volume=True, 
                            fig_size=(15, 8), chart_title='Bollinger Bands Chart', xaxis_title='Date', yaxis_title='Price', 
                            bollinger_band_colors=('gray', 'orange', 'gray'), volume_colors=('#00F4B0', '#FF3747'))
fig.show()
```

Kết quả như sau:

![bollinger bands](../assets/images/bollinger_bands_chart.png?raw=true)

Trong đó, DataFrame `df` có thể không phải tính toán lại nếu đã khai báo trước đó trong dự án.

Hàm bollinger_bands cho phép tùy chỉnh các tham số tính toán giá trị để sử dụng trong biểu diễn dữ liệu, các tham số bao gồm:
- `df`: DataFrame chứa dữ liệu giá định dạng OHLC, sử dụng hàm stock_historical_data.
- `window`: Khung thời gian để tính toán giá trị trung bình động đơn giản (SMA), mặc định là 20 ngày.
- `num_std_dev`: Số kỳ tính độ lệch chuẩn. Mặc định là 2.

Hàm vẽ đồ thị Bollinger Bands bao gồm các tham số:

- `df`: DataFrame chứa dữ liệu Bollinger Bands: time, open, high, low, close, volume, ticker, upper_band, middle_band, lower_band. Dữ liệu này có được sau khi xử lý dữ liệu giá định dạng OHLC (hàm stock_historical_data) với hàm `bollinger_bands`.
- `use_candlestick`: Chọn sử dụng đồ thị nến (giá trị True) hay chỉ biểu diễn giá đóng cửa dạng đồ thị đường (giá trị False). Mặc định dùng đồ thị nến.
- `show_volume`: Chọn hiển thị thông tin khối lượng giao dịch (True) hoặc ẩn đi (False). Mặc định hiển thị.
- `fig_size`: Tupple chứa giá trị kích thước đồ thị (width, height). Ví dụ (15, 8) thể hiện 1500 x 800px.
- `chart_title`: Tên của đồ thị. Nếu không chỉ rõ, sẽ dùng tên mặc định
- `xaxis_title`: Tên của trục x (hoành)
- `yaxis_title`: Tên của trục y (tung)
- `bollinger_band_colors`: Tupple chứa bộ mã màu cho dải Bollinger Bands (upper, middle, lower).
- `volume_colors`: Tuple chứa mã màu cho thông tin khối lượng giao dịch trong những ngày giá tăng, giảm. Ví dụ ('green', 'red').

## Lưu đồ thị thành file ảnh

Để lưu đồ thị với câu lệnh, bạn cần cài đặt gói phụ thuộc `kaleido` sau đó thực hiện lưu file như dưới đây. Sau khi cài đặt thì cần phải khởi động lại runtime của Jupyter Notebook. Trên Google Colab chọn Menu `Runtime` -> `Restart runtime`. Sau đó bạn cần chạy lại các lệnh để vẽ đồ thị rồi mới có thể lưu. Việc này khá bất tiện, do đó nếu không có nhu cầu lưu file bằng câu lệnh, bạn có thể thực hiện từ giao diện đồ họa của đồ thị, chọn biểu tượng cái máy ảnh (thanh công cụ phía trên bên phải), click vào và chọn thư mục để lưu file.

```python
!pip install -U kaleido
```
Việc cài đặt chỉ cần thực hiện một lần, cuối cùng dùng câu lệnh sau để lưu file ảnh. Thay đổi đường dẫn thư mục và tên file theo ý bạn để lưu file ảnh vào thư mục mong muốn.

```python
fig.write_image("THƯ_MỤC_CỦA_BẠN/VNINDEX_candlestick.png")
```

## Gỡ lỗi thư viện phụ thuộc

Bạn có thể chạy lệnh cài đặt toàn bộ thư viện phụ thuộc từ file `requirements.txt`. Tải file [requirements.txt](https://github.com/thinh-vu/vnstock/blob/beta/requirements.txt) về máy của bạn. 
Hãy đảm bảo bạn đã `cd` đến đúng thư mục chứa file requirements.txt trước khi chạy lệnh.

```shell
cd THƯ_MỤC_CHỨA_FILE
```

```shell
pip install -r requirements.txt
```

## Xây dựng dashboard với Streamlit
Để tối ưu sức mạnh của vnstock và xây dựng những sản phẩm thực sự  trong phân tích đầu tư chứng khoán thì Streamlit là lựa chọn hàng đầu. 
[Streamlit](https://streamlit.io/) là một thư viện mã nguồn mở, cho phép bạn xây dựng các ứng dụng web trực quan với Python một cách nhanh chóng và dễ dàng. 
[Vnstock Web App](https://vnstock.site/web-app?utm_source=vnstock-docs&utm_medium=chart) chính là một ví dụ sinh động cho việc sử dụng dữ liệu từ chính vnstock để tạo ra ứng dụng với giao diện đồ họa trực quan và thân thiện. Web App này hoạt động hoàn toàn trên môi trường đám mây, không cần thiết lập bất cứ cơ sở dữ liệu nào, dữ liệu đầu vào của Web App chính là các APIs do vnstock cung cấp.

<iframe width="800" height="452" src="https://www.youtube.com/embed/0tVOnyCNagA?si=ATZ4ov3dxJetukaA" title="YouTube video player" frameborder="0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share" allowfullscreen></iframe>

Để có thể làm chủ Streamlit nhanh chóng với lộ trình đào tạo thực tế, ứng dụng cho chính thị trường chứng khoán Việt Nam và sử dụng vnstock. Bạn có thể trao đổi thêm với Thịnh về khóa học ngắn hạn sắp triển khai.

[![Thinh Vu - Nhắn tin](https://img.shields.io/badge/Thinh_Vu-Nhắn_tin-F74F8A?style=for-the-badge&logo=messenger&logoColor=F74F8A)](https://www.messenger.com/t/mr.thinh.ueh)