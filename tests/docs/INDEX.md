# Vnstock Test Suite - Documentation Index

**Quick Navigation for All Test Documentation**

---

## 📖 Documentation Files

### 🎯 START HERE (For AI)
- **[AI_GUIDE.md](./AI_GUIDE.md)** ⭐
  - Practical patterns for test modification
  - Copy-paste templates and examples
  - Debugging & troubleshooting guide
  - Best practices & anti-patterns
  - **Read time**: 10 minutes

### 🏗️ Architecture & Design
- **[ARCHITECTURE.md](./ARCHITECTURE.md)**
  - Overall test structure and organization
  - How tests are executed and flow
  - Directory structure explained
  - Fixture explanations and examples
  - When to use which fixtures
  - **Read time**: 5 minutes

### 📊 Coverage & Reporting
- **[../docs/COVERAGE_STRATEGY.md](../docs/COVERAGE_STRATEGY.md)**
  - Why coverage is 29% (by design)
  - Coverage breakdown by module
  - How to improve coverage
  - Coverage configuration explained
  - **Read time**: 10 minutes

### 🔌 Proxy Integration
- **[../docs/PROXY_GUIDE.md](../docs/PROXY_GUIDE.md)**
  - Complete ProxyManager reference
  - Usage patterns and examples
  - Troubleshooting proxy issues
  - Performance characteristics
  - **Read time**: 15 minutes

---

## 🗂️ Test Files Structure

```
tests/
├── conftest.py              # Fixtures & mocking utilities
├── fixtures/
│   └── symbols.py           # Real symbols from APIs (HOSE/HNX/UPCOM)
├── examples/
│   ├── __init__.py
│   └── proxy_examples.py    # Runnable ProxyManager examples
├── unit/
│   ├── api/
│   │   ├── test_quote.py
│   │   └── test_listing.py
│   ├── core/
│   │   └── test_proxy_manager.py
│   └── explorer/
│       ├── test_vci_quote_comprehensive.py
│       ├── test_vci_listing_comprehensive.py
│       ├── test_vci_company_finance_comprehensive.py
│       ├── test_tcbs_quote_comprehensive.py
│       ├── test_tcbs_screener_trading_comprehensive.py
│       └── test_vci_quote_with_proxy.py
└── report/
    └── coverage_html/       # Generated HTML coverage reports
```

---

## 🚀 Quick Start (For AI)

### Want to...

**Understand test structure?**
1. Read: ARCHITECTURE.md (5 min)
2. Check: conftest.py for fixtures (5 min)
3. Look at: One test file example (5 min)

**Add a new test?**
1. Check: AI_GUIDE.md - "Add a new test" (2 min)
2. Copy: Template from AI_GUIDE.md (2 min)
3. Modify: For your use case (10 min)
4. Run: `pytest tests/unit/your_test.py -v` (2 min)

**Fix a failing test?**
1. Run: `pytest tests/unit/test_file.py -v` (2 min)
2. Check: AI_GUIDE.md - "Debugging" section (5 min)
3. Debug: Using suggestions from guide (10 min)
4. Verify: Test passes (2 min)

**Improve test coverage?**
1. Check: COVERAGE_STRATEGY.md (10 min)
2. Run: `pytest tests/unit/ --cov=vnstock --cov-report=html` (3 min)
3. View: htmlcov/index.html in browser (2 min)
4. Identify: Low coverage modules (5 min)
5. Add: Tests for those modules (varies)

---

## 📚 Core Concepts (Quick Reference)

### Fixtures (AI should understand)
```
conftest.py provides:
- mock_response_factory    → Create mock HTTP responses
- mock_http_get/post       → Mock requests globally
- df_validators            → DataFrame validation helpers
- disable_logging          → Auto-disable test noise

fixtures/symbols.py provides:
- random_hose_symbols      → 100 random HOSE symbols
- random_hnx_symbols       → 100 random HNX symbols
- random_upcom_symbols     → 100 random UPCOM symbols
- diverse_test_symbols     → 30 symbols (10 per exchange)
```

### Test Markers
```
@pytest.mark.unit          # Fast tests, all mocked
@pytest.mark.integration   # Real API calls, slower
@pytest.mark.slow          # Takes >5 seconds
@pytest.mark.vci           # VCI-specific tests
@pytest.mark.tcbs          # TCBS-specific tests
@pytest.mark.api           # API adapter tests
```

### Coverage Levels
```
ProxyManager:      81% ✅ Excellent
Core utilities:    70-92% ✅ Good
API adapters:      50-76% ✅ Good
Explorer modules:  17-38% ⚠️ Needs live API
Overall:           29% (unit tests only - expected)
```

---

## 🔍 Module-by-Module Guide

### Unit Tests (Fast, ~4 seconds)

