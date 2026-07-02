"""Quote module for DNSE (Entrade) data source."""

from datetime import datetime, timezone
from typing import List, Optional, Union

import pandas as pd
from vnai import optimize_execution

from vnstock.core.registry import ProviderRegistry  # noqa: E402, F401
from vnstock.core.utils.client import ProxyConfig, send_request
from vnstock.core.utils.logger import get_logger
from vnstock.core.utils.lookback import (
    get_start_date_from_lookback,
    interpret_lookback_length,
)
from vnstock.core.utils.user_agent import get_headers
from vnstock.explorer.dnse.const import (
    _INTERVAL_MAP,
    _INTRADAY_CORE_COLUMNS,
    _INTRADAY_MAP,
    _INTRADAY_URL,
    _OHLC_DTYPE,
    _OHLC_MAP,
    _OHLC_URL,
)

logger = get_logger(__name__)


def _to_unix_timestamp(date_str: str) -> int:
    """Convert YYYY-MM-DD to Unix epoch seconds (UTC midnight)."""
    try:
        dt = datetime.strptime(date_str, "%Y-%m-%d")
        return int(dt.replace(tzinfo=timezone.utc).timestamp())
    except ValueError as e:
        raise ValueError(
            f"Ngày không hợp lệ: {date_str}. Định dạng yêu cầu: YYYY-MM-DD"
        ) from e


