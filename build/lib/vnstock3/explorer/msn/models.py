"""Mô hình xác thực dữ liệu đầu vào cho VCI"""
from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class TickerModel(BaseModel):
    symbol: str
    start: str
    end: Optional[str] = None
    interval: Optional[str] = "1D"
