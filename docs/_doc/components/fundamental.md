---
title: Phân tích tài chính
sections:
  - Bộ chỉ số tài chính
  - Báo cáo KQKD, CĐKT và LCTT
  - Chỉ số định giá
---

## Bộ chỉ số tài chính

<div class="balance_sheet">
  <a href="assets/images/financial_ratio.png?raw=true" data-title="Bộ chỉ số tài chính do TCBS cung cấp" data-toggle="lightbox"><img class="img-responsive" src="assets/images/financial_ratio.png?raw=true" alt="screenshot" /></a>
  <a class="mask" href="assets/images/financial_ratio.png?raw=true" data-title="Bộ chỉ số tài chính do TCBS cung cấp" data-toggle="lightbox"><i class="icon fa fa-search-plus"></i></a>
</div>

Bộ chỉ số tài chính do TCBS cung cấp có thể được trích một cách dễ dàng để có toàn bộ thông tin phân tích như bạn thấy trên giao diện website TCBS bằng câu lệnh:

```python
financial_ratio(symbol="TCB", report_range='yearly', is_all=False)
```
Trong đó:
- **symbol** là mã chứng khoán bạn muốn phân tích
- **report_range** nhận 1 trong 2 giá trị: **yearly** cho phép trả về chỉ số theo năm, **quarterly** trả về dữ liệu theo quý
- **is_all** có giá trị mặc định là **True** cho phép lấy chỉ số qua tất cả các kỳ (năm hoặc quý), **False** cho phép lấy các kỳ gần nhất (5 năm hoặc 10 quý gần đây). Đây là tham số tùy chọn, nếu bạn không chỉ rõ, nó sẽ nhận giá trị mặc định là **False** tức rút gọn báo cáo để lấy 5 năm hoặc 10 quý gần nhất.

- Kết quả:

```shell
>>> financial_ratio('TCB', 'yearly')
year                      2022   2021   2020   2019   2018
ticker                     TCB    TCB    TCB    TCB    TCB
priceToEarning             4.5    9.7    9.0    8.2   10.7
priceToBook                0.8    1.9    1.5    1.3    1.8
roe                      0.197  0.217  0.181  0.178  0.215
roa                      0.032  0.036   0.03  0.029  0.029
earningPerShare           5729   5132   3504   2869   2410
bookValuePerShare        32248  26452  21214  17679  14749
interestMargin           0.053  0.057  0.049  0.043  0.041
nonInterestOnToi         0.259   0.28  0.307  0.323  0.379
badDebtPercentage        0.007  0.007  0.005  0.013  0.018
provisionOnBadDebt       1.573  1.629   1.71  0.948  0.851
costOfFinancing          0.028  0.022  0.031  0.038  0.041
equityOnTotalAsset       0.162  0.164   0.17  0.162  0.161
equityOnLoan              0.27  0.268  0.269  0.269  0.324
costToIncome             0.328  0.301  0.319  0.347  0.318
equityOnLiability          0.2    0.2    0.2    0.2    0.2
epsChange                0.116  0.465  0.221  0.191  0.313
assetOnEquity              6.2    6.1    5.9    6.2    6.2
preProvisionOnToi        0.537  0.554  0.542   0.52  0.542
postTaxOnToi               0.5  0.497  0.465  0.485  0.462
loanOnEarnAsset          0.684  0.665  0.681  0.649  0.537
loanOnAsset              0.602  0.611  0.631  0.602  0.498
loanOnDeposit            1.173  1.104    1.0  0.998  0.794
depositOnEarnAsset       0.583  0.603   0.68  0.651  0.676
badDebtOnAsset           0.004  0.004  0.003  0.008  0.009
liquidityOnLiability     0.347  0.382  0.372  0.411  0.531
payableOnEquity            5.2    5.1    4.9    5.2    5.2
cancelDebt               0.002  0.004  0.013  0.002  0.008
bookValuePerShareChange  0.219  0.247    0.2  0.199  0.923
creditGrowth             0.211  0.252  0.202  0.443 -0.006
  ```

