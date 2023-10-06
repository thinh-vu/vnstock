---
title: Giao dịch thông minh
sections:
  - Lựa chọn cổ phiếu
  - Dữ liệu khớp lệnh
---

## Lựa chọn cổ phiếu (Stock Screening)

### So sánh các cổ phiếu tiềm năng

#### Bảng giá (Price board)

Bạn có thể tải xuống bảng giá của một danh sách các cổ phiếu được chọn để phân tích, thiết lập thuật toán dễ dàng hơn (khi xuất ra Google Sheets/Excel) so với việc xem trực tiếp trên bảng giá của các công ty chứng khoán.

- Minh họa Bảng giá TCBS

  <div class="price_board">
   <a href="assets/images/tcbs_trading_board_sector.png?raw=true" data-title="Minh họa bảng giá TCBS" data-toggle="lightbox"><img class="img-responsive" src="assets/images/tcbs_trading_board_sector.png?raw=true" alt="screenshot" /></a>
   <a class="mask" href="assets/images/tcbs_trading_board_sector.png?raw=true" data-title="Minh họa bảng giá TCBS" data-toggle="lightbox"><i class="icon fa fa-search-plus"></i></a>
  </div>

##### a. Thông tin bước giá, khối lượng và khớp lệnh

```python
price_depth('TCB,SSI,VND')
```
Sử dụng hàm này cho phép thống kê các bước giá và khối lượng trên bảng giá của một hoặc một danh sách các mã cổ phiếu. Bạn có thể sử dụng kết hợp hàm này với hàm `price_board` để kết hợp các thông tin đa dạng về giá, khối lượng, chỉ số, thông tin giao dịch để chọn lọc và theo dõi cổ phiếu theo mục đích sử dụng của mình.

- Kết quả:

```shell
  >>> price_depth('TCB,SSI,VND')
  Mã CP  Giá tham chiếu  Giá Trần  Giá Sàn  Giá mua 3 KL mua 3  Giá mua 2 KL mua 2  Giá mua 1  ... KL bán 1  Giá bán 2  KL bán 2  Giá bán 3 KL bán 3  Tổng Khối Lượng ĐTNN Mua  ĐTNN Bán  ĐTNN Room
0   TCB           31950     34150    29750      31900       10      31850      130      31800  ...     9240      32000     19940      32049     7750           447200        0         0          0     
1   SSI           28400     30350    26450      28450      100      28400     9850      28350  ...    30640      28550     22730      28600    48410          1610280   142759     17353  803963854     
2   VND           17950     19200    16700      18450    11620      18400    38790      18350  ...    73180      18550     87830      18600   223700          4360710   152966      8355  932083910     

[3 rows x 22 columns]
```

##### b. Thông tin giao dịch bổ sung và các chỉ số

```python
price_board('TCB,SSI,VND')
```
Hàm này cho phép tải về thông tin giá, khối lượng và các chỉ số quan trọng cho một hoặc một danh sách mã cổ phiếu. Sử dụng kết hợp với hàm `price_depth` cho hiệu quả tốt nhất.

- Kết quả:

```shell
>>> price_board('TCB,SSI,VND')

Mã CP  Giá Khớp Lệnh  KLBD/TB5D  T.độ GD  KLGD ròng(CM)  ...  vnid1m  vnid3m  vnid1y  vnipe    vnipb
0   TCB        48600.0        0.6     0.49         -23200  ...    -3.7    -2.0    22.4  17.99  2.46159
1   SSI        43300.0        0.5     0.50        -112200  ...    -3.7    -2.0    22.4  17.99  2.46159
2   VND        32600.0        0.7     0.68          37300  ...    -3.7    -2.0    22.4  17.99  2.46159
```

#### Phân tích chỉ số các cổ phiếu cùng ngành (Industry Analysis)

```python
industry_analysis("VNM", lang='vi)
```
- Trả về thông tin các mã cổ phiếu cùng ngành với mã cổ phiếu nằm trong cùng nhóm ngành với mã `VNM`.
- Tham số `lang='vi` mặc định trả về tên các chỉ số bằng tiếng Việt, đổi thành `en` để giữ nguyên chỉ số với tên tiếng Anh.

