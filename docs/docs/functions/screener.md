# Bộ lọc cổ phiếu

!!! tip "Lưu ý"
    Để tiện theo dõi và tra cứu, trong một số trường hợp chúng tôi sẽ xoay DataFrame trả về từ hàm với với phép `transpose` để thấy đầy đủ thông tin dễ hơn. Với các câu lệnh có phần kết thúc với `.T` tức là đang áp dụng phép `transpose` này.

## Giới thiệu

![stock screener](../assets/images/stock_screener-tcbs.png)

Bộ lọc cổ phiếu là một hàm cho phép bạn truy vấn và lọc các cổ phiếu theo nhiều tiêu chí đa dạng dựa trên dữ liệu phân tích của TCBS. 
Hàm này sẽ trả về một DataFrame chứa các thông tin toàn diện về các cổ phiếu thỏa mãn điều kiện lọc của bạn. Bạn có thể dùng DataFrame này để tiếp tục phân tích, biểu diễn hoặc xuất ra dữ liệu dạng bảng tính. Đây là cập nhật ưu việt giúp bạn tiết kiệm thời gian và công sức đáng kể khi làm việc với dữ liệu cổ phiếu, đồng thời cho phép lập trình để lọc là cập nhật danh sách cổ phiếu hiệu quả không cần sử dụng giao diện web từ công ty chứng khoán.

- Bộ lọc cổ phiếu TCBS

Tham số

- params (dict): một từ điển chứa các tham số và giá trị của chúng cho việc lọc cổ phiếu. Các `key` là tên của các bộ lọc, và các `value` là một giá trị đơn hoặc một tupple gồm hai giá trị (min và max) cho bộ lọc đó. Đây là ví dụ cho tham số params được thiết lập đúng:
- drop_lang: Loại bỏ các cột dữ liệu sử dụng tên tiếng Việt (`vi`) hoặc Anh (`en`)

```python
params = {
            "exchangeName": "HOSE,HNX,UPCOM",
            "marketCap": (100, 1000),
            "dividendYield": (5, 10)
        }
```

Áp dụng bộ lọc với hàm để lấy kết quả

```
df = stock_screening_insights (params, size=1700, drop_lang='vi')
```

## Điều kiện lọc

??? note "Bộ lọc gợi ý"
    Sử dụng các tiêu chí lọc như sau để thiết lập tham số params.

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

??? note "Thông tin chung"
    - `exchangeName`: sàn giao dịch của cổ phiếu, ví dụ "HOSE", "HNX", hoặc "UPCOM". Bạn có thể dùng dấu phẩy để phân tách nhiều sàn, ví dụ "HOSE,HNX,UPCOM".
    - `hasFinancialReport`: Có báo cáo tài chính gần nhất. `1` nghĩa là có, `0` nghĩa là không.
    - `industryName`: Lọc các cổ phiếu theo ngành cụ thể. Giá trị dạng `Retail` cho ngành Bán lẻ. Các giá trị khác có thể là:
        - `Insurance`: Bảo hiểm
        - `Real Estate`: Bất động sản
        - `Technology`: Công nghệ thông tin
        - `Oil & Gas`: Dầu khí
        - `Financial Services`: Dịch vụ tài chính
        - `Utilities`: Điện, nước, xăng dầu và khí đốt
        - `Travel & Leisure`: Du lịch và giải trí
        - `Industrial Goods & Services`: Hàng và dịch vụ công nghiệp
        - `Personal & Household Goods`: Hàng cá nhân và gia dụng
        - `Chemicals`: Hóa chất
        - `Banks`: Ngân hàng
        - `Automobiles & Parts`: Ô tô và phụ tùng
        - `Basic Resources`: Tài nguyên cơ bản
        - `Food & Beverage`: Thực phẩm và đồ uống
        - `Media`: Truyền thông
        - `Telecommunications`: Viễn thông
        - `Construction & Materials`: Xây dựng và vật liệu
        - `Health Care`: Y tế
    - `marketCap`: vốn hóa thị trường của cổ phiếu tính bằng tỷ VND.
    - `priceNearRealtime`: giá hiện tại của cổ phiếu tính bằng VND.
    - `foreignVolumePercent`: tỷ lệ phần trăm khối lượng nước ngoài trong tổng khối lượng.
    - `alpha`: lợi nhuận vượt trội của cổ phiếu so với lợi nhuận thị trường.
    - `beta`: độ biến động của cổ phiếu so với thị trường.
    - `freeTransferRate`: tỷ lệ phần trăm cổ phiếu có thể chuyển nhượng tự do.

