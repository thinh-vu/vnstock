# Run the test with coverage report:

# pytest tests/test_explorer/2_functional/utils/parser.py \
#   --cov=vnstock.core.utils.parser \
#   --cov-report=term-missing \
#   --cov-report=html:htmlcov/parser

import re
import pytest
from datetime import date, datetime, timedelta
import pandas as pd
import numpy as np
from cryptography.fernet import Fernet
import base64

from vnstock.core.utils import parser
from vnstock.core.config.const import UA

# Helpers for decd tests
def _make_fernet():
    kb = UA['Chrome'].replace(' ', '').ljust(32)[:32].encode('utf-8')
    kb64 = base64.urlsafe_b64encode(kb)
    return Fernet(kb64)

class TestParseTimestamp:
    def test_with_datetime(self):
        dt = datetime(2025,5,10,15,30,0)
        ts = parser.parse_timestamp(dt)
        assert isinstance(ts, int)
        # roughly equals dt.timestamp()
        assert ts == int(parser.timezone('Asia/Ho_Chi_Minh').localize(dt).timestamp())

    @pytest.mark.parametrize("s,expected", [
        ("2025-05-10 15:30:00", datetime(2025,5,10,15,30,0)),
        ("2025-05-10 15:30",    datetime(2025,5,10,15,30,0)),
        ("2025-05-10",          datetime(2025,5,10,0,0,0)),
    ])
    def test_with_string(self, s, expected):
        ts = parser.parse_timestamp(s)
        # convert back to localized datetime
        dt_local = datetime.fromtimestamp(ts, parser.timezone('Asia/Ho_Chi_Minh'))
        assert dt_local.year == expected.year
        assert dt_local.month == expected.month
        assert dt_local.day == expected.day
        assert dt_local.hour == expected.hour
        assert dt_local.minute == expected.minute

    def test_invalid_string(self, capsys):
        assert parser.parse_timestamp("not a date") is None
        captured = capsys.readouterr()
        assert "Invalid timestamp format" in captured.out

    def test_invalid_type(self, capsys):
        assert parser.parse_timestamp(12345) is None
        captured = capsys.readouterr()
        assert "Invalid input type" in captured.out

class TestLocalizeTimestamp:
    @pytest.fixture
    def sample_ts(self):
        # 1 Jan 2025 00:00 UTC
        return 1735689600

    def test_scalar_default(self, sample_ts):
        series = parser.localize_timestamp(sample_ts)
        assert isinstance(series, pd.Series)
        assert len(series) == 1
        ts0 = series.iloc[0]
        assert ts0.tzinfo.zone == 'Asia/Ho_Chi_Minh'

    def test_scalar_return_scalar(self, sample_ts):
        ts = parser.localize_timestamp(sample_ts, return_scalar=True)
        assert isinstance(ts, pd.Timestamp)
        assert ts.tzinfo.zone == 'Asia/Ho_Chi_Minh'

    def test_scalar_return_string(self, sample_ts):
        s = parser.localize_timestamp(
            sample_ts,
            return_scalar=True,
            return_string=True,
            string_format="%Y"
        )
        assert s == "2025"

    def test_list_return_string_series(self, sample_ts):
        arr = [sample_ts, sample_ts + 60]
        sr = parser.localize_timestamp(
            arr,
            unit='s',
            return_string=True,
            string_format="%Y-%m-%d"
        )
        assert all(v == "2025-01-01" for v in sr)

    def test_series_length1(self, sample_ts):
        sr_in = pd.Series([sample_ts])
        out = parser.localize_timestamp(sr_in, return_scalar=True)
        assert isinstance(out, pd.Timestamp)

class TestGetAssetType:
    @pytest.mark.parametrize("sym,exp", [
        ("VNINDEX", "index"),
        ("vn30",    "index"),
        ("ABC",     "stock"),
        ("VN30F1M", "derivative"),
        ("VN30F2512","derivative"),
        ("GB05F2506","bond"),
        ("BAB122032","bond"),
        ("XYZ123456","bond"),
        ("ABCDEF01","coveredWarr"),
    ])
    def test_valid(self, sym, exp):
        assert parser.get_asset_type(sym) == exp

    @pytest.mark.parametrize("sym", ["TOO_LONG_SYMBOL", "AB", "ZZZ999"])
    def test_invalid(self, sym):
        with pytest.raises(ValueError):
            parser.get_asset_type(sym)

class TestCamelToSnake:
    @pytest.mark.parametrize("inp,exp", [
        ("CamelCase", "camel_case"),
        ("HTTPResponseCode", "http_response_code"),
        ("name.with.dots", "name_with_dots"),
        ("simple", "simple"),
    ])
    def test_conversion(self, inp, exp):
        assert parser.camel_to_snake(inp) == exp

class TestFlattenData:
    def test_flatten_simple(self):
        data = {"a":1, "b":{"c":2, "d":{"e":3}}}
        flat = parser.flatten_data(data)
        assert flat == {"a":1, "b_c":2, "b_d_e":3}

class TestLastNDays:
    def test_zero(self):
        today = datetime.today().strftime('%Y-%m-%d')
        assert parser.last_n_days(0) == today

    def test_positive(self):
        yesterday = (datetime.today() - timedelta(days=1)).strftime('%Y-%m-%d')
        assert parser.last_n_days(1) == yesterday

class TestDecd:
    def test_decd_roundtrip(self):
        f = _make_fernet()
        plaintext = "hello world"
        token = f.encrypt(plaintext.encode('utf-8'))
        result = parser.decd(token)
        assert result == plaintext

    def test_decd_wrong_input(self):
        with pytest.raises(Exception):
            parser.decd(b"notvalidtoken")

class TestVN30Contracts:
    @pytest.fixture
    def ref_date(self):
        return date(2025, 5, 15)

    @pytest.mark.parametrize("abbr,full", [
        ("VN30F1M", "VN30F2505"),  # May: first monthly
        ("VN30F2M", "VN30F2506"),  # June: second monthly expansion
        ("VN30F1Q", "VN30F2506"),  # June: also valid as first quarterly
        ("VN30F2Q", "VN30F2509"),  # September: second quarterly
    ])
    def test_expand(self, abbr, full, ref_date):
        # Ensure expand handles both M and Q inputs correctly
        assert parser.vn30_expand_contract(abbr, ref_date) == full

    @pytest.mark.parametrize("full,abbr", [
        ("VN30F2505", "VN30F1M"),  # May → first monthly
        ("VN30F2506", "VN30F1Q"),  # June → first quarterly (per current logic)
        ("VN30F2509", "VN30F2Q"),  # September → second quarterly
    ])
    def test_abbrev(self, full, abbr, ref_date):
        out = parser.vn30_abbrev_contract(full, ref_date)
        assert out == abbr

    def test_expand_invalid(self, ref_date):
        # invalid abbreviation format and wrong types
        with pytest.raises(ValueError):
            parser.vn30_expand_contract("VN30F0M", ref_date)
        with pytest.raises(TypeError):
            parser.vn30_expand_contract(123, ref_date)

    def test_abbrev_invalid(self, ref_date):
        # invalid full code format and wrong types
        with pytest.raises(ValueError):
            parser.vn30_abbrev_contract("VN30F9999", ref_date)
        with pytest.raises(TypeError):
            parser.vn30_abbrev_contract("VN30F2505", "notadate")