- Trong đó các chỉ số sau được thể hiện dưới dạng thập phân sử dụng để thể hiện chỉ số dưới dạng %: 
  ```dividend (Cổ tức), ROE, ROA, ebitOnInterest (Thanh toán lãi vay), currentPayment (Thanh toán hiện hành), quickPayment (Thanh toán nhanh), grossProfitMargin (Biên LNG), postTaxMargin (Biên LNST), badDebtPercentage (Tỉ lệ nợ xấu), debtOnEquity (Nợ/Vốn CSH), debtOnEbitda (Nợ/EBITDA), income5year (LNST 5 năm),  sale5year (Doanh thu 5 năm), income1quarter (LNST quý gần nhất), sale1quarter (Doanh thu quý gần nhất), nextIncome (LNST năm tới), nextSale (Doanh thu quý tới)```
- Lưu ý: Tên các column có thể chưa được chuyển đổi đầy đủ thành tiếng Việt. Nếu gặp chỉ số nào chưa được chuyển đổi tên thành tiếng Việt, bạn vui lòng comment cho tác giả nhé.

- Kết quả:

```shell
>>> industry_analysis('VNM', label='vi')
Mã CP                          VNM     MSN    MCH    QNS    KDC     IDP    SBT    MML    PAN    MCM    VSF    VOC    OCH    VSN    CLX    LSS     KTC    HSL    HKB
Vốn hóa (tỷ)                  None  107634  51307  17543  16102   13204  11478  10108   4303   4232   3979   2890   1680   1618   1274    932     383    219     46
Giá                           None   75600  71603  49149  62600  224000  15500  30900  20600  38473   7958  23727   8400  19994  14713  12500   10500   6180    900
Số phiên tăng/giảm liên tiếp  None       3      2      4      0      -3      3      1     -1      1     -2      0      0      0      1      3       0     -1      0
P/E                            NaN    49.2    9.1   12.3 -215.9    16.7   16.6  -18.7   13.2   11.7 -384.1    2.4   15.2   11.9    7.1   23.5    37.3   14.6   -0.8
PEG                            NaN    -0.6   -8.0    0.9    1.9    -1.6   -1.4    0.1   -1.9    5.9    4.0    0.0   -0.1   -1.6    1.1    2.2    -0.8    0.8    0.5
P/B                            NaN     4.1    2.2    2.3    2.5     6.5    1.2    1.9    1.0    1.8    1.7    1.1    1.3    1.2    0.8    0.6     1.0    0.5    0.2
EV/EBITDA                      NaN    20.0    8.2   10.4   36.1    13.1   13.7 -267.0    7.2   11.4   25.9   -8.9    6.3    8.3   10.5    6.5    20.0   12.8   -3.1
Cổ tức                         NaN   0.009    0.0    0.0  0.086   0.033    0.0    0.0    0.0    0.0    0.0    0.0    0.0    0.0    0.0    0.0     0.0    0.0    0.0
ROE                            NaN   0.081  0.277  0.195 -0.011   0.442  0.076 -0.098  0.075  0.159 -0.005  0.591  0.086  0.107  0.118  0.025   0.025  0.036 -0.263
ROA                            NaN   0.016  0.175  0.128 -0.006    0.22  0.025 -0.042  0.021   0.14 -0.001  0.484  0.049  0.067  0.082  0.014   0.007  0.031  -0.15
Thanh toán lãi vay             NaN     0.5    9.1    8.5   -0.2    19.4    0.9   -0.8    1.3    NaN    0.3   -2.0   -3.2   67.7   22.1    2.2     0.9    6.9   -4.4
Thanh toán hiện hành           NaN     0.8    2.7    1.8    1.6     1.5    1.2    1.4    1.3    8.6    1.0    4.2    1.9    2.5    3.1    1.3     0.9    9.7    0.3
Thanh toán nhanh               NaN     0.6    2.5    1.4    1.2     1.3    0.9    1.1    0.9    7.7    0.4    3.4    1.7    1.7    2.9    0.3     0.5    8.6    0.3
Biên LNG                       NaN   0.272  0.432   0.28  0.188   0.385  0.115  0.117  0.171  0.323  0.067    NaN  0.286  0.247  0.264  0.121   0.035  0.039  0.728
Biên LNST                      NaN   0.011  0.228  0.149    NaN   0.138  0.026    NaN  0.016  0.138    NaN  6.467    NaN  0.039  0.372  0.017   0.004  0.024    NaN
Nợ/Vốn CSH                     NaN     2.0    0.3    0.4    0.6     0.4    1.3    1.0    0.7    0.0    1.5    0.1    0.1    0.0    0.0    0.4     2.3    0.0    0.5
Nợ/EBITDA                      NaN     7.6    1.1    1.5    8.1     0.7    7.2  -88.3    3.4    0.1   12.3   -1.1    0.7    1.1    0.4    2.6    15.5    0.8   -2.0
LNST 5 năm                     NaN   0.028  0.207  0.046  -0.04     NaN   0.12    NaN  0.001  0.098    NaN    NaN    NaN  0.012  0.065   -0.1  -0.157 -0.081    NaN
Doanh thu 5 năm                NaN   0.152  0.153  0.016  0.123     NaN   0.22 -0.239  0.274  0.049 -0.053 -0.181 -0.018 -0.002  0.088 -0.008   0.067   0.16 -0.474
LNST quý gần nhất              NaN  -0.519 -0.255 -0.258    NaN   0.316  0.443    NaN -0.694  0.397    NaN    NaN    NaN -0.131  0.092    NaN  36.983  -0.44    NaN
Doanh thu quý gần nhất         NaN  -0.094 -0.252  0.093 -0.302  -0.057 -0.181  0.031 -0.352 -0.067  -0.31 -0.675 -0.197 -0.134 -0.123  0.102  -0.122 -0.142  0.009
LNST năm tới                   NaN   0.285   0.26  0.173 -0.202   0.074  0.047 -0.719 -0.041   0.04 -0.939  0.116  6.025 -0.034   0.09 -0.155   0.813  0.022    NaN
Doanh thu năm tới              NaN     0.2    0.3  0.162  0.283     0.1    0.1   -0.7   0.05   0.05   0.03   0.15   -0.5    0.1    0.3  -0.08   -0.06   0.02    NaN
RSI                            NaN    50.7   43.1   71.8   24.0    28.5   59.2   33.7   68.2   53.5   46.6   44.1   51.1   32.3   55.5   55.3    33.3   54.8   61.1
```

