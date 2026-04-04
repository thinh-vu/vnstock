"""Compare the current vnstock repo against the installed standard vnstock package.

Usage examples:
- python -m tests.examples.compare_vnstock_libraries --symbols ACB,VCB,TCB --runs 1 --count-back 5 --start 2026-03-31 --end 2026-04-03
- python -m tests.examples.compare_vnstock_libraries --symbols ACB,VCB,TCB,HPG,VNM --runs 3 --count-back 20 --start 2026-03-20 --end 2026-04-03 --repo-concurrency 8
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
import tempfile
import textwrap
from dataclasses import dataclass
from pathlib import Path
from typing import Any, List


@dataclass
class LibraryBenchmarkResult:
    label: str
    import_path: str
    version: str
    strategy: str
    symbols: int
    runs: int
    warmup_runs: int
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
    error: str = ""


@dataclass
class WorkloadComparisonRow:
    workload: str
    symbols: int
    runs: int
    warmup_runs: int
    repo_concurrency: int
    installed_strategy: str
    repo_strategy: str
    installed_rpm: float
    repo_rpm: float
    installed_elapsed: float
    repo_elapsed: float
    speedup: float
    installed_success: int
    repo_success: int
    installed_fail: int
    repo_fail: int
    installed_error: str
    repo_error: str


def parse_symbols(raw_symbols: str) -> List[str]:
    values = [value.strip().upper() for value in raw_symbols.split(",") if value.strip()]
    if not values:
        raise ValueError("No symbols provided")
    return values


def parse_positive_int_list(raw: str, fallback: int) -> List[int]:
    values = [part.strip() for part in raw.split(",") if part.strip()]
    if not values:
        return [fallback]
    parsed = [int(value) for value in values]
    if any(value <= 0 for value in parsed):
        raise ValueError("All values must be positive integers")
    return parsed


def build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Compare current vnstock repo with installed vnstock package")
    parser.add_argument("--symbols", type=str, default="ACB,VCB,TCB")
    parser.add_argument("--interval", type=str, default="1D")
    parser.add_argument("--start", type=str, default="")
    parser.add_argument("--end", type=str, default="")
    parser.add_argument("--length", type=str, default="")
    parser.add_argument("--count-back", type=int, default=0)
    parser.add_argument("--runs", type=int, default=1)
    parser.add_argument("--workload-runs-list", type=str, default="")
    parser.add_argument("--warmup-runs", type=int, default=1)
    parser.add_argument("--repo-concurrency", type=int, default=8)
    parser.add_argument("--repo-concurrency-list", type=str, default="")
    return parser


def build_child_code() -> str:
    return textwrap.dedent(
        r'''
        import importlib.metadata
        import json
        import statistics
        import sys
        import time

        MODE = sys.argv[1]
        PAYLOAD = json.loads(sys.argv[2])

        try:
            from vnstock.explorer.vci.quote import Quote
            import vnstock

            version = importlib.metadata.version("vnstock")
            import_path = getattr(vnstock, "__file__", "") or ""
            symbols = PAYLOAD["symbols"]
            latencies = []
            success_count = 0
            failure_count = 0
            strategy_holder = {"value": "sequential"}

            def execute_once():
                if MODE == "repo" and hasattr(Quote, "fetch_multiple"):
                    import asyncio

                    strategy_holder["value"] = "batch"
                    return asyncio.run(
                        Quote.fetch_multiple(
                            symbols=symbols,
                            start=PAYLOAD["start"],
                            end=PAYLOAD["end"],
                            interval=PAYLOAD["interval"],
                            count_back=PAYLOAD["count_back"],
                            length=PAYLOAD["length"],
                            max_concurrency=PAYLOAD["repo_concurrency"],
                            show_log=False,
                        )
                    )

                results = []
                for symbol in symbols:
                    quote = Quote(symbol=symbol, show_log=False)
                    try:
                        df = quote.history(
                            start=PAYLOAD["start"],
                            end=PAYLOAD["end"],
                            interval=PAYLOAD["interval"],
                            count_back=PAYLOAD["count_back"],
                            length=PAYLOAD["length"],
                            show_log=False,
                        )
                        results.append(df)
                    except Exception:
                        pass
                return results

            for _ in range(PAYLOAD["warmup_runs"]):
                execute_once()

            started = time.perf_counter()
            for _ in range(PAYLOAD["runs"]):
                t0 = time.perf_counter()
                results = execute_once()

                t1 = time.perf_counter()
                latencies.append(t1 - t0)
                success_count += len(results)
                failure_count += max(len(symbols) - len(results), 0)

            finished = time.perf_counter()
            elapsed = max(finished - started, 1e-9)
            total_requests = PAYLOAD["runs"] * len(symbols)
            sorted_latencies = sorted(latencies)

            result = {
                "label": PAYLOAD["label"],
                "import_path": import_path,
                "version": version,
                "strategy": strategy_holder["value"],
                "symbols": len(symbols),
                "runs": PAYLOAD["runs"],
                "warmup_runs": PAYLOAD["warmup_runs"],
                "success_count": success_count,
                "failure_count": failure_count,
                "elapsed_seconds": elapsed,
                "requests_per_second": total_requests / elapsed,
                "requests_per_minute": (total_requests / elapsed) * 60,
                "p50_latency_seconds": statistics.median(sorted_latencies),
                "p95_latency_seconds": (
                    statistics.quantiles(sorted_latencies, n=100)[94]
                    if len(sorted_latencies) >= 2
                    else sorted_latencies[0]
                ),
                "min_latency_seconds": min(sorted_latencies),
                "max_latency_seconds": max(sorted_latencies),
                "mean_latency_seconds": statistics.mean(sorted_latencies),
                "error": "",
            }
        except Exception as exc:
            result = {
                "label": PAYLOAD["label"],
                "import_path": "",
                "version": "",
                "strategy": "error",
                "symbols": len(PAYLOAD.get("symbols", [])),
                "runs": PAYLOAD.get("runs", 0),
                "warmup_runs": PAYLOAD.get("warmup_runs", 0),
                "success_count": 0,
                "failure_count": 0,
                "elapsed_seconds": 0.0,
                "requests_per_second": 0.0,
                "requests_per_minute": 0.0,
                "p50_latency_seconds": 0.0,
                "p95_latency_seconds": 0.0,
                "min_latency_seconds": 0.0,
                "max_latency_seconds": 0.0,
                "mean_latency_seconds": 0.0,
                "error": str(exc),
            }

        print(json.dumps(result, ensure_ascii=True))
        '''
    ).strip()


def run_benchmark_subprocess(
    mode: str,
    cwd: Path,
    payload: dict[str, Any],
) -> LibraryBenchmarkResult:
    command = [
        sys.executable,
        "-c",
        build_child_code(),
        mode,
        json.dumps(payload, ensure_ascii=True),
    ]
    completed = subprocess.run(
        command,
        cwd=str(cwd),
        capture_output=True,
        text=True,
        timeout=600,
        check=False,
    )

    raw_output = completed.stdout.strip().splitlines()
    if not raw_output:
        error = completed.stderr.strip() or "No output from child benchmark"
        return LibraryBenchmarkResult(
            label=payload["label"],
            import_path="",
            version="",
            strategy="error",
            symbols=len(payload["symbols"]),
            runs=payload["runs"],
            warmup_runs=payload["warmup_runs"],
            success_count=0,
            failure_count=0,
            elapsed_seconds=0.0,
            requests_per_second=0.0,
            requests_per_minute=0.0,
            p50_latency_seconds=0.0,
            p95_latency_seconds=0.0,
            min_latency_seconds=0.0,
            max_latency_seconds=0.0,
            mean_latency_seconds=0.0,
            error=error,
        )

    parsed = json.loads(raw_output[-1])
    if completed.returncode != 0 and not parsed.get("error"):
        parsed["error"] = completed.stderr.strip() or f"Child exited with code {completed.returncode}"
    return LibraryBenchmarkResult(**parsed)


def format_seconds(value: float) -> str:
    return f"{value:8.2f}s"


def format_float(value: float) -> str:
    return f"{value:8.2f}"


def print_table(results: List[LibraryBenchmarkResult]) -> None:
    headers = [
        "library",
        "strategy",
        "success",
        "fail",
        "elapsed",
        "rpm",
        "p50",
        "p95",
        "mean",
    ]
    rows = []
    for result in results:
        rows.append([
            result.label,
            result.strategy,
            str(result.success_count),
            str(result.failure_count),
            format_seconds(result.elapsed_seconds),
            format_float(result.requests_per_minute),
            format_seconds(result.p50_latency_seconds),
            format_seconds(result.p95_latency_seconds),
            format_seconds(result.mean_latency_seconds),
        ])

    widths = [len(header) for header in headers]
    for row in rows:
        for index, value in enumerate(row):
            widths[index] = max(widths[index], len(value))

    def _print_row(values: List[str]) -> None:
        print(" | ".join(value.ljust(widths[index]) for index, value in enumerate(values)))

    _print_row(headers)
    print("-+-".join("-" * width for width in widths))
    for row in rows:
        _print_row(row)


def print_summary(results: List[LibraryBenchmarkResult]) -> None:
    print("\n=== Details ===")
    for result in results:
        print(f"{result.label}: version={result.version} | import={result.import_path}")
        if result.error:
            print(f"  error: {result.error}")

    healthy = [result for result in results if not result.error]
    if len(healthy) >= 2:
        baseline = healthy[0]
        challenger = healthy[1]
        if baseline.elapsed_seconds > 0 and challenger.elapsed_seconds > 0:
            speedup = baseline.elapsed_seconds / challenger.elapsed_seconds
            rpm_gain = challenger.requests_per_minute - baseline.requests_per_minute
            print("\n=== Comparison ===")
            print(
                f"{challenger.label} is {speedup:.2f}x faster than {baseline.label} "
                f"for this workload by elapsed time."
            )
            print(
                f"RPM delta: {rpm_gain:.2f} | "
                f"{baseline.label}={baseline.requests_per_minute:.2f}, "
                f"{challenger.label}={challenger.requests_per_minute:.2f}"
            )


def print_workload_table(rows: List[WorkloadComparisonRow]) -> None:
    headers = [
        "workload",
        "runs",
        "repo_cc",
        "installed_rpm",
        "repo_rpm",
        "speedup",
        "installed_elapsed",
        "repo_elapsed",
        "installed_ok/fail",
        "repo_ok/fail",
    ]
    matrix: List[List[str]] = []
    for row in rows:
        matrix.append(
            [
                row.workload,
                str(row.runs),
                str(row.repo_concurrency),
                f"{row.installed_rpm:.2f}",
                f"{row.repo_rpm:.2f}",
                f"{row.speedup:.2f}x",
                f"{row.installed_elapsed:.2f}s",
                f"{row.repo_elapsed:.2f}s",
                f"{row.installed_success}/{row.installed_fail}",
                f"{row.repo_success}/{row.repo_fail}",
            ]
        )

    widths = [len(header) for header in headers]
    for row in matrix:
        for index, value in enumerate(row):
            widths[index] = max(widths[index], len(value))

    def _print(values: List[str]) -> None:
        print(" | ".join(value.ljust(widths[index]) for index, value in enumerate(values)))

    _print(headers)
    print("-+-".join("-" * width for width in widths))
    for row in matrix:
        _print(row)


def run_one_workload(
    repo_root: Path,
    payload: dict[str, Any],
) -> tuple[LibraryBenchmarkResult, LibraryBenchmarkResult]:
    with tempfile.TemporaryDirectory(prefix="vnstock-installed-") as tmp_dir:
        installed_result = run_benchmark_subprocess(
            mode="installed",
            cwd=Path(tmp_dir),
            payload={**payload, "label": "vnstock-installed"},
        )

        repo_result = run_benchmark_subprocess(
            mode="repo",
            cwd=repo_root,
            payload={**payload, "label": "vnstock-repo"},
        )
    return installed_result, repo_result


def main() -> int:
    args = build_arg_parser().parse_args()
    repo_root = Path(__file__).resolve().parents[2]
    symbols = parse_symbols(args.symbols)
    run_levels = parse_positive_int_list(args.workload_runs_list, args.runs)
    repo_concurrency_levels = parse_positive_int_list(
        args.repo_concurrency_list,
        args.repo_concurrency,
    )

    print("=== Vnstock Library Comparison Benchmark ===")
    print(f"Symbols: {symbols}")
    print(f"Runs levels: {run_levels}")
    print(f"Warmup runs: {args.warmup_runs}")
    print(f"Interval: {args.interval}")
    if args.start or args.end:
        print(f"Range: {args.start or '-'} -> {args.end or '-'}")
    if args.count_back > 0:
        print(f"Count back: {args.count_back}")
    if args.length:
        print(f"Length: {args.length}")
    print(f"Repo concurrency levels: {repo_concurrency_levels}")
    print()

    comparison_rows: List[WorkloadComparisonRow] = []
    first_workload_results: List[LibraryBenchmarkResult] | None = None

    for run_value in run_levels:
        for concurrency_value in repo_concurrency_levels:
            payload = {
                "symbols": symbols,
                "interval": args.interval,
                "start": args.start or None,
                "end": args.end or None,
                "length": args.length or None,
                "count_back": args.count_back if args.count_back > 0 else None,
                "runs": run_value,
                "warmup_runs": args.warmup_runs,
                "repo_concurrency": concurrency_value,
            }
            installed_result, repo_result = run_one_workload(repo_root, payload)
            if first_workload_results is None:
                first_workload_results = [installed_result, repo_result]

            speedup = 0.0
            if installed_result.elapsed_seconds > 0 and repo_result.elapsed_seconds > 0:
                speedup = installed_result.elapsed_seconds / repo_result.elapsed_seconds

            comparison_rows.append(
                WorkloadComparisonRow(
                    workload=f"w{run_value}-c{concurrency_value}",
                    symbols=len(symbols),
                    runs=run_value,
                    warmup_runs=args.warmup_runs,
                    repo_concurrency=concurrency_value,
                    installed_strategy=installed_result.strategy,
                    repo_strategy=repo_result.strategy,
                    installed_rpm=installed_result.requests_per_minute,
                    repo_rpm=repo_result.requests_per_minute,
                    installed_elapsed=installed_result.elapsed_seconds,
                    repo_elapsed=repo_result.elapsed_seconds,
                    speedup=speedup,
                    installed_success=installed_result.success_count,
                    repo_success=repo_result.success_count,
                    installed_fail=installed_result.failure_count,
                    repo_fail=repo_result.failure_count,
                    installed_error=installed_result.error,
                    repo_error=repo_result.error,
                )
            )

    print("=== Workload Comparison Table ===")
    print_workload_table(comparison_rows)

    if first_workload_results is not None:
        print("\n=== First Workload Raw Details ===")
        print_table(first_workload_results)
        print_summary(first_workload_results)

    errored = [
        row for row in comparison_rows if row.installed_error or row.repo_error
    ]
    if errored:
        print("\n=== Workload Errors ===")
        for row in errored:
            print(f"{row.workload} installed_error={row.installed_error or '-'}")
            print(f"{row.workload} repo_error={row.repo_error or '-'}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())