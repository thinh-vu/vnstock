# Áp dụng repo hiện tại cho Portfolio Tracker và Robo-Advisor

Tài liệu này trả lời câu hỏi thực dụng hơn sau khi so sánh với `vnstock` chuẩn:

- Nếu xây hệ thống theo kiểu `portfolio tracker` hoặc `robo-advisor`, repo hiện tại nên được dùng như thế nào?
- Những phần nào đã đủ tốt để tận dụng ngay?
- Những phần nào vẫn cần tự bọc thêm ở tầng ứng dụng?

Nếu bạn đang chuyển hẳn môi trường từ bản chuẩn sang bản fork, đọc thêm `docs/FORK_MIGRATION_GUIDE.md`.

## Kết luận nhanh

Nếu mục tiêu là xây một hệ thống gồm:

- đồng bộ dữ liệu giá cho nhiều mã,
- lưu cache và snapshot theo lịch,
- phục vụ API cho dashboard,
- chạy rule-based signal hoặc allocation job định kỳ,

thì repo hiện tại phù hợp hơn `vnstock` chuẩn vì đã tiến gần đến mô hình “data service” hơn là chỉ một thư viện gọi dữ liệu thủ công.

Nói ngắn gọn:

- `vnstock` chuẩn: đủ cho nghiên cứu và notebook.
- Repo hiện tại: phù hợp hơn cho backend job, worker và data ingestion pipeline.

## Phân rã theo use case

### 1. Portfolio tracker

Nhu cầu chính thường là:

- lấy lịch sử giá cho watchlist hoặc holdings,
- cập nhật EOD hoặc intraday snapshot,
- tính PnL, drawdown, sector exposure,
- nuôi cache cho frontend.

Repo hiện tại hỗ trợ tốt hơn ở các điểm sau:

- Có hướng batch fetch cho nhiều mã.
- Có proxy support và retry để job nền ít gãy hơn.
- Có benchmark và telemetry để tìm concurrency phù hợp.
- Có cấu trúc test đủ ổn để refactor thêm mà không bị mù.

Điều đó có nghĩa là nếu bạn có worker nền chạy mỗi 5 phút hoặc cuối ngày, repo này hợp hơn nhiều so với việc gọi tuần tự từng mã bằng wrapper đơn giản.

### 2. Robo-advisor rule-based

Nếu robo-advisor của bạn hiện ở mức:

- lọc mã theo liquidity/sector,
- tính momentum/value/quality score,
- rebalance theo lịch,
- xuất đề xuất tỷ trọng,

thì repo hiện tại cũng phù hợp hơn vì phần data ingestion là nền móng quan trọng nhất. Một robo-advisor yếu ở dữ liệu sẽ fail trước cả khi phần model hoặc ranking phát huy tác dụng.

Repo này giúp ở 3 việc:

- giảm thời gian nạp dữ liệu nền,
- tăng độ bền khi backend nguồn chập chờn,
- cho phép đo benchmark để biết giới hạn tải thật.

## Mapping từ repo này sang kiến trúc hệ thống

Nếu hệ thống của bạn dùng React + Django + Pandas + Redis + Celery, có thể map như sau:

### Tầng dữ liệu

- `vnstock/api/*` và `vnstock/explorer/*`: adapter lấy dữ liệu từ các provider.
- `vnstock/core/utils/async_client.py`: dùng cho batch fetch, retry, rate limit, telemetry.
- `vnstock/core/utils/proxy_manager.py`: quản lý proxy pool khi chạy môi trường dễ block IP.

### Tầng ingestion/service

- Celery worker gọi `Quote.fetch_multiple(...)` hoặc wrapper tương đương để nạp nhiều mã.
- Redis giữ cache ngắn hạn cho quote, watchlist, benchmark result.
- Django management command hoặc scheduled task gọi benchmark theo khung giờ.

### Tầng analytics

- Pandas xử lý indicator, score, ranking, allocation.
- Snapshot dữ liệu đã chuẩn hóa được lưu thành table hoặc parquet/CSV tùy hệ thống.

