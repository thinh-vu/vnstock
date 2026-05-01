# @title utils/market_hours.py
# Simple utility to check market trading hours and data availability

import datetime
import logging
from typing import Any, Dict, Optional

import pytz

# Setup logging
logger = logging.getLogger(__name__)


def trading_hours(
    market: str = "HOSE",
    custom_time: Optional[datetime.datetime] = None,
    enable_log: bool = False,
    language: str = "en",
) -> Dict[str, Any]:
    """
    Check if current time is within trading hours with data availability context.

    Args:
        market (str): Market to check ('HOSE', 'HNX', 'UPCOM', 'Futures', or None)
                     If None, returns simplified data based on common market hours
        custom_time (datetime.datetime, optional): Custom time for testing
        enable_log (bool): Whether to enable funny log messages
        language (str): Language for messages ('en' for English, 'vi' for Vietnamese)

    Returns:
        dict: Trading status information with keys:
            - is_trading_hour (bool): Whether it's currently trading hours
            - trading_session (str): Current trading session type
            - data_status (str): Data availability status
            - time (str): Current time in HH:MM:SS format
            - market (str): Market being checked or "general" if market is None
    """
    # Validate market parameter
    if market is not None and market not in ["HOSE", "HNX", "UPCOM", "Futures"]:
        raise ValueError(
            f"Unknown market: {market}. Valid markets: HOSE, HNX, UPCOM, Futures, None"
        )

    # Validate language parameter
    if language not in ["en", "vi"]:
        language = "en"  # Default to English if invalid language

    # Set up logging if enabled
    if enable_log and not logger.handlers:
        handler = logging.StreamHandler()
        formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        logger.setLevel(logging.INFO)

    # Market schedules based on the provided image
    market_schedules = {
        "HOSE": {
            "trading_start": "09:00",
            "ato_end": "09:15",
            "lunch_start": "11:30",
            "lunch_end": "13:00",
            "atc_start": "14:30",
            "atc_end": "14:45",
            "trading_end": "15:00",
        },
        "HNX": {
            "trading_start": "09:00",
            "lunch_start": "11:30",
            "lunch_end": "13:00",
            "atc_start": "14:30",
            "atc_end": "14:45",
            "trading_end": "15:00",
        },
        "UPCOM": {
            "trading_start": "09:00",
            "lunch_start": "11:30",
            "lunch_end": "13:00",
            "trading_end": "14:30",
        },
        "Futures": {
            "trading_start": "08:45",
            "ato_end": "09:00",
            "lunch_start": "11:30",
            "lunch_end": "13:00",
            "atc_start": "14:30",
            "atc_end": "14:45",
            "trading_end": "14:45",
        },
    }

    # Vietnam timezone (Ho Chi Minh City)
    tz = pytz.timezone("Asia/Ho_Chi_Minh")

    # Get current time in Vietnam timezone
    if custom_time:
        now = custom_time.astimezone(tz)
    else:
        now = datetime.datetime.now(tz)

    # Log messages in English
    log_messages_en = {
        "pre_market": "🌅 Markets still snoozing! Your data might be wearing pajamas too.",
        "ato": "🔔 ATO in progress! Prices are playing musical chairs.",
        "continuous": "💸 Trading in full swing! Money printer go brrrr!",
        "lunch_break": "🍜 Lunch break! Even algorithms need to slurp some digital noodles.",
        "atc": "🏁 ATC time! Final sprint to determine closing prices.",
        "post_close": "🧹 Post-close cleanup. Last chance to sweep up some bargains!",
        "post_market": "🌙 Markets closed but data's still settling in... like your food after dinner.",
        "weekend": "🏖️ Weekend mode! Markets closed. Time to touch grass instead of charts.",
        "historical": "📚 Deep in after-hours territory. Only historical data here, like dinosaur fossils.",
    }

    # Log messages in Vietnamese
    log_messages_vi = {
        "pre_market": "🌅 Thị trường vẫn đang ngủ! Dữ liệu của bạn cũng có thể đang nghỉ ngơi.",
        "ato": "🔔 ATO đang diễn ra! Giá cả đang định hình.",
        "continuous": "💸 Giao dịch đang diễn ra sôi động! Thị trường đang hoạt động mạnh.",
        "lunch_break": "🍜 Giờ nghỉ trưa! Ngay cả thuật toán cũng cần nghỉ ngơi.",
        "atc": "🏁 Giờ ATC! Nước rút cuối cùng để xác định giá đóng cửa.",
        "post_close": "🧹 Dọn dẹp sau giờ đóng cửa. Cơ hội cuối để giao dịch thỏa thuận!",
        "post_market": "🌙 Thị trường đã đóng cửa nhưng dữ liệu vẫn đang ổn định...",
        "weekend": "🏖️ Chế độ cuối tuần! Thị trường đóng cửa. Thời gian để nghỉ ngơi.",
        "historical": "📚 Ngoài giờ giao dịch. Chỉ có dữ liệu lịch sử ở đây.",
    }

    # Select log messages based on language
    log_messages = log_messages_en if language == "en" else log_messages_vi

    # Check for weekend
    if now.weekday() >= 5:  # Saturday (5) or Sunday (6)
        if enable_log:
            logger.info(log_messages["weekend"])

        return {
            "is_trading_hour": False,
            "trading_session": "weekend",
            "data_status": "historical_only",
            "time": now.strftime("%H:%M:%S"),
            "market": "general" if market is None else market,
        }

    # Handle market=None case - use HOSE as reference for general market hours
    if market is None:
        schedule = market_schedules["HOSE"]
        market_display = "general"
    else:
        schedule = market_schedules[market]
        market_display = market

    # Parse times from schedule
    trading_start = datetime.datetime.strptime(
        schedule["trading_start"], "%H:%M"
    ).time()
    lunch_start = datetime.datetime.strptime(schedule["lunch_start"], "%H:%M").time()
    lunch_end = datetime.datetime.strptime(schedule["lunch_end"], "%H:%M").time()
    trading_end = datetime.datetime.strptime(schedule["trading_end"], "%H:%M").time()

    # Define data availability windows
    prep_window_start = (
        datetime.datetime.combine(datetime.date.today(), trading_start)
        - datetime.timedelta(hours=2)
    ).time()

    settling_window_end = (
        datetime.datetime.combine(datetime.date.today(), trading_end)
        + datetime.timedelta(hours=4)
    ).time()

    # Current time as time object for comparison
    current_time = now.time()

    # Determine market phase and trading status
    is_trading = False
    trading_session = ""
    data_status = ""

    # Before market open
    if current_time < trading_start:
        trading_session = "pre_market"
        if current_time >= prep_window_start:
            data_status = "preparing"  # Within 2 hours before market open
        else:
            data_status = "historical_only"  # More than 2 hours before market open

        if enable_log:
            logger.info(log_messages["pre_market"])

    # After market close
    elif current_time >= trading_end:
        if current_time <= settling_window_end:
            trading_session = "post_market"
            data_status = "settling"  # Within 4 hours after market close

            if enable_log:
                logger.info(log_messages["post_market"])
        else:
            trading_session = "after_hours"
            data_status = "historical_only"  # More than 4 hours after market close

            if enable_log:
                logger.info(log_messages["historical"])

    # During market hours
    else:
        # Check if we're in ATO period
        if (
            "ato_end" in schedule
            and trading_start
            <= current_time
            < datetime.datetime.strptime(schedule["ato_end"], "%H:%M").time()
        ):
            trading_session = "ato"
            is_trading = True
            data_status = "real_time"

            if enable_log:
                logger.info(log_messages["ato"])

        # Check if we're in lunch break
        elif lunch_start <= current_time < lunch_end:
            trading_session = "lunch_break"
            is_trading = False
            data_status = "real_time"  # Data should still be current during lunch

            if enable_log:
                logger.info(log_messages["lunch_break"])

        # Check if we're in ATC period
        elif (
            "atc_start" in schedule
            and "atc_end" in schedule
            and datetime.datetime.strptime(schedule["atc_start"], "%H:%M").time()
            <= current_time
            < datetime.datetime.strptime(schedule["atc_end"], "%H:%M").time()
        ):
            trading_session = "atc"
            is_trading = True
            data_status = "real_time"

            if enable_log:
                logger.info(log_messages["atc"])

        # Check if we're in post-close period
        elif (
            "atc_end" in schedule
            and datetime.datetime.strptime(schedule["atc_end"], "%H:%M").time()
            <= current_time
            < trading_end
        ):
            trading_session = "post_close"
            is_trading = False  # Not active trading
            data_status = "real_time"

            if enable_log:
                logger.info(log_messages["post_close"])

        # Otherwise, we're in continuous trading
        else:
            trading_session = "continuous"
            is_trading = True
            data_status = "real_time"

            if enable_log:
                logger.info(log_messages["continuous"])

    # Return comprehensive result
    return {
        "is_trading_hour": is_trading,
        "trading_session": trading_session,
        "data_status": data_status,
        "time": now.strftime("%H:%M:%S"),
        "market": market_display,
    }


# # Example usage
# if __name__ == "__main__":
#     print(check_market_hours(market="HOSE", custom_time=datetime.datetime(2025, 3, 17, 10, 0, 0), enable_log=True, language="en"))
