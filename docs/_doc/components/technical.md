---
title: Phân tích kỹ thuật
sections:
  - Truy xuất dữ liệu giá lịch sử
---

### Truy xuất dữ liệu giá lịch sử

<div class="ohlc_dataset">
  <a href="assets/images/stock_ohlc_data.png?raw=true" data-title="Dữ liệu giá lịch sử được trích xuất từ DNSE EntradeX" data-toggle="lightbox"><img class="img-responsive" src="assets/images/stock_ohlc_data.png?raw=true" alt="screenshot" /></a>
  <a class="mask" href="assets/images/stock_ohlc_data.png?raw=true" data-title="Dữ liệu giá lịch sử được trích xuất từ DNSE EntradeX" data-toggle="lightbox"><i class="icon fa fa-search-plus"></i></a>
</div>


<div class="callout-block callout-success"><div class="icon-holder">*&nbsp;*{: .fa .fa-thumbs-up}	
</div><div class="content">
{: .callout-title}
Lưu ý:

Phiên bản API hiện tại cho phép truy cập giá lịch sử tối đa đến ngày 2012-03-20 đối với tất cả mã cổ phiếu. Nếu bạn có nhu cầu lấy lịch sử giá từ thời điểm thị trường chứng khoán bắt đầu hoạt động (REE là mã cổ phiếu có giao dịch sớm nhất thị trường vào 2000-07-31), hãy tham gia nhóm thành viên vnstock trên Facebook để được hỗ trợ.

</div></div>

vnstock cho phép người dùng tải xuống dữ liệu lịch sử giao dịch của **mã cổ phiếu, chỉ số, hợp đồng phái sinh**.
- Dữ liệu **cổ phiếu** và **chỉ số** hỗ trợ 5 mức độ chi tiết theo khoảng thời gian bao gồm: 1 phút, 15 phút, 30 phút, 1 giờ, 1 ngày. 
- Dữ liệu **phái sinh** hỗ trợ 8 mức độ chi tiết theo khoảng thời gian bao gồm: 1 phút, 3 phút, 5 phút, 15 phút, 30 phút, 45 phút, 1 giờ, 1 ngày
- Trường dữ liệu **time** sẽ là giá trị ngày tháng **YYYY-mm-dd** nếu **resolution** nhập vào là **1D**, trong khi **resolution** là cấp độ phút và giờ sẽ cho thêm thông tin thời gian giờ/phút.
- Đơn vị giá OHLC được làm tròn, chỉ lấy phần nguyên. Đơn vị tính là VND.

Trong ví dụ dưới đây, dữ liệu giá được truy xuất theo cấp độ ngày.

```python
df =  stock_historical_data(symbol='GMD', 
                            start_date="2021-01-01", 
                            end_date='2022-02-25', resolution='1D', type='stock')
print(df)
```

- Lưu ý: Đối với khung thời gian (resolution) nhỏ hơn 1 ngày (1D), API này (do DNSE cung cấp) chỉ cho phép truy ngược lại trong  khoảng thời gian 90 ngày. Bạn có thể gặp lỗi khi cố gắng lấy dữ liệu cũ hơn trong thời gian dài hơn.
- Giá trị mà tham số **resolution** có thể nhận là **1D** (mặc định, 1 ngày), '1' (1 phút), 3 (3 phút), 5 (5 phút), 15 (15 phút), 30 (30 phút), 45 (45 phút), '1H' (hàng giờ).
- **type = 'stock'** cho phép lấy dữ liệu giá của mã cổ cổ phiếu, **type = 'index'** cho phép lấy dữ liệu giá của mã chỉ số, và **type='derivative** cho phép lấy dữ liệu phái sinh. Các mã được hỗ trợ bao gồm (nhưng không giới hạn): VNINDEX, VN30, HNX, HNX30, UPCOM, VNXALLSHARE, VN30F1M, VN30F2M, VN30F1Q, VN30F2Q

Bạn cũng có thể viết hàm theo dạng rút gọn như dưới đây, điều này đúng với tất cả các hàm, miễn là thông số được nhập vào đúng thứ tự:

  - Lấy dữ liệu lịch sử cổ phiếu
  ```python
  df = stock_historical_data("GMD", "2021-01-01", "2022-02-25", "1D", 'stock')
  print(df)
  ```
Và đây là kết quả

- Kết quả

  ```
   time        open     high     low      close    volume
0  2021-01-04  32182.0  33157.0  31987.0  32279.0  4226500
1  2021-01-05  32279.0  33596.0  31938.0  32962.0  4851900
2  2021-01-06  33352.0  33352.0  32279.0  32572.0  3641300
  ```

- Lấy dữ liệu lịch sử của mã chỉ số
```python
df = stock_historical_data("VNINDEX", "2021-01-01", "2022-02-25", "1D", 'index')
print(df)
```

- Lấy dữ liệu lịch sử của hợp đồng phái sinh
```python
df = stock_historical_data("VN30F1M", "2023-07-01", "2023-07-24", "1D", 'derivative')
print(df)
```
