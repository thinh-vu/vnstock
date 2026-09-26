"""
KB Securities (KBS) data explorer, free edition.

Kept deliberately small to limit maintenance. Compared with the sponsor package
`vnstock_data`, it does not include:
- Trading: derivatives, odd lots, put-through deals, trade history
  (trade_history, matched_by_price).
- Quote: order book depth (price_depth).
- Financial: deeper statement history.
- Listing: the detailed sub-index coverage.

Those features are in `vnstock_data`. Their availability and accuracy still depend
on the third-party source.
"""

from vnstock.explorer.kbs.company import Company  # noqa: E402
from vnstock.explorer.kbs.financial import Finance  # noqa: E402
from vnstock.explorer.kbs.listing import Listing  # noqa: E402
from vnstock.explorer.kbs.quote import Quote  # noqa: E402
from vnstock.explorer.kbs.trading import Trading  # noqa: E402

__all__ = ["Listing", "Quote", "Company", "Finance", "Trading"]
