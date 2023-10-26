## Truy xuất dữ liệu giá lịch sử

![](../assets/images/stock_ohlc_data.png)

!!! info "Lưu ý"
    Phiên bản API hiện tại cho phép truy cập giá lịch sử tối đa đến ngày 2012-03-20 đối với tất cả mã cổ phiếu. Nếu bạn có nhu cầu lấy lịch sử giá từ thời điểm thị trường chứng khoán bắt đầu hoạt động (REE là mã cổ phiếu có giao dịch sớm nhất thị trường vào 2000-07-31), hãy tham gia nhóm thành viên vnstock trên Facebook để được hỗ trợ. Xem thêm chi tiết tại [FAQ](../faq/community.md).

vnstock cho phép người dùng tải xuống dữ liệu lịch sử giao dịch của `mã cổ phiếu, chỉ số, hợp đồng phái sinh`.

- Dữ liệu hỗ trợ 7 mức độ chi tiết theo khoảng thời gian bao gồm: 1 phút, 3 phút, 5 phút, 15 phút, 30 phút, 1 giờ, 1 ngày.

- Trường dữ liệu `time` sẽ là giá trị ngày tháng `YYYY-mm-dd` nếu `resolution` nhập vào là `1D`, trong khi `resolution` là cấp độ phút và giờ sẽ cho thêm thông tin thời gian giờ/phút.

- Đơn vị giá OHLC cho mã cổ phiếu được làm tròn theo mặc định, chỉ lấy phần nguyên. Đơn vị tính là VND. Bạn có thể tắt tính năng làm tròn bằng tham số `beautify=False`.

Trong ví dụ dưới đây, dữ liệu giá được truy xuất theo cấp độ ngày.

```python
df =  stock_historical_data(symbol='GMD', 
                            start_date="2021-01-01", 
                            end_date='2022-02-25', resolution='1D', type='stock', beautify=True)
print(df)
```

- Lưu ý: Đối với khung thời gian (resolution) nhỏ hơn 1 ngày (1D), API này (do DNSE cung cấp) chỉ cho phép truy ngược lại trong  khoảng thời gian 90 ngày. Bạn có thể gặp lỗi khi cố gắng lấy dữ liệu cũ hơn trong thời gian dài hơn.
- Giá trị mà tham số `resolution` có thể nhận là `1D` (mặc định, 1 ngày), '1' (1 phút), 3 (3 phút), 5 (5 phút), 15 (15 phút), 30 (30 phút), '1H' (hàng giờ).
- `type = 'stock'` cho phép lấy dữ liệu giá của mã cổ cổ phiếu, `type = 'index'` cho phép lấy dữ liệu giá của mã chỉ số, và `type='derivative` cho phép lấy dữ liệu phái sinh. Các mã được hỗ trợ bao gồm (nhưng không giới hạn): VNINDEX, VN30, HNX, HNX30, UPCOM, VNXALLSHARE, VN30F1M, VN30F2M, VN30F1Q, VN30F2Q
- `beautify=True` cho phép làm tròn giá trị OHLC theo mặc định (nhân với 1000, ví dụ giá 32.05 thành 32500). Đặt `beautify=False` để tắt chế độ làm tròn cho cổ phiếu. Với mã chỉ số, giá trị trả về luôn là số thập phân nguyên bản.

Bạn cũng có thể viết hàm theo dạng rút gọn như dưới đây, điều này đúng với tất cả các hàm, miễn là thông số được nhập vào đúng thứ tự:

  - Lấy dữ liệu lịch sử cổ phiếu
  ```python
  df = stock_historical_data("GMD", "2021-01-01", "2022-02-25", "1D", 'stock')
  print(df)
  ```

    Và đây là kết quả

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

### Dữ liệu khớp lệnh trong ngày giao dịch

- Minh hoạ giao diện TCBS

![](../assets/images/tcbs_intraday_screen1.png)
![](../assets/images/tcbs_intraday_screen2.png)

vnstock cho phép người dùng tải xuống dữ liệu khớp lệnh trong ngày giao dịch theo thời gian thực. Nếu mốc thời gian bạn truy cứu rơi vào Thứ Bảy, Chủ Nhật thì dữ liệu nhận được thể hiện cho ngày giao dịch của Thứ 6 của tuần đó.

