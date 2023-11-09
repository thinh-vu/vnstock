# Kiểm thử chiến lược đầu tư

!!! abstract "Kiểm thử chiến lược"
    Hàm [stock_historical_data](https://docs.vnstock.site/functions/technical/#truy-xuat-du-lieu-gia-lich-su) của vnstock sau khi tuỳ biến lại cách trình bày (sử dụng tham số `decor=True`), có thể dễ dàng tích hợp ngay với các thư viện giúp kiểm thử chiến lược giao dịch trong môi trường Python. 

vnstock giới thiệu tới bạn một số tùy chọn cho backtesting để tham khảo. Chúng tôi sẽ cung cấp thêm thông tin hướng dẫn chi tiết trong thời gian tới.

| Thư viện                                                  | Dễ sử dụng | Tính năng | Tốc độ | Hoạt động cộng đồng | Tài liệu | Hoạt động dự án | Cập nhật gần nhất | Xếp hạng |
| --------------------------------------------------------- | ---------- | --------- | ------ | ------------------- | -------- | --------------- | ----------------- | -------- |
| [Backtesting.py](https://kernc.github.io/backtesting.py/) | High       | High      | Medium | High                | High     | Medium          | 1 năm             | 5        |
| [VectorBT](https://vectorbt.dev/)                         | Medium     | High      | High   | High                | High     | High            | 2 tháng           | 5        |
| [Backtrader](https://www.backtrader.com/)                 | High       | High      | Low    | High                | High     | Low             | 7 tháng           | 4        |
| [Zipline](https://github.com/quantopian/zipline)          | Medium     | Medium    | Low    | Medium              | Medium   | None            | 3 năm             | 3        |
| [bt](https://pmorissette.github.io/bt/)                   | Low        | Medium    | Low    | Medium              | Medium   | Low             | 6 tháng           | 2        |
| [PyBacktest](https://github.com/ematvey/pybacktest)       | Low        | Low       | Medium | Low                 | Poor     | None            | 4 năm             | 1        |

Lưu ý: Điểm xếp hạng càng cao càng tốt. Nguồn tham khảo: [QMR AI](https://www.qmr.ai/best-backtesting-library-for-python/)