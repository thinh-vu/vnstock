# Báo cáo tài chính

![](../assets/images/financial_report_tcbs.png)

Ba loại báo cáo này được truy xuất từ nguồn TCBS thông qua hàm `financial_flow`. Hàm này nhận 3 tham số:

- `symbol` là mã chứng khoán bạn muốn phân tích
- `report_type` nhận 1 trong 3 giá trị: `incomestatement` cho phép trả về báo cáo kết quả kinh doanh, `balancesheet` trả về báo cáo cân đối kế toán, `cashflow` trả về báo cáo lưu chuyển tiền tệ
- `report_range` nhận 1 trong 2 giá trị: `yearly` cho phép trả về báo cáo theo năm, `quarterly` trả về dữ liệu theo quý

Cụ thể từng báo cáo được minh họa chi tiết thành từng phần như dưới đây.

## Báo cáo kinh doanh

![](../assets/images/financial_income_statement.png)

Báo cáo kết quả kinh doanh có thể được truy xuất bằng câu lệnh:

```
income_df = financial_flow(symbol="TCB", report_type='incomestatement', report_range='quarterly')
```

Kết quả trả về như dưới đây. 

```
ticker  revenue  yearRevenueGrowth  quarterRevenueGrowth costOfGoodSold grossProfit  ...  investProfit  serviceProfit  otherProfit  provisionExpense operationIncome  ebitda
index                                                                                        ...
2021-Q4    TCB     7245              0.328                 0.074           None        None  ...           279           2103          532              -627            6767    None
2021-Q3    TCB     6742              0.310                 0.023           None        None  ...           384           1497          156              -589            6151    None
2021-Q2    TCB     6588              0.674                 0.076           None        None  ...           717           1457          444              -598            6615    None
2021-Q1    TCB     6124              0.454                 0.122           None        None  ...           812           1325          671              -851            6369    None
```

Để hiển thị báo cáo như cách trình bày trên website TCBS, bạn cần xoay (transpose) DataFrame trả về. Giả sử bạn lưu kết quả trả về vào biến `income_df` như trên, bạn có thể sử dụng phương thức `transpose` để xoay DataFrame như sau: `income_df.T`

Trong đó tên các cột được chuẩn hóa bằng tiếng Anh. Để đổi tên sang tiếng Việt, có thể sử dụng phương thức `rename` tiêu chuẩn của Pandas trong Python. Tôi đã chia sẻ một video cụ thể cách sử dụng Bard để trích xuất thông tin và ghép nối bản dịch tiếng Việt của các chỉ số. Các bạn có thể theo dõi để tự thực hiện nếu cần. Cách làm này áp dụng với tất cả các báo cáo tài chính được cung cấp ở đây.

<iframe width="800" height="452" src="https://www.youtube.com/embed/D3QekSAJU2s?si=r6shqYCewp1IRl31" title="YouTube video player" frameborder="0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share" allowfullscreen></iframe>

## Bảng cân đối kế toán

![](../assets/images/financial_balancesheet.png)

Để tải dữ liệu bảng cân đối kế toán, bạn sử dụng câu lệnh:

```
balance_df = financial_flow(symbol="TCB", report_type='balancesheet', report_range='quarterly')
```

Kết quả:

```
ticker shortAsset  cash shortInvest shortReceivable inventory longAsset  fixedAsset  ...  payableInterest  receivableInterest deposit otherDebt  fund  unDistributedIncome  minorShareHolderProfit  payable
index                                                                                        ...

2021-Q4    TCB       None  3579        None            None      None      None        7224  ...             3098                5808  314753     33680  9156                47469                     845   475756
2021-Q3    TCB       None  3303        None            None      None      None        7106  ...             3074                6224  316376     34003  6784                45261                     753   453251
2021-Q2    TCB       None  3554        None            None      None      None        6739  ...             2643                5736  289335     27678  6790                40924                     659   420403
2021-Q1    TCB       None  4273        None            None      None      None        4726  ...             2897                5664  287446     26035  6790                36213                     563   3837
```

Để hiển thị báo cáo như cách trình bày trên website TCBS, bạn cần xoay (transpose) DataFrame trả về. Giả sử bạn lưu kết quả trả về vào biến `balance_df` như trên, bạn có thể sử dụng phương thức `transpose` để xoay DataFrame như sau: `balance_df.T`

## Báo cáo lưu chuyển tiền tệ

Để tải dữ liệu báo cáo lưu chuyển tiền tệ, bạn sử dụng câu lệnh:

Để tải dữ liệu báo cáo lưu chuyển tiền tệ, bạn sử dụng câu lệnh:

```
cashflow_df = financial_flow(symbol="TCB", report_type='cashflow', report_range='quarterly')
```

Kết quả:

```
        ticker  investCost  fromInvest  fromFinancial  fromSale  freeCashFlow
index
2021-Q4    TCB        -280        -276              0     -9328             0
2021-Q3    TCB        -180        -179             60     17974             0
2021-Q2    TCB        -337        -282              0     11205             0
2021-Q1    TCB        -143        -143              0     -6954             0
```

Để hiển thị báo cáo như cách trình bày trên website TCBS, bạn cần xoay (transpose) DataFrame trả về. Giả sử bạn lưu kết quả trả về vào biến `cashflow_df` như trên, bạn có thể sử dụng phương thức `transpose` để xoay DataFrame như sau: `cashflow_df.T`