```python
df =  stock_intraday_data(symbol='TCB', 
                            page_size=500)
print(df)
```

- Kết quả:

```shell
>>> stock_intraday_data('TCB', 500)

  ticker      time  orderType investorType  volume  averagePrice  orderCount
0    TCB  14:29:55  Sell Down        SHEEP    1000       32700.0           1
1    TCB  14:29:47     Buy Up        SHEEP     200       32750.0           1
2    TCB  14:29:44  Sell Down         WOLF    8000       32700.0          14
3    TCB  14:29:41  Sell Down        SHEEP    1000       32700.0           5
4    TCB  14:29:36  Sell Down         WOLF   23800       32700.0          10
```

!!! info "Giải thích ý nghĩa chỉ số"

    Khi 1 lệnh lớn (từ Cá mập, tay to, tổ chức....) mua chủ động (hoặc bán chủ động) được đưa vào Sàn, thường thì nó sẽ được khớp với nhiều lệnh nhỏ đang chờ bán (hoặc chờ mua). 
    Nếu chỉ nhìn realtime theo từng lệnh khớp riêng lẻ, thì sẽ không thể phát hiện được các lệnh to (của Cá mập, tay to...) vừa được đẩy vào Sàn. 
    Vì vậy, chúng tôi "cộng dồn" các lệnh khớp này lại (phát sinh bởi 1 lệnh lớn chủ động vào sàn trong 1 khoảng thời gian rất nhanh) để giúp NĐT phát hiện các lệnh lớn (của Cá mập, tay to....) chính xác hơn. Lệnh Cá mập sẽ được tô xanh (cho Mua chủ động) và đỏ (cho Bán chủ động). 

    • **Cá mập: (CM - SHARK)** nhà đầu tư tay to, tổ chức, đầu tư lớn, dẫn dắt thị trường. Giá trị 1 lệnh đặt > 1 tỷ đồng/lệnh đặt. Đồ thị 1N dùng số liệu 1 phút cho 60’ gần nhất; 1W là tổng mỗi 15’ cho 1 tuần; 1M là tổng hàng ngày cho 1 tháng

    • **Sói già: (SG - WOLF)** nhà đầu tư kinh nghiệm, giá trị lệnh đặt cao. Giá trị 1 lệnh đặt từ 200 tr đến 1 tỷ đồng/lệnh đặt.

    • **Cừu non: (CN - SHEEP)** nhà đầu tư nhỏ lẻ, giá trị giao dịch và mua bán chủ động thấp. Giá trị 1 lệnh đặt Mua hoặc Bán chủ động < 200 triệu đồng/lệnh đặt vào.

    • **Mua chủ động (hay Buy Up)** là khi NĐT thực hiện chủ động mua lên qua việc đặt lệnh mua với giá bằng giá dư bán gần nhất để có thể khớp luôn. Như thế, giá khớp cho lệnh này thường sẽ đẩy giá khớp lên cao hơn thị giá trước đó.

    • **Bán chủ động (hay Sell Down)** là khi NĐT thực hiện chủ động Bán dưới giá hiện tại (hay thị giá) của cổ phiếu bằng việc đặt lệnh bán với giá bán bằng giá dư mua gần nhất để khớp ngay. Và như thế, thị giá sẽ bị kéo xuống thấp hơn so với thị giá trước đó. Thống kê khối lượng giao dich theo Mua CĐ và Bán CĐ dùng để đánh giá tương quan giữa cung (Bán CĐ) và cầu (Mua CĐ) trên giao dịch khớp lệnh thực tế, nhằm nhận định tương đối về sự vận động của xu hướng dòng tiền. Khi tỷ lệ % Mua CĐ trên (Tổng Mua và Bán CĐ) lớn hơn 50%, đồng nghĩa với việc thị trường đang có xu hướng mua vào nhiều hơn bán ra và ngược lại, qua đó xác định được dòng tiền vào/ra với mỗi cổ phiếu. Khi tỷ lệ này cao đột biến (>70% hay <30%) so với điểm cân bằng (50%) , đó là tín hiệu của việc mua hoặc bán bất chấp của thị trường.