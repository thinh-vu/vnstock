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
lang: chọn ngôn ngữ của dữ liệu trả về là tiếng Việt `vi`, hoặc Anh `en`

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