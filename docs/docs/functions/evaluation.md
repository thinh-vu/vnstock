# Chỉ số định giá 

!!! tip "Lưu ý"
    Để tiện theo dõi và tra cứu, trong một số trường hợp chúng tôi sẽ xoay DataFrame trả về từ hàm với với phép `transpose` để thấy đầy đủ thông tin dễ hơn. Với các câu lệnh có phần kết thúc với `.T` tức là đang áp dụng phép `transpose` này.

![](../assets/images/tcbs_stock_evaluation.png)

Chỉ số định giá được truy xuất từ nguồn TCBS thông qua hàm `stock_evaluation`. Hàm này nhận 3 tham số:

- `symbol` là mã chứng khoán bạn muốn phân tích

- `period` nhận 1 trong 2 giá trị: `1` cho phép trả về chỉ số theo ngày, `2` trả về dữ liệu theo tuần

- `time_window` nhận 1 trong 2 giá trị: `D` cho phép trả về chỉ số theo ngày, `W` trả về dữ liệu theo tuần

Minh họa cho hàm này như sau:

![](../assets/images/tcbs_stock_evaluation.png)

Chỉ số định giá được truy xuất từ nguồn TCBS thông qua hàm `stock_evaluation`. Hàm này nhận 3 tham số:
- `symbol` là mã chứng khoán bạn muốn phân tích

- `period` nhận 1 trong 2 giá trị: `1` cho phép trả về chỉ số theo ngày, `2` trả về dữ liệu theo tuần

- `time_window` nhận 1 trong 2 giá trị: `D` cho phép trả về chỉ số theo ngày, `W` trả về dữ liệu theo tuần

Minh họa cho hàm này như sau:

```
stock_evaluation (symbol='TCB', period=1, time_window='D')
```

- Kết quả:

```
>>> stock_evaluation (symbol='TCB', period=1, time_window='D')
    ticker   fromDate     toDate   PE   PB  industryPE  vnindexPE  industryPB  vnindexPB
0      TCB 2022-09-05 2022-09-05  6.4  1.2         9.8       14.0         1.7        2.0
1      TCB 2022-09-06 2022-09-06  6.4  1.2         9.9       14.0         1.7        2.0
2      TCB 2022-09-07 2022-09-07  6.2  1.2         9.6       13.7         1.7        2.0
3      TCB 2022-09-08 2022-09-08  6.2  1.2         9.4       13.5         1.6        1.9
4      TCB 2022-09-09 2022-09-09  6.2  1.2         9.5       13.7         1.6        2.0
..     ...        ...        ...  ...  ...         ...        ...         ...        ...
245    TCB 2023-08-25 2023-08-25  6.7  1.0         9.3       14.8         1.5        1.7
246    TCB 2023-08-28 2023-08-28  6.7  1.0         9.3       15.0         1.6        1.7
247    TCB 2023-08-29 2023-08-29  6.7  1.0         9.4       15.1         1.6        1.7
248    TCB 2023-08-30 2023-08-30  6.7  1.0         9.5       15.2         1.6        1.7
249    TCB 2023-08-31 2023-08-31  6.8  1.0         9.6       15.4         1.6        1.7

[250 rows x 9 columns]
```