### Tầng API/UI

- Django REST trả danh mục, watchlist, signals, benchmark report.
- React chỉ tiêu thụ dữ liệu đã được cache hoặc materialize, không gọi trực tiếp nguồn market data ở frontend.

## Những gì nên dùng ngay

Các phần nên tận dụng ngay trong repo hiện tại:

1. `Quote.fetch_multiple(...)` cho batch fetch VCI.
2. `ProxyManager.get_proxy_pool(...)` cho môi trường cloud hoặc IP dễ bị chặn.
3. Benchmark script để chốt safe concurrency theo từng workload.
4. Telemetry `attempts/retries/429/5xx/timeout/transport` để chẩn đoán bottleneck.

## Những gì vẫn nên tự bọc thêm ở tầng ứng dụng

Repo hiện tại tốt hơn `vnstock` chuẩn, nhưng vẫn chưa nên bị hiểu là một data platform hoàn chỉnh. Ở tầng ứng dụng bạn vẫn nên tự thêm:

1. Data cache policy.
2. Persistent storage schema cho OHLC, holdings, signals, rebalance history.
3. Idempotent job orchestration.
4. Alerting khi backend data source bất ổn.
5. Access control và tenant separation nếu nhiều user dùng chung hệ thống.

## Roadmap tích hợp đề xuất

### Phase 1: Data ingestion ổn định

Mục tiêu:

- chốt provider chính,
- chốt concurrency an toàn,
- có benchmark baseline,
- có cache quote ngắn hạn.

Việc nên làm:

1. Dùng benchmark script để đo workload thật theo watchlist hoặc holdings của bạn.
2. Chốt `max_concurrency` cho VCI/KBS theo từng nhóm tác vụ.
3. Bọc một service layer riêng trong Django/Celery thay vì gọi thẳng từ view.

### Phase 2: Chuẩn hóa data model

Mục tiêu:

- dữ liệu giá, thông tin doanh nghiệp, danh mục và tín hiệu có schema rõ ràng.

Việc nên làm:

1. Chuẩn hóa OHLC schema chung cho mọi provider.
2. Tách raw fetch và processed snapshot.
3. Lưu benchmark report định kỳ để theo dõi drift hiệu năng.

### Phase 3: Rule engine cho robo-advisor

Mục tiêu:

- từ data ingestion chuyển sang signal generation.

Việc nên làm:

1. Tạo pipeline tính features bằng Pandas.
2. Tách signal job và rebalance job.
3. Lưu audit trail cho mỗi lần sinh khuyến nghị.

### Phase 4: Production hardening

Mục tiêu:

- hệ thống chạy bền hơn khi thị trường tải cao hoặc nguồn dữ liệu lỗi.

Việc nên làm:

1. Thêm cache layer theo symbol/timeframe.
2. Thêm fallback source khi provider chính lỗi.
3. Thêm alert theo tỷ lệ fail, timeout, 429.
4. Benchmark định kỳ theo giờ giao dịch.

## Khi nào repo hiện tại đáng giá hơn `vnstock` chuẩn

Bạn nên dùng repo hiện tại nếu có ít nhất 2 điều sau:

- Watchlist hoặc holdings đủ lớn để batch fetch có ý nghĩa.
- Cần chạy job định kỳ thay vì notebook thủ công.
- Có môi trường cloud dễ bị chặn IP.
- Muốn tuning hiệu năng bằng số liệu thay vì cảm giác.
- Muốn tiếp tục fork và tối ưu như một data engine nội bộ.

Nếu chưa có các nhu cầu trên, `vnstock` chuẩn có thể vẫn là lựa chọn đơn giản hơn.

## Mốc code liên quan

- `vnstock/explorer/vci/quote.py`
- `vnstock/core/utils/proxy_manager.py`
- `vnstock/core/utils/async_client.py`
- `tests/examples/vci_perf_benchmark.py`
- `docs/VNSTOCK_COMPARISON.md`