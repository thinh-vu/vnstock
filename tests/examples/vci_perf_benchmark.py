"""Benchmark VCI quote throughput and latency.

Usage examples:
- python -m tests.examples.vci_perf_benchmark --symbols ACB,VCB,TCB,HPG,VNM --runs 3
- python -m tests.examples.vci_perf_benchmark --symbol-file assets/data/vn30_symbols.csv --concurrency 12,24,36 --interval 1D --length 3M
"""

from __future__ import annotations

import argparse
import asyncio
import csv
import json
import sys
import statistics
import time
import types
from dataclasses import asdict, dataclass
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List

try:
    import vnai  # type: ignore
except Exception:
    # Minimal shim to run benchmarks when vnai is unavailable in local env.
    def _noop_decorator(*_args, **_kwargs):
        def _wrap(func):
            return func
        return _wrap

    vnai = types.SimpleNamespace(optimize_execution=_noop_decorator, setup=lambda: None)
    sys.modules["vnai"] = vnai

from vnstock.explorer.vci.quote import Quote
from vnstock.core.utils.async_client import (
    get_async_request_stats,
    reset_async_request_stats,
)


@dataclass
class BatchResult:
    concurrency: int
    runs: int
    symbols: int
    success_count: int
    failure_count: int
    elapsed_seconds: float
    requests_per_second: float
    requests_per_minute: float
    p50_latency_seconds: float
    p95_latency_seconds: float
    min_latency_seconds: float
    max_latency_seconds: float
    mean_latency_seconds: float
    total_attempts: int
    retry_attempts: int
    throttled_responses: int
    server_error_responses: int
    timeout_errors: int
    transport_errors: int


def batch_result_to_dict(result: BatchResult) -> Dict[str, Any]:
    data = asdict(result)
    total = result.runs * result.symbols
    data["total_requests"] = total
    data["success_rate"] = (
        (result.success_count / total) * 100 if total else 0.0
    )
    return data


def parse_symbols(raw_symbols: str) -> List[str]:
    values = [s.strip().upper() for s in raw_symbols.split(",") if s.strip()]
    if not values:
        raise ValueError("No symbols provided")
    return values