??? note "Tăng trưởng"
    - `revenueGrowth1Year`: tốc độ tăng trưởng doanh thu trong năm qua.
    - `revenueGrowth5Year`: tốc độ tăng trưởng doanh thu trung bình trong 5 năm qua.
    - `epsGrowth1Year`: tốc độ tăng trưởng lợi nhuận trên mỗi cổ phiếu trong năm qua.
    - `epsGrowth5Year`: tốc độ tăng trưởng lợi nhuận trên mỗi cổ phiếu trung bình trong 5 năm qua.
    - `lastQuarterRevenueGrowth`: tốc độ tăng trưởng doanh thu trong quý gần nhất.
    - `secondQuarterRevenueGrowth`: tốc độ tăng trưởng doanh thu trong quý thứ hai.
    - `lastQuarterProfitGrowth`: tốc độ tăng trưởng lợi nhuận trong quý gần nhất.
    - `secondQuarterProfitGrowth`: tốc độ tăng trưởng lợi nhuận trong quý thứ hai.

??? note "Chỉ số tài chính"
    - `grossMargin`: tỷ suất lợi nhuận gộp của cổ phiếu.
    - `netMargin`: tỷ suất lợi nhuận ròng của cổ phiếu.
    - `roe`: tỷ suất sinh lời về vốn chủ sở hữu của cổ phiếu.
    - `doe`: tỷ suất cổ tức về vốn chủ sở hữu của cổ phiếu.
    - `dividendYield`: tỷ suất cổ tức của cổ phiếu.
    - `eps`: lợi nhuận trên mỗi cổ phiếu của cổ phiếu tính bằng VND.
    - `pe`: tỷ số giá/lợi nhuận của cổ phiếu.
    - `pb`: tỷ số giá/giá trị sổ sách của cổ phiếu.
    - `evEbitda`: tỷ số giá trị doanh nghiệp/lợi nhuận trước thuế, lãi vay, khấu hao và amortization của cổ phiếu.
    - `netCashPerMarketCap`: tỷ số tiền mặt ròng/vốn hóa thị trường của cổ phiếu.
    - `netCashPerTotalAssets`: tỷ số tiền mặt ròng/tổng tài sản của cổ phiếu.
    - `profitForTheLast4Quarters`: tổng lợi nhuận trong 4 quý gần nhất của cổ phiếu tính bằng tỷ VND.