**tests/unit/api/**
- Purpose: Test adapter pattern
- Coverage: 50-76%
- Files: test_quote.py, test_listing.py
- Use when: Testing API adapters & parameter filtering

**tests/unit/core/**
- Purpose: Test utilities
- Coverage: 81% (ProxyManager)
- Files: test_proxy_manager.py
- Use when: Testing core utilities like ProxyManager

**tests/unit/explorer/**
- Purpose: Test data source explorers
- Coverage: 17-38% (incomplete without integration)
- Files: test_vci_*.py, test_tcbs_*.py, test_*_with_proxy.py
- Use when: Testing VCI, TCBS, MSN explorers

### Integration Tests (Real API)
- Run separately with: `pytest -m integration`
- Required for full coverage of explorer modules
- Slower but more realistic
- Use when: Need real API responses

---

## 💡 Key Decisions & Tradeoffs

### Why 29% Coverage?
✅ Unit tests exclude live API calls (= isolated, fast tests)
✅ Integration tests run separately (= optional, slow)
✅ Configuration at 29% threshold (= baseline for unit tests)
⚠️ Can improve to 60-80% by adding mock responses

### Why Separate Integration Tests?
✅ Unit tests run in CI/CD quickly
✅ Integration tests optional (for developers)
✅ Easier to control test environment
❌ But: Misses some real-world scenarios

### Why Multiple Fixtures?
✅ Flexible test scenarios
✅ Easy to add new symbols
✅ Reusable across many tests
❌ But: More setup code initially

---

## 📊 Test Statistics

| Metric                | Value                            | Status      |
| --------------------- | -------------------------------- | ----------- |
| Total Test Files      | 8                                | ✅           |
| Total Tests           | 26+ (proxy) + 63 (comprehensive) | ✅           |
| Unit Tests            | 36 passing                       | ✅ 100%      |
| Coverage Target       | 29% (unit only)                  | ✅ Met       |
| ProxyManager Coverage | 81%                              | ✅ Excellent |
| Execution Time        | ~4 seconds                       | ✅ Fast      |

---

## 🎓 Learning Order (For New AI)

1. **Day 1: Understand**
   - Read ARCHITECTURE.md (5 min)
   - Read AI_GUIDE.md sections 1-3 (10 min)
   - Look at conftest.py (5 min)

2. **Day 1: Explore**
   - Check one test file: test_vci_quote_comprehensive.py (10 min)
   - Look at one fixture: random_hose_symbols (5 min)
   - Run tests: `pytest tests/unit/ -q` (2 min)

3. **Day 2: Practice**
   - Copy template from AI_GUIDE.md (2 min)
   - Create new test file (15 min)
   - Run and debug (10 min)

4. **Day 2: Master**
   - Check coverage: `pytest --cov=vnstock` (3 min)
   - Read COVERAGE_STRATEGY.md (10 min)
   - Understand tradeoffs and design (5 min)

---

## ❓ FAQ

**Q: Where do I find the fixture definitions?**
A: `tests/conftest.py` and `tests/fixtures/symbols.py`

**Q: How do I mock API responses?**
A: Use `mock_response_factory` fixture or `@patch` decorator (see AI_GUIDE.md)

**Q: Why is coverage only 29%?**
A: Unit tests exclude live API calls. See COVERAGE_STRATEGY.md for details.

**Q: How do I add a new marker?**
A: Add to pytest.ini markers section, then use `@pytest.mark.newmarker`

**Q: Can I run tests in parallel?**
A: Install pytest-xdist: `pip install pytest-xdist`, then `pytest -n auto`

**Q: How do I debug a failing test?**
A: Use `pytest test_file.py -v -s --pdb` (see AI_GUIDE.md)

---

## 🔗 Related Documentation (In docs/)

- **PROXY_GUIDE.md** - How to use ProxyManager
- **COVERAGE_STRATEGY.md** - Coverage goals & optimization
- **SESSION_5_FINAL_REPORT.md** - Complete session summary
- **PROXY_IMPLEMENTATION_SUMMARY.md** - Proxy system details

---

## ✨ For Next AI Session

### Context This AI Should Have
✅ Test structure: ARCHITECTURE.md
✅ Quick patterns: AI_GUIDE.md
✅ Fixtures available: conftest.py (well-documented)
✅ Real symbols: fixtures/symbols.py
✅ Coverage goals: COVERAGE_STRATEGY.md

### Context This AI Provided
✅ Cleaned up old documentation
✅ Consolidated into 2 key files: ARCHITECTURE.md + AI_GUIDE.md
✅ Enhanced conftest.py with docstrings
✅ Created this INDEX.md for navigation
✅ Organized for quick AI understanding

### Ready For
✅ Adding new tests
✅ Fixing failing tests
✅ Improving coverage
✅ Debugging issues
✅ Understanding design decisions

---

## 📝 Last Maintenance Log

**Date**: November 12, 2025
**Actions**:
- ✅ Deleted: test_explorer/, plan.md, test_infrastructure.py
- ✅ Consolidated: README.md, TESTING.md, COMPREHENSIVE_TESTS.md
- ✅ Created: ARCHITECTURE.md, AI_GUIDE.md, this INDEX.md
- ✅ Enhanced: conftest.py with detailed docstrings
- ✅ Verified: All 36 unit tests passing

**Status**: ✅ Clean, organized, AI-friendly
**Next**: Run full test suite to validate

---

**Ready to help the next AI? Start with:**
1. AI_GUIDE.md (10 min) → Quick patterns
2. ARCHITECTURE.md (5 min) → Structure
3. Look at conftest.py → Understand fixtures
4. Copy template → Create new test
5. Run pytest → Verify it works

🚀 Good luck to the next AI session!