#### So sánh các chỉ số của danh sách các cổ phiếu tùy chọn

```python
stock_ls_analysis("TCB, BID, CEO, GMD", lang='vi')
```

  <div class="stock_ls_comparison">
   <a href="assets/images/stock_ls_comparison.png?raw=true" data-title="So sánh chỉ số của các mã CP" data-toggle="lightbox"><img class="img-responsive" src="assets/images/stock_ls_comparison.png?raw=true" alt="screenshot" /></a>
   <a class="mask" href="assets/images/stock_ls_comparison.png?raw=true" data-title="So sánh chỉ số của các mã CP" data-toggle="lightbox"><i class="icon fa fa-search-plus"></i></a>
  </div>

- Kết quả:

```shell
  ticker  marcap  price  numberOfDays  priceToEarning  peg  priceToBook  valueBeforeEbitda  dividend  ...  debtOnEbitda  income5year  sale5year income1quarter  sale1quarter  nextIncome  nextSale   rsi    rs
0    GMD   15220  50500            -3            25.2  0.4          2.4               16.2       0.0  ...           1.8        0.092     -0.030          0.500         0.425         NaN       NaN  60.3  50.0
1    CEO   17062  66300             1           183.2 -0.8          5.7               81.8       0.0  ...           7.8       -0.099     -0.086            NaN         3.002      -1.469      -0.2  51.9  82.0
2    BID  225357  44550            -3            21.3  0.4          2.6                NaN       0.0  ...           NaN        0.115      0.154          0.083         0.000         NaN       NaN  49.1  34.0
3    TCB  178003  50700             1             9.9  0.2          1.9                NaN       0.0  ...           NaN        0.418      0.255          0.059         0.157         NaN       NaN  45.2  28.0
```

#### Đánh giá xếp hạng 
##### Đánh giá chung

  <div class="general_rating">
   <a href="assets/images/general_rating.jpeg?raw=true" data-title="Đánh giá chung" data-toggle="lightbox"><img class="img-responsive" src="assets/images/general_rating.jpeg?raw=true" alt="screenshot" /></a>
   <a class="mask" href="assets/images/general_rating.jpeg?raw=true" data-title="Đánh giá chung" data-toggle="lightbox"><i class="icon fa fa-search-plus"></i></a>
  </div>

```python
general_rating("VNM")
```

- Kết quả:

```shell
   stockRating  valuation  financialHealth  businessModel  businessOperation  rsRating  taScore  ... ticker highestPrice  lowestPrice  priceChange3m  priceChange1y  beta   alpha
0          2.4        1.5              4.8            3.0                3.2       1.0      1.0  ...    VNM     102722.2      78600.0         -0.092         -0.232  0.49 -0.0014
```


##### Đánh giá mô hình kinh doanh

```python
biz_model_rating("VNM")
```

- Kết quả:

