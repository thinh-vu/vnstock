# Thông tin quỹ mở

!!! abstract "Giới thiệu"
    Thông tin các quỹ mở được cung cấp thông qua vnstock được truy xuất từ Public API của [fmarket.vn](https://fmarket.vn/). Hiện tại, vnstock cung cấp cách thức truy xuất các nhóm thông tin quỹ mở quan trọng được mô tả chi tiết dưới dây.

    vnstock xin gửi lời cám ơn chân thành tới bạn [andrey_jef](https://github.com/andrey-jef) đã đề xuất và đóng góp mã nguồn khởi xướng cho nhóm tính năng này qua Github.


Tính năng tra cứu thông tin quỹ mở hiện đã được cập nhật qua nhánh beta của vnstock trên Github. Bạn có thể cài đặt bản beta theo hướng dẫn tại đây:

[Cài đặt bản beta :material-rocket-launch:](https://docs.vnstock.site/start/installation/#xac-inh-phien-ban-phu-hop){ .md-button }

## Liệt kê danh sách quỹ

Để truy xuất thông tin toàn bộ các quỹ mở, bạn sử dụng hàm dưới đây:

```python
funds_listing(lang='vi', fund_type="")
```

Trong đó:

- `lang`: ngôn ngữ hiển thị thông tin quỹ. Hiện tại, vnstock hỗ trợ hai ngôn ngữ là `vi` (Tiếng Việt) và `en` (Tiếng Anh). Mặc định là `vi`.
- `fund_type`: loại quỹ, chấp nhận các giá trị sau: `STOCK` cho quỹ cổ phiếu, `BOND` cho quỹ trái phiếu, `BALANCED` cho quỹ cân bằng. Nếu để trống, kết quả trả về là tất cả các quỹ hiện có.

Thông tin trả về có là một DataFrame với các thông tin tóm tắt như sau:

```shell
>>> funds_listing(lang='vi', fund_type="").head()
Total number of funds currently listed on Fmarket:  41
  fundId Tên viết tắt                                            Tên CCQ  ... Giá gần nhất     code     vsdFeeId
0     23        VESAF  QUỸ ĐẦU TƯ CỔ PHIẾU TIẾP CẬN THỊ TRƯỜNG VINACA...  ...     25620.68    VESAF    VESAFN002
1     20         VEOF         QUỸ ĐẦU TƯ CỔ PHIẾU HƯNG THỊNH VINACAPITAL  ...     24748.62     VEOF     VEOFN003
2     11       SSISCA         QUỸ ĐẦU TƯ LỢI THẾ CẠNH TRANH BỀN VỮNG SSI  ...     29880.06   SSISCA   SSISCAN001
3     32     VCBF-BCF                  QUỸ ĐẦU TƯ CỔ PHIẾU HÀNG ĐẦU VCBF  ...     27526.16  VCBFBCF  VCBFBCFN001
4     22         VIBF           QUỸ ĐẦU TƯ CÂN BẰNG TUỆ SÁNG VINACAPITAL  ...     14983.38     VIBF     VIBFN003

[5 rows x 11 columns]
```

## Truy xuất thông tin quỹ

Bạn có thể truy xuất các thông tin cơ bản của một quỹ qua hàm `fund_details` như dưới dây:

### Danh mục các mã quỹ nắm giữ

```python
fund_details (symbol='SSISCA', type='top_holding_list')
```

Dữ liệu trả về có dạng như sau:

```shell
>>> fund_details (symbol='SSISCA', type='top_holding_list')
Getting data for SSISCA
   Tên                   Ngành  % Giá trị tài sản Loại tài sản Cập nhật lần cuối fundId  symbol
0  FPT  Công nghệ và thông tin              19.48        STOCK        2023-12-08     11  SSISCA
1  MWG                  Bán lẻ               8.73        STOCK        2023-12-08     11  SSISCA
2  ACB               Ngân hàng               4.80        STOCK        2023-12-08     11  SSISCA
3  HPG       Vật liệu xây dựng               4.53        STOCK        2023-12-08     11  SSISCA
4  MBB               Ngân hàng               4.29        STOCK        2023-12-08     11  SSISCA
5  CTG               Ngân hàng               3.88        STOCK        2023-12-08     11  SSISCA
6  VRE            Bất động sản               3.44        STOCK        2023-12-08     11  SSISCA
7  DRC         Sản phẩm cao su               3.43        STOCK        2023-12-08     11  SSISCA
8  TV2  Dịch vụ tư vấn, hỗ trợ               3.42        STOCK        2023-12-08     11  SSISCA
9  TCB               Ngân hàng               3.31        STOCK        2023-12-08     11  SSISCA
```

### Tỉ trọng các ngành mà quỹ đang đầu tư

```python
fund_details (symbol='VESAF', type='industry_holding_list')
```

Dữ liệu trả về có dạng như sau:
    
```shell
>>> fund_details (symbol='VESAF', type='industry_holding_list')
Getting data for VESAF
                       Ngành  % Giá trị tài sản symbol
0     Công nghệ và thông tin              15.12  VESAF
1                  Ngân hàng              11.52  VESAF
2               Bất động sản              10.77  VESAF
3           Sản xuất Phụ trợ              10.03  VESAF
4          Vận tải - Kho bãi               8.22  VESAF
5                Khai khoáng               5.44  VESAF
6        Thực phẩm - Đồ uống               5.28  VESAF
7          Chế biến thủy sản               4.80  VESAF
8   Sản xuất Nhựa - Hóa chất               3.48  VESAF
9                   Xây dựng               2.91  VESAF
10                    Bán lẻ               2.77  VESAF
11               Chứng khoán               2.54  VESAF
12                  Tiện ích               2.31  VESAF
13                  Bảo hiểm               1.41  VESAF
```

### Báo cáo NAV quỹ

```python
fund_details (symbol='VESAF', type='nav_report')
```

Dữ liệu trả về là DataFrame có dạng như sau:

```
>>> fund_details (symbol='VESAF', type='nav_report')
Getting data for VESAF
           Ngày  Giá trị tài sản ròng/CCQ (VND)  fundId symbol
0    2017-04-25                        10000.00      23  VESAF
1    2017-04-29                        10058.00      23  VESAF
2    2017-05-09                        10093.00      23  VESAF
3    2017-05-16                        10165.00      23  VESAF
4    2017-05-23                        10254.00      23  VESAF
..          ...                             ...     ...    ...
816  2023-12-04                        25300.86      23  VESAF
817  2023-12-05                        25707.10      23  VESAF
818  2023-12-06                        25713.20      23  VESAF
819  2023-12-07                        25825.37      23  VESAF
820  2023-12-08                        25620.68      23  VESAF

[821 rows x 4 columns]
```

### Tỉ trọng tài sản nắm giữ

```python
fund_details (symbol='VESAF', type='asset_holding_list')
```

Dữ liệu trả về là DataFrame như sau:

```shell
>>> fund_details (symbol='VESAF', type='asset_holding_list')
Getting data for VESAF
   Tỉ trọng    updateAt              Loại tài sản symbol
0     86.61  2023-12-08                  Cổ phiếu  VESAF
1     13.39  2023-12-08  Tiền và tương đương tiền  VESAF
```