# GitHub Actions Testing Integration

Comprehensive guide for vnstock's automated testing and quality assurance using GitHub Actions.

## Overview

The vnstock project uses GitHub Actions to automatically test, validate, and report on code quality whenever changes are pushed or pull requests are created.

## Workflows

### 1. Main Test Suite (`test.yml`)

**Trigger**: Push to main/develop, PR to main/develop, Daily schedule (2 AM UTC)

**What it does**:
- Runs comprehensive test suite across multiple platforms and Python versions
- Tests on: Ubuntu, macOS, Windows
- Python versions: 3.10, 3.11, 3.12, 3.13
- Generates coverage reports
- Uploads results to Codecov

**Key Jobs**:
- `test`: Unit and integration tests with coverage
- `code-quality`: Linting, formatting, type checking
- `security`: Security scanning with Bandit and Safety
- `build`: Package building and validation
- `test-report`: Test result reporting

**Artifacts**:
- Coverage reports (HTML, XML)
- JUnit test results
- Distribution packages

### 2. Coverage Report (`coverage-report.yml`)

**Trigger**: Push to main/develop, PR to main/develop

**What it does**:
- Generates detailed coverage reports
- Uploads to Codecov for tracking
- Comments on PRs with coverage changes
- Sets coverage thresholds (Green: 80%, Orange: 60%)

**Artifacts**:
- HTML coverage report
- Coverage XML report

### 3. Code Quality (`code-quality.yml`)

**Trigger**: Push to main/develop, PR to main/develop

**What it does**:
- Linting with flake8
- Code formatting check with black
- Import sorting check with isort
- Type checking with mypy
- Security scanning with Bandit
- Dependency vulnerability check with Safety

**Reports**:
- Linting violations
- Security issues
- Dependency vulnerabilities

### 4. Performance Testing (`performance.yml`)

**Trigger**: Push to main/develop, PR to main/develop, Daily schedule (3 AM UTC)

**What it does**:
- Runs performance benchmarks
- Compares with baseline
- Tracks performance trends
- Alerts on performance regressions (>10%)

**Artifacts**:
- Benchmark results (JSON)
- Performance comparison reports

## Test Coverage

### Current Coverage Targets

- **Minimum**: 29% (unit tests without live integration)
- **Target**: 80%+
- **Critical modules**: 90%+

### Covered Modules

- `vnstock/api/` - API layer (Quote, Listing, Company, Finance, Trading)
- `vnstock/explorer/` - Data source explorers (VCI, TCBS, KBS)
- `vnstock/core/utils/` - Core utilities (field handling, client, auth)
- `vnstock/common/` - Common utilities (data, visualization)

### Test Categories

- **Unit Tests**: Fast, isolated tests (~500+ tests)
- **Integration Tests**: Tests with external services
- **Smoke Tests**: Basic functionality checks
- **Regression Tests**: Tests for fixed bugs

## Running Tests Locally

### Quick Start

```bash
# Install test dependencies
pip install -e ".[test]"

# Run all tests
pytest tests/

# Run with coverage
pytest tests/ --cov=vnstock --cov-report=html
```

### Advanced Usage

```bash
# Run specific test file
pytest tests/unit/api/test_quote.py -v

# Run tests matching pattern
pytest tests/ -k "quote" -v

# Run tests with specific marker
pytest tests/ -m "unit and vci" -v

# Run tests in parallel
pytest tests/ -n auto

# Run with timeout
pytest tests/ --timeout=30

# Generate detailed report
pytest tests/ -v --tb=long --durations=10
```

## Viewing Results

### GitHub Actions Dashboard

1. Go to repository → Actions tab
2. Select workflow (Test, Coverage, Code Quality, Performance)
3. View job logs and artifacts

### Coverage Reports

1. Download coverage artifact from Actions
2. Extract and open `htmlcov/index.html` in browser
3. View coverage by file and line

### Performance Reports

1. Check Performance workflow artifacts
2. View benchmark comparisons
3. Track performance trends over time

## PR Checks

When you create a pull request, the following checks run automatically:

1. ✅ **Tests Pass** - All unit and integration tests must pass
2. ✅ **Coverage** - Coverage must not decrease significantly
3. ✅ **Code Quality** - No major linting violations
4. ✅ **Security** - No security vulnerabilities detected
5. ✅ **Build** - Package must build successfully

### PR Comments

GitHub Actions will comment on your PR with:
- Coverage changes
- Test results summary
- Code quality issues
- Performance changes

## Troubleshooting

### Tests Fail on CI but Pass Locally

**Common causes**:
- Python version differences
- Platform-specific issues (Windows/macOS/Linux)
- Network/API issues
- Timing issues

**Solutions**:
- Test on same Python version as CI
- Use mocks for external dependencies
- Add retry logic for flaky tests
- Check for platform-specific code

### Coverage Drops

**Common causes**:
- New code without tests
- Removed tests
- Conditional code not covered

**Solutions**:
- Add tests for new code
- Check coverage report for uncovered lines
- Use `--cov-report=term-missing` to see missing lines

### Performance Regression

**Common causes**:
- Algorithm changes
- New dependencies
- Resource usage increase

**Solutions**:
- Review performance changes
- Optimize hot paths
- Profile with benchmarks
- Check for memory leaks

## Best Practices

### For Developers

1. **Run tests locally before pushing**
   ```bash
   pytest tests/ --cov=vnstock
   ```

2. **Use meaningful commit messages**
   - Helps identify which changes caused issues

3. **Add tests for new features**
   - Maintain coverage above 80%

4. **Fix failing tests immediately**
   - Don't let test failures accumulate

5. **Review PR comments**
   - Address coverage and quality issues

### For Maintainers

1. **Monitor workflow runs**
   - Check for flaky tests
   - Track performance trends

2. **Update dependencies regularly**
   - Keep tools and libraries current
   - Monitor security advisories

3. **Adjust thresholds as needed**
   - Increase coverage targets gradually
   - Set realistic performance baselines

4. **Document test requirements**
   - Keep TESTING_GUIDE.md updated
   - Document new test patterns

## Configuration Files

### `.github/workflows/`
- `test.yml` - Main test suite
- `coverage-report.yml` - Coverage reporting
- `code-quality.yml` - Code quality checks
- `performance.yml` - Performance testing

### Root Level
- `pytest.ini` - Pytest configuration
- `.flake8` - Flake8 linting rules
- `pyproject.toml.testing` - Tool configurations

### Tests Directory
- `tests/conftest.py` - Pytest fixtures
- `tests/conftest_enhancements.py` - Advanced fixtures
- `tests/TESTING_GUIDE.md` - Testing documentation

## Customization

### Modify Test Schedule

Edit `.github/workflows/test.yml`:
```yaml
schedule:
  - cron: '0 2 * * *'  # Change time here
```

### Adjust Coverage Threshold

Edit `pytest.ini`:
```ini
--cov-fail-under=29  # Change threshold here
```

### Add New Workflow

1. Create new file in `.github/workflows/`
2. Define triggers and jobs
3. Commit and push
4. GitHub Actions will automatically detect and run it

## Resources

- [GitHub Actions Documentation](https://docs.github.com/en/actions)
- [Pytest Documentation](https://docs.pytest.org/)
- [Coverage.py](https://coverage.readthedocs.io/)
- [Codecov](https://codecov.io/)

## Support

For issues or questions about testing:

1. Check `tests/TESTING_GUIDE.md`
2. Review workflow logs in Actions tab
3. Open issue with test failure details
4. Contact maintainers