def load_symbols_from_csv(path: Path, limit: int) -> List[str]:
    if not path.exists():
        raise FileNotFoundError(f"Symbol file not found: {path}")

    symbols: List[str] = []
    with path.open("r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        cols = {name.lower(): name for name in (reader.fieldnames or [])}
        symbol_col = cols.get("symbol")
        if symbol_col is None:
            raise ValueError("CSV must contain a 'symbol' column")

        for row in reader:
            symbol = str(row.get(symbol_col, "")).strip().upper()
            if symbol:
                symbols.append(symbol)
            if limit > 0 and len(symbols) >= limit:
                break

    if not symbols:
        raise ValueError("No symbols loaded from CSV")
    return symbols


async def run_one_batch(
    symbols: List[str],
    concurrency: int,
    interval: str,
    start: str | None,
    end: str | None,
    length: str | int | None,
    count_back: int | None,
    runs: int,
) -> BatchResult:
    latencies: List[float] = []
    success_count = 0
    failure_count = 0
    reset_async_request_stats()

    started = time.perf_counter()
    for _ in range(runs):
        t0 = time.perf_counter()
        results = await Quote.fetch_multiple(
            symbols=symbols,
            start=start,
            end=end,
            interval=interval,
            count_back=count_back,
            length=length,
            max_concurrency=concurrency,
            show_log=False,
        )
        t1 = time.perf_counter()

        run_latency = t1 - t0
        latencies.append(run_latency)
        success_count += len(results)
        failure_count += max(len(symbols) - len(results), 0)

    finished = time.perf_counter()
    elapsed = max(finished - started, 1e-9)

    total_requests = runs * len(symbols)
    rps = total_requests / elapsed
    rpm = rps * 60

    sorted_latencies = sorted(latencies)
    p50 = statistics.median(sorted_latencies)
    p95 = (
        statistics.quantiles(sorted_latencies, n=100)[94]
        if len(sorted_latencies) >= 2
        else sorted_latencies[0]
    )
    request_stats = get_async_request_stats()

    return BatchResult(
        concurrency=concurrency,
        runs=runs,
        symbols=len(symbols),
        success_count=success_count,
        failure_count=failure_count,
        elapsed_seconds=elapsed,
        requests_per_second=rps,
        requests_per_minute=rpm,
        p50_latency_seconds=p50,
        p95_latency_seconds=p95,
        min_latency_seconds=min(sorted_latencies),
        max_latency_seconds=max(sorted_latencies),
        mean_latency_seconds=statistics.mean(sorted_latencies),
        total_attempts=request_stats["total_attempts"],
        retry_attempts=request_stats["retry_attempts"],
        throttled_responses=request_stats["throttled_responses"],
        server_error_responses=request_stats["server_error_responses"],
        timeout_errors=request_stats["timeout_errors"],
        transport_errors=request_stats["transport_errors"],
    )


def format_row(r: BatchResult) -> str:
    total = r.runs * r.symbols
    success_rate = (r.success_count / total) * 100 if total else 0
    return (
        f"concurrency={r.concurrency:>3} | total={total:>4} | success={r.success_count:>4} "
        f"| fail={r.failure_count:>4} "
        f"({success_rate:6.2f}%) | elapsed={r.elapsed_seconds:7.2f}s | "
        f"rps={r.requests_per_second:7.2f} | rpm={r.requests_per_minute:8.2f} | "
        f"p50={r.p50_latency_seconds:6.2f}s | p95={r.p95_latency_seconds:6.2f}s | "
        f"min={r.min_latency_seconds:6.2f}s | max={r.max_latency_seconds:6.2f}s | "
        f"mean={r.mean_latency_seconds:6.2f}s | attempts={r.total_attempts:>4} | "
        f"retries={r.retry_attempts:>4} | 429={r.throttled_responses:>3} | "
        f"5xx={r.server_error_responses:>3} | timeout={r.timeout_errors:>3} | "
        f"transport={r.transport_errors:>3}"
    )


def ensure_parent_dir(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)


def write_results_csv(path: Path, rows: List[BatchResult]) -> None:
    ensure_parent_dir(path)
    fieldnames = list(batch_result_to_dict(rows[0]).keys()) if rows else []
    with path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        if fieldnames:
            writer.writeheader()
            for row in rows:
                writer.writerow(batch_result_to_dict(row))


def build_report_payload(
    rows: List[BatchResult],
    symbols: List[str],
    args: argparse.Namespace,
) -> Dict[str, Any]:
    best = max(rows, key=lambda r: r.requests_per_second) if rows else None
    return {
        "generated_at": datetime.now().isoformat(timespec="seconds"),
        "symbols": symbols,
        "config": {
            "runs": args.runs,
            "concurrency": parse_concurrency(args.concurrency),
            "interval": args.interval,
            "start": args.start or None,
            "end": args.end or None,
            "length": args.length or None,
            "count_back": args.count_back if args.count_back > 0 else None,
            "symbol_file": args.symbol_file or None,
            "symbol_limit": args.symbol_limit,
        },
        "rows": [batch_result_to_dict(row) for row in rows],
        "best": batch_result_to_dict(best) if best else None,
    }


def write_results_json(
    path: Path,
    rows: List[BatchResult],
    symbols: List[str],
    args: argparse.Namespace,
) -> None:
    ensure_parent_dir(path)
    payload = build_report_payload(rows=rows, symbols=symbols, args=args)
    with path.open("w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=True, indent=2)
        f.write("\n")


def parse_concurrency(raw: str) -> List[int]:
    values = [int(x.strip()) for x in raw.split(",") if x.strip()]
    if not values:
        raise ValueError("Concurrency list is empty")
    if any(v <= 0 for v in values):
        raise ValueError("Concurrency must be positive")
    return values


def build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="VCI performance benchmark")
    parser.add_argument("--symbols", type=str, default="ACB,VCB,TCB,HPG,VNM")
    parser.add_argument("--symbol-file", type=str, default="")
    parser.add_argument("--symbol-limit", type=int, default=30)
    parser.add_argument("--concurrency", type=str, default="8,16,24")
    parser.add_argument("--interval", type=str, default="1D")
    parser.add_argument("--start", type=str, default="")
    parser.add_argument("--end", type=str, default="")
    parser.add_argument("--length", type=str, default="3M")
    parser.add_argument("--count-back", type=int, default=0)
    parser.add_argument("--runs", type=int, default=3)
    parser.add_argument("--output-csv", type=str, default="")
    parser.add_argument("--output-json", type=str, default="")
    return parser


async def main_async(args: argparse.Namespace) -> int:
    if args.symbol_file:
        symbols = load_symbols_from_csv(Path(args.symbol_file), limit=args.symbol_limit)
    else:
        symbols = parse_symbols(args.symbols)

    concurrency_levels = parse_concurrency(args.concurrency)

    print("=== VCI Throughput Benchmark ===")
    print(f"Symbols: {len(symbols)}")
    print(f"Runs per level: {args.runs}")
    print(f"Concurrency levels: {concurrency_levels}")
    print("Target backend limit: 600 req/min")

    rows: List[BatchResult] = []
    for c in concurrency_levels:
        result = await run_one_batch(
            symbols=symbols,
            concurrency=c,
            interval=args.interval,
            start=args.start or None,
            end=args.end or None,
            length=(args.length if args.length else None),
            count_back=(args.count_back if args.count_back > 0 else None),
            runs=args.runs,
        )
        rows.append(result)
        print(format_row(result))

    print("\n=== Summary ===")
    best = max(rows, key=lambda r: r.requests_per_second)
    print("Best throughput:")
    print(format_row(best))

    if args.output_csv:
        csv_path = Path(args.output_csv)
        write_results_csv(csv_path, rows)
        print(f"CSV report: {csv_path}")

    if args.output_json:
        json_path = Path(args.output_json)
        write_results_json(json_path, rows, symbols, args)
        print(f"JSON report: {json_path}")

    return 0


def main() -> int:
    parser = build_arg_parser()
    args = parser.parse_args()
    return asyncio.run(main_async(args))


if __name__ == "__main__":
    raise SystemExit(main())