??? note "Biến động giá & khối lượng"
    - `suddenlyHighVolumeMatching`: tín hiệu chỉ ra nếu có sự tăng đột biến khối lượng khớp lệnh cho cổ phiếu này. 0 nghĩa là không, 1 nghĩa là có.
    - `totalTradingValue`: tổng giá trị giao dịch của cổ phiếu này tính bằng tỷ VND hôm nay.
    - `avgTradingValue5Day`: giá trị giao dịch trung bình của cổ phiếu này tính bằng tỷ VND trong 5 ngày.
    - `avgTradingValue10Day`: giá trị giao dịch trung bình của cổ phiếu này tính bằng tỷ VND trong 10 ngày.
    - `avgTradingValue20Day`: giá trị giao dịch trung bình của cổ phiếu này tính bằng tỷ VND trong 20 ngày.
    - `priceGrowth1Week`: tốc độ tăng trưởng giá của cổ phiếu trong tuần qua.
    - `priceGrowth1Month`: tốc độ tăng trưởng giá của cổ phiếu trong tháng qua.
    - `percent1YearFromPeak`: tỷ lệ phần trăm thay đổi của cổ phiếu từ giá cao nhất trong 1 năm.
    - `percentAwayFromHistoricalPeak`: tỷ lệ phần trăm thay đổi của cổ phiếu từ giá cao nhất lịch sử.
    - `percent1YearFromBottom`: tỷ lệ phần trăm thay đổi của cổ phiếu từ giá thấp nhất trong 1 năm.
    - `percentOffHistoricalBottom`: tỷ lệ phần trăm thay đổi của cổ phiếu từ giá thấp nhất lịch sử.
    - `priceVsSMA5`: mối quan hệ giữa giá hiện tại và SMA 5 ngày của cổ phiếu. Các giá trị có thể là `ABOVE`, `BELOW`, `CROSS_ABOVE`, hoặc `CROSS_BELOW`.
    - `priceVsSma10`: mối quan hệ giữa giá hiện tại và SMA 10 ngày của cổ phiếu. Các giá trị có thể là `ABOVE`, `BELOW`, `CROSS_ABOVE`, hoặc `CROSS_BELOW`.
    - `priceVsSMA20`: mối quan hệ giữa giá hiện tại và SMA 20 ngày của cổ phiếu. Các giá trị có thể là `ABOVE`, `BELOW`, `CROSS_ABOVE`, hoặc `CROSS_BELOW`.
    - `priceVsSma50`: mối quan hệ giữa giá hiện tại và SMA 50 ngày của cổ phiếu. Các giá trị có thể là `ABOVE`, `BELOW`, `CROSS_ABOVE`, hoặc `CROSS_BELOW`.
    - `priceVsSMA100`: mối quan hệ giữa giá hiện tại và SMA 100 ngày của cổ phiếu. Các giá trị có thể là `ABOVE`, `BELOW`, `CROSS_ABOVE`, hoặc `CROSS_BELOW`.
    - `forecastVolumeRatio`: tỷ số giữa khối lượng dự báo và khối lượng thực tế của cổ phiếu hôm nay.
    - `volumeVsVSma5`: tỷ số giữa khối lượng hiện tại và SMA khối lượng 5 ngày của cổ phiếu.
    - `volumeVsVSma10`: tỷ số giữa khối lượng hiện tại và SMA khối lượng 10 ngày của cổ phiếu.
    - `volumeVsVSma20`: tỷ số giữa khối lượng hiện tại và SMA khối lượng 20 ngày của cổ phiếu.
    - `volumeVsVSma50`: tỷ số giữa khối lượng hiện tại và SMA khối lượng 50 ngày của cổ phiếu.

??? note "Hành vi thị trường"
    - `strongBuyPercentage`: tỷ lệ phần trăm tín hiệu mua mạnh cho cổ phiếu này dựa trên phân tích kỹ thuật.
    - `activeBuyPercentage`: tỷ lệ phần trăm tín hiệu mua tích cực cho cổ phiếu này dựa trên phân tích kỹ thuật.
    - `foreignTransaction`: loại giao dịch nước ngoài cho cổ phiếu này hôm nay. Các giá trị có thể là `buyMoreThanSell`, `sellMoreThanBuy`, hoặc `noTransaction`.
    - `foreignBuySell20Session`: giá trị mua bán ròng nước ngoài cho cổ phiếu này tính bằng tỷ VND trong 20 phiên.
    - `numIncreaseContinuousDay`: số ngày liên tiếp cổ phiếu này tăng giá.
    - `numDecreaseContinuousDay`: số ngày liên tiếp cổ phiếu này giảm giá.