```shell
  ticker  businessModel  businessEfficiency  assetQuality  cashFlowQuality  bom  businessAdministration  productService  businessAdvantage  companyPosition  industry  operationRisk
0    VNM            3.0                   3             3                3    3                       3               3                  3                3         3              3
```


##### Đánh giá hiệu quả hoạt động

```python
biz_operation_rating("VNM")
```

- Kết quả:

```shell
      industryEn loanGrowth depositGrowth netInterestIncomeGrowth netInterestMargin  ... last5yearsFCFFGrowth lastYearGrossProfitMargin lastYearOperatingProfitMargin  lastYearNetProfitMargin  TOIGrowth
0  Food Products       None          None                    None              None  ...                    2                         5                             3                        4       None
```

##### Đánh giá sức khỏe tài chính

```python
financial_health_rating("VNM")
```

- Kết quả:

```shell
      industryEn loanDeposit badLoanGrossLoan badLoanAsset provisionBadLoan ticker  financialHealth  netDebtEquity  currentRatio  quickRatio  interestCoverage  netDebtEBITDA
0  Food Products        None             None         None             None    VNM              4.8              4             5           5                 5              5
```


##### Đánh giá về Định giá

```python
valuation_rating("VNM")
```

- Kết quả:

```
      industryEn ticker  valuation  pe  pb  ps  evebitda  dividendRate
0  Food Products    VNM        1.5   2   1   1         1             3
```

##### Sức khỏe tài chính theo ngành

```python
industry_financial_health("VNM")
```

- Kết quả:

```shell
  industryEn loanDeposit badLoanGrossLoan badLoanAsset provisionBadLoan ticker  financialHealth  netDebtEquity  currentRatio  quickRatio  interestCoverage  netDebtEBITDA
0       None        None             None         None             None    VNM              3.4              4             4           3                 3              3
```

### Bộ lọc cổ phiếu

Bộ lọc cổ phiếu là một hàm cho phép bạn truy vấn và lọc các cổ phiếu theo nhiều tiêu chí đa dạng dựa trên dữ liệu phân tích của TCBS. Hàm này sẽ trả về một DataFrame chứa các thông tin toàn diện về các cổ phiếu thỏa mãn điều kiện lọc của bạn. Bạn có thể dùng DataFrame này để tiếp tục phân tích, biểu diễn hoặc xuất ra dữ liệu dạng bảng tính. Đây là cập nhật ưu việt giúp bạn tiết kiệm thời gian và công sức đáng kể khi làm việc với dữ liệu cổ phiếu, đồng thời cho phép lập trình để lọc là cập nhật danh sách cổ phiếu hiệu quả không cần sử dụng giao diện web từ công ty chứng khoán.

- Bộ lọc cổ phiếu TCBS

  <div class="stock_scanner">
   <a href="assets/images/stock_ls_comparison.png?raw=true" data-title="Bộ lọc cổ phiếu TCBS" data-toggle="lightbox"><img class="img-responsive" src="assets/images/stock_ls_comparison.png?raw=true" alt="screenshot" /></a>
   <a class="mask" href="assets/images/stock_ls_comparison.png?raw=true" data-title="Bộ lọc cổ phiếu TCBS" data-toggle="lightbox"><i class="icon fa fa-search-plus"></i></a>
  </div>


Tham số
- params (dict): một từ điển chứa các tham số và giá trị của chúng cho việc lọc cổ phiếu. Các **key** là tên của các bộ lọc, và các **value** là một giá trị đơn hoặc một tupple gồm hai giá trị (min và max) cho bộ lọc đó. Đây là ví dụ cho tham số params được thiết lập đúng:
- drop_lang: Loại bỏ các cột dữ liệu sử dụng tên tiếng Việt (**vi**) hoặc Anh (**en**)

```python
params = {
            "exchangeName": "HOSE,HNX,UPCOM",
            "marketCap": (100, 1000),
            "dividendYield": (5, 10)
        }
```

# Áp dụng bộ lọc với hàm để lấy kết quả

```
df = stock_screening_insights (params, size=1700, drop_lang='vi')
```

