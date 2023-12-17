---
title: Cài đặt
---

# Hướng dẫn nhanh

<div id="logo" align="center">
    <a href="http://vnstock.site?utm_source=vnstock_docs&utm_medium=start&utm_content=logo">
        <img src="https://raw.githubusercontent.com/thinh-vu/vnstock/beta/docs/docs/assets/images/vnstock_logo_color.png" alt="vnstock_logo"/>
    </a>
</div>

<div id="badges" align="center">
<img src="https://img.shields.io/pypi/pyversions/vnstock?logoColor=brown&style=plastic" alt= "Version"/>
<img src="https://img.shields.io/pypi/dm/vnstock" alt="Download Badge"/>
<img src="https://img.shields.io/github/last-commit/thinh-vu/vnstock" alt="Commit Badge"/>
<img src="https://img.shields.io/github/license/thinh-vu/vnstock?color=red" alt="License Badge"/>
</div>

---

## Giới thiệu chung
vnstock là thư viện Python được thiết kế để tải dữ liệu chứng khoán Việt Nam một cách dễ dàng và miễn phí. Gói thư viện được thiết kế dựa trên nguyên tắc về sự đơn giản và tiện lợi, hầu hết các hàm đều có thể chạy ngay trên Google Colab khi cài đặt vnstock mà không yêu cầu thêm gói phụ thuộc.

- vnstock có [40K+ lượt download](https://lookerstudio.google.com/reporting/06f4896d-21c5-4c4a-942e-126609c55fba) trên PyPI tính đến 5/11/2023. Lượt download trong tháng 10/2023 đạt mốc kỷ lục 5.266 kể từ lúc phát hành.

## Cài đặt nhanh

Để bắt đầu sử dụng vnstock, bạn sử dụng câu lệnh cài đặt đơn giản sau trên Google Colab hoặc Command Prompt/Terminal:

```shell
pip install --upgrade vnstock
```

Hoặc chỉ cần mở file Demo Notebook với Google Colab, chạy lần lượt các câu lệnh để trải nghiệm các tính năng của vnstock.

[Mở Notebook :material-rocket-launch:](https://colab.research.google.com/github/thinh-vu/vnstock/blob/beta/docs/gen2_vnstock_demo_index_all_functions_testing_2023.ipynb){ .md-button }

## Nguồn cấp dữ liệu

Thư viện **vnstock** cung cấp khả năng kết nối tới các API công khai của các nguồn cấp dữ liệu đáng tin cậy để người dùng có thể truy xuất dữ liệu chứng khoán Việt Nam và tương tác với các đối tượng Pandas DataFrame trong môi trường Python. Bạn cũng có thể xuất dữ liệu sang các định dạng phổ thông như csv, Excel, Google Sheets, Database để tiến hành phân tích nếu muốn. Việc truy xuất dữ liệu này là **TỰ DO** và hoàn toàn **MIỄN PHÍ**.

## Đánh dấu yêu thích

- Giúp **vnstock** đạt mục tiêu 1000 lượt yêu thích trên Github thông qua việc đánh dấu sao - **Star** tại trang dự án. Đây cũng là cách các bạn ủng hộ dự án và giúp lan tỏa vnstock đơn giản nhất giúp ích cho cộng đồng.
![](../assets/images/vnstock-watch-and-star.png)

## Sử dụng trang tài liệu tối ưu

Dưới đây là các gợi ý để bạn tra cứu trang tài liệu vnstock tối ưu:

- **Tìm kiếm**: Bạn có thể sử dụng thanh tìm kiếm trên trang tài liệu :octicons-search-16: để tìm kiếm tài liệu và các nội dung mình quan tâm

- **Chuyển đổi giao diện sáng/tối**: Để có trải nghiệm đọc trong điều kiện ánh sáng tốt nhất, bạn có thể chuyển đổi chế độ sáng/tối bằng cách nhấp vào biểu tượng :material-brightness-7: trên đầu trang.

- **Sử dụng bảng mục lục**: Thanh điều hướng bên trái :material-table-of-contents: cung cấp các đề mục để bạn có thể nhấp vào và di chuyển đến nội dung mình cần dễ dàng.

- **Copy Code**: Ở mỗi ô chứa dòng lệnh luôn có biểu tượng copy :material-content-copy: cho phép bạn click vào và sao chép đoạn mã dễ dàng.

## Docstring
Tất cả các hàm của vnstock đều được cung cấp docstring đầy đủ, do đó bạn có thể xem phần gợi ý khi viết câu lệnh trên các IDE như Google Colab, Visual Studio Code, hay Jupyter Notebook. 

Sau khi nạp thư viện vnstock vào môi trường làm việc thông qua câu lệnh `import`, bạn có thể in phần hướng dẫn sử dụng hàm vnstock bất kỳ thông qua thuộc tính `__doc__` của hàm đó như sau (dấu `__` được tạo bởi 2 dấu `_` tức shift `-`):

```shell
>>> print(listing_companies.__doc__)

This function returns the list of all available stock symbols from a csv file or a live api request.
    Parameters: 
        live (bool): If True, return the list of all available stock symbols from a live api request. If False, return the list of all available stock symbols from the Github csv file (monthly update). Default is False.
    Returns: df (DataFrame): A pandas dataframe containing the stock symbols and other information.
```

Tất nhiên, bạn luôn có thể mở phần mã nguồn của vnstock trên Github để xem chi tiết.

=== "Docstring trong Google Colab"

    Gợi ý cú pháp hàm được hiển thị khi viết bất kỳ hàm nào thuộc vnstock, trong ví dụ này hiển thị trong giao diện Google Colab.

    ![docstring suggestion](../assets/images/docstring_suggestion.jpeg)

=== "Docstring trong mã nguồn"

    Mở mã nguồn Github tại thư mục vnstock, tìm hàm bạn cần tra cứu docstring.

    ![docstring source](../assets/images/docstring_source_code.png)