??? note "Tín hiệu kỹ thuật"
    - `rsi14`: chỉ số sức mạnh tương đối (RSI) của cổ phiếu với chu kỳ 14 ngày.
    - `rsi14Status`: trạng thái của RSI cho cổ phiếu này. Các giá trị có thể là `intoOverBought`, `intoOverSold`, `outOfOverBought`, hoặc `outOfOverSold`.
    - `tcbsBuySellSignal`: tín hiệu mua bán cho cổ phiếu này dựa trên phân tích của TCBS. Các giá trị có thể là `BUY` hoặc `SELL`.
    - `priceBreakOut52Week`: tín hiệu chỉ ra nếu có sự đột phá giá cho cổ phiếu này trong 52 tuần. Các giá trị có thể là `BREAK_OUT` hoặc `NO_BREAK_OUT`.
    - `priceWashOut52Week`: tín hiệu chỉ ra nếu có sự rửa giá cho cổ phiếu này trong 52 tuần. Các giá trị có thể là `WASH_OUT` hoặc `NO_WASH_OUT`.
    - `macdHistogram`: tín hiệu chỉ ra nếu có tín hiệu MACD histogram cho cổ phiếu này. Các giá trị có thể là `macdHistGT0Increase`, `macdHistGT0Decrease`, `macdHistLT0Increase`, hoặc `macdHistLT0Decrease`.
    - `relativeStrength3Day`: sức mạnh tương đối của cổ phiếu so với thị trường trong 3 ngày.
    - `relativeStrength1Month`: sức mạnh tương đối của cổ phiếu so với thị trường trong 1 tháng.
    - `relativeStrength3Month`: sức mạnh tương đối của cổ phiếu so với thị trường trong 3 tháng.
    - `relativeStrength1Year`: sức mạnh tương đối của cổ phiếu so với thị trường trong 1 năm.
    - `tcRS`: sức mạnh tương đối của TCBS của cổ phiếu so với thị trường.
    - `sarVsMacdHist`: tín hiệu chỉ ra nếu có tín hiệu SAR vs MACD histogram cho cổ phiếu này. Các giá trị có thể là `BUY` hoặc `SELL`.


??? note "Tín hiệu mua bán"
    - `bollingBandSignal`: tín hiệu chỉ ra nếu có tín hiệu Bollinger Band cho cổ phiếu này. Các giá trị có thể là `BUY` hoặc `SELL`.
    - `dmiSignal`: tín hiệu chỉ ra nếu có tín hiệu chỉ số chuyển động hướng (DMI) cho cổ phiếu này. Các giá trị có thể là `BUY` hoặc `SELL`.
    - `uptrend`: tín hiệu chỉ ra nếu có tín hiệu xu hướng tăng cho cổ phiếu này. Các giá trị có thể là `buy-signal` hoặc `sell-signal`.
    - `breakout`: tín hiệu chỉ ra nếu có tín hiệu đột phá cho cổ phiếu này. Các giá trị có thể là `BULLISH` hoặc `BEARISH`.

??? note "TCBS đánh giá"
    - `tcbsRecommend`: tín hiệu chỉ ra nếu có khuyến nghị của TCBS cho cổ phiếu này. Các giá trị có thể là `BUY` hoặc `SELL`.
    - `stockRating`: điểm đánh giá cổ phiếu cho cổ phiếu này dựa trên phân tích của TCBS. Điểm từ 1 đến 5, với 5 là tốt nhất.
    - `businessModel`: điểm đánh giá mô hình kinh doanh cho cổ phiếu này dựa trên phân tích của TCBS. Điểm từ 1 đến 5, với 5 là tốt nhất.
    - `businessOperation`: điểm đánh giá hoạt động kinh doanh cho cổ phiếu này dựa trên phân tích của TCBS. Điểm từ 1 đến 5, với 5 là tốt nhất.
    - `financialHealth`: điểm đánh giá sức khỏe tài chính cho cổ phiếu này dựa trên phân tích của TCBS. Điểm từ 1 đến 5, với 5 là tốt nhất.