## Báo cáo kết quả kinh doanh, cân đối kế toán và lưu chuyển tiền tệ

<div class="financial_report">
  <a href="assets/images/financial_report_tcbs.png?raw=true" data-title="Báo cáo tài chính do TCBS cung cấp" data-toggle="lightbox"><img class="img-responsive" src="assets/images/financial_report_tcbs.png?raw=true" alt="screenshot" /></a>
  <a class="mask" href="assets/images/financial_report_tcbs.png?raw=true" data-title="Báo cáo tài chính do TCBS cung cấp" data-toggle="lightbox"><i class="icon fa fa-search-plus"></i></a>
</div>

Ba loại báo cáo này được truy xuất từ nguồn TCBS thông qua hàm **financial_flow**. Hàm này nhận 3 tham số:
- **symbol** là mã chứng khoán bạn muốn phân tích
- **report_type** nhận 1 trong 3 giá trị: **incomestatement** cho phép trả về báo cáo kết quả kinh doanh, **balancesheet** trả về báo cáo cân đối kế toán, **cashflow** trả về báo cáo lưu chuyển tiền tệ
- **report_range** nhận 1 trong 2 giá trị: **yearly** cho phép trả về báo cáo theo năm, **quarterly** trả về dữ liệu theo quý

Cụ thể từng báo cáo được minh họa chi tiết thành từng phần như dưới đây.

### Báo cáo kinh doanh

<div class="balance_sheet">
  <a href="assets/images/financial_income_statement.png?raw=true" data-title="Dữ liệu báo cáo doanh thu tại TCBS" data-toggle="lightbox"><img class="img-responsive" src="assets/images/financial_income_statement.png?raw=true" alt="screenshot" /></a>
  <a class="mask" href="assets/images/financial_income_statement.png?raw=true" data-title="Dữ liệu báo cáo doanh thu tại TCBS" data-toggle="lightbox"><i class="icon fa fa-search-plus"></i></a>
</div>

Báo cáo kết quả kinh doanh có thể được truy xuất bằng câu lệnh:

```python
income_df = financial_flow(symbol="TCB", report_type='incomestatement', report_range='quarterly')
```

- Kết quả trả về như dưới đây. 

```shell
ticker  revenue  yearRevenueGrowth  quarterRevenueGrowth costOfGoodSold grossProfit  ...  investProfit  serviceProfit  otherProfit  provisionExpense operationIncome  ebitda
index                                                                                        ...
2021-Q4    TCB     7245              0.328                 0.074           None        None  ...           279           2103          532              -627            6767    None
2021-Q3    TCB     6742              0.310                 0.023           None        None  ...           384           1497          156              -589            6151    None
2021-Q2    TCB     6588              0.674                 0.076           None        None  ...           717           1457          444              -598            6615    None
2021-Q1    TCB     6124              0.454                 0.122           None        None  ...           812           1325          671              -851            6369    None
```

Để hiển thị báo cáo như cách trình bày trên website TCBS, bạn cần xoay (transpose) DataFrame trả về. Giả sử bạn lưu kết quả trả về vào biến **income_df** như trên, bạn có thể sử dụng phương thức **transpose** để xoay DataFrame như sau: `income_df.T`

Trong đó tên các cột được chuẩn hóa bằng tiếng Anh. Để đổi tên sang tiếng Việt, có thể sử dụng phương thức **rename** tiêu chuẩn của Pandas trong Python. Tôi đã chia sẻ một video cụ thể cách sử dụng Bard để trích xuất thông tin và ghép nối bản dịch tiếng Việt của các chỉ số. Các bạn có thể theo dõi để tự thực hiện nếu cần. Cách làm này áp dụng với tất cả các báo cáo tài chính được cung cấp ở đây.

<iframe width="1068" height="600" src="https://www.youtube.com/embed/D3QekSAJU2s?si=r6shqYCewp1IRl31" title="YouTube video player" frameborder="0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share" allowfullscreen></iframe>

### Bảng cân đối kế toán

