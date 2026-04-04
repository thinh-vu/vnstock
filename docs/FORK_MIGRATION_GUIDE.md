# Hướng dẫn dùng bản fork này thay `vnstock` chuẩn

Tài liệu này hướng dẫn chuyển từ bản `vnstock` chuẩn (PyPI/upstream) sang bản fork trong repo hiện tại một cách an toàn.

## 1. Khi nào nên dùng bản fork

Nên chuyển sang bản fork khi bạn cần:

- batch fetch nhiều mã với hiệu năng tốt hơn,
- proxy fallback và proxy pool ổn định hơn,
- benchmark/telemetry để tune concurrency,
- workflow backend job (Django + Celery + Redis) thay vì chỉ notebook thủ công.

Nếu bạn chỉ dùng notebook đơn giản với khối lượng nhỏ, bản chuẩn vẫn có thể đủ.

## 2. Cách cài đặt bản fork

## 2.1 Local dev

```bash
pip uninstall -y vnstock
pip install git+https://github.com/<your-user>/<your-repo>.git@main
```

## 2.2 Khóa theo commit cụ thể (ổn định hơn)

```bash
pip uninstall -y vnstock
pip install git+https://github.com/<your-user>/<your-repo>.git@<commit-sha>
```

## 2.3 Cài editable khi phát triển trực tiếp trong repo

```bash
pip uninstall -y vnstock
pip install -e .
```

## 3. Kiểm tra đã thay thành công chưa

```bash
python -c "import vnstock, importlib.metadata as m; print(m.version('vnstock')); print(vnstock.__file__)"
```

Kỳ vọng:

- `m.version('vnstock')` có version mong muốn.
- `vnstock.__file__` trỏ tới source của repo fork hoặc site-packages được cài từ fork.

## 4. Cập nhật requirements cho team

Trong `requirements.txt` hoặc file lock tương đương:

```txt
git+https://github.com/<your-user>/<your-repo>.git@main#egg=vnstock
```

Hoặc pin commit:

```txt
git+https://github.com/<your-user>/<your-repo>.git@<commit-sha>#egg=vnstock
```

## 5. Cập nhật CI/CD

Trong pipeline:

1. Gỡ bản cache cũ nếu cần.
2. Cài package từ fork URL.
3. Chạy smoke test xác nhận import path.

Ví dụ lệnh smoke test:

```bash
python -c "import vnstock; print(vnstock.__file__)"
```

## 6. Tương thích cách gọi hàm

## 6.1 Những call thường không cần đổi

Đa số call phổ biến vẫn giữ nguyên, ví dụ:

- `Quote(...).history(...)`
- `Listing(...)`, `Company(...)`, `Finance(...)`, `Trading(...)`

## 6.2 Điều nên chuẩn hóa để tránh khác biệt hành vi

1. Chỉ định `source` rõ ràng thay vì phụ thuộc mặc định.
2. Viết test cho các luồng đang dùng thật trong dự án.
3. Chỉ bật thêm tính năng mới (batch/proxy/telemetry) sau khi baseline pass.

## 6.3 Tính năng mới có thể áp dụng dần

- `length`/`count_back` cho lookback linh hoạt.
- batch fetch cho VCI.
- proxy pool + refresh policy.
- benchmark so sánh bản cài và bản fork.

## 7. Checklist migration thực tế

1. Chốt branch/commit của fork sẽ deploy.
2. Cập nhật requirements sang Git URL của fork.
3. Cài lại môi trường sạch.
4. Chạy smoke test import path.
5. Chạy unit/integration test quan trọng của dự án.
6. Chạy benchmark workload thật để chốt concurrency.
7. Triển khai canary trước khi rollout toàn bộ.

## 8. Tài liệu liên quan

- `docs/VNSTOCK_COMPARISON.md`
- `docs/PORTFOLIO_ROBOADVISOR_GUIDE.md`
- `tests/examples/vci_perf_benchmark.py`
- `tests/examples/compare_vnstock_libraries.py`