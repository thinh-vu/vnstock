## Test Plan for `vnstock` Explorer Modules

### 1. Introduction

This document outlines the test plan for the `explorer/` directory of the `vnstock` Python package. It defines objectives, scope, testing phases, structure, execution strategy, and CI integration.

### 2. Objectives

* **1\_smoke (Phase 1)**: Verify all public explorer APIs import, instantiate, and return a `pandas.DataFrame` without errors.
* **2\_functional (Phase 2)**: Validate parsing logic, column names, dtypes, and business rules against representative fixtures.
* **3\_edge (Phase 3)**: Cover empty responses, malformed payloads, HTTP errors, timeouts, and boundary conditions.
* **4\_scenarios (Phase 4)**: Simulate real usage by combining multiple classes and methods, mixing data sources, and end-to-end scenario workflows.
* **5\_performance (Phase 5)**: Benchmark parsing speed, memory usage, and built-in rate-limit handling for large-batch operations.
* **6\_regression (Phase 6)**: Prevent recurrence of specific, previously fixed bugs with dedicated test cases.
* Achieve at least **90% code coverage** on the `explorer/` directory.
* Generate test results and coverage reports under `tests/report/` for CI consumption.

### 3. Scope Scope

**In scope:**

* All modules under `vnstock/explorer/`:

  * `fmarket/const.py`, `fmarket/fund.py`
  * `misc/exchange_rate.py`, `misc/gold_price.py`
  * `msn/const.py`, `msn/helper.py`, `msn/listing.py`, `msn/models.py`, `msn/quote.py`
  * `tcbs/quote.py`, `tcbs/screener.py`, `tcbs/trading.py`
  * `vci/analysis.py`, `vci/company.py`, `vci/const.py`, `vci/financial.py`, `vci/listing.py`, `vci/models.py`, `vci/quote.py`, `vci/trading.py`

**Out of scope:**

* Core utilities outside the explorer directory.
* Live API integration beyond Phase 4 tests.

### 4. Test Phases & Directory Structure

```
tests/
├── fixtures/                   # Sample API payloads for Phase 2+3
│   ├── fmarket_fund.json
│   ├── exchange_rate.json
│   ├── gold_price.json
│   └── ...
├── report/                     # Test results & coverage outputs
│   ├── junit-results.xml
│   ├── coverage.xml
│   └── coverage_html/
└── test_explorer/
    ├── 1_smoke/                # Phase 1: Smoke tests
    │   └── test_smoke.py
    ├── 2_functional/           # Phase 2: Functional correctness
    │   ├── test_fmarket_fund.py
    │   ├── test_misc_exchange_rate.py
    │   ├── test_misc_gold_price.py
    │   ├── test_msn_listing.py
    │   ├── test_msn_quote.py
    │   ├── test_tcbs_quote.py
    │   ├── test_tcbs_screener.py
    │   ├── test_tcbs_trading.py
    │   ├── test_vci_listing.py
    │   ├── test_vci_quote.py
    │   └── ...
    ├── 3_edge/                 # Phase 3: Edge-case & error handling
    │   ├── test_empty_payloads.py
    │   ├── test_malformed_json.py
    │   └── test_http_error_codes.py
    ├── 4_integration/          # Phase 4: Live/staging integration tests
    │   ├── test_live_msn_listing.py
    │   └── ...
    ├── 5_performance/          # Phase 5: Performance benchmarks
    │   └── test_parsing_speed.py
    └── 6_regression/           # Phase 6: Regression tests for fixed bugs
        ├── test_bug_1234_fix.py
        └── ...
```

### 5. Phase Descriptions

* **Phase 1: Smoke Tests**

  * **Objective:** Quickly catch broken imports, missing signatures, or runtime errors.
  * **Implementation:** Parametrized pytest in `1_smoke/test_smoke.py` that monkeypatches HTTP calls to return minimal responses and asserts a `DataFrame` is returned.

* **Phase 2: Functional Tests**

  * **Objective:** Verify correct data extraction, column names, dtypes, and business logic.
  * **Implementation:** Module-specific tests under `2_functional/` using fixtures in `fixtures/` and monkeypatched HTTP clients.

* **Phase 3: Edge-Case Tests**

  * **Objective:** Ensure modules handle empty responses, malformed data, timeouts, and non-200 HTTP codes gracefully.
  * **Implementation:** Dedicated tests in `3_edge/` feeding edge-case fixtures and asserting appropriate fallback or exceptions.

* **Phase 4: Scenario Combination Tests**

  * **Objective:** Simulate real usage by combining multiple classes and methods, mixing data sources, and exercising overlapping functionality (e.g., initializing different explorer classes in sequence, chaining methods, or mixing responses from multiple sources).
  * **Implementation:** Tests in `4_integration/` (renamed to reflect scenario tests) that:

    * Instantiate several explorer classes in one test.
    * Monkeypatch different fixtures per class to verify isolation and composition.
    * Use parametrization to run cross-class workflows (e.g., fetch listing then quote then trading history for same symbol).

* **Phase 5: Performance & Rate-Limit Tests**

  * **Objective:** Detect regressions in parsing speed, memory usage, and built-in rate-limit handling when processing large batches (hundreds to thousands of symbols).
  * **Implementation:** Tests in `5_performance/` that use `pytest-benchmark` or manual timing to:

    * Request intraday or history data for 100+ symbols in parallel or sequentially.
    * Assert average per-request latency stays below threshold.
    * Simulate rate-limit responses (e.g., HTTP 429) and verify package backoff or retry behavior.

* **Phase 6: Regression Tests**

  * **Objective:** Prevent recurrence of specific, previously fixed bugs.
  * **Implementation:** One-off test files in `6_regression/` that replicate bug conditions and assert correct behavior.

### 6. Test Execution & Reporting Test Execution & Reporting

* **Run all tests:**

  ```bash
  pytest --maxfail=1 --disable-warnings -q
  ```
* **JUnit report:**

  ```bash
  pytest --junitxml=tests/report/junit-results.xml
  ```
* **Coverage reports:**

  ```bash
  pytest --cov=vnstock/explorer \
         --cov-report=html:tests/report/coverage_html \
         --cov-report=xml:tests/report/coverage.xml
  ```

### 7. Continuous Integration

1. **Install dependencies** including `pytest`, `pytest-cov`, `pytest-benchmark`.
2. **Run Phases**: You can split jobs by folder (e.g., smoke first), or run all together.
3. **Fail fast** on smoke failures or coverage below threshold.
4. **Publish** badges and archive reports.

### 8. Execute the tests

#### Install package from source

```bash
python3.10 -m pip install .
```

#### 1. Smoke Tests

```bash
python3.10 -m pytest tests/test_explorer/1_smoke --maxfail=1 -q
```

#### 2. Functional Tests

```bash
python3.10 -m pytest tests/test_explorer/2_functional --maxfail=1 -q
```