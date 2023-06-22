<div id="badges" align="center">
<img src="https://img.shields.io/pypi/pyversions/vnstock?logoColor=brown&style=plastic" alt= "Version"/>
<img src="https://img.shields.io/pypi/dm/vnstock" alt="Download Badge"/>
<img src="https://img.shields.io/github/last-commit/thinh-vu/vnstock" alt="Commit Badge"/>
<img src="https://img.shields.io/github/license/thinh-vu/vnstock?color=red" alt="License Badge"/>
</div>

---

🌐 View in **[English](https://github.com/thinh-vu/vnstock/blob/main/README-en.md)**

MỤC LỤC
- [I. 🎤 Giới thiệu](#i--giới-thiệu)
- [II. 📚 Hướng dẫn sử dụng cho người mới](#ii-hướng-dẫn-sử-dụng-cho-người-mới)
- [III. 💻 Cách sử dụng các hàm trong vnstock](#iii--cách-sử-dụng-các-hàm-trong-vnstock)
- [IV. 🙋‍♂️ Contact Information](#iv-️-contact-information)
- [V. 💪 Hỗ trợ phát triển dự án vnstock](#v--hỗ-trợ-phát-triển-dự-án-vnstock)
- [VI. ⚖ Tuyên bố miễn trừ trách nhiệm](#vi--tuyên-bố-miễn-trừ-trách-nhiệm)
- [VII. Bản quyền và giấy phép](#vii-bản-quyền-và-giấy-phép)

# I. 🎤 Giới thiệu
## 1.1. Giới thiệu chung
vnstock là thư viện Python được thiết kế để tải dữ liệu chứng khoán Việt Nam một cách dễ dàng và miễn phí. vnstock sử dụng các nguồn cấp dữ liệu đáng tin cậy, bao gồm nhưng không giới hạn từ công ty chứng khoán và công ty phân tích thị trường tại Việt Nam. Gói thư viện được thiết kế dựa trên nguyên tắc về sự đơn giản và mã nguồn mở, hầu hết các hàm được viết dựa trên thư viện request và pandas có sẵn trên môi trường Google Colab do đó người dùng không cần cài đặt thêm các gói thư viện kèm theo.

## 1.2. Tính năng chính
vnstock cung cấp nhiều tính năng đa dạng như tải dữ liệu lịch sử giá, thông tin công ty niêm yết, thông tin thị trường cho tất cả các mã chứng khoán niêm yết.

## 1.3. Nguồn cấp dữ liệu
Thư viện python này kết nối tới các API công khai của các nguồn cấp dữ liệu để tải về để làm việc dưới dạng các DataFrame trong dự án Python. Việc truy xuất dữ liệu này là hoàn toàn **MIỄN PHÍ** và không có **GIỚI HẠN**. 

# II. 📚 Hướng dẫn sử dụng cho người mới

👉 Để biết thêm thông tin và minh hoạt về cách sử dụng, bạn vui lòng truy cập bài viết trên blog của tôi, có sẵn bằng tiếng Việt/Anh [tại đây](https://thinhvu.com/2022/09/22/vnstock-api-tai-du-lieu-chung-khoan-python?utm_source=github&utm_medium=vnstock).

👉 Bạn có thể mở tệp Jupyter Notebook [vnstock_demo_index_all_functions_testing_2023_06_22.ipynb](https://github.com/thinh-vu/vnstock/blob/beta/vnstock_demo_index_all_functions_testing_2023_06_22.ipynb) để dùng thử tất cả các hàm của vnstock. Để sử dụng, nhấp vào nút ![Open in Colab](https://colab.research.google.com/assets/colab-badge.svg) ở đầu trang của notebook để mở với Google Colab.

🖐 Nếu bạn thấy thư viện này có giá trị và muốn hỗ trợ tác giả duy trì vnstock dưới dạng mã nguồn mở, miễn phí thì có thể tham gia ủng hộ gây quỹ phát triển dự án này. Để biết thêm chi tiết, vui lòng tham khảo bài viết trên blog sau: [Cùng nhau xây dựng cộng đồng VNStock vững mạnh](https://thinhvu.com/2023/04/15/xay-dung-cong-dong-vnstock-vung-manh/).

🔥 Bạn có thể tham khảo thêm [Ý tưởng cho các tính năng nâng cao cho các phiên bản sắp tới](https://github.com/users/thinh-vu/projects/1/views/4) để đồng hành cùng vnstock. 

👉 Từ phiên bản 1.0.3, tất cả các cập nhật về tính năng và nâng cấp cho thư viện được tổng hợp trong file [Lịch sử thay đổi](https://github.com/thinh-vu/vnstock/blob/beta/changes_log.md).

## 2.2 🛠 Cài đặt

Để sử dụng thư viên vnstock,bạn cần **sử dụng pip để cài đặt** (yêu cầu phiên bản Python 3.7 trở lên) với câu lệnh sau trong giao diện cửa sổ dòng lệnh Terminal với macOS, Linux hoặc Command Prompt với Windows. Bạn cũng có thể chèn đoạn mã này vào một ô lệnh trong Jupyter Notebook và thực thi nó, có thể cần sử dụng dấu `!` trước câu lệnh:

`pip install vnstock`

Ngoài ra, **nếu bạn muốn sử dụng phiên bản `vnstock` mới nhất từ nguồn Github thay vì phiên bản ổn định từ [Pypi](https://pypi.org/project/vnstock/)** thì sử dụng lệnh cài đặt sau:

`pip install git+https://github.com/thinh-vu/vnstock.git@beta`

**Nhánh `main` của repository này đảm bảo thể hiện mã nguồn vnstock được phát hành trên Pypi** trong khi đó, nhánh `beta` cho phép tải những cập nhật mới nhất từ thư viện, đôi khi có thể phát sinh lỗi.
---

# III. 💻 Cách sử dụng các hàm trong vnstock
Bạn có thể hiểu cách sử dụng các hàm cơ bản của vnstock bằng cách tham khảo hướng dẫn này hoặc đơn giản là mở file [vnstock demo index - all functions testing // 2023-03-25.ipynb](https://github.com/thinh-vu/vnstock/blob/main/vnstock_demo_index_all_functions_testing_2023_03_25.ipynb) để chạy các dòng lệnh mẫu và xem kết quả. Ngoài ra, tất cả các hàm có trong vnstock đều được cung cấp docstring đầy đủ, do đó bạn có thể xem phần lời nhắc khi viết câu lệnh trên các IDE như Google Colab, Visual Studio Code, hay Jupyter Notebook, ... để biết thêm thông tin chi tiết về cách sử dụng các hàm.

Để nạp các hàm của vnstock vào dự án Python của bạn, cần dùng lệnh `import` như dưới đây, sau đó bạn có thể sử dụng các hàm được liệt kê bên dưới.

```python
from vnstock import *
```

## 2.1 📰 Danh sách các công ty niêm yết
```python
listing_companies()
```
Hàm này đọc dữ liệu từ tệp csv đính kèm trên Github theo mặc định (trong thư mục /data của repo này). Bởi danh sách các công ty niêm yết thường không thay đổi liên tục nên việc này không gây trở ngại nhiều. Hiện tại chế độ đọc dữ liệu từ APIs đã được tạm gỡ bỏ do bị chặn truy cập bởi các nhà cung cấp dữ liệu.

<details>
  <summary>Output</summary>

```
     ticker  group_code                                       company_name            company_short_name
0       HSV  UpcomIndex                   Công ty Cổ phần Gang Thép Hà Nội              Gang Thép Hà Nội
1       SCV  UpcomIndex                      Công ty Cổ phần Muối Việt Nam                  Visalco.,JSC
2       LYF  UpcomIndex              Công ty Cổ phần  Lương Thực Lương Yên  Công ty Lương Thực Lương Yên
3       CST  UpcomIndex                 Công ty Cổ phần Than Cao Sơn - TKV            Than Cao Sơn - TKV
4       BVL  UpcomIndex                            Công ty Cổ phần BV Land                       BV Land
```

</details>

## 2.2. Tổng quan về một mã chứng khoán cụ thể
```python
company_overview('TCB')
```

<details>
  <summary>Output</summary>

  ```
  >>> company_overview('TCB')
    exchange    shortName  industryID industryIDv2   industry  ... deltaInMonth deltaInYear  outstandingShare  issueShare  ticker
  0     HOSE  Techcombank         289         8355  Ngân hàng  ...       -0.027      -0.038            3510.9      3510.9     TCB
  ```

</details>

## 2.3. 📈 Truy xuất dữ liệu giá lịch sử

vnstock cho phép người dùng **tải xuống dữ liệu lịch sử giao dịch cổ phiếu** với theo 5 mức độ chi tiết theo khoảng thời gian bao gồm: 1 phút, 15 phút, 30 phút, 1 giờ, 1 ngày. Trong ví dụ dưới đây, dữ liệu giá được truy xuất theo cấp độ ngày.

```python
df =  stock_historical_data(symbol='GMD', 
                            start_date="2021-01-01", 
                            end_date='2022-02-25', resolution='1D')
print(df.head())
```
- Mới: Giá trị mà tham số `resolution` có thể nhận là `1D` (mặc định, 1 ngày), '1' (1 phút), 15 (15 phút), 30 (30 phút), '1H' (hàng giờ).

Bạn cũng có thể viết hàm theo dạng rút gọn như dưới đây, điều này đúng với tất cả các hàm, miễn là thông số được nhập vào đúng thứ tự:

```python
df = stock_historical_data("GMD", "2021-01-01", "2022-02-25", "1D")
print(df.head())
```
Và đây là kết quả

<details>
  <summary>Output</summary>

  ```{r, engine='python', count_lines}
   time        open     high     low      close    volume
0  2021-01-04  32182.0  33157.0  31987.0  32279.0  4226500
1  2021-01-05  32279.0  33596.0  31938.0  32962.0  4851900
2  2021-01-06  33352.0  33352.0  32279.0  32572.0  3641300
  ```

</details>

## 2.4. 📊 Bảng giá
Bạn có thể tải xuống bảng giá của một danh sách các cổ phiếu được chọn để phân tích dễ dàng hơn (khi xuất ra Google Sheets/Excel) so với việc xem trực tiếp trên bảng giá của các công ty chứng khoán.

<details>
  <summary>Bảng giá</summary>

  ![price_board](https://raw.githubusercontent.com/thinh-vu/vnstock/main/src/tcbs_trading_board_sector.png)

</details>

Tất cả việc bạn cần làm là nhập vào danh sách các mã cổ phiếu bạn chọn:

```
price_board('TCB,SSI,VND')
```

<details>
  <summary>Output</summary>

```
>>> price_board('TCB,SSI,VND')
  Mã CP  Giá Khớp Lệnh  KLBD/TB5D  T.độ GD  KLGD ròng(CM)  ...  vnid1m  vnid3m  vnid1y  vnipe    vnipb
0   TCB        48600.0        0.6     0.49         -23200  ...    -3.7    -2.0    22.4  17.99  2.46159
1   SSI        43300.0        0.5     0.50        -112200  ...    -3.7    -2.0    22.4  17.99  2.46159
2   VND        32600.0        0.7     0.68          37300  ...    -3.7    -2.0    22.4  17.99  2.46159
```
</details>

## 2.5. 🔥 Dữ liệu thời gian thực trong ngày giao dịch (Intraday)

<details>
  <summary>Intraday view on TCBS</summary>

  ![intraday](https://raw.githubusercontent.com/thinh-vu/vnstock/main/src/tcbs_intraday_screen1.png)
  ![intraday](https://raw.githubusercontent.com/thinh-vu/vnstock/main/src/tcbs_intraday_screen2.png)

</details>
vnstock cho phép người dùng tải xuống dữ liệu giao dịch theo thời gian thực trong ngày ngày giao dịch. Nếu mốc thời gian bạn truy cứu rơi vào Thứ Bảy, Chủ Nhật thì dữ liệu nhận được thể hiện cho ngày giao dịch của Thứ 6 của tuần đó.

```python
df =  stock_intraday_data(symbol='GMD', 
                            page_num=0, 
                            page_size=100)
print(df.head())
```

<details>
  <summary>Output</summary>

  ```{r, engine='python', count_lines}
  p     volume       cp       rcp   a   ba   sa     hl  pcp      time
  0     50700.0  169700  0.0  0.0      0.0  0.0   True  0.0  14:45:08
  1     50800.0    1000  0.0  0.0  BU  0.0  0.0  False  0.0  14:30:05
  2     50800.0     500  0.0  0.0  BU  0.0  0.0  False  0.0  14:30:05
  3     50800.0   20000  0.0  0.0  BU  0.0  0.0   True  0.0  14:29:54
  4     50700.0     300  0.0  0.0  SD  0.0  0.0  False  0.0  14:29:53
  ```

</details>

## 2.6. 💰 Các chỉ số tài chính
### 2.6.1. So sánh các chỉ số tài chính của nhiều mã cổ phiếu

<details>
  <summary>Tạm ngưng hoạt động do nguồn dữ liệu từ SSI bị chặn</summary>

  ```python
  financial_ratio_compare (symbol_ls=['TCB', 'CTG', 'BID'], industry_comparison='true', frequency= 'Yearly', start_year=2020)
  ```
  - _symbol_ls_: danh sách các mã cổ phiếu quán tâm
  - _industry_comparison_: `true` hoặc `false`
  - _frequency:_ `Yearly` hoặc `Quarterly`

  <details>
    <summary>Output</summary>

  ```
                                    Chỉ số          2017          2018          2019          2020          2021
  0                                    P/E           NaN           NaN           NaN           NaN           NaN
  1                                    BID  1.931659e+01  1.579755e+01  2.156374e+01  2.392118e+01  2.109997e+01
  2                                    TCB  1.589460e+01  1.099041e+01  7.712361e+00  1.110489e+01  9.790559e+00
  3                                    CTG  1.578063e+01  1.476715e+01  1.015345e+01  1.031625e+01  1.135594e+01
  4                                    BID  1.931659e+01  1.579755e+01  2.156374e+01  2.392118e+01  2.109997e+01
  ..                                   ...           ...           ...           ...           ...           ...
  171                           Toàn ngành  2.272894e+10  2.932384e+10  3.172492e+10  3.927128e+10  5.101939e+10
  172                                  NaN           NaN           NaN           NaN           NaN           NaN
  173                                  NaN           NaN           NaN           NaN           NaN           NaN
  174  Dữ liệu được cung cấp bởi FiinTrade           NaN           NaN           NaN           NaN           NaN
  175                https://fiintrade.vn/           NaN           NaN           NaN           NaN           NaN
  ```
  </details>

</details>

### 2.6.2. Chỉ số tài chính của một mã cổ phiếu
```python
financial_ratio("TCB", 'quarterly', True)
```

<details>
  <summary>Output</summary>

  ```
  ticker  quarter  year  priceToEarning  priceToBook valueBeforeEbitda dividend  ...  badDebtOnAsset  liquidityOnLiability payableOnEquity cancelDebt ebitdaOnStockChange bookValuePerShareChange  creditGrowth
  0     TCB        4  2021             9.9          1.9              None     None  ...           0.004                 0.382             5.1      0.004                None                   0.053         0.252
  1     TCB        3  2021            10.0          2.0              None     None  ...           0.003                 0.405             5.1      0.004                None                   0.053         0.392
  2     TCB        2  2021            11.4          2.2              None     None  ...           0.002                 0.370             5.0      0.008                None                   0.061         0.353
  3     TCB        1  2021             9.9          1.8              None     None  ...           0.002                 0.354             4.9      0.012                None                   0.060         0.277
  4     TCB        4  2020             9.0          1.5              None     None  ...           0.003                 0.372             4.9      0.013                None                   0.057         0.202
  ```
</details>

## 2.7. So sánh cổ phiếu
### 2.7.1. 🏭 Phân tích các mã cổ phiếu cùng ngành
```python
industry_analysis("VNM")
```
Trả về thông tin các mã cổ phiếu cùng ngành với mã cổ phiếu nằm trong cùng nhóm ngành với mã `VNM`.

<details>
  <summary>Output</summary>

![preview](./src/stock_comparison_industries.png?raw=true)

```
>>> industry_analysis("VNM")
   ticker  marcap   price  numberOfDays  priceToEarning   peg  priceToBook  valueBeforeEbitda  dividend  ...  debtOnEbitda  income5year  sale5year income1quarter sale1quarter nextIncome  nextSale   rsi    rs
0     VNM  164897   78900             1            15.7  -3.1          5.0               12.6     0.037  ...           0.6        0.024      0.054         -0.249       -0.023       None      None  34.9  18.0
0     MSN  186524  158000            -1            21.8   0.0          5.7               22.5     0.008  ...           5.5        0.251      0.154          4.610        0.009        NaN       NaN  54.5  58.0
1     MCH   80250  112100             1            14.7   0.7          4.9               12.0     0.000  ...           1.2        0.152      0.150          0.381        0.372        NaN       NaN  48.6  36.0
2     MML   26061   79700            -1            19.6   0.0          4.7               24.9     0.000  ...           4.2       -0.029     -0.050          6.771       -0.243      0.904      0.22  58.8  60.0
```
</details>

### 2.7.2. 🔬 So sánh các chỉ số của danh sách các cổ phiếu tùy chọn
```python
stock_ls_analysis("TCB, BID, CEO, GMD")
```

<details>
  <summary>Output</summary>

![preview](./src/stock_ls_comparison.png)

```
  ticker  marcap  price  numberOfDays  priceToEarning  peg  priceToBook  valueBeforeEbitda  dividend  ...  debtOnEbitda  income5year  sale5year income1quarter  sale1quarter  nextIncome  nextSale   rsi    rs
0    GMD   15220  50500            -3            25.2  0.4          2.4               16.2       0.0  ...           1.8        0.092     -0.030          0.500         0.425         NaN       NaN  60.3  50.0
1    CEO   17062  66300             1           183.2 -0.8          5.7               81.8       0.0  ...           7.8       -0.099     -0.086            NaN         3.002      -1.469      -0.2  51.9  82.0
2    BID  225357  44550            -3            21.3  0.4          2.6                NaN       0.0  ...           NaN        0.115      0.154          0.083         0.000         NaN       NaN  49.1  34.0
3    TCB  178003  50700             1             9.9  0.2          1.9                NaN       0.0  ...           NaN        0.418      0.255          0.059         0.157         NaN       NaN  45.2  28.0
```

</details>

### 2.7.3. 🏢 Tổng quan công ty
```python
company_overview('TCB')
```

<details>
  <summary>Output</summary>

```
>>> company_overview('TCB')
  exchange    shortName  industryID industryIDv2  ... deltaInYear outstandingShare issueShare  ticker
0     HOSE  Techcombank         289         8355  ...      -0.075           3510.9     3510.9     TCB
```
</details>

### 2.7.4. 💵 Báo cáo kết quả kinh doanh, cân đối kế toán và lưu chuyển tiền tệ

#### 2.7.4.1. Báo cáo từ SSI

<details>
  <summary>Tạm ngưng hoạt động do SSI từ chối truy cập</summary>

> Theo nhận định của tác giả, định dạng báo cáo được cung cấp bởi SSI khá đầy đủ và dễ theo dõi so với bản báo cáo tài chính do TCBS cung cấp (rút gọn).

```python
financial_report (symbol='SSI', report_type='BalanceSheet', frequency='Quarterly')
```
- _report_type:_ Bạn có thể chọn 1 trong ba mẫu báo cáo: `BalanceSheet` cho Bảng cân đối kế toán, `IncomeStatement` cho báo cáo kết quả kinh doanh, hoặc `CashFlow` cho báo cáo lưu chuyển tiền tệ
- _frequency:_ `Yearly` or `Quarterly`

<details>
  <summary>Output</summary>

  ```
                                        CHỈ TIÊU          2012          2013  ...          2019          2020          2021
  0                            TỔNG CỘNG TÀI SẢN  7.980876e+12  7.705074e+12  ...  2.704412e+13  3.576953e+13  5.079306e+13
  1                             TÀI SẢN NGẮN HẠN  4.837002e+12  4.467396e+12  ...  2.229087e+13  2.904003e+13  4.653960e+13
  3                    Tiền và tương đương tiền   1.947090e+12  1.838619e+12  ...  1.040783e+12  3.632519e+11  1.114235e+12
  4                                         Tiền  8.068605e+11  1.437619e+12  ...  2.606318e+11  2.319712e+11  4.741978e+11
  5                   Các khoản tương đương tiền  1.140230e+12  4.010000e+11  ...  7.801508e+11  1.312807e+11  6.400373e+11
  ..                                         ...           ...           ...  ...           ...           ...           ...
  149                   Lợi nhuận chưa phân phối  1.127003e+12  1.118080e+12  ...  2.941467e+12  2.676816e+12  2.927813e+12
  153         Vốn Ngân sách nhà nước và quỹ khác  0.000000e+00  0.000000e+00  ...  0.000000e+00  0.000000e+00  0.000000e+00
  154    Quỹ khen thưởng , phúc lợi (trước 2010)  0.000000e+00  0.000000e+00  ...  0.000000e+00  0.000000e+00  0.000000e+00
  157  LỢI ÍCH CỦA CỔ ĐÔNG THIỂU SỐ (trước 2015)  8.369917e+10  8.299030e+10  ...  0.000000e+00  0.000000e+00  0.000000e+00
  158                        TỔNG CỘNG NGUỒN VỐN  7.980876e+12  7.705074e+12  ...  2.704412e+13  3.576953e+13  5.079306e+13
  ```
</details>

</details>

#### 2.7.4.2. Báo cáo từ TCBS

##### 📄 Báo cáo kinh doanh

![income_statement](https://raw.githubusercontent.com/thinh-vu/vnstock/main/src/financial_income_statement.png)
```python
financial_flow(symbol="TCB", report_type='incomestatement', report_range='quarterly')
```


<details>
  <summary>Output</summary>

```
        ticker  revenue  yearRevenueGrowth  quarterRevenueGrowth costOfGoodSold grossProfit  ...  investProfit  serviceProfit  otherProfit  provisionExpense operationIncome  ebitda
index                                                                                        ...
2021-Q4    TCB     7245              0.328                 0.074           None        None  ...           279           2103          532              -627            6767    None
2021-Q3    TCB     6742              0.310                 0.023           None        None  ...           384           1497          156              -589            6151    None
2021-Q2    TCB     6588              0.674                 0.076           None        None  ...           717           1457          444              -598            6615    None
2021-Q1    TCB     6124              0.454                 0.122           None        None  ...           812           1325          671              -851            6369    None
```
</details>

##### 🧾 Bảng cân đối kế toán

![balance_sheet](https://raw.githubusercontent.com/thinh-vu/vnstock/main/src/financial_balancesheet.png)
```python
financial_flow(symbol="TCB", report_type='balancesheet', report_range='quarterly')
```

<details>
  <summary>Output</summary>

```
        ticker shortAsset  cash shortInvest shortReceivable inventory longAsset  fixedAsset  ...  payableInterest  receivableInterest deposit otherDebt  fund  unDistributedIncome  minorShareHolderProfit  payable
index                                                                                        ...

2021-Q4    TCB       None  3579        None            None      None      None        7224  ...             3098                5808  314753     33680  9156                47469                     845   475756
2021-Q3    TCB       None  3303        None            None      None      None        7106  ...             3074                6224  316376     34003  6784                45261                     753   453251
2021-Q2    TCB       None  3554        None            None      None      None        6739  ...             2643                5736  289335     27678  6790                40924                     659   420403
2021-Q1    TCB       None  4273        None            None      None      None        4726  ...             2897                5664  287446     26035  6790                36213                     563   3837
```
</details>

##### 💶 Báo cáo lưu chuyển tiền tệ

```python
financial_flow(symbol="TCB", report_type='cashflow', report_range='quarterly')
```

<details>
  <summary>Output</summary>

```
        ticker  investCost  fromInvest  fromFinancial  fromSale  freeCashFlow
index
2021-Q4    TCB        -280        -276              0     -9328             0
2021-Q3    TCB        -180        -179             60     17974             0
2021-Q2    TCB        -337        -282              0     11205             0
2021-Q1    TCB        -143        -143              0     -6954             0
```
</details>

## 2.8. 🧧 Lịch sử chi trả cổ tức

```python
dividend_history("VNM")
```

<details>
  <summary>Output</summary>

```
   exerciseDate  cashYear  cashDividendPercentage issueMethod
0      10/01/22      2021                    0.14        cash
1      07/09/21      2021                    0.15        cash
2      07/06/21      2020                    0.11        cash
3      05/01/21      2020                    0.10        cash
```
</details>

## 2.9. ⭐ Đánh giá xếp hạng chung
![general_rating](https://raw.githubusercontent.com/thinh-vu/vnstock/beta/src/general_rating.png)

```python
general_rating("VNM")
```

<details>
  <summary>Output</summary>

```
   stockRating  valuation  financialHealth  businessModel  businessOperation  rsRating  taScore  ... ticker highestPrice  lowestPrice  priceChange3m  priceChange1y  beta   alpha
0          2.4        1.5              4.8            3.0                3.2       1.0      1.0  ...    VNM     102722.2      78600.0         -0.092         -0.232  0.49 -0.0014
```
</details>

## 2.10. 🌱 Đánh giá mô hình kinh doanh
```python
biz_model_rating("VNM")
```

<details>
  <summary>Output</summary>

```
  ticker  businessModel  businessEfficiency  assetQuality  cashFlowQuality  bom  businessAdministration  productService  businessAdvantage  companyPosition  industry  operationRisk
0    VNM            3.0                   3             3                3    3                       3               3                  3                3         3              3
```
</details>

## 2.11. 🎮 Đánh giá hiệu quả hoạt động
```python
biz_operation_rating("VNM")
```

<details>
  <summary>Output</summary>

```
      industryEn loanGrowth depositGrowth netInterestIncomeGrowth netInterestMargin  ... last5yearsFCFFGrowth lastYearGrossProfitMargin lastYearOperatingProfitMargin  lastYearNetProfitMargin  TOIGrowth
0  Food Products       None          None                    None              None  ...                    2                         5                             3                        4       None
```
</details>

## 2.12. 📑 Đánh giá sức khỏe tài chính
```python
financial_health_rating("VNM")
```

<details>
  <summary>Output</summary>

```
      industryEn loanDeposit badLoanGrossLoan badLoanAsset provisionBadLoan ticker  financialHealth  netDebtEquity  currentRatio  quickRatio  interestCoverage  netDebtEBITDA
0  Food Products        None             None         None             None    VNM              4.8              4             5           5                 5              5
```
</details>

## 2.13. 💲 Đánh giá về Định giá
```python
valuation_rating("VNM")
```

<details>
  <summary>Output</summary>

```
      industryEn ticker  valuation  pe  pb  ps  evebitda  dividendRate
0  Food Products    VNM        1.5   2   1   1         1             3
```
</details>

## 2.14.  💳 Sức khỏe tài chính theo ngành
```python
industry_financial_health("VNM")
```

<details>
  <summary>Output</summary>

```
  industryEn loanDeposit badLoanGrossLoan badLoanAsset provisionBadLoan ticker  financialHealth  netDebtEquity  currentRatio  quickRatio  interestCoverage  netDebtEBITDA
0       None        None             None         None             None    VNM              3.4              4             4           3                 3              3
```
</details>

## 2.15. 🌏 Thông tin thị trường

<details>
  <summary>Tạm ngưng hoạt động do SSI từ chối truy cập</summary>

### 2.15.1. Các mã cổ phiếu đứng đầu theo tiêu chí xếp loại 

<details>
  <summary>SSI Top Stocks</summary>

Top Breakout (Đột phá) > Top Gainers (Tăng giá) > Top Losers (Giảm giá) > Top Value (Giá trị) > Top Volume (Khối lượng)
![top_mover](./src/ssi_top_breakout_gainer_loser.png)

Top New High (vượt đỉnh) > Top Foreign Trading (nhà đầu tư ngước ngoài) > Top New Low (thủng đáy)
![top_foreigntrading_high_low](./src/top_foreigntrading_newhigh_newlow.png)

</details>

```python
market_top_mover('ForeignTrading')
```

<details>
  <summary>Output</summary>

```
    foreignBuyVolume  foreignBuyValue  ...                                          financial                                          technical
0          3826600.0     1.703888e+11  ...  {'organCode': 'DXG', 'rtd7': 14713.265320738, ...  {'organCode': 'DXG', 'sma20Past4': 34887.5, 's...
1          3270200.0     1.088892e+11  ...  {'organCode': 'STB', 'rtd7': 18173.6958318461,...  {'organCode': 'STB', 'sma20Past4': 34332.5, 's...
2          1456800.0     4.199166e+10  ...  {'organCode': 'FUEVFVND', 'rtd7': None, 'rtd11...  {'organCode': 'FUEVFVND', 'sma20Past4': 27993....
3          1033300.0     1.281170e+10  ...  {'organCode': 'FLC', 'rtd7': 12898.0038031343,...  {'organCode': 'FLC', 'sma20Past4': 12062.5, 's...
4           998600.0     5.324337e+10  ...  {'organCode': 'NLG', 'rtd7': 23318.1252311207,...  {'organCode': 'NLG', 'sma20Past4': 52385.0, 's...
```
</details>

### 2.15.2. Thông tin giao dịch nhà đầu tư nước ngoài (NDTNN)
Trong ví dụ dưới đây, thể hiện giao dịch mua vào của NDTNN.

```python
fr_trade_heatmap ('All', 'FrBuyVol')
```
<details>
  <summary>Output</summary>

  ```
    organCode  name      value  percentPriceChange  ...  ceilingPrice  floorPrice        industry_name      rate
  0        PVD   PVD  1433300.0            0.068627  ...       16350.0     14250.0              Dầu khí  0.040308
  1        PVS   PVS   370100.0            0.096154  ...       22800.0     18800.0              Dầu khí  0.040308
  2      PETRO   PLX   249700.0            0.014516  ...       33150.0     28850.0              Dầu khí  0.040308
  3   PETECHIM   PTV     4000.0            0.064000  ...        5400.0      4000.0              Dầu khí  0.040308
  4       BSRC   BSR     3800.0            0.002000  ...       17200.0     12800.0              Dầu khí  0.040308
  ..       ...   ...        ...                 ...  ...           ...         ...                  ...       ...
  10      None  Khác   210200.0            0.027762  ...           0.0         0.0            Ngân hàng  0.050653
  0        CMG   CMG    74400.0            0.024390  ...       43850.0     38150.0  Công nghệ Thông tin  0.034816
  1        SAM   SAM    35700.0            0.020833  ...        7700.0      6700.0  Công nghệ Thông tin  0.034816
  2        ELC   ELC     4100.0            0.049197  ...       10650.0      9270.0  Công nghệ Thông tin  0.034816
  3        ITD   ITD     2000.0            0.068548  ...       13250.0     11550.0  Công nghệ Thông tin  0.034816

  [92 rows x 10 columns]
  ```
</details>

### 2.15.3. Biến động của các nhóm chỉ số
![latest_indices](https://raw.githubusercontent.com/thinh-vu/vnstock/main/src/get_latest_indices.png)

Thông tin các nhóm chỉ số phổ biến của thị trường chứng khoán Việt Nam.

```python
get_latest_indices()
```

<details>
  <summary>Output</summary>

  ```
  >>> get_latest_indices()
    indexId comGroupCode  indexValue          tradingDate  ...  matchValue  ceiling  floor  marketStatus
0         0      VNINDEX     1108.08  2023-01-19T00:00:00  ...         0.0      0.0    0.0          None
1         0         VN30     1121.92  2023-01-19T00:00:00  ...         0.0      0.0    0.0          None
2         0     HNXIndex      219.87  2023-01-19T00:00:00  ...         0.0      0.0    0.0          None
3         0        HNX30      378.94  2023-01-19T00:00:00  ...         0.0      0.0    0.0          None
4         0   UpcomIndex       73.98  2023-01-19T00:00:00  ...         0.0      0.0    0.0          None
5         0       VNXALL     1707.39  2023-01-19T00:00:00  ...         0.0      0.0    0.0          None
6         0        VN100     1063.59  2023-01-19T00:00:00  ...         0.0      0.0    0.0          None
7         0        VNALL     1066.54  2023-01-19T00:00:00  ...         0.0      0.0    0.0          None
8         0       VNCOND     1537.34  2023-01-19T00:00:00  ...         0.0      0.0    0.0          None
9         0       VNCONS      793.25  2023-01-19T00:00:00  ...         0.0      0.0    0.0          None
10        0    VNDIAMOND     1689.15  2023-01-19T00:00:00  ...         0.0      0.0    0.0          None
11        0        VNENE      541.51  2023-01-19T00:00:00  ...         0.0      0.0    0.0          None
12        0        VNFIN     1252.54  2023-01-19T00:00:00  ...         0.0      0.0    0.0          None
13        0    VNFINLEAD     1631.16  2023-01-19T00:00:00  ...         0.0      0.0    0.0          None
14        0  VNFINSELECT     1676.21  2023-01-19T00:00:00  ...         0.0      0.0    0.0          None
15        0       VNHEAL     1552.19  2023-01-19T00:00:00  ...         0.0      0.0    0.0          None
16        0        VNIND      628.34  2023-01-19T00:00:00  ...         0.0      0.0    0.0          None
17        0         VNIT     2631.82  2023-01-19T00:00:00  ...         0.0      0.0    0.0          None
18        0        VNMAT     1534.50  2023-01-19T00:00:00  ...         0.0      0.0    0.0          None
19        0        VNMID     1394.75  2023-01-19T00:00:00  ...         0.0      0.0    0.0          None
20        0       VNREAL      981.94  2023-01-19T00:00:00  ...         0.0      0.0    0.0          None
21        0         VNSI     1715.37  2023-01-19T00:00:00  ...         0.0      0.0    0.0          None
22        0        VNSML     1140.40  2023-01-19T00:00:00  ...         0.0      0.0    0.0          None
23        0        VNUTI      874.84  2023-01-19T00:00:00  ...         0.0      0.0    0.0          None
24        0        VNX50     1805.33  2023-01-19T00:00:00  ...         0.0      0.0    0.0          None
  ```
</details>

### 2.15.4. Dữ liệu chuyên sâu theo nhóm chỉ số cụ thể
![index_series_data](https://raw.githubusercontent.com/thinh-vu/vnstock/main/src/get_index_series_data.png)

```python
get_index_series(index_code='VNINDEX', time_range='OneYear')
```
- Nhà cung cấp dữ liệu: SSI iBoard sử dụng dữ liệu từ FiinTrade.
- Sử dụng một trong các mã chỉ số sau để tra cứu:
  
  ```
  'VNINDEX', 'VN30', 'HNXIndex', 'HNX30', 'UpcomIndex', 'VNXALL',
  'VN100','VNALL', 'VNCOND', 'VNCONS','VNDIAMOND', 'VNENE', 'VNFIN',
  'VNFINLEAD', 'VNFINSELECT', 'VNHEAL', 'VNIND', 'VNIT', 'VNMAT', 'VNMID',
  'VNREAL', 'VNSI', 'VNSML', 'VNUTI', 'VNX50'
  ```
  Bạn có thể liệt kê toàn bộ các nhóm chỉ số với hàm `get_latest_indices()`.

- `time_range`: Sử dụng khung thời gian là một trong các giá trị sau
 ```
 'OneDay', 'OneWeek', 'OneMonth', 'ThreeMonth', 'SixMonths', 'YearToDate', 'OneYear', 'ThreeYears', 'FiveYears'
 ```
<details>
  <summary>Output</summary>

  ```
  >>> get_index_series(index_code='VNINDEX', time_range='OneYear')
      comGroupCode  indexValue          tradingDate  ...    matchValue  totalMatchVolume  totalMatchValue
  0        VNINDEX     1470.76  2022-01-27T00:00:00  ...  1.554536e+13       498256400.0     1.554536e+13
  1        VNINDEX     1478.96  2022-01-28T00:00:00  ...  1.913215e+13       634887600.0     1.913215e+13
  2        VNINDEX     1497.66  2022-02-07T00:00:00  ...  1.710999e+13       516533800.0     1.710999e+13
  3        VNINDEX     1500.99  2022-02-08T00:00:00  ...  2.106676e+13       660158600.0     2.106676e+13
  4        VNINDEX     1505.38  2022-02-09T00:00:00  ...  2.360041e+13       722161500.0     2.360041e+13
  ..           ...         ...                  ...  ...           ...               ...              ...
  241      VNINDEX     1060.17  2023-01-13T00:00:00  ...  7.884840e+12       459494342.0     7.884840e+12
  242      VNINDEX     1066.68  2023-01-16T00:00:00  ...  6.724499e+12       391079501.0     6.724499e+12
  243      VNINDEX     1088.29  2023-01-17T00:00:00  ...  1.016031e+13       566247477.0     1.016031e+13
  244      VNINDEX     1098.28  2023-01-18T00:00:00  ...  9.377296e+12       531786150.0     9.377296e+12
  245      VNINDEX     1108.08  2023-01-19T00:00:00  ...  1.054607e+13       556193050.0     1.054607e+13

  [246 rows x 14 columns]
  ```
</details>

</details>

# IV. 🙋‍♂️ Contact Information

Bạn có thể kết nối với tác giả qua các hình thức sau. Trong trường hợp cần hỗ trợ nhanh, bạn có thể chọn nhắn tin qua Messenger hoặc Linkedin, tôi sẽ phản hồi ngay lập tức nếu có thể trong hầu hết các trường hợp.

<div id="badges" align="center">
  <a href="https://www.linkedin.com/in/thinh-vu">
    <img src="https://img.shields.io/badge/LinkedIn-blue?style=for-the-badge&logo=linkedin&logoColor=white" alt="LinkedIn Badge"/>
  </a>
  <a href="https://www.messenger.com/t/mr.thinh.ueh">
    <img src="https://img.shields.io/badge/Messenger-00B2FF?style=for-the-badge&logo=messenger&logoColor=white" alt="Messenger Badge"/>
  <a href="https://www.youtube.com/channel/UCYgG-bmk92OhYsP20TS0MbQ">
    <img src="https://img.shields.io/badge/YouTube-red?style=for-the-badge&logo=youtube&logoColor=white" alt="Youtube Badge"/>
  </a>
  </a>
    <a href="https://github.com/thinh-vu">
    <img src="https://img.shields.io/badge/GitHub-100000?style=for-the-badge&logo=github&logoColor=white" alt="Github Badge"/>
  </a>
</div>

# V. 💪 Hỗ trợ phát triển dự án vnstock

Nếu bạn nhận thấy giá trị từ vnstock và các dự án mã nguồn mở của tôi, bạn có thể hỗ trợ phát triển chúng bằng cách quyên góp hoặc đơn giản là gửi tặng tôi một ly cà phê để cảm ơn.
Bạn có thể chọn 1 trong 3 hình thức đóng góp bao gồm Momo, Chuyển khoản ngân hàng và Gửi tiền qua Paypal. Sự đóng góp của bạn sẽ giúp tôi duy trì phí lưu trữ blog và tiếp tục tạo ra nội dung chất lượng cao. Cảm ơn sự ủng hộ của bạn!

- [Paypal](https://paypal.me/thinhvuphoto?country.x=VN&locale.x=en_US)
- ![momo-qr](https://raw.githubusercontent.com/thinh-vu/vnstock/beta/src/momo-qr-thinhvu.jpeg)
- ![vcb-qr](https://raw.githubusercontent.com/thinh-vu/vnstock/beta/src/vcb-qr-thinhvu.jpg)

# VI. ⚖ Tuyên bố miễn trừ trách nhiệm
vnstock được phát triển nhằm mục đích cung cấp các công cụ nghiên cứu đơn giản và miễn phí, nhằm giúp người nghiên cứu tiếp cận và phân tích dữ liệu chứng khoán một cách dễ dàng. Dữ liệu được cung cấp phụ thuộc vào nguồn cấp dữ liệu, do đó, khi sử dụng, bạn cần thận trọng và cân nhắc.

💰 Trong bất kỳ trường hợp nào, người sử dụng hoàn toàn chịu trách nhiệm về quyết định sử dụng dữ liệu trích xuất từ vnstock và chịu trách nhiệm với bất kỳ tổn thất nào có thể phát sinh. Bạn nên tự mình đảm bảo tính chính xác và đáng tin cậy của dữ liệu trước khi sử dụng chúng.

Việc sử dụng dữ liệu chứng khoán và quyết định đầu tư là hoạt động có rủi ro và có thể gây mất mát tài sản. Bạn nên tìm kiếm lời khuyên từ các chuyên gia tài chính và tuân thủ các quy định pháp luật về chứng khoán tại Việt Nam và quốc tế khi tham gia vào hoạt động giao dịch chứng khoán.

Xin lưu ý rằng vnstock không chịu trách nhiệm và không có bất kỳ trách nhiệm pháp lý nào đối với bất kỳ tổn thất hoặc thiệt hại nào phát sinh từ việc sử dụng gói phần mềm này.

🐱‍👤 vnstock được thiết kế hoàn toàn cho mục đích phân tích và thực hành nghiên cứu đầu tư. Mọi hình thức sử dụng không đúng mục đích hoặc việc sử dụng trái phép thư viện với mục đích xấu như tấn công public API hay gây hại cho hệ thống thông qua từ chối truy cập hoặc các hành động tương tự, hoàn toàn nằm ngoài phạm vi sử dụng dự định và không thuộc trách nhiệm của nhóm phát triển.

## VII. Bản quyền và giấy phép


```
Bản quyền (c) 2022 Thinh Vu | thinh-vu @ Github | MIT

Được cấp phép theo quyền tự do, miễn phí, cho bất kỳ cá nhân nào nhận được một bản sao của phần mềm này và các tệp tài liệu liên quan (gọi chung là "Phần mềm"), để sử dụng Phần mềm mà không có bất kỳ hạn chế nào, bao gồm nhưng không giới hạn quyền sử dụng, sao chép, sửa đổi, hợp nhất, xuất bản, phân phối, cấp phép lại và/hoặc bán các bản sao của Phần mềm, và cho phép những người nhận Phần mềm được nhúng vào Phần mềm này, tuân thủ các điều kiện sau đây:

Thông báo bản quyền trên và thông báo giấy phép này phải được bao gồm trong tất cả các bản sao hoặc phần quan trọng của Phần mềm.

PHẦN MỀM ĐƯỢC CUNG CẤP "NHƯ NÓ LÀ", KHÔNG BẢO ĐẢM BẤT KỲ LOẠI NÀO, BAO GỒM NHƯNG KHÔNG GIỚI HẠN ĐẾN SỰ BẢO ĐẢM VỀ CHẤT LƯỢNG KINH DOANH, PHÙ HỢP VỚI MỤC ĐÍCH CỤ THỂ VÀ VI PHẠM QUYỀN SỞ HỮU. TRONG MỌI TRƯỜNG HỢP, TÁC GIẢ HOẶC CHỦ SỞ HỮU BẢN QUYỀN KHÔNG CHỊU TRÁCH NHIỆM ĐỐI VỚI BẤT KỲ YÊU CẦU BỒI THƯỜNG, THIỆT HẠI HOẶC TRÁCH NHIỆM PHÁP LÝ NÀO PHÁT SINH TỪ HOẶC LIÊN QUAN ĐẾN SỬ DỤNG HOẶC HIỆN HỮU CỦA PHẦN MỀM.
