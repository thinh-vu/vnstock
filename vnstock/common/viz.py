"""
Visualization and charting utilities for data exploration.

This module provides a pandas DataFrame/Series extension for creating
various types of charts. It supports two charting backends:

1. vnstock_chart (Professional, recommended if available):
   - LineChart, BarChart, CandleChart, ScatterChart, BoxplotChart, HeatmapChart
   - Install: pip install --extra-index-url https://vnstocks.com/api/simple vnstock_chart
   
2. vnstock_ezchart (Fallback, basic charts):
    - bar: Bar charts
    - hist: Histograms
    - pie: Pie charts
    - scatter: Scatter plots
    - heatmap: Heatmaps
    - boxplot: Box plots
    - pairplot: Pair plots
    - timeseries: Time series visualization
    - treemap: Treemap charts
    - wordcloud: Word clouds
    - table: Table visualization
    - combo_chart: Combo charts with bars and lines

Example:
    >>> import pandas as pd
    >>> from vnstock.common.viz import Chart
    >>> df = pd.DataFrame({'A': [1, 2, 3], 'B': [4, 5, 6]})
    >>> chart = Chart(df)
    >>> chart.bar()
    
    Or use the convenient extension:
    >>> df.viz.bar()
    >>> df.viz.scatter(x='A', y='B')
"""

from typing import Any, Union, Optional

import pandas as pd

from vnstock.core.utils.logger import get_logger

logger = get_logger(__name__)

# Try to import vnstock_chart first (professional charting library)
HAS_VNSTOCK_CHART = False
try:
    import vnstock_chart
    from vnstock_chart import (
        LineChart, BarChart, CandleChart,
        ScatterChart, BoxplotChart, HeatmapChart
    )
    HAS_VNSTOCK_CHART = True
except ImportError:
    pass  # Silently skip if not available

# Fallback to vnstock_ezchart if vnstock_chart not available
HAS_VNSTOCK_EZCHART = False
try:
    from vnstock_ezchart.mplot import MPlot
    HAS_VNSTOCK_EZCHART = True
except ImportError:
    pass

# Ensure at least one charting library is available
if not HAS_VNSTOCK_CHART and not HAS_VNSTOCK_EZCHART:
    raise ImportError(
        "No charting library available. Please install one of:\n"
        "1. vnstock_chart (recommended): "
        "pip install --extra-index-url https://vnstocks.com/api/simple vnstock_chart\n"
        "2. vnstock_ezchart (fallback): pip install vnstock_ezchart"
    )


class Chart:
    """
    Chart wrapper for creating various types of data visualizations.

    Supports two charting backends:
    1. vnstock_chart (Professional, recommended) - if available
    2. vnstock_ezchart (Fallback) - basic charts

    Available chart methods depend on the backend:
    
    vnstock_chart methods:
        - line(): Line charts
        - bar(): Bar charts
        - candle(): Candlestick charts
        - scatter(): Scatter plots
        - boxplot(): Box plots
        - heatmap(): Heatmaps
    
    vnstock_ezchart methods (fallback):
        - bar(), hist(), pie(), scatter(), heatmap(), boxplot(), pairplot()
        - timeseries(), treemap(), wordcloud(), table(), combo_chart()

    Example:
        >>> df = pd.DataFrame({'A': [1, 2, 3], 'B': [4, 5, 6]})
        >>> chart = Chart(df)
        >>> chart.bar()
        
        Or use the convenient extension:
        >>> df.viz.bar()
        >>> df.viz.scatter(x='A', y='B')
    """

    def __init__(self, data: Union[pd.DataFrame, pd.Series], backend: Optional[str] = None):
        """
        Initialize Chart instance.

        Args:
            data: pandas DataFrame or Series to visualize
            backend: Charting backend to use ('vnstock_chart', 'vnstock_ezchart', or None for auto)

        Raises:
            ValueError: If data is not DataFrame or Series
        """
        if not isinstance(data, (pd.DataFrame, pd.Series)):
            raise ValueError(
                f"Data must be a pandas DataFrame or Series, got {type(data).__name__}"
            )
        
        self.data = data
        self.backend = None
        self.chart = None
        
        # Determine which backend to use
        if backend == 'vnstock_chart':
            if HAS_VNSTOCK_CHART:
                self.backend = 'vnstock_chart'
            else:
                # Provide helpful error with installation instructions
                raise ImportError(
                    "vnstock_chart is not installed. To install:\n"
                    "pip install --extra-index-url https://vnstocks.com/api/simple vnstock_chart\n"
                    "\nOr use the fallback backend:\n"
                    "Chart(data, backend='vnstock_ezchart') or Chart(data) # auto-select"
                )
        
        if backend == 'vnstock_ezchart':
            if HAS_VNSTOCK_EZCHART:
                self.backend = 'vnstock_ezchart'
                self.chart = MPlot()
            else:
                raise ImportError(
                    "vnstock_ezchart is not installed. To install:\n"
                    "pip install vnstock_ezchart"
                )
        
        # Auto-select backend if not specified
        if self.backend is None:
            if HAS_VNSTOCK_CHART:
                self.backend = 'vnstock_chart'
            elif HAS_VNSTOCK_EZCHART:
                self.backend = 'vnstock_ezchart'
                self.chart = MPlot()
            else:
                raise RuntimeError("No charting backend available")
        
        # Only log errors, not debug info
        if self.backend == 'vnstock_chart' and not HAS_VNSTOCK_CHART:
            logger.error("vnstock_chart backend selected but not available")
        elif self.backend == 'vnstock_ezchart' and not HAS_VNSTOCK_EZCHART:
            logger.error("vnstock_ezchart backend selected but not available")

    def line(self, **kwargs):
        """Create line chart using vnstock_chart."""
        if self.backend == 'vnstock_chart':
            try:
                if isinstance(self.data, pd.Series):
                    x = self.data.index.tolist()
                    y = self.data.values.tolist()
                elif isinstance(self.data, pd.DataFrame):
                    x = self.data.index.tolist()
                    y = self.data.iloc[:, 0].values.tolist()
                else:
                    raise ValueError("Data must be Series or DataFrame")
                
                chart = LineChart(x=x, y=y, **kwargs)
                
                # Auto-render by default
                try:
                    import sys
                    if 'ipykernel' in sys.modules or 'IPython' in sys.modules:
                        try:
                            from IPython.display import display
                            display(chart.render())
                        except ImportError:
                            chart.render()
                    else:
                        chart.render()
                except Exception:
                    pass
                
                return chart
            except Exception as e:
                if "not installed" not in str(e):
                    logger.error(f"Error creating line chart: {e}")
                raise
        elif self.backend == 'vnstock_ezchart' and self.chart:
            return self.chart.timeseries(self.data, **kwargs)
        else:
            raise AttributeError(f"line chart not available in {self.backend} backend")

    def bar(self, **kwargs):
        """Create bar chart using vnstock_chart."""
        if self.backend == 'vnstock_chart':
            try:
                if isinstance(self.data, pd.Series):
                    x = self.data.index.tolist()
                    y = self.data.values.tolist()
                elif isinstance(self.data, pd.DataFrame):
                    x = self.data.index.tolist()
                    y = self.data.iloc[:, 0].values.tolist()
                else:
                    raise ValueError("Data must be Series or DataFrame")
                
                chart = BarChart(x=x, y=y, **kwargs)
                
                # Auto-render by default
                try:
                    import sys
                    if 'ipykernel' in sys.modules or 'IPython' in sys.modules:
                        try:
                            from IPython.display import display
                            display(chart.render())
                        except ImportError:
                            chart.render()
                    else:
                        chart.render()
                except Exception:
                    pass
                
                return chart
            except Exception as e:
                if "not installed" not in str(e):
                    logger.error(f"Error creating bar chart: {e}")
                raise
        elif self.backend == 'vnstock_ezchart' and self.chart:
            return self.chart.bar(self.data, **kwargs)
        else:
            raise AttributeError(f"bar chart not available in {self.backend} backend")

    def scatter(self, x=None, y=None, **kwargs):
        """Create scatter plot using vnstock_chart or vnstock_ezchart."""
        if self.backend == 'vnstock_chart':
            try:
                if isinstance(self.data, pd.DataFrame):
                    if x is None or y is None:
                        if len(self.data.columns) >= 2:
                            x = x or self.data.columns[0]
                            y = y or self.data.columns[1]
                        else:
                            raise ValueError("DataFrame must have at least 2 columns for scatter plot")
                    
                    x_data = self.data[x].tolist()
                    y_data = self.data[y].tolist()
                else:
                    raise ValueError("Scatter plot requires DataFrame")
                
                chart = ScatterChart(x=x_data, y=y_data, **kwargs)
                
                # Auto-render by default
                try:
                    import sys
                    if 'ipykernel' in sys.modules or 'IPython' in sys.modules:
                        try:
                            from IPython.display import display
                            display(chart.render())
                        except ImportError:
                            chart.render()
                    else:
                        chart.render()
                except Exception:
                    pass
                
                return chart
            except Exception as e:
                if "not installed" not in str(e):
                    logger.error(f"Error creating scatter chart: {e}")
                raise
        elif self.backend == 'vnstock_ezchart' and self.chart:
            if isinstance(self.data, pd.DataFrame):
                if x is None or y is None:
                    if len(self.data.columns) >= 2:
                        x = x or self.data.columns[0]
                        y = y or self.data.columns[1]
                    else:
                        raise ValueError("DataFrame must have at least 2 columns for scatter plot")
                return self.chart.scatter(self.data, x, y, **kwargs)
            else:
                raise ValueError("Scatter plot requires DataFrame for vnstock_ezchart")
        else:
            raise AttributeError(f"scatter chart not available in {self.backend} backend")

    def candle(self, **kwargs):
        """Create candlestick chart using vnstock_chart."""
        if self.backend == 'vnstock_chart':
            try:
                if isinstance(self.data, pd.DataFrame):
                    required_cols = ['open', 'high', 'low', 'close']
                    if not all(col in self.data.columns for col in required_cols):
                        raise ValueError("Candlestick chart requires 'open', 'high', 'low', 'close' columns")
                    
                    # Prepare DataFrame with required columns
                    # Add time column if it's in index
                    df = self.data.copy()
                    if isinstance(df.index, pd.DatetimeIndex):
                        df = df.reset_index()
                        if 'time' not in df.columns and df.index.name != 'time':
                            df = df.rename(columns={df.columns[0]: 'time'})
                    
                    # Ensure we have volume column (required by CandleChart)
                    if 'volume' not in df.columns:
                        df['volume'] = [1] * len(df)  # Default volume
                    
                    # Reorder columns to expected order: time, open, close, low, high, volume
                    expected_cols = ['time', 'open', 'close', 'low', 'high', 'volume']
                    available_cols = [col for col in expected_cols if col in df.columns]
                    df = df[available_cols]
                    
                    chart = CandleChart(df=df, **kwargs)
                else:
                    raise ValueError("Candlestick chart requires DataFrame with OHLC data")
                
                # Auto-render by default
                try:
                    import sys
                    if 'ipykernel' in sys.modules or 'IPython' in sys.modules:
                        try:
                            from IPython.display import display
                            display(chart.render())
                        except ImportError:
                            chart.render()
                    else:
                        chart.render()
                except Exception:
                    pass
                
                return chart
            except Exception as e:
                if "not installed" not in str(e):
                    logger.error(f"Error creating candlestick chart: {e}")
                raise
        elif self.backend == 'vnstock_ezchart' and self.chart:
            # vnstock_ezchart doesn't have candlestick, fallback to line
            return self.chart.timeseries(self.data, **kwargs)
        else:
            raise AttributeError(f"candlestick chart not available in {self.backend} backend")

    def heatmap(self, **kwargs):
        """Create heatmap using vnstock_chart."""
        if self.backend == 'vnstock_chart':
            try:
                if isinstance(self.data, pd.DataFrame):
                    x = self.data.columns.tolist()
                    y = self.data.index.tolist()
                    value = self.data.values.tolist()
                else:
                    raise ValueError("Heatmap requires DataFrame")
                
                chart = HeatmapChart(x=x, y=y, value=value, **kwargs)
                
                # Auto-render by default
                try:
                    import sys
                    if 'ipykernel' in sys.modules or 'IPython' in sys.modules:
                        try:
                            from IPython.display import display
                            display(chart.render())
                        except ImportError:
                            chart.render()
                    else:
                        chart.render()
                except Exception:
                    pass
                
                return chart
            except Exception as e:
                if "not installed" not in str(e):
                    logger.error(f"Error creating heatmap chart: {e}")
                raise
        elif self.backend == 'vnstock_ezchart' and self.chart:
            return self.chart.heatmap(self.data, **kwargs)
        else:
            raise AttributeError(f"heatmap chart not available in {self.backend} backend")

    def boxplot(self, **kwargs):
        """Create boxplot using vnstock_chart."""
        if self.backend == 'vnstock_chart':
            try:
                if isinstance(self.data, pd.DataFrame):
                    x = self.data.index.tolist()
                    y = self.data.values.tolist()
                elif isinstance(self.data, pd.Series):
                    x = self.data.index.tolist()
                    y = self.data.values.tolist()
                else:
                    raise ValueError("Data must be Series or DataFrame")
                
                chart = BoxplotChart(x=x, y=y, **kwargs)
                
                # Auto-render by default
                try:
                    import sys
                    if 'ipykernel' in sys.modules or 'IPython' in sys.modules:
                        try:
                            from IPython.display import display
                            display(chart.render())
                        except ImportError:
                            chart.render()
                    else:
                        chart.render()
                except Exception:
                    pass
                
                return chart
            except Exception as e:
                if "not installed" not in str(e):
                    logger.error(f"Error creating boxplot chart: {e}")
                raise
        elif self.backend == 'vnstock_ezchart' and self.chart:
            return self.chart.boxplot(self.data, **kwargs)
        else:
            raise AttributeError(f"boxplot chart not available in {self.backend} backend")

    # vnstock_ezchart specific methods
    def hist(self, **kwargs):
        """Create histogram using vnstock_ezchart."""
        if self.backend == 'vnstock_ezchart' and self.chart:
            return self.chart.hist(self.data, **kwargs)
        elif self.backend == 'vnstock_chart':
            # vnstock_chart doesn't have hist, fallback to bar
            return self.bar(**kwargs)
        else:
            raise AttributeError(f"histogram chart not available in {self.backend} backend")

    def pie(self, labels=None, **kwargs):
        """Create pie chart using vnstock_ezchart."""
        if self.backend == 'vnstock_ezchart' and self.chart:
            # Handle labels for pie chart
            if labels is None:
                if isinstance(self.data, pd.DataFrame):
                    if len(self.data.columns) >= 2:
                        labels = self.data.iloc[:, 0].tolist()
                        data = self.data.iloc[:, 1]
                    else:
                        labels = self.data.index.tolist()
                        data = self.data.iloc[:, 0]
                elif isinstance(self.data, pd.Series):
                    labels = self.data.index.tolist()
                    data = self.data
            else:
                data = self.data
            
            return self.chart.pie(data, labels, **kwargs)
        else:
            raise AttributeError(f"pie chart not available in {self.backend} backend")

    def timeseries(self, **kwargs):
        """Create time series chart using vnstock_ezchart."""
        if self.backend == 'vnstock_ezchart' and self.chart:
            return self.chart.timeseries(self.data, **kwargs)
        elif self.backend == 'vnstock_chart':
            # Use line chart for vnstock_chart
            return self.line(**kwargs)
        else:
            raise AttributeError(f"time series chart not available in {self.backend} backend")

    def treemap(self, values=None, labels=None, **kwargs):
        """Create treemap using vnstock_ezchart."""
        if self.backend == 'vnstock_ezchart' and self.chart:
            if values is None and labels is None:
                if isinstance(self.data, pd.DataFrame):
                    if len(self.data.columns) >= 2:
                        values = self.data.iloc[:, 0].tolist()
                        labels = self.data.iloc[:, 1].tolist()
                    else:
                        values = self.data.iloc[:, 0].tolist()
                        labels = self.data.index.tolist()
                elif isinstance(self.data, pd.Series):
                    values = self.data.values.tolist()
                    labels = self.data.index.tolist()
            
            return self.chart.treemap(values, labels, **kwargs)
        else:
            raise AttributeError(f"treemap chart not available in {self.backend} backend")

    def wordcloud(self, text=None, **kwargs):
        """Create word cloud using vnstock_ezchart."""
        if self.backend == 'vnstock_ezchart' and self.chart:
            if text is None:
                if isinstance(self.data, pd.DataFrame):
                    # Convert DataFrame to text
                    text = ' '.join(self.data.astype(str).values.flatten())
                elif isinstance(self.data, pd.Series):
                    text = ' '.join(self.data.astype(str).values)
                else:
                    text = str(self.data)
            
            return self.chart.wordcloud(text, **kwargs)
        else:
            raise AttributeError(f"word cloud chart not available in {self.backend} backend")

    def table(self, **kwargs):
        """Create table using vnstock_ezchart."""
        if self.backend == 'vnstock_ezchart' and self.chart:
            if isinstance(self.data, pd.DataFrame):
                return self.chart.table(self.data, **kwargs)
            elif isinstance(self.data, pd.Series):
                # Convert Series to DataFrame for table
                df = self.data.to_frame()
                return self.chart.table(df, **kwargs)
            else:
                raise ValueError("Table requires DataFrame or Series")
        else:
            raise AttributeError(f"table chart not available in {self.backend} backend")

    def combo_chart(self, bar_data=None, line_data=None, **kwargs):
        """Create combo chart using vnstock_ezchart."""
        if self.backend == 'vnstock_ezchart' and self.chart:
            if bar_data is None and line_data is None:
                if isinstance(self.data, pd.DataFrame) and len(self.data.columns) >= 2:
                    bar_data = self.data.iloc[:, 0]
                    line_data = self.data.iloc[:, 1]
                else:
                    raise ValueError("Combo chart requires DataFrame with at least 2 columns")
            elif isinstance(bar_data, str) and isinstance(self.data, pd.DataFrame):
                # If bar_data is column name, extract the Series
                bar_data = self.data[bar_data]
            if isinstance(line_data, str) and isinstance(self.data, pd.DataFrame):
                # If line_data is column name, extract the Series
                line_data = self.data[line_data]
            
            return self.chart.combo_chart(bar_data, line_data, **kwargs)
        else:
            raise AttributeError(f"combo chart not available in {self.backend} backend")

    def pairplot(self, **kwargs):
        """Create pair plot using vnstock_ezchart."""
        if self.backend == 'vnstock_ezchart' and self.chart:
            return self.chart.pairplot(self.data, **kwargs)
        else:
            raise AttributeError(f"pair plot chart not available in {self.backend} backend")

    def __getattr__(self, name: str) -> Any:
        """Delegate unknown methods to vnstock_ezchart if available."""
        if self.backend == 'vnstock_ezchart' and self.chart:
            if hasattr(self.chart, name):
                attr = getattr(self.chart, name)
                if callable(attr):
                    def method_wrapper(*args, **kwargs):
                        try:
                            if args:
                                return attr(*args, **kwargs)
                            else:
                                return attr(self.data, **kwargs)
                        except Exception as e:
                            if "not installed" not in str(e):
                                logger.error(f"Error calling {name}: {e}")
                            raise
                    return method_wrapper
                return attr
        
        raise AttributeError(f"'Chart' object has no attribute '{name}' in {self.backend} backend")



def _add_viz_property(cls):
    """
    Add .viz property to pandas DataFrame and Series.

    This enables convenient chart access: df.viz.bar()

    Args:
        cls: pandas DataFrame or Series class
    """
    @property
    def viz(self):
        """
        Access visualization methods through .viz extension.
        
        Returns:
            Chart instance for the current DataFrame/Series
            
        Example:
            >>> df = pd.DataFrame({'A': [1, 2, 3], 'B': [4, 5, 6]})
            >>> df.viz.bar()
            >>> df.viz.timeseries()
            >>> df.viz.scatter(x='A', y='B')
        """
        return Chart(self)

    cls.viz = viz


# Register .viz property with pandas classes
try:
    _add_viz_property(pd.DataFrame)
    _add_viz_property(pd.Series)
except Exception as e:
    logger.error(f"Could not register .viz extension: {e}")


def get_chart(data: Union[pd.DataFrame, pd.Series], backend: Optional[str] = None) -> Chart:
    """
    Create a Chart instance from DataFrame or Series.
    
    Args:
        data: pandas DataFrame or Series
        backend: Charting backend ('vnstock_chart', 'vnstock_ezchart', or None for auto)
        
    Returns:
        Chart instance
        
    Example:
        >>> df = pd.DataFrame({'A': [1, 2, 3], 'B': [4, 5, 6]})
        >>> chart = get_chart(df)
        >>> chart.bar()
        
        >>> # Use specific backend
        >>> chart = get_chart(df, backend='vnstock_chart')
    """
    return Chart(data, backend=backend)


__all__ = ['Chart', 'get_chart', 'HAS_VNSTOCK_CHART', 'HAS_VNSTOCK_EZCHART']
