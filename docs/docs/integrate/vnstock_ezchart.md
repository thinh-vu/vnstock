## Giới thiệu

<div id="logo" align="center">
    <a href="http://vnstock.site?utm_source=vnstock_docs&utm_medium=start&utm_content=logo">
        <img src="https://raw.githubusercontent.com/thinh-vu/vnstock/legacy/docs/docs/assets/images/vnstock_logo_color.png" alt="vnstock_logo"/>
    </a>
</div>

---

<div id="badges" align="center">
<img src="https://img.shields.io/pypi/pyversions/vnstock_ezchart?logoColor=brown&style=plastic" alt= "Version"/>
<img src="https://img.shields.io/pypi/dm/vnstock_ezchart" alt="Download Badge"/>
<img src="https://img.shields.io/github/last-commit/vnstock-hq/vnstock_ezchart" alt="Commit Badge"/>
<img src="https://img.shields.io/github/license/vnstock-hq/vnstock_ezchart?color=red" alt="License Badge"/>
</div>


!!! tip "Giới thiệu Vnstock ezchart"
     `vnstock_ezchart` ra đời với một sứ mệnh đơn giản nhưng đầy ý nghĩa: Làm cho việc phân tích dữ liệu trở nên dễ dàng và tiện lợi hơn bao giờ hết đặc biệt là lĩnh vực tài chính/chứng khoán. `vnstock_ezchart` được phát triển như một công cụ bổ trợ cho gói dữ liệu vnstock, nhằm mục đích cung cấp tới cộng đồng một giải pháp toàn diện để biểu diễn và phân tích dữ liệu tài chính một cách dễ dàng, mà không yêu cầu người dùng phải am hiểu sâu về lập trình. Dữ liệu đầu vào của các hàm trong `vnstock_ezchart` nhận kiểu dữ liệu Python phổ biến như List, DataFrame, Series, Numpy array. Vnstock ezchart sẽ được tích hợp trực tiếp vào tính năng cốt lõi của thư viện vnstock trong các phiên bản phát hành tới.

`vnstock_ezchart` giúp bạn đáp ứng 80% nhu cầu biểu diễn dữ liệu hàng ngày của mình chỉ bằng cách thay đổi các tham số đầu vào của hàm để tùy biến hay đơn giản chỉ cần nạp dữ liệu để xem trước, sau đó quyết định tinh chỉnh để tạo ra biểu đồ đẹp mắt và chia sẻ. 

`vnstock_ezchart` sử dụng kết hợp các thư viện bao gồm (nhưng không giới hạn): matplotlib, seaborn, squarify, wordcloud và cung cấp tùy biến thông dụng và tiêu chuẩn hóa chúng để bạn có thể sử dụng dễ dàng thay vì phải dành nhiều công sức nghiên cứu hay loay hoay viết prompt với AI.

Khi khởi động `vnstock_ezchart`, theme sẽ được áp dụng cho toàn bộ các đồ thị Matplotlib tạo ra sau đó trong cùng Notebook do đó, bạn vẫn có thể làm việc với Matplotlib nếu thích trong khi duy trì bộ nhận diện và màu sắc một cách nhất quán.

