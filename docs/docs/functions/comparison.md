# So sánh cổ phiếu tiềm năng
!!! tip  "Gợi ý"
    Bạn có thể tải xuống bảng giá của một danh sách các cổ phiếu được chọn để phân tích, thiết lập thuật toán dễ dàng hơn (khi xuất ra Google Sheets/Excel) so với việc xem trực tiếp trên bảng giá của các công ty chứng khoán.

## Bảng giá

Minh họa Bảng giá TCBS

![](../assets/images/tcbs_trading_board_sector.png)

### Khớp lệnh, Bước giá & khối lượng
```python
price_depth('TCB,SSI,VND')
```
Sử dụng hàm này cho phép thống kê các bước giá và khối lượng trên bảng giá của một hoặc một danh sách các mã cổ phiếu. Bạn có thể sử dụng kết hợp hàm này với hàm **price_board** để kết hợp các thông tin đa dạng về giá, khối lượng, chỉ số, thông tin giao dịch để chọn lọc và theo dõi cổ phiếu theo mục đích sử dụng của mình.

- Kết quả:

```shell
>>> price_depth('TCB,SSI,VND').T
                      0          1          2
Mã CP               TCB        SSI        VND
Giá tham chiếu    30650      30100      19150
Giá Trần          32750      32200      20450
Giá Sàn           28550      28000      17850
Giá mua 3         31100      29850      18900
KL mua 3           1630       3240       8310
Giá mua 2         31050      29800      18850
KL mua 2           1320      10690      13480
Giá mua 1         31000      29750      18800
KL mua 1           2260       3220      12160
Giá khớp lệnh     31100      29900      18900
KL Khớp lệnh         90        140        100
Giá bán 1         31200      29900      18950
KL bán 1           2140       2980       6720
Giá bán 2         31250      29950      19000
KL bán 2           5410       4340      16200
Giá bán 3         31300      30000      19050
KL bán 3            810      17840      11000
Tổng Khối Lượng  164810    1783250    1812410
ĐTNN Mua              0      45896      20285
ĐTNN Bán              0      77526      38110
ĐTNN Room             0  837230225  936537977
```

### Thông tin giao dịch

```python
price_board('TCB,SSI,VND')
```
Hàm này cho phép tải về thông tin giá, khối lượng và các chỉ số quan trọng cho một hoặc một danh sách mã cổ phiếu. Sử dụng kết hợp với hàm **price_depth** cho hiệu quả tốt nhất.

- Kết quả:

```shell
>>> price_board('TCB,SSI,VND').T
                            0           1           2
Mã CP                     TCB         SSI         VND
Giá                   31100.0     29900.0     18850.0
KLBD/TB5D                0.95        1.33        1.28
T.độ GD                  0.82        0.68        0.83
KLGD ròng(CM)               0     -219100      198000
%KLGD ròng (CM)           0.0       -19.6        14.2
RSI                 35.168889    38.43115   35.726964
MACD Hist               -0.13       -0.34       -0.23
MACD Signal           Neutral        Sell        Sell
Tín hiệu KT           Neutral     Neutral     Neutral
Tín hiệu TB động   Strong Buy  Strong Buy  Strong Buy
MA20                  32265.0     31957.5     20772.5
MA50                  33446.0     32258.0     21899.0
MA100                 33034.5     29527.0     20479.0
Phiên +/-                  -6          -1          -1
% thay đổi giá 3D        -3.5        -4.3        -4.3
% thay đổi giá 1M       -10.1       -15.7       -22.0
% thay đổi giá 3M        -5.1         5.4         4.1
% thay đổi giá 1Y        21.1        75.8        31.2
RS 3D                    50.0        34.0        22.0
RS 1M                    38.0        23.0        11.0
RS 3M                    45.0        76.0        73.0
RS 1Y                    69.0        95.0        77.0
RS TB                    50.0        57.0        46.0
Đỉnh 1M                 34350       36450       25250
Đỉnh 3M                 35750       36450       25250
Đỉnh 1Y                 35750       36450       25250
Đáy 1M                  30650       30100       19150
Đáy 3M                  30650       28000       18100
Đáy 1Y                  20700       13373        9720
%Đỉnh 1Y                -14.3       -17.4       -24.2
%Đáy 1Y                  48.1       125.1        97.0
P/E                       6.1        22.4        41.0
P/B                       0.9         2.0         1.5
ROE                   0.15834    0.090235    0.038377
TCRating                  4.2         3.8         3.8
Khối lượng Dư bán       84500      251400      292000
Khối lượng Dư mua       51000      168800      503100
TCBS định giá           48627       17496       12096
Khớp nhiều nhất         30650       29500       18800
Đ.góp VNINDEX             0.4       -0.08       -0.09
%Giá - %VNI (1M)          0.1        -5.5       -11.8
%Giá - %VNI (1Y)         18.9        73.5        28.9
VNINDEX P/E           13.9448     13.9448     13.9448
VNINDEX P/B           1.58262     1.58262     1.58262
vnid3d                   -3.0        -3.0        -3.0
vnid1m                  -10.2       -10.2       -10.2
vnid3m                   -7.3        -7.3        -7.3
vnid1y                    2.3         2.3         2.3
```

## So sánh cổ phiếu cùng ngành

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

## So sánh các cổ phiếu tùy ý

!!! bug "Ghi nhận lỗi"
    20/10/2023: Hiện tại hàm ghi nhận lỗi không trả về kết quả như mong muốn từ chính nguồn cấp dữ liệu là TCBS.

```python
stock_ls_analysis("TCB, BID, CEO, GMD", lang='vi')
```

Kết quả:

```shell
>>> stock_ls_analysis("TCB, BID, CEO, GMD", lang='vi')
Mã CP                            BID    CEO    GMD     TCB
Vốn hóa (tỷ)                  203353   9367  19853  107803
Giá                            40200  18200  64900   30650
Số phiên tăng/giảm liên tiếp       1      0      2      -6
P/E                             10.0   32.8    8.7     6.1
PEG                              0.2    2.3    0.1    -0.5
P/B                              1.8    2.8    2.3     0.9
Cổ tức                           0.0    0.0  0.045     0.0
ROE                            0.203   0.09  0.294   0.158
ROA                             0.01   0.04   0.18   0.026
Nợ/Vốn CSH                      17.6    0.2    0.2     5.0
LNST 5 năm                     0.218  0.094  0.144   0.256
Doanh thu 5 năm                0.123  0.068 -0.004     0.2
LNST quý gần nhất             -0.008  0.412  7.163  -0.009
Doanh thu quý gần nhất        -0.001 -0.073  0.011   0.003
LNST năm tới                  -0.023 -0.012  1.288  -0.084
Doanh thu năm tới              0.124   -0.1    0.0   0.084
RSI                             29.2   34.9   54.9    29.0
RS                              44.0   48.0   85.0    50.0
```