# Chuyển động thị trường

!!! abstract "SSI - Chuyển động thị trường"
    Thông tin chuyển động thị trường của vnstock được cung cấp từ nguồn SSI. Bạn có thể truy xuất các thông tin được hiển thị trên giao diện người dùng của SSI vào môi trường Python bằng các hàm dưới đây. Điểm khác biệt căn bản giữa việc lấy dữ liệu thị trường bằng hàm vnstock so với tải file excel trực tiếp từ SSI là dữ liệu của vnstock có độ chi tiết cao hơn, đồng thời có thể được lấy trực tiếp vào môi trường Python mà không cần phải lưu file excel về máy để phân tích.

## Bản đồ nhiệt giá

![](../assets/images/ssi_heatmap.png)

Sử dụng hàm:

```python
fr_trade_heatmap (symbol='HOSE', report_type='FrBuyVal')
```
Trong đó:

- `symbol`: Mã sàn chứng khoán hoặc mã Chỉ số.

    - Mã sàn: `HOSE`, `HNX` hoặc `UPCOM`
    - Mã Chỉ số: `VN30`, `VN100`, hoặc bất kỳ mã chỉ số nào có trong hình bên trên, được khoanh vùng màu xanh.

- `report_type`: Loại bản đồ nhiệt giá.

    - `FrBuyVal`: Giá trị NĐTNN mua ròng
    - `FrSellVal`: Giá trị NĐTNN bán ròng
    - `FrBuyVol`: Khối lượng NĐTNN mua ròng
    - `FrSellVol`: Khối lượng NĐTNN bán ròng
    - `Volume`: Khối lượng giao dịch
    - `Value`: Giá trị giao dịch
    - `MarketCap`: Vốn hóa thị trường

Kết quả:

```shell
>>> fr_trade_heatmap (symbol='VN30', report_type='FrBuyVal').T
                                                         0   ...                                 29
avgPrice                                           21583.35  ...                           24757.58
best1Bid                                            21550.0  ...                                NaN
best1BidVol                                        205900.0  ...                                NaN
best1Offer                                            21600  ...                              24600
best1OfferVol                                         39500  ...                             690100
best2Bid                                            21500.0  ...                                NaN
best2BidVol                                        620300.0  ...                                NaN
best2Offer                                            21650  ...                              24650
best2OfferVol                                         65700  ...                              86200
best3Bid                                            21450.0  ...                                NaN
best3BidVol                                        483100.0  ...                                NaN
best3Offer                                            21700  ...                              24700
best3OfferVol                                         29700  ...                              20500
caStatus                                                     ...
ceiling                                               23400  ...                              28300
corporateEvents                                          []  ...                                 []
coveredWarrantType                                           ...
exchange                                               hose  ...                               hose
exercisePrice                                             0  ...                                  0
exerciseRatio                                                ...
floor                                                 20400  ...                              24600
highest                                               21750  ...                              25900
issuerName                                                   ...
lastTradingDate                                              ...
lastVol                                               38999  ...                              54716
lowest                                                21450  ...                              24600
matchedPrice                                          21550  ...                              24600
maturityDate                                                 ...
nmTotalTradedValue                              84172900000  ...                       135463580000
openPrice                                             21750  ...                              25900
priorClosePrice                                       21900  ...                              26450
refPrice                                              21900  ...                              26450
securityName                          NGAN HANG TMCP A CHAU  ...                 CTCP VINCOM RETAIL
stockSymbol                                             ACB  ...                                VRE
stockType                                                 s  ...                                  s
totalShare                                            38999  ...                              54716
tradingStatus                                                ...
tradingUnit                                             100  ...                                100
underlyingSymbol                                             ...
companyNameEn              Asia Commercial Joint Stock Bank  ...  Vincom Retail Joint Stock Company
companyNameVi           Ngân hàng Thương mại Cổ phần Á Châu  ...      Công ty Cổ phần Vincom Retail
oddSession                                               LO  ...                                 LO
session                                                  LO  ...                                 LO
buyForeignQtty                                       120300  ...                             748207
remainForeignQtty                                         0  ...                          382909157
sellForeignQtty                                      120365  ...                             695725
matchedVolume                                            30  ...                                 50
priceChange                                            -350  ...                              -1850
priceChangePercent                                     -1.6  ...                              -6.99
lastMatchedPrice                                      21550  ...                              24600
lastMatchedVolume                                        30  ...                                 50
lastPriceChange                                        -350  ...                              -1850
lastPriceChangePercent                                 -1.6  ...                              -6.99
nmTotalTradedQty                                    3899900  ...                            5471600

[54 rows x 30 columns]
```

## Top cổ phiếu

![](../assets/images/ssi_top_move.png)

Sử dụng hàm:

```python
market_top_mover (report_name='Value', exchange='All', filter= 'NetBuyVol', report_range='ThreeMonths', rate='OnePointFive', lang='vi')
```

Trong đó `report_name` là tên loại báo cáo cần truy xuất, nhận một trong các giá trị sau:

- report_name: Tên của loại báo cáo
    - `Breakout`: Top đột phá
    - `Value`: Top giá trị
    - `Losers`: Top giảm giá
    - `Gainers`: Top tăng giá
    - `Volume`: Top khối lượng
    - `ForeignTrading`: Top NĐTNN
    - `NewHigh`: Top vượt đỉnh
    - `NewLow`: Top thủng đáy
- `exchange`: Chọn sàn giao dịch để truy xuất báo cáo. `All` cho tất cả, hoặc riêng lẻ từng sàn `HOSE`, `HNX`, `UPCOM`
- `filter`: Lọc loại báo cáo, áp dụng cho loại báo cáo Top NĐTNN, hàm sẽ tự động áp dụng với loại báo cáo phù hợp.
    - `NetBuyVol`: Top khối lượng mua ròng
    - `NetBuyVal`: Top giá trị mua ròng
    - `NetSellVol`: Top khối lượng bán ròng
    - `NetSellVal`: Top giá trị bán ròng
- `report_range`: Chọn khung thời gian báo cáo `OneWeek` cho 5 ngày, `TwoWeek` cho 10 ngày, `OneMonth` cho 1 tháng, `ThreeMonths` cho 3 tháng, `SixMonths` cho 6 tháng, `OneYear` cho 1 năm
- `rate`: Tỉ lệ Khối lượng giao dịch so với Khối lượng giao dịch trung bình trong số phiên xác định (ví dụ 10 ngày, 1 tháng). Nhận một trong các giá trị `OnePointTwo` cho 1.2, `OnePointFive` cho 1.5, `Two` cho 2, `Five` cho 5, `Ten` cho 10
- `lang`: chọn ngôn ngữ của dữ liệu trả về là tiếng Việt `vi`, hoặc Anh `en`

Dưới đây là các mẫu lệnh để tải từng loại báo cáo nêu trên. Xem thêm chi tiết Demo Notebook để tham chiếu kết quả từng hàm cụ thể.

```python
market_top_mover (report_name='Value', exchange='All', filter= 'NetBuyVol', report_range='ThreeMonths', rate='OnePointFive', lang='vi')
```

```python
market_top_mover (report_name='Losers', exchange='All', filter= 'NetBuyVol', report_range='ThreeMonths', rate='OnePointFive', lang='vi')
```


```python
market_top_mover (report_name='Gainers', exchange='All', filter= 'NetBuyVol', report_range='ThreeMonths', rate='OnePointFive', lang='vi')
```


```python
market_top_mover (report_name='Volume', exchange='All', filter= 'NetBuyVol', report_range='ThreeMonths', rate='OnePointFive', lang='vi')
```


```python
market_top_mover (report_name='ForeignTrading', exchange='All', filter= 'NetBuyVol', report_range='ThreeMonths', rate='OnePointFive', lang='vi')
```

```python
market_top_mover (report_name='NewLow', exchange='All', filter= 'NetBuyVol', report_range='ThreeMonths', rate='OnePointFive', lang='vi')
```

```python
market_top_mover (report_name='NewHigh', exchange='All', filter= 'NetBuyVol', report_range='ThreeMonths', rate='OnePointFive', lang='vi')
```

```python
market_top_mover (report_name='Breakout', exchange='All', filter= 'NetBuyVol', report_range='TwoWeeks', rate='OnePointFive', lang='vi')
```

## 🔐 Giao dịch NĐTNN