<details>

  <summary>Các bộ lọc gợi ý và tiêu chí hỗ trợ</summary>

    a. BỘ LỌC GỢI Ý (PRESET)

      > Sử dụng các tiêu chí lọc như sau để thiết lập tham số params.

      - CANSLIM: epsGrowth1Year, lastQuarterProfitGrowth, roe, avgTradingValue20Day, relativeStrength1Month
      - Giá trị: roe, pe, avgTradingValue20Day
      - Cổ tức cao: dividendYield, avgTradingValue20Day
      - Phá nền mua: avgTradingValue20Day, forecastVolumeRatio, breakout: 'BULLISH'
      - Giá tăng + Đột biến khối lượng: avgTradingValue20Day, forecastVolumeRatio
      - Vượt đỉnh 52 tuần: avgTradingValue20Day, priceBreakOut52Week: 'BREAK_OUT'
      - Phá đáy 52 tuần: avgTradingValue20Day, priceWashOut52Week: 'WASH_OUT'
      - Uptrend ngắn hạn: avgTradingValue20Day, uptrend: 'buy-signal'
      - Vượt trội ngắn hạn: relativeStrength3Day, 
      - Tăng trưởng: epsGrowth1Year, roe, avgTradingValue20Day

    b. THÔNG TIN CHUNG

      - exchangeName: sàn giao dịch của cổ phiếu, ví dụ "HOSE", "HNX", hoặc "UPCOM". Bạn có thể dùng dấu phẩy để phân tách nhiều sàn, ví dụ "HOSE,HNX,UPCOM".
      - hasFinancialReport: Có báo cáo tài chính gần nhất. **1** nghĩa là có, **0** nghĩa là không.
      - industryName: Lọc các cổ phiếu theo ngành cụ thể. Giá trị dạng **Retail** cho ngành Bán lẻ. Các giá trị khác có thể là:
        - **Insurance**: Bảo hiểm
        - **Real Estate**: Bất động sản
        - **Technology**: Công nghệ thông tin
        - **Oil & Gas**: Dầu khí
        - **Financial Services**: Dịch vụ tài chính
        - **Utilities**: Điện, nước, xăng dầu và khí đốt
        - **Travel & Leisure**: Du lịch và giải trí
        - **Industrial Goods & Services**: Hàng và dịch vụ công nghiệp
        - **Personal & Household Goods**: Hàng cá nhân và gia dụng
        - **Chemicals**: Hóa chất
        - **Banks**: Ngân hàng
        - **Automobiles & Parts**: Ô tô và phụ tùng
        - **Basic Resources**: Tài nguyên cơ bản
        - **Food & Beverage**: Thực phẩm và đồ uống
        - **Media**: Truyền thông
        - **Telecommunications**: Viễn thông
        - **Construction & Materials**: Xây dựng và vật liệu
        - **Health Care**: Y tế
        - marketCap: vốn hóa thị trường của cổ phiếu tính bằng tỷ VND.
        - priceNearRealtime: giá hiện tại của cổ phiếu tính bằng VND.
        - foreignVolumePercent: tỷ lệ phần trăm khối lượng nước ngoài trong tổng khối lượng.
        - alpha: lợi nhuận vượt trội của cổ phiếu so với lợi nhuận thị trường.
        - beta: độ biến động của cổ phiếu so với thị trường.
        - freeTransferRate: tỷ lệ phần trăm cổ phiếu có thể chuyển nhượng tự do.

    c. TĂNG TRƯỞNG

      - revenueGrowth1Year: tốc độ tăng trưởng doanh thu trong năm qua.
      - revenueGrowth5Year: tốc độ tăng trưởng doanh thu trung bình trong 5 năm qua.
      - epsGrowth1Year: tốc độ tăng trưởng lợi nhuận trên mỗi cổ phiếu trong năm qua.
      - epsGrowth5Year: tốc độ tăng trưởng lợi nhuận trên mỗi cổ phiếu trung bình trong 5 năm qua.
      - lastQuarterRevenueGrowth: tốc độ tăng trưởng doanh thu trong quý gần nhất.
      - secondQuarterRevenueGrowth: tốc độ tăng trưởng doanh thu trong quý thứ hai.
      - lastQuarterProfitGrowth: tốc độ tăng trưởng lợi nhuận trong quý gần nhất.
      - secondQuarterProfitGrowth: tốc độ tăng trưởng lợi nhuận trong quý thứ hai.

    d. CHỈ SỐ TÀI CHÍNH

      - grossMargin: tỷ suất lợi nhuận gộp của cổ phiếu.
      - netMargin: tỷ suất lợi nhuận ròng của cổ phiếu.
      - roe: tỷ suất sinh lời về vốn chủ sở hữu của cổ phiếu.
      - doe: tỷ suất cổ tức về vốn chủ sở hữu của cổ phiếu.
      - dividendYield: tỷ suất cổ tức của cổ phiếu.
      - eps: lợi nhuận trên mỗi cổ phiếu của cổ phiếu tính bằng VND.
      - pe: tỷ số giá/lợi nhuận của cổ phiếu.
      - pb: tỷ số giá/giá trị sổ sách của cổ phiếu.
      - evEbitda: tỷ số giá trị doanh nghiệp/lợi nhuận trước thuế, lãi vay, khấu hao và amortization của cổ phiếu.
      - netCashPerMarketCap: tỷ số tiền mặt ròng/vốn hóa thị trường của cổ phiếu.
      - netCashPerTotalAssets: tỷ số tiền mặt ròng/tổng tài sản của cổ phiếu.
      - profitForTheLast4Quarters: tổng lợi nhuận trong 4 quý gần nhất của cổ phiếu tính bằng tỷ VND.

    e. BIẾN ĐỘNG GIÁ & KHỐI LƯỢNG

      - suddenlyHighVolumeMatching: tín hiệu chỉ ra nếu có sự tăng đột biến khối lượng khớp lệnh cho cổ phiếu này. 0 nghĩa là không, 1 nghĩa là có.
      - totalTradingValue: tổng giá trị giao dịch của cổ phiếu này tính bằng tỷ VND hôm nay.
      - avgTradingValue5Day: giá trị giao dịch trung bình của cổ phiếu này tính bằng tỷ VND trong 5 ngày.
      - avgTradingValue10Day: giá trị giao dịch trung bình của cổ phiếu này tính bằng tỷ VND trong 10 ngày.
      - avgTradingValue20Day: giá trị giao dịch trung bình của cổ phiếu này tính bằng tỷ VND trong 20 ngày.
      - priceGrowth1Week: tốc độ tăng trưởng giá của cổ phiếu trong tuần qua.
      - priceGrowth1Month: tốc độ tăng trưởng giá của cổ phiếu trong tháng qua.
      - percent1YearFromPeak: tỷ lệ phần trăm thay đổi của cổ phiếu từ giá cao nhất trong 1 năm.
      - percentAwayFromHistoricalPeak: tỷ lệ phần trăm thay đổi của cổ phiếu từ giá cao nhất lịch sử.
      - percent1YearFromBottom: tỷ lệ phần trăm thay đổi của cổ phiếu từ giá thấp nhất trong 1 năm.
      - percentOffHistoricalBottom: tỷ lệ phần trăm thay đổi của cổ phiếu từ giá thấp nhất lịch sử.
      - priceVsSMA5: mối quan hệ giữa giá hiện tại và SMA 5 ngày của cổ phiếu. Các giá trị có thể là "ABOVE", "BELOW", "CROSS_ABOVE", hoặc "CROSS_BELOW".
      - priceVsSma10: mối quan hệ giữa giá hiện tại và SMA 10 ngày của cổ phiếu. Các giá trị có thể là "ABOVE", "BELOW", "CROSS_ABOVE", hoặc "CROSS_BELOW".
      - priceVsSMA20: mối quan hệ giữa giá hiện tại và SMA 20 ngày của cổ phiếu. Các giá trị có thể là "ABOVE", "BELOW", "CROSS_ABOVE", hoặc "CROSS_BELOW".
      - priceVsSma50: mối quan hệ giữa giá hiện tại và SMA 50 ngày của cổ phiếu. Các giá trị có thể là "ABOVE", "BELOW", "CROSS_ABOVE", hoặc "CROSS_BELOW".
      - priceVsSMA100: mối quan hệ giữa giá hiện tại và SMA 100 ngày của cổ phiếu. Các giá trị có thể là "ABOVE", "BELOW", "CROSS_ABOVE", hoặc "CROSS_BELOW".
      - forecastVolumeRatio: tỷ số giữa khối lượng dự báo và khối lượng thực tế của cổ phiếu hôm nay.
      - volumeVsVSma5: tỷ số giữa khối lượng hiện tại và SMA khối lượng 5 ngày của cổ phiếu.
      - volumeVsVSma10: tỷ số giữa khối lượng hiện tại và SMA khối lượng 10 ngày của cổ phiếu.
      - volumeVsVSma20: tỷ số giữa khối lượng hiện tại và SMA khối lượng 20 ngày của cổ phiếu.
      - volumeVsVSma50: tỷ số giữa khối lượng hiện tại và SMA khối lượng 50 ngày của cổ phiếu.

    f. HÀNH VI THỊ TRƯỜNG

      - strongBuyPercentage: tỷ lệ phần trăm tín hiệu mua mạnh cho cổ phiếu này dựa trên phân tích kỹ thuật.
      - activeBuyPercentage: tỷ lệ phần trăm tín hiệu mua tích cực cho cổ phiếu này dựa trên phân tích kỹ thuật.
      - foreignTransaction: loại giao dịch nước ngoài cho cổ phiếu này hôm nay. Các giá trị có thể là "buyMoreThanSell", "sellMoreThanBuy", hoặc "noTransaction".
      - foreignBuySell20Session: giá trị mua bán ròng nước ngoài cho cổ phiếu này tính bằng tỷ VND trong 20 phiên.
      - numIncreaseContinuousDay: số ngày liên tiếp cổ phiếu này tăng giá.
      - numDecreaseContinuousDay: số ngày liên tiếp cổ phiếu này giảm giá.

    g. TÍN HIỆU KỸ THUẬT

      - rsi14: chỉ số sức mạnh tương đối (RSI) của cổ phiếu với chu kỳ 14 ngày.
      - rsi14Status: trạng thái của RSI cho cổ phiếu này. Các giá trị có thể là "intoOverBought", "intoOverSold", "outOfOverBought", hoặc "outOfOverSold".
      - tcbsBuySellSignal: tín hiệu mua bán cho cổ phiếu này dựa trên phân tích của TCBS. Các giá trị có thể là "BUY" hoặc "SELL".
      - priceBreakOut52Week: tín hiệu chỉ ra nếu có sự đột phá giá cho cổ phiếu này trong 52 tuần. Các giá trị có thể là "BREAK_OUT" hoặc "NO_BREAK_OUT".
      - priceWashOut52Week: tín hiệu chỉ ra nếu có sự rửa giá cho cổ phiếu này trong 52 tuần. Các giá trị có thể là "WASH_OUT" hoặc "NO_WASH_OUT".
      - macdHistogram: tín hiệu chỉ ra nếu có tín hiệu MACD histogram cho cổ phiếu này. Các giá trị có thể là "macdHistGT0Increase", "macdHistGT0Decrease", "macdHistLT0Increase", hoặc "macdHistLT0Decrease".
      - relativeStrength3Day: sức mạnh tương đối của cổ phiếu so với thị trường trong 3 ngày.
      - relativeStrength1Month: sức mạnh tương đối của cổ phiếu so với thị trường trong 1 tháng.
      - relativeStrength3Month: sức mạnh tương đối của cổ phiếu so với thị trường trong 3 tháng.
      - relativeStrength1Year: sức mạnh tương đối của cổ phiếu so với thị trường trong 1 năm.
      - tcRS: sức mạnh tương đối của TCBS của cổ phiếu so với thị trường.
      - sarVsMacdHist: tín hiệu chỉ ra nếu có tín hiệu SAR vs MACD histogram cho cổ phiếu này. Các giá trị có thể là "BUY" hoặc "SELL".

    h. TÍN HIỆU MUA/BÁN

      - bollingBandSignal: tín hiệu chỉ ra nếu có tín hiệu Bollinger Band cho cổ phiếu này. Các giá trị có thể là "BUY" hoặc "SELL".
      - dmiSignal: tín hiệu chỉ ra nếu có tín hiệu chỉ số chuyển động hướng (DMI) cho cổ phiếu này. Các giá trị có thể là "BUY" hoặc "SELL".
      - uptrend: tín hiệu chỉ ra nếu có tín hiệu xu hướng tăng cho cổ phiếu này. Các giá trị có thể là "buy-signal" hoặc "sell-signal".
      - breakout: tín hiệu chỉ ra nếu có tín hiệu đột phá cho cổ phiếu này. Các giá trị có thể là "BULLISH" hoặc "BEARISH".

    i. TCBS ĐÁNH GIÁ

      - tcbsRecommend: tín hiệu chỉ ra nếu có khuyến nghị của TCBS cho cổ phiếu này. Các giá trị có thể là "BUY" hoặc "SELL".
      - stockRating: điểm đánh giá cổ phiếu cho cổ phiếu này dựa trên phân tích của TCBS. Điểm từ 1 đến 5, với 5 là tốt nhất.
      - businessModel: điểm đánh giá mô hình kinh doanh cho cổ phiếu này dựa trên phân tích của TCBS. Điểm từ 1 đến 5, với 5 là tốt nhất.
      - businessOperation: điểm đánh giá hoạt động kinh doanh cho cổ phiếu này dựa trên phân tích của TCBS. Điểm từ 1 đến 5, với 5 là tốt nhất.
      - financialHealth: điểm đánh giá sức khỏe tài chính cho cổ phiếu này dựa trên phân tích của TCBS. Điểm từ 1 đến 5, với 5 là tốt nhất.