<div class="balance_sheet">
  <a href="assets/images/financial_balancesheet.png?raw=true" data-title="Dữ liệu bảng cân đối kế toán tại TCBS" data-toggle="lightbox"><img class="img-responsive" src="assets/images/financial_balancesheet.png?raw=true" alt="screenshot" /></a>
  <a class="mask" href="assets/images/financial_balancesheet.png?raw=true" data-title="Dữ liệu bảng cân đối kế toán tại TCBS" data-toggle="lightbox"><i class="icon fa fa-search-plus"></i></a>
</div>

Để tải dữ liệu bảng cân đối kế toán, bạn sử dụng câu lệnh:

```python
balance_df = financial_flow(symbol="TCB", report_type='balancesheet', report_range='quarterly')
```

- Kết quả:

```shell
        ticker shortAsset  cash shortInvest shortReceivable inventory longAsset  fixedAsset  ...  payableInterest  receivableInterest deposit otherDebt  fund  unDistributedIncome  minorShareHolderProfit  payable
index                                                                                        ...

2021-Q4    TCB       None  3579        None            None      None      None        7224  ...             3098                5808  314753     33680  9156                47469                     845   475756
2021-Q3    TCB       None  3303        None            None      None      None        7106  ...             3074                6224  316376     34003  6784                45261                     753   453251
2021-Q2    TCB       None  3554        None            None      None      None        6739  ...             2643                5736  289335     27678  6790                40924                     659   420403
2021-Q1    TCB       None  4273        None            None      None      None        4726  ...             2897                5664  287446     26035  6790                36213                     563   3837
```

Để hiển thị báo cáo như cách trình bày trên website TCBS, bạn cần xoay (transpose) DataFrame trả về. Giả sử bạn lưu kết quả trả về vào biến **balance_df** như trên, bạn có thể sử dụng phương thức **transpose** để xoay DataFrame như sau: `balance_df.T`

### Báo cáo lưu chuyển tiền tệ

Để tải dữ liệu báo cáo lưu chuyển tiền tệ, bạn sử dụng câu lệnh:

```python
cashflow_df = financial_flow(symbol="TCB", report_type='cashflow', report_range='quarterly')
```

- Kết quả:

```shell
        ticker  investCost  fromInvest  fromFinancial  fromSale  freeCashFlow
index
2021-Q4    TCB        -280        -276              0     -9328             0
2021-Q3    TCB        -180        -179             60     17974             0
2021-Q2    TCB        -337        -282              0     11205             0
2021-Q1    TCB        -143        -143              0     -6954             0
```

Để hiển thị báo cáo như cách trình bày trên website TCBS, bạn cần xoay (transpose) DataFrame trả về. Giả sử bạn lưu kết quả trả về vào biến **cashflow_df** như trên, bạn có thể sử dụng phương thức **transpose** để xoay DataFrame như sau: `cashflow_df.T`

## Chỉ số định giá

<div class="stock_evaluation">
  <a href="assets/images/tcbs_stock_evaluation.png?raw=true" data-title="Dữ liệu định giá cổ phiếu từ TCBS" data-toggle="lightbox"><img class="img-responsive" src="assets/images/tcbs_stock_evaluation.png?raw=true" alt="screenshot" /></a>
  <a class="mask" href="assets/images/tcbs_stock_evaluation.png?raw=true" data-title="Dữ liệu định giá cổ phiếu từ TCBS" data-toggle="lightbox"><i class="icon fa fa-search-plus"></i></a>
</div>

Chỉ số định giá được truy xuất từ nguồn TCBS thông qua hàm **stock_evaluation**. Hàm này nhận 3 tham số:
- **symbol** là mã chứng khoán bạn muốn phân tích
- **period** nhận 1 trong 2 giá trị: **1** cho phép trả về chỉ số theo ngày, **2** trả về dữ liệu theo tuần
- **time_window** nhận 1 trong 2 giá trị: **D** cho phép trả về chỉ số theo ngày, **W** trả về dữ liệu theo tuần

Minh họa cho hàm này như sau:

```python
stock_evaluation (symbol='TCB', period=1, time_window='D')
```

- Kết quả:

```shell
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