Khám phá vnstock_ezchart hôm nay, đánh dâu ⭐ cho [thư viện](https://github.com/vnstock-hq/vnstock_ezchart) trên Github và đừng quên lan tỏa tới cộng đồng của bạn.

## Cài đặt

Bạn chạy câu lệnh với pip trong Jupyter Notebook hoặc Terminal của mình để cài đặt Vnstock ezchart.

`pip install vnstock-ezchart`

## Sử dụng

Sử dụng demo notebook để khám phá nhanh các thao tác và kiểu đồ thị được hỗ trợ.

[Mở Notebook :material-rocket-launch:](https://colab.research.google.com/github/vnstock-hq/vnstock_ezchart/blob/main/docs/vnstock_ezchart_demo.ipynb){ .md-button }

- Khởi tạo client: 

```
ezchart = MPlot()
```

- Gọi hàm và biểu diễn dữ liệu: 

```
ezchart.combo_chart(candle_df['volume'] / 1000_000, candle_df['close']/1000,
                  left_ylabel='Volume (M)', right_ylabel='Price (K)',
                  color_palette='vnstock', palette_shuffle=True,
                  show_legend=False,
                  figsize=(10, 6),
                  title='Khối lượng giao dịch và giá đóng cửa theo thời gian',
                  title_fontsize=14
                  )
```

Và đây là thành quả đầu tay của bạn:

![Combo chart](https://github.com/vnstock-hq/vnstock_ezchart/blob/main/docs/assets/images/combo_chart.png?raw=true)

## Biểu đồ được hỗ trợ

| Tên Biểu Đồ      | Mô Tả                                                                                    |
|------------------|------------------------------------------------------------------------------------------|
| Bar              | So sánh giá trị giữa các nhóm qua thanh dọc/ngang.                                       |
| Line / Time series | Biểu diễn sự thay đổi dữ liệu theo thời gian, nhận diện xu hướng.                        |
| Combo (Bar + Line) | Kết hợp thanh và đường để so sánh nhiều loại dữ liệu hoặc biểu thị yếu tố tỷ lệ khác biệt. |
| Histogram       | Phân bố tần suất dữ liệu, nhận diện mô hình phân phối.                                    |
| Boxplot         | Phân bố dữ liệu qua 5 số liệu thống kê, đánh giá sự phân bố và giá trị ngoại lệ.          |
| Pie             | Biểu diễn tỷ lệ phần trăm của các phần trong tổng thể, so sánh sự chênh lệch.             |
| Scatter         | Mối quan hệ giữa hai biến qua điểm dữ liệu, nhận diện xu hướng và mẫu lệch tương quan.    |
| Treemap         | Cấu trúc phân cấp dữ liệu qua các khối vuông, so sánh và hiểu rõ cấu trúc.                |
| Word cloud      | Tần suất xuất hiện từ ngữ trong văn bản qua kích thước từ, mức độ phổ biến.               |
| Table           | Cái nhìn tổng quan và chi tiết về dữ liệu, dễ dàng so sánh và phân tích.                  |
| Pairplot        | Kiểm tra mối quan hệ và phân bố của từng cặp biến, nhiều biểu đồ phân tán và histogram.   |


## Tiện ích

### Xem hướng dẫn tích hợp: 
```
ezchart.help('bar)`
```

Kết quả trả về:

```
Vẽ biểu đồ cột với các tùy chỉnh chi tiết.

Tham số:
    - data (pd.DataFrame hoặc pd.Series): Dữ liệu đầu vào dạng DataFrame hoặc Series.
    - title (str): Tiêu đề của biểu đồ.
    - title_fontsize (int): Cỡ chữ cho tiêu đề.
    - xlabel (str): Nhãn cho trục X.
    - ylabel (str): Nhãn cho trục Y.
    - color_palette (str): Tên của bảng màu đã được định trước hoặc danh sách các màu tùy chỉnh. Mặc định là 'vnstock'. Các bảng màu có sẵn: 'percentage', 'amount', 'category', 'trend', 'flatui', 'vnstock', 'learn_anything'. Có thể liệt kê tất cả bảng màu với Utils.brand_palettes.keys().
    - palette_shuffle (bool): Xáo trộn thứ tự màu sắc trong bảng màu, cho phép chọn màu ngẫu nhiên trong bảng màu để biểu diễn cho đến khi bạn ưng ý. Mặc định là False.
    - grid (bool): Hiển thị lưới. Nhận True để hiện thị hoặc False để ẩn lưới.
    - data_labels (bool): Hiển thị nhãn dữ liệu trên biểu đồ.
    - data_label_format (str): Định dạng cho nhãn dữ liệu. Nhận các giá trị rút gọn như 1K, 1M, 1B, 1T tương ứng với 1 ngàn, 1 triệu, 1 tỷ, 1 nghìn tỷ.
    - label_fontsize (int): Cỡ chữ cho nhãn trục X và Y.
    - legend_title (str): Tiêu đề cho chú giải.
    - show_legend (bool): Hiển thị chú giải. Nhận True để hiển thị hoặc False để ẩn chú giải.
    - series_names (list): Danh sách tên cho các dải (series) dữ liệu trong biểu đồ. Nhận giá trị là 1 danh sách (list).
    - font_name (str): Tên của font chữ muốn áp dụng.
    - figsize (tuple): Kích thước của biểu đồ, ví dụ (10, 6).
    - show_xaxis (bool): Hiển thị trục X. Nhận True để hiển thị hoặc False để ẩn trục X.
    - show_yaxis (bool): Hiển thị trục Y. Nhận True để hiển thị hoặc False để ẩn trục Y.
    - tick_labelsize (int): Cỡ chữ cho các nhãn trục.
    - xtick_format (str): Định dạng cho nhãn trục X. Ví dụ định dạng số thập phân '{:.0f}'.
    - ytick_format (str): Định dạng cho nhãn trục Y. Ví dụ định dạng phần trăm '{:.0%}'.
    - tick_rotation (int): Góc quay cho các nhãn trục.
    - xlim (tuple): Giới hạn cho trục X, ví dụ (0, 100).
    - ylim (tuple): Giới hạn cho trục Y, ví dụ (0, 100).
    - background_color (str): Màu nền cho biểu đồ.
    - bar_edge_color (str): Màu viền cho các cột (bar) trong biểu đồ.
```

### Tùy chọn bảng màu
#### Áp dụng bảng màu cho Matplotlib

`Utils.apply_palette(color_palette='vnstock', palette_shuffle=False)`

Cho phép áp dụng bảng màu bạn chọn cho toàn môi trường làm việc (Jupyter Notbook/Google Colab). Bạn có thể tiếp tục sử dụng Matplotlib theo cách bạn thích với code bạn tạo ra nhưng giao diện sử dụng bảng màu được áp dụng. Bằng cách này bạn vừa có thể dễ dàng tạo ra giao diện đồ thị mình muốn trong khi thoải mái tùy biến biểu đồ.

#### Bảng màu tùy chỉnh

```
Utils.create_cmap('vnstock')
```

![color_map](https://github.com/vnstock-hq/vnstock_ezchart/blob/main/docs/assets/images/color_map.png?raw=true)

#### Liệt kê bảng màu mặc định

Cho phép bạn liệt kê tất cả bảng màu mặc định đi kèm Matplotlib, sử dụng khi áp dụng màu cho heatmap.

```
Utils.list_cmap ()
```

### Tùy chọn font chữ

#### Liệt kê font có sẵn

Để liệt kê các font có trong môi trường làm việc được nhận diện bởi Matplotlib, bạn sử dụng câu lệnh dưới đây. Tùy chọn này cho phép bạn sử dụng đúng font được hỗ trợ, hữu ích trong trường hợp bạn dùng Google Colab không có sẵn các font như trên máy tính của mình.
```
Utils.list_font()
```

#### Tải font chữ mới

Tải thêm font mới bằng câu lệnh dưới đây, cho phép tải mới font về thư mục làm việc từ Google Fonts. Bạn có thể sử dụng đường dẫn font để cài đặt hiển thị trong biểu đồ Word Cloud.
```
Utils.download_font('Roboto')
```

#### Áp dụng font chữ

Tùy chọn này hữu dụng trong trường hợp font bạn chọn không có trong hệ thống và bạn muốn sửa chữa sai lầm của mình bằng cách áp dụng font có trong danh sách font được liệt kê (có hỗ trợ tiếng Việt chẳng hạn).

```
set_font(font_family='DejaVu Sans')
```