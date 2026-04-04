# So sánh `vnstock` chuẩn và repo hiện tại

Tài liệu này tóm tắt các khác biệt đáng chú ý giữa:

- `vnstock` chuẩn: cách hiểu thực dụng là bản stable/upstream mà đa số người dùng cài trực tiếp để sử dụng API công khai.
- Repo hiện tại: bản đang làm việc trong workspace này, bao gồm cả các tối ưu đã được thêm cho VCI async, proxy pool, benchmark và telemetry.

Mục tiêu của bảng này không phải liệt kê mọi khác biệt nhỏ, mà tập trung vào những thay đổi có tác động trực tiếp đến vận hành, hiệu năng và khả năng mở rộng.

## Bảng so sánh nhanh

| Nhóm | `vnstock` chuẩn | Repo hiện tại | Tác động thực tế |
| --- | --- | --- | --- |
| Kiến trúc provider | Có adapter/provider nhưng người dùng thường chỉ cảm nhận như API wrapper truyền thống | Tách provider, registry, lazy loading rõ hơn; dễ mở rộng nhiều nguồn dữ liệu | Dễ thay backend, giảm coupling khi xây dashboard, ETL và service nội bộ |
| Nguồn dữ liệu mặc định | Thiên về trải nghiệm dùng sẵn | KBS đã trở thành nguồn mặc định, VCI vẫn giữ vai trò quan trọng cho explorer | Giảm phụ thuộc một nguồn duy nhất, linh hoạt hơn khi một backend lỗi hoặc thay đổi |
| API lịch sử giá | Hỗ trợ `history` theo `start/end` là chính | Hỗ trợ thêm `length`, `count_back`, lookback linh hoạt | Dễ viết pipeline nạp dữ liệu định kỳ, ít phải tự tính ngày |
| Độ bền request | Có retry ở adapter public | Có retry ở adapter và thêm đường async cho batch, proxy fallback, auto proxy mode | Chạy ổn hơn trên cloud, notebook, IP dễ bị block |
| Proxy support | Có nhưng thường chưa được tối ưu cho batch performance | ProxyManager có cache TTL, refresh interval, test song song, pool dùng chung cho batch | Giảm overhead khi fetch nhiều mã, giảm tail latency do proxy discovery lặp lại |
| Batch/concurrency | Thiên về gọi API theo từng mã hoặc từng tác vụ | VCI có `fetch_multiple`, dùng shared proxy pool, rate limit async client | Phù hợp hơn cho tracker, screener nội bộ, warm-up cache, job nền |
| Quan sát hiệu năng | Thường người dùng tự đo bằng script ngoài | Có benchmark script, export CSV/JSON, telemetry retry/429/5xx/timeout/transport | Dễ tìm đúng điểm nghẽn thay vì đoán theo latency tổng |
| Test/CI | Có test nhưng trải nghiệm người dùng cuối ít thấy rõ | Cấu trúc test rõ, benchmark regression, CI/CD đa nền tảng | An toàn hơn khi refactor hoặc thêm nguồn dữ liệu mới |
| Hỗ trợ hệ thống đầu tư cá nhân | Đủ để nghiên cứu và truy xuất dữ liệu | Phù hợp hơn để nhúng vào service hoặc batch workflow bán-production | Hợp với bài toán portfolio tracker, robo-advisor, data sync job |

## Điểm cải thiện quan trọng nhất của repo hiện tại

### 1. Tối ưu cho batch workload thay vì chỉ gọi lẻ

Phần VCI trong repo hiện tại đã có đường gọi async cho nhiều mã cùng lúc, thay vì mỗi lần xử lý một mã theo phong cách request-response đơn giản. Khi chạy benchmark hoặc prefetch dữ liệu cho danh mục, khác biệt này là đáng kể.

Ý nghĩa thực tế:

- Thích hợp hơn cho job đồng bộ watchlist hoặc holdings.
- Dễ tune concurrency theo tải thật.
- Giảm thời gian chờ tổng khi nạp nhiều mã một lúc.

### 2. Proxy manager thực dụng hơn cho môi trường dễ bị chặn IP

Repo hiện tại không chỉ có proxy support ở mức “có thể dùng”, mà đã được đẩy sang hướng vận hành thực tế hơn:

- Có cache pool đã test.
- Có giới hạn refresh để tránh retest liên tục.
- Có test proxy song song.
- Có pool dùng chung cho cả batch thay vì mỗi symbol tự đi tìm proxy.

Ý nghĩa thực tế:

- Giảm chi phí warm-up khi chạy trên Colab/Kaggle/cloud VM.
- Giảm p95 do bỏ được phần proxy discovery lặp lại ở đường nóng.
- Ít request chết vì chọn proxy kém ổn định quá thường xuyên.

### 3. Benchmark có giá trị vận hành hơn

Repo hiện tại đã có benchmark không chỉ trả về throughput, mà còn có thể ghi lại:

- success/fail
- p50/p95/min/max/mean
- attempts/retries
- số lần gặp `429`
- số lỗi `5xx`
- timeout và transport error

Ý nghĩa thực tế:

- Nếu tốc độ chậm nhưng `retries=0`, vấn đề nghiêng về latency upstream hơn là retry storm.
- Nếu `429` tăng theo concurrency, có thể khóa ngưỡng safe concurrency theo backend.
- Nếu timeout/transport error tăng khi bật proxy, bottleneck nằm ở proxy path chứ không phải API chính.

### 4. Hợp hơn với hệ thống portfolio tracker hoặc robo-advisor

Với bài toán ứng dụng thực tế như:

- đồng bộ giá cuối ngày cho danh mục,
- làm service cập nhật watchlist,
- cache dữ liệu cho dashboard,
- tính tín hiệu định kỳ,

repo hiện tại tốt hơn `vnstock` chuẩn ở chỗ nó gần với yêu cầu “vận hành được” hơn là chỉ “gọi được dữ liệu”.

## Những điểm vẫn cần nhìn thực tế

Repo hiện tại mạnh hơn về engineering, nhưng không có nghĩa là mọi thứ đều tốt hơn trong mọi tình huống.

Một số đánh đổi:

- Code phức tạp hơn bản dùng đơn giản.
- Khi thêm proxy, async và benchmark, chi phí bảo trì cũng tăng.
- Nếu nhu cầu chỉ là notebook cá nhân, bản chuẩn có thể đã đủ.
- Nếu muốn chạy production-like workflow, repo hiện tại đáng giá hơn rõ rệt.

## Kết luận ngắn

Nếu mục tiêu là học, thử API và phân tích thủ công, `vnstock` chuẩn là đủ cho nhiều trường hợp.

Nếu mục tiêu là xây hệ thống theo kiểu:

- nạp dữ liệu nhiều mã,
- chạy job định kỳ,
- cần fallback/proxy,
- cần biết tại sao chậm,
- cần benchmark để tune,

thì repo hiện tại là một bước tiến rõ rệt theo hướng engineering và vận hành.

Nếu cần nhìn theo đúng use case ứng dụng, xem thêm `docs/PORTFOLIO_ROBOADVISOR_GUIDE.md`.

Nếu mục tiêu là thay bản chuẩn bằng bản fork trong môi trường dev/prod/CI, xem `docs/FORK_MIGRATION_GUIDE.md`.

## Mốc code nên xem tiếp

- `vnstock/base.py`
- `vnstock/api/quote.py`
- `vnstock/explorer/vci/quote.py`
- `vnstock/core/utils/proxy_manager.py`
- `vnstock/core/utils/async_client.py`
- `tests/examples/vci_perf_benchmark.py`