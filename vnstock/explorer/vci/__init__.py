"""
VCI data explorer, free edition.

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

from .company import *  # noqa: F403
from .financial import *  # noqa: F403
from .listing import *  # noqa: F403
from .quote import *  # noqa: F403
from .trading import *  # noqa: F403