class Quote:
    """
    Lớp truy cập dữ liệu giá lịch sử từ DNSE (Entrade).
    """

    def __init__(
        self,
        symbol: str,
        random_agent: Optional[bool] = False,
        proxy_config: Optional[ProxyConfig] = None,
        show_log: Optional[bool] = False,
        proxy_mode: Optional[str] = None,
        proxy_list: Optional[List[str]] = None,
    ):
        """
        Khởi tạo Quote client cho DNSE.

        Args:
            symbol: Mã chứng khoán (VD: 'ACB', 'VNM').
            random_agent: Sử dụng user agent ngẫu nhiên. Mặc định False.
            proxy_config: Cấu hình proxy. Mặc định None.
            show_log: Hiển thị log debug. Mặc định False.
            proxy_mode: Chế độ proxy. Mặc định None.
            proxy_list: Danh sách proxy URLs. Mặc định None.
        """
        self.symbol = symbol.upper()
        self.data_source = "DNSE"
        self.headers = get_headers(
            data_source=self.data_source, random_agent=random_agent
        )
        self.show_log = show_log
        self.interval_map = _INTERVAL_MAP

        if proxy_config is None:
            p_mode = proxy_mode if proxy_mode else "try"
            req_mode = "proxy" if proxy_list and len(proxy_list) > 0 else "direct"
            self.proxy_config = ProxyConfig(
                proxy_mode=p_mode, proxy_list=proxy_list, request_mode=req_mode
            )
        else:
            self.proxy_config = proxy_config

        if not show_log:
            logger.setLevel("CRITICAL")

    @optimize_execution("DNSE")
    def history(
        self,
        start: Optional[str] = None,
        end: Optional[str] = None,
        interval: Optional[str] = "1D",
        to_df: Optional[bool] = True,
        show_log: Optional[bool] = False,
        count_back: Optional[int] = None,
        floating: Optional[int] = 2,
        length: Optional[Union[str, int]] = None,
        get_all: Optional[bool] = False,
    ) -> Union[pd.DataFrame, str]:
        """
        Tải lịch sử giá của mã chứng khoán từ DNSE.

        Args:
            start: Ngày bắt đầu (YYYY-MM-DD). Bắt buộc nếu không có length/count_back.
            end: Ngày kết thúc (YYYY-MM-DD). Mặc định hôm nay.
            interval: Khung thời gian. Nhận: 1m, 5m, 15m, 30m, 1H, 1D, 1W, 1M.
            to_df: Trả về DataFrame. Mặc định True.
            show_log: Hiển thị log debug.
            count_back: Số lượng nến cần lấy.
            floating: Số chữ số thập phân. Mặc định 2.
            length: Khoảng thời gian phân tích (vd: '3M', 150, '100b').
            get_all: Lấy tất cả cột. Mặc định False.

        Returns:
            DataFrame với cột [time, open, high, low, close, volume].
        """
        if end is None:
            end = datetime.now().strftime("%Y-%m-%d")

        if start is None:
            if length is not None:
                bars_from_len, len_remainder = interpret_lookback_length(length)
                if bars_from_len is not None:
                    count_back = bars_from_len
                    length = None
                else:
                    length = len_remainder

            if length is not None:
                start = get_start_date_from_lookback(
                    lookback_length=length, end_date=end
                )
            elif count_back is not None:
                start = get_start_date_from_lookback(
                    bars=count_back, interval=interval, end_date=end
                )
            else:
                raise ValueError(
                    "Tham số 'start' là bắt buộc nếu không cung cấp 'length' hoặc 'count_back'."
                )

        if interval not in self.interval_map:
            valid_intervals = ", ".join(self.interval_map.keys())
            raise ValueError(
                f"Giá trị interval không hợp lệ: {interval}. Vui lòng chọn: {valid_intervals}"
            )

        resolution = self.interval_map[interval]
        from_ts = _to_unix_timestamp(start)
        # Add one day to end so the final day is included
        try:
            end_dt = datetime.strptime(end, "%Y-%m-%d")
        except ValueError as e:
            raise ValueError(f"Ngày kết thúc không hợp lệ: {end}") from e
        # DNSE uses inclusive 'to' — use end-of-day epoch
        to_ts = int(
            end_dt.replace(
                hour=23, minute=59, second=59, tzinfo=timezone.utc
            ).timestamp()
        )

        params = {
            "resolution": resolution,
            "symbol": self.symbol,
            "from": from_ts,
            "to": to_ts,
        }

        json_data = send_request(
            url=_OHLC_URL,
            headers=self.headers,
            method="GET",
            params=params,
            show_log=show_log or self.show_log,
            proxy_list=self.proxy_config.proxy_list,
            proxy_mode=self.proxy_config.proxy_mode,
            request_mode=self.proxy_config.request_mode,
        )

        if not json_data:
            raise ValueError(
                f"Không tìm thấy dữ liệu cho mã {self.symbol}. "
                "Vui lòng kiểm tra lại mã chứng khoán hoặc khoảng thời gian."
            )

        # DNSE returns {"t": [...], "o": [...], "h": [...], "l": [...], "c": [...], "v": [...]}
        # or a list of dicts — handle both shapes
        if isinstance(json_data, dict) and "t" in json_data:
            # Array-of-arrays format
            length_data = len(json_data["t"])
            records = []
            for i in range(length_data):
                records.append(
                    {
                        "t": json_data["t"][i],
                        "o": json_data.get("o", [None] * length_data)[i],
                        "h": json_data.get("h", [None] * length_data)[i],
                        "l": json_data.get("l", [None] * length_data)[i],
                        "c": json_data.get("c", [None] * length_data)[i],
                        "v": json_data.get("v", [0] * length_data)[i],
                    }
                )
            df = pd.DataFrame(records)
        elif isinstance(json_data, list):
            df = pd.DataFrame(json_data)
        else:
            raise ValueError(
                f"Định dạng dữ liệu không được nhận dạng từ DNSE cho {self.symbol}."
            )

        if df.empty:
            raise ValueError(
                f"Dữ liệu trống cho mã {self.symbol} với interval {interval}."
            )

        if not to_df:
            import json

            return json.dumps(df.to_dict(orient="records"))

        # Rename columns
        df = df.rename(columns=_OHLC_MAP)

        # Keep only standard columns unless get_all
        if not get_all:
            base_cols = ["time", "open", "high", "low", "close", "volume"]
            df = df[[c for c in base_cols if c in df.columns]]

        # Convert time: DNSE returns Unix epoch seconds → datetime (Asia/Ho_Chi_Minh)
        if "time" in df.columns:
            try:
                df["time"] = (
                    pd.to_datetime(df["time"], unit="s", utc=True)
                    .dt.tz_convert("Asia/Ho_Chi_Minh")
                    .dt.tz_localize(None)
                )
            except Exception:
                # If already strings or different format, leave as-is
                pass

        # Apply dtypes
        for col, dtype in _OHLC_DTYPE.items():
            if col in df.columns and col != "time":
                try:
                    df[col] = df[col].astype(dtype)
                except (ValueError, TypeError):
                    pass

        # Round prices
        price_cols = ["open", "high", "low", "close"]
        if floating is not None:
            for col in price_cols:
                if col in df.columns:
                    df[col] = df[col].round(floating)

        # Metadata
        df.attrs["symbol"] = self.symbol
        df.attrs["source"] = self.data_source
        df.attrs["interval"] = interval
        df.attrs["start"] = start
        df.attrs["end"] = end

        if show_log or self.show_log:
            logger.info(
                f"Truy xuất thành công {len(df)} bản ghi OHLCV cho {self.symbol} "
                f"({interval}, {start} → {end})."
            )

        return df

    @optimize_execution("DNSE")
    def intraday(
        self,
        date: Optional[str] = None,
        to_df: Optional[bool] = True,
        show_log: Optional[bool] = False,
        get_all: Optional[bool] = False,
    ) -> Union[pd.DataFrame, str]:
        """
        Tải dữ liệu khớp lệnh intraday từ DNSE cho một ngày giao dịch.

        Args:
            date: Ngày giao dịch (YYYY-MM-DD). Mặc định hôm nay.
            to_df: Trả về DataFrame. Mặc định True.
            show_log: Hiển thị log debug.
            get_all: Lấy thêm các cột mở rộng. Mặc định False.

        Returns:
            DataFrame với cột [time, price, volume, match_type, id].

        Raises:
            ValueError: Nếu date là ngày tương lai.
        """
        if date is None:
            date = datetime.now().strftime("%Y-%m-%d")

        try:
            date_dt = datetime.strptime(date, "%Y-%m-%d")
        except ValueError as e:
            raise ValueError(
                f"Ngày không hợp lệ: {date}. Định dạng yêu cầu: YYYY-MM-DD"
            ) from e

        if date_dt.date() > datetime.now().date():
            raise ValueError(
                f"Không thể lấy dữ liệu intraday cho ngày tương lai: {date}."
            )

        params = {
            "symbol": self.symbol,
            "date": date,
        }

        json_data = send_request(
            url=_INTRADAY_URL,
            headers=self.headers,
            method="GET",
            params=params,
            show_log=show_log or self.show_log,
            proxy_list=self.proxy_config.proxy_list,
            proxy_mode=self.proxy_config.proxy_mode,
            request_mode=self.proxy_config.request_mode,
        )

        if not json_data:
            if to_df:
                return pd.DataFrame(columns=_INTRADAY_CORE_COLUMNS)
            return "[]"

        # json_data may be a list of dicts or a dict with a "data" key
        if isinstance(json_data, dict) and "data" in json_data:
            records = json_data["data"]
        elif isinstance(json_data, list):
            records = json_data
        else:
            records = []

        if not records:
            if to_df:
                return pd.DataFrame(columns=_INTRADAY_CORE_COLUMNS)
            return "[]"

        if not to_df:
            import json

            return json.dumps(records)

        df = pd.DataFrame(records)

        # Rename columns via _INTRADAY_MAP
        df = df.rename(columns=_INTRADAY_MAP)

        # Normalize match_type: map raw 'B'/'S' values to 'buy'/'sell'
        if "match_type" in df.columns:
            df["match_type"] = (
                df["match_type"]
                .fillna("")
                .astype(str)
                .str.upper()
                .map({"B": "buy", "S": "sell"})
                .fillna("unknown")
            )

        # Ensure id column exists
        if "id" not in df.columns:
            # Synthesize id from time+price+volume (same pattern as KBS)
            time_col = df.get("time", pd.Series(range(len(df))))
            price_col = df.get("price", pd.Series([0.0] * len(df)))
            vol_col = df.get("volume", pd.Series([0] * len(df)))
            df["id"] = (
                time_col.astype(str).str.replace(" ", "_").str.replace(":", "")
                + "_"
                + price_col.astype(str).str.replace(".", "")
                + "_"
                + vol_col.astype(str)
            )

        if get_all:
            result_df = df
        else:
            existing_core = [c for c in _INTRADAY_CORE_COLUMNS if c in df.columns]
            result_df = df[existing_core]

        # Metadata
        result_df.attrs["symbol"] = self.symbol
        result_df.attrs["source"] = self.data_source
        result_df.attrs["date"] = date

        if show_log or self.show_log:
            logger.info(
                f"Truy xuất thành công {len(result_df)} bản ghi intraday cho {self.symbol} ({date})."
            )

        return result_df


# Register DNSE Quote provider
ProviderRegistry.register("quote", "dnse", Quote)
