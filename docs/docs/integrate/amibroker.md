# Amibroker

!!! abstract "Thử nghiệm thành công"
    08/11/2023, Hiện tại vnstock đã thử nghiệm thành công hàm xuất dữ liệu từ vnstock sang Amibroker cho phép lưu dữ liệu giá lịch sử từ hàm `stock_historical_data` với tất cả độ phân giải thời gian khả dụng sang Amibroker dưới dạng file CSV. Đây là một tin vui cho cộng đồng người dùng vnstock. Nếu bạn chưa sẳn sàng sử dụng bộ công cụ Python, vnstock dành cho bạn một số tính năng hữu ích trong thời gian chuyển đổi phương pháp làm việc mới linh hoạt và hiệu quả hơn. vnstock chào đón tất cả các bạn với mọi trình độ, kinh nghiệm khác nhau để xây dựng cộng đồng đầu tư chứng khoán Việt Nam ngày càng phát triển.

Để sử dụng tính năng xuất dữ liệu cho Amibroker, bạn thực hiện như sau:

## Xuất file CSV cho Amibroker

```python
amibroker_ohlc (path=r'C:\Users\mrthi\Desktop', symbol='TCB', start_date='2023-01-01', end_date='2023-11-08', resolution='1D', type='stock', source='DNSE')
```

Trong đó:

- `path`: là địa chỉ thư mục bạn muốn lưu file, tiện cho việc sử dụng Import Wizard trong Amibroker để nạp dữ liệu.
- Các tham số khác, vui lòng xem chi tiết hàm [stock_historical_data](https://docs.vnstock.site/functions/technical/#truy-xuat-du-lieu-gia-lich-su)

```shell
>>> amibroker_ohlc (path=r'C:\Users\mrthi\Desktop', symbol='TCB', start_date='2023-01-01', end_date='2023-11-08', resolution='1D', type='stock', source='DNSE')

Data preview:
   <Ticker> <DTYYYYMMDD>  <Open>  <High>  <Low>  <Close>  <Volume>
0      TCB     20230103   25.75   27.45  25.75    27.45   3786800
1      TCB     20230104   27.45   27.80  27.25    27.30   3185500
2      TCB     20230105   27.30   27.80  27.15    27.65   2716900
3      TCB     20230106   27.45   28.40  27.30    27.70   4803900
4      TCB     20230109   27.80   27.95  27.60    27.75   2387700
```

## Nạp dữ liệu cho Amibroker

!!! abstract "Sử dụng Import Wizard"
    Hiện tại, vnstock chỉ hỗ trợ xuất dữ liệu sang dạng CSV được định dạng để sẳn sàng nạp vào Amibroker. Quá trình này vẫn cần sử dụng bước dữ liệu thủ công dùng Import Wizard. Các bạn có thể viết thêm chương trình để thực hiện việc này hoàn toàn tự động thay cho data plugin nếu có thể. Tính năng này phù hợp với các bạn muốn tận dụng nguồn dữ liệu vnstock sẵn có để tiết kiệm cho việc nghiên cứu và phân tích đầu tư mà không cần đến dữ liệu real-time cho giao dịch thực tế (như phái sinh).

### Tạo database

Áp dụng nếu bạn chưa tạo sẵn cơ sở dữ liệu.

??? info "Khởi tạo Database. Click để mở rộng"
    Thực hiện mở Menu `File` > `New` > `Database` và thiết lập các thông số như hình (mặc định) hoặc thay đổi theo đúng kiểu dữ liệu bạn cần sử dụng (EOD hay theo phút cụ thể).

    ![](../assets/images/create_ami_database.png)

### Sử dụng Import Wizard

??? info "Import Wizard. Click để mở rộng"

    - Mở Import Wizard từ Menu

    ![](../assets/images/ami_open_import_wizard.png)

    - Chọn file cần Import

    ![](../assets/images/ami_pick_file_to_import_wizard.png)

    - Chọn `Next` tới màn hình tiếp theo. Tại đây tick vào 2 ô là `No quotation data` và `Allow negative price` sau đó `Next` cho đến bước `Finish` để kết thúc.

    ![](../assets/images/ami_config_import_wizard_setting.png)

Thử nghiệm thành công nạp dữ liệu EOD cho Amibroker từ vnstock.

![](../assets/images/EOD_ohlccdata_amibroker_TCB.png)

Thử nghiệm thành công nạp dữ liệu 1 phút cho Amibroker từ vnstock.

![](../assets/images/1_min_ohlccdata_amibroker_TCB.png)