# So sánh cổ phiếu tiềm năng
## Bảng giá

!!! tip  "Gợi ý"
    Bạn có thể tải xuống bảng giá của một danh sách các cổ phiếu được chọn để phân tích, thiết lập thuật toán dễ dàng hơn (khi xuất ra Google Sheets/Excel) so với việc xem trực tiếp trên bảng giá của các công ty chứng khoán.

Minh họa Bảng giá TCBS

![](../assets/images/tcbs_trading_board_sector.png)

### Thông tin bước giá, khối lượng và khớp lệnh
```python
price_depth('TCB,SSI,VND')
```
Sử dụng hàm này cho phép thống kê các bước giá và khối lượng trên bảng giá của một hoặc một danh sách các mã cổ phiếu. Bạn có thể sử dụng kết hợp hàm này với hàm **price_board** để kết hợp các thông tin đa dạng về giá, khối lượng, chỉ số, thông tin giao dịch để chọn lọc và theo dõi cổ phiếu theo mục đích sử dụng của mình.

- Kết quả:

```shell
  >>> price_depth('TCB,SSI,VND')
  Mã CP  Giá tham chiếu  Giá Trần  Giá Sàn  Giá mua 3 KL mua 3  Giá mua 2 KL mua 2  Giá mua 1  ... KL bán 1  Giá bán 2  KL bán 2  Giá bán 3 KL bán 3  Tổng Khối Lượng ĐTNN Mua  ĐTNN Bán  ĐTNN Room
0   TCB           31950     34150    29750      31900       10      31850      130      31800  ...     9240      32000     19940      32049     7750           447200        0         0          0     
1   SSI           28400     30350    26450      28450      100      28400     9850      28350  ...    30640      28550     22730      28600    48410          1610280   142759     17353  803963854     
2   VND           17950     19200    16700      18450    11620      18400    38790      18350  ...    73180      18550     87830      18600   223700          4360710   152966      8355  932083910     

[3 rows x 22 columns]
```

### Thông tin giao dịch

```python
price_board('TCB,SSI,VND')
```
Hàm này cho phép tải về thông tin giá, khối lượng và các chỉ số quan trọng cho một hoặc một danh sách mã cổ phiếu. Sử dụng kết hợp với hàm **price_depth** cho hiệu quả tốt nhất.

- Kết quả:

```shell
>>> price_board('TCB,SSI,VND')

Mã CP  Giá Khớp Lệnh  KLBD/TB5D  T.độ GD  KLGD ròng(CM)  ...  vnid1m  vnid3m  vnid1y  vnipe    vnipb
0   TCB        48600.0        0.6     0.49         -23200  ...    -3.7    -2.0    22.4  17.99  2.46159
1   SSI        43300.0        0.5     0.50        -112200  ...    -3.7    -2.0    22.4  17.99  2.46159
2   VND        32600.0        0.7     0.68          37300  ...    -3.7    -2.0    22.4  17.99  2.46159
```

## Phân tích chỉ số các cổ phiếu cùng ngành

```python
industry_analysis("VNM", lang='vi')
```
- Trả về thông tin các mã cổ phiếu cùng ngành với mã cổ phiếu nằm trong cùng nhóm ngành với mã **VNM**.
- Tham số **lang='vi** mặc định trả về tên các chỉ số bằng tiếng Việt, đổi thành **en** để giữ nguyên chỉ số với tên tiếng Anh.

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

## So sánh chỉ số của danh sách cổ phiếu tùy chọn
```python
stock_ls_analysis("TCB, BID, CEO, GMD", lang='vi')
```

- Kết quả:

```shell
  ticker  marcap  price  numberOfDays  priceToEarning  peg  priceToBook  valueBeforeEbitda  dividend  ...  debtOnEbitda  income5year  sale5year income1quarter  sale1quarter  nextIncome  nextSale   rsi    rs
0    GMD   15220  50500            -3            25.2  0.4          2.4               16.2       0.0  ...           1.8        0.092     -0.030          0.500         0.425         NaN       NaN  60.3  50.0
1    CEO   17062  66300             1           183.2 -0.8          5.7               81.8       0.0  ...           7.8       -0.099     -0.086            NaN         3.002      -1.469      -0.2  51.9  82.0
2    BID  225357  44550            -3            21.3  0.4          2.6                NaN       0.0  ...           NaN        0.115      0.154          0.083         0.000         NaN       NaN  49.1  34.0
3    TCB  178003  50700             1             9.9  0.2          1.9                NaN       0.0  ...           NaN        0.418      0.255          0.059         0.157         NaN       NaN  45.2  28.0
```