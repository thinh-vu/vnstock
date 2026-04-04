"""Tests for VCI benchmark report export helpers."""

from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path

from tests.examples.vci_perf_benchmark import (
    BatchResult,
    batch_result_to_dict,
    build_report_payload,
    write_results_csv,
    write_results_json,
)


def make_result(concurrency: int) -> BatchResult:
    return BatchResult(
        concurrency=concurrency,
        runs=2,
        symbols=3,
        success_count=6,
        failure_count=0,
        elapsed_seconds=1.5,
        requests_per_second=4.0,
        requests_per_minute=240.0,
        p50_latency_seconds=0.7,
        p95_latency_seconds=1.1,
        min_latency_seconds=0.6,
        max_latency_seconds=1.2,
        mean_latency_seconds=0.8,
        total_attempts=6,
        retry_attempts=1,
        throttled_responses=0,
        server_error_responses=0,
        timeout_errors=0,
        transport_errors=0,
    )


def make_args() -> argparse.Namespace:
    return argparse.Namespace(
        runs=2,
        concurrency="4,8",
        interval="1D",
        start="2026-03-31",
        end="2026-04-03",
        length="",
        count_back=5,
        symbol_file="",
        symbol_limit=30,
        output_csv="",
        output_json="",
    )


def test_batch_result_to_dict_adds_summary_fields():
    result = make_result(8)

    payload = batch_result_to_dict(result)

    assert payload["total_requests"] == 6
    assert payload["success_rate"] == 100.0
    assert payload["retry_attempts"] == 1


def test_write_results_csv_creates_report(tmp_path: Path):
    out_path = tmp_path / "reports" / "benchmark.csv"
    rows = [make_result(4), make_result(8)]

    write_results_csv(out_path, rows)

    with out_path.open("r", encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f)
        records = list(reader)

    assert len(records) == 2
    assert records[0]["concurrency"] == "4"
    assert records[1]["retry_attempts"] == "1"


def test_write_results_json_creates_report(tmp_path: Path):
    out_path = tmp_path / "reports" / "benchmark.json"
    rows = [make_result(4), make_result(8)]
    args = make_args()

    write_results_json(out_path, rows, ["ACB", "VCB", "TCB"], args)

    with out_path.open("r", encoding="utf-8") as f:
        payload = json.load(f)

    assert payload["symbols"] == ["ACB", "VCB", "TCB"]
    assert payload["best"]["concurrency"] == 4
    assert payload["config"]["count_back"] == 5
    assert len(payload["rows"]) == 2


def test_build_report_payload_selects_best_by_rps():
    rows = [make_result(4), make_result(8)]
    rows[1].requests_per_second = 5.0

    payload = build_report_payload(rows, ["ACB"], make_args())

    assert payload["best"]["concurrency"] == 8