!!! tip "Giới thiệu" 
	Dữ liệu được trích xuất từ CafeF, không giới hạn thời gian tra cứu. Nếu bạn xuất dữ liệu trực tiếp từ CafeF chỉ có thể xuất từng trang với giới hạn 20 dòng gần nhất. 
	Tính năng chỉ dành cho người dùng tài trợ dự án qua chương trình Insiders Program và sử dụng gói thư viện bổ sung `vnstock-data-pro`. Xem hướng dẫn tham gia Insiders Program [tại đây](https://docs.vnstock.site/insiders-program/gioi-thieu-chuong-trinh-vnstock-insiders-pro)

Bạn có thể sử dụng câu lệnh sau:

```python
foreign_trade_data(symbol='VIC', start_date='2003-01-01', end_date='2023-12-22', limit=5000, page=1, lang='vi')
```

Trong đó:

- `symbol`: Mã chứng khoán hoặc chỉ số cần tra cứu. Không phân biệt chữ hoa/thường.
- `start_date`: Ngày bắt đầu tra cứu, định dạng `YYYY-MM-DD`
- `end_date`: Ngày kết thúc tra cứu, định dạng `YYYY-MM-DD`
- `limit`: Số lượng bản ghi trả về trong một lần truy vấn, mặc định là 500
- `page`: Trang kết quả trả về, mặc định là 1. Bỏ qua tham số này và điều chỉnh `limit` để truy vấn tất cả các bản ghi.
- `lang`: Ngôn ngữ của tên cột dữ liệu trả về, nhận giá trị `vi` hoặc `en` 


Dưới đây là kết quả minh họa:

```shell
>>> foreign_trade_data(symbol='VIC', start_date='2003-01-01', end_date='2023-12-22', limit=5000, page=1, lang='vi')

Total records: 4141. Returned records: 4141
            Ngay  KLGDRong      GTDGRong         ThayDoi   KLMua         GtMua   KLBan         GtBan  RoomConLai  DangSoHuu MaCK
0     22/12/2023   -396290 -1.700099e+10  43.15(-0.12 %)  231200  9.950400e+09  627490  2.695139e+10           0        0.0  VIC
1     21/12/2023   -129968 -5.564799e+09   43.2(-0.12 %)  224100  9.642125e+09  354068  1.520692e+10           0        0.0  VIC
2     20/12/2023    -59541 -2.503370e+09   43.25(0.12 %)  268088  1.158413e+10  327629  1.408750e+10           0        0.0  VIC
3     19/12/2023   -199294 -8.485858e+09    43.2(0.00 %)  195100  8.357565e+09  394394  1.684342e+10           0        0.0  VIC
4     18/12/2023   -145146 -6.305306e+09   43.2(-1.14 %)  263710  1.145286e+10  408856  1.775816e+10           0        0.0  VIC
...          ...       ...           ...             ...     ...           ...     ...           ...         ...        ...  ...
4136  07/03/2007         0  0.000000e+00       0(0.00 %)       0  0.000000e+00       0  0.000000e+00           0        0.0  VIC
4137  06/03/2007         0  0.000000e+00       0(0.00 %)       0  0.000000e+00       0  0.000000e+00           0        0.0  VIC
4138  05/03/2007         0  0.000000e+00       0(0.00 %)       0  0.000000e+00       0  0.000000e+00           0        0.0  VIC
4139  02/03/2007         0  0.000000e+00       0(0.00 %)       0  0.000000e+00       0  0.000000e+00           0        0.0  VIC
4140  01/03/2007         0  0.000000e+00       0(0.00 %)       0  0.000000e+00       0  0.000000e+00           0        0.0  VIC

[4141 rows x 11 columns]
```

## 🔐 Giao dịch tự doanh

> Tính năng chỉ dành cho người dùng Tài trợ dự án và sử dụng gói thư viện bổ sung `vnstock-data-pro`. Xem hướng dẫn người dùng tham gia tài trợ dự án qua Insiders Program [tại đây](https://docs.vnstock.site/insiders-program/gioi-thieu-chuong-trinh-vnstock-insiders-program/)

!!! tip "Giới thiệu" 
	Dữ liệu được trích xuất từ CafeF, giới hạn thời gian tra cứu trong vòng 1 năm. Nếu bạn xuất dữ liệu trực tiếp từ CafeF chỉ có thể xuất từng trang với giới hạn 20 dòng gần nhất. 
	Tính năng chỉ dành cho người dùng tài trợ dự án qua chương trình Insiders Program và sử dụng gói thư viện bổ sung `vnstock-data-pro`. Xem hướng dẫn tham gia Insiders Program [tại đây](https://docs.vnstock.site/insiders-program/gioi-thieu-chuong-trinh-vnstock-insiders-pro)

Bạn có thể sử dụng câu lệnh sau:

```python
proprietary_trade_data(symbol='VIC', start_date='2022-01-01', end_date='2023-12-22', limit=1000, page=1, lang='vi')
```

Trong đó:

- `symbol`: Mã chứng khoán hoặc chỉ số cần tra cứu. Không phân biệt chữ hoa/thường.
- `start_date`: Ngày bắt đầu tra cứu, định dạng `YYYY-MM-DD`
- `end_date`: Ngày kết thúc tra cứu, định dạng `YYYY-MM-DD`
- `limit`: Số lượng bản ghi trả về trong một lần truy vấn, mặc định là 500
- `page`: Trang kết quả trả về, mặc định là 1. Bỏ qua tham số này và điều chỉnh `limit` để truy vấn tất cả các bản ghi.
- `lang`: Ngôn ngữ của tên cột dữ liệu trả về, nhận giá trị `vi` hoặc `en` 

Dưới đây là kết quả minh họa:

```shell
>>> proprietary_trade_data(symbol='VIC', start_date='2022-01-01', end_date='2023-12-22', limit=1000, page=1, lang='vi')

Total records: 287. Returned records: 287
           Ngay  KLcpMua  KlcpBan        GtMua        GtBan MaCK
0    22/12/2023   112100   361000   4832690000  15497035000  VIC
1    21/12/2023   257900   402100  11096970000  17287675000  VIC
2    20/12/2023    56400   353200   2423970000  15201520000  VIC
3    19/12/2023   226300   357100   9690645000  15290020000  VIC
4    18/12/2023   160000   177800   6955905000   7715020000  VIC
..          ...      ...      ...          ...          ...  ...
282  07/11/2022   183600    27200   9778640000   1424160000  VIC
283  04/11/2022   153000   165700   8108240000   8866530000  VIC
284  03/11/2022    71700    15300   3907960000    836750000  VIC
285  02/11/2022    87700   180000   4817810000   9893270000  VIC
286  01/11/2022   198900    81800  10938740000   4461310000  VIC

[287 rows x 6 columns]
```