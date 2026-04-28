from typing import Any, Optional
import pandas as pd
from vnstock.ui._base import BaseUI

class EventsReference(BaseUI):
    """
    Events Reference Data.
    Provides access to market events, news, and other time-bound occurrences.
    """
    def __init__(self, symbol: str = None, **kwargs):
        super().__init__(**kwargs)
        self.symbol = symbol

    def __call__(self, symbol: str = None) -> 'EventsReference':
        """Allow calling the domain object with a symbol."""
        self.symbol = symbol
        return self

    def calendar(self, start: Optional[str] = None, end: Optional[str] = None, 
                 event_type: Optional[str] = None,
                 page: int = 0, limit: int = 20000, source: str = 'kbs') -> pd.DataFrame:
        """
        Retrieve events calendar (dividends, AGM, new listings, ...)
        """
        return self._dispatch('Reference', 'events', 'calendar', 
                              start=start, end=end, event_type=event_type, 
                              page=page, limit=limit, source=source)

    def market(self, start: Optional[str] = None, end: Optional[str] = None, 
               event_type: Optional[str] = None) -> pd.DataFrame:
        """
        Retrieve special stock market events (holidays, system incidents, ...)
        """
        from vnstock.core.utils.market_events import MARKET_EVENTS
        
        if not MARKET_EVENTS:
            return pd.DataFrame()
            
        records = []
        for date_str, details in MARKET_EVENTS.items():
            record = {"date": date_str}
            record.update(details)
            records.append(record)
            
        df = pd.DataFrame(records)
        
        # Apply start, end, event_type filtering
        if not df.empty:
            df['date'] = pd.to_datetime(df['date'])
            
            if start:
                try:
                    df = df[df['date'] >= pd.to_datetime(start)]
                except Exception:
                    pass
            if end:
                try:
                    df = df[df['date'] <= pd.to_datetime(end)]
                except Exception:
                    pass
            if event_type:
                df = df[df['event_type'].str.lower() == event_type.lower()]
                
        return df.reset_index(drop=True)