</details>

## Dữ liệu khớp lệnh trong ngày giao dịch

<details>
  <summary>Minh hoạ giao diện TCBS</summary>

  <div class="intraday_1">
   <a href="assets/images/tcbs_intraday_screen1.png?raw=true" data-title="hình chụp 1" data-toggle="lightbox"><img class="img-responsive" src="assets/images/tcbs_intraday_screen1.png?raw=true" alt="screenshot" /></a>
   <a class="mask" href="assets/images/tcbs_intraday_screen1.png?raw=true" data-title="hình chụp 1" data-toggle="lightbox"><i class="icon fa fa-search-plus"></i></a>
  </div>

    <div class="intraday_2">
   <a href="assets/images/tcbs_intraday_screen2.png?raw=true" data-title="hình chụp 2" data-toggle="lightbox"><img class="img-responsive" src="assets/images/tcbs_intraday_screen2.png?raw=true" alt="screenshot" /></a>
   <a class="mask" href="assets/images/tcbs_intraday_screen2.png?raw=true" data-title="hình chụp 2" data-toggle="lightbox"><i class="icon fa fa-search-plus"></i></a>
  </div>

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

### Giải thích ý nghĩa chỉ số
• Khi 1 lệnh lớn (từ Cá mập, tay to, tổ chức....) mua chủ động (hoặc bán chủ động) được đưa vào Sàn, thường thì nó sẽ được khớp với nhiều lệnh nhỏ đang chờ bán (hoặc chờ mua). Nếu chỉ nhìn realtime theo từng lệnh khớp riêng lẻ, thì sẽ không thể phát hiện được các lệnh to (của Cá mập, tay to...) vừa được đẩy vào Sàn. Vì vậy, chúng tôi "cộng dồn" các lệnh khớp này lại (phát sinh bởi 1 lệnh lớn chủ động vào sàn trong 1 khoảng thời gian rất nhanh) để giúp NĐT phát hiện các lệnh lớn (của Cá mập, tay to....) chính xác hơn. Lệnh Cá mập sẽ được tô xanh (cho Mua chủ động) và đỏ (cho Bán chủ động). 

