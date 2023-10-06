---
title: Xuất & chia sẻ dữ liệu
sections:
    - Xuất dữ liệu ra csv
    - Xuất dữ liệu ra Google Sheets
---

## Xuất dữ liệu ra csv

Dành cho những bạn mới làm quen Python và Pandas có thể sử dụng dữ liệu từ vnstock dễ dàng với công cụ bảng tính quen thuộc. Bạn có thể xuất dữ liệu từ hàm bất kỳ ra csv và mở bằng Excel hoặc upload lên Google Drive và mở bằng Google Sheets.

```python
start_date = '2023-06-01'
end_date = '2023-07-24'
# Truy xuất dữ liệu
df = stock_historical_data('TCB', start_date, end_date)
# Xuất dữ liệu ra csv, chèn ngày tháng và mã CP
df.to_csv(f'THƯ-MỤC-CỦA-BẠN/TCB_historical_price_{start_date}_{end_date}.csv', index=True)
```

## Xuất dữ liệu ra Google Sheets

Phương thức này được thiết kế riêng để xuất dữ liệu trực tiếp từ Google Colab sang Google Sheets (sẽ không hoạt động nếu chạy ở môi trường local, không thiết lập môi trường tương đồng Colab). Tham khảo cách làm chi tiết trong file demo, mục `III. Data Export`