• Cá mập: (CM - SHARK) nhà đầu tư tay to, tổ chức, đầu tư lớn, dẫn dắt thị trường. Giá trị 1 lệnh đặt > 1 tỷ đồng/lệnh đặt. Đồ thị 1N dùng số liệu 1 phút cho 60’ gần nhất; 1W là tổng mỗi 15’ cho 1 tuần; 1M là tổng hàng ngày cho 1 tháng

• Sói già: (SG - WOLF) nhà đầu tư kinh nghiệm, giá trị lệnh đặt cao. Giá trị 1 lệnh đặt từ 200 tr đến 1 tỷ đồng/lệnh đặt.

• Cừu non: (CN - SHEEP) nhà đầu tư nhỏ lẻ, giá trị giao dịch và mua bán chủ động thấp. Giá trị 1 lệnh đặt Mua hoặc Bán chủ động < 200 triệu đồng/lệnh đặt vào.

• Mua chủ động (hay Buy Up) là khi NĐT thực hiện chủ động mua lên qua việc đặt lệnh mua với giá bằng giá dư bán gần nhất để có thể khớp luôn. Như thế, giá khớp cho lệnh này thường sẽ đẩy giá khớp lên cao hơn thị giá trước đó.

• Bán chủ động (hay Sell Down) là khi NĐT thực hiện chủ động Bán dưới giá hiện tại (hay thị giá) của cổ phiếu bằng việc đặt lệnh bán với giá bán bằng giá dư mua gần nhất để khớp ngay. Và như thế, thị giá sẽ bị kéo xuống thấp hơn so với thị giá trước đó. Thống kê khối lượng giao dich theo Mua CĐ và Bán CĐ dùng để đánh giá tương quan giữa cung (Bán CĐ) và cầu (Mua CĐ) trên giao dịch khớp lệnh thực tế, nhằm nhận định tương đối về sự vận động của xu hướng dòng tiền. Khi tỷ lệ % Mua CĐ trên (Tổng Mua và Bán CĐ) lớn hơn 50%, đồng nghĩa với việc thị trường đang có xu hướng mua vào nhiều hơn bán ra và ngược lại, qua đó xác định được dòng tiền vào/ra với mỗi cổ phiếu. Khi tỷ lệ này cao đột biến (>70% hay <30%) so với điểm cân bằng (50%) , đó là tín hiệu của việc mua hoặc bán bất chấp của thị trường.