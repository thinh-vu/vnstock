"""
Visualization and charting utilities for data exploration.

This module provides a pandas DataFrame/Series extension for creating
various types of charts using the MPlot library.
"""

from typing import Any, Union

import pandas as pd
from vnstock_ezchart.mplot import MPlot, Utils
from vnstock.core.utils.logger import get_logger

logger = get_logger(__name__)


class Chart:
    """
    Chart wrapper for creating various types of data visualizations.

    Provides a simple interface for creating bar, line, pie, scatter,
    heatmap, and other chart types from pandas DataFrames or Series.

    Example:
        >>> df = pd.DataFrame({'A': [1, 2, 3], 'B': [4, 5, 6]})
        >>> chart = Chart(df)
        >>> chart.bar()
    """

    def __init__(self, data: pd.DataFrame | pd.Series):
        """
        Initialize Chart instance.

        Args:
            data: pandas DataFrame or Series to visualize

        Raises:
            ValueError: If data is not DataFrame or Series
        """
        self.data = data
        self.chart = MPlot()
        self.utils = Utils()
        self.validate_data()
        self._add_utils_methods()

    def validate_data(self):
        """
        Validate input data format.

        Raises:
            ValueError: If data is not DataFrame or Series
        """
        if not isinstance(self.data, (pd.DataFrame, pd.Series)):
            raise ValueError("Data must be a pandas DataFrame or Series")

        # Ensure datetime index if present
        if isinstance(self.data.index, pd.DatetimeIndex):
            self.data.index = pd.to_datetime(self.data.index)

    def _add_utils_methods(self):
        """Dynamically add utility methods from Utils class."""
        for method_name in dir(self.utils):
            if not method_name.startswith("_"):
                method = getattr(self.utils, method_name)
                if callable(method):
                    setattr(self, method_name, method)

    def help(self, func_name: str) -> str:
        """
        Display help for a specific chart function.

        Args:
            func_name: Name of the function

        Returns:
            Help text/docstring
        """
        return self.chart.help(func_name)

    def bar(self, **kwargs) -> Any:
        """
        Create a bar chart.

        Args:
            **kwargs: Arguments passed to plot function

        Returns:
            Chart figure object
        """
        return self.chart.bar(self.data, **kwargs)

    def hist(self, **kwargs) -> Any:
        """
        Create a histogram.

        Args:
            **kwargs: Arguments passed to plot function

        Returns:
            Chart figure object
        """
        return self.chart.hist(self.data, **kwargs)

    def pie(self, labels=None, values=None, **kwargs) -> Any:
        """
        Create a pie chart.

        Args:
            labels: Labels for pie slices (column name, list, or Series)
            values: Values for pie slices (column name)
            **kwargs: Arguments passed to plot function

        Returns:
            Chart figure object

        Raises:
            ValueError: If data is not DataFrame or Series
        """
        if isinstance(self.data, pd.DataFrame):
            if values:
                data = self.data[values]
            else:
                data = self.data.index
        elif isinstance(self.data, pd.Series):
            data = self.data
        else:
            raise ValueError("Data must be a pandas DataFrame or Series")

        # Handle labels
        if labels is not None:
            if (isinstance(labels, str) and
                isinstance(self.data, pd.DataFrame) and
                    labels in self.data.columns):
                labels = self.data[labels]
            else:
                labels = pd.Series(labels, index=data.index)

        return self.chart.pie(data, labels, **kwargs)

    def timeseries(self, **kwargs) -> Any:
        """
        Create a time series chart.

        Args:
            **kwargs: Arguments passed to plot function

        Returns:
            Chart figure object
        """
        return self.chart.timeseries(self.data, **kwargs)

    def heatmap(self, **kwargs) -> Any:
        """
        Create a heatmap.

        Args:
            **kwargs: Arguments passed to plot function

        Returns:
            Chart figure object
        """
        return self.chart.heatmap(self.data, **kwargs)

    def scatter(self, x: str, y: str, **kwargs) -> Any:
        """
        Create a scatter plot.

        Args:
            x: Column name for X-axis
            y: Column name for Y-axis
            **kwargs: Arguments passed to plot function

        Returns:
            Chart figure object
        """
        return self.chart.scatter(self.data, x, y, **kwargs)

    def treemap(self, values, labels, **kwargs) -> Any:
        """
        Create a treemap chart.

        Args:
            values: Column name(s) or list for treemap values
            labels: Column name(s) or list for treemap labels
            **kwargs: Arguments passed to plot function

        Returns:
            Chart figure object

        Raises:
            ValueError: If data is not DataFrame or Series
        """
        if isinstance(self.data, pd.DataFrame):
            if values:
                data = self.data[values]
            else:
                data = self.data.index
        elif isinstance(self.data, pd.Series):
            data = self.data
        else:
            raise ValueError("Data must be a pandas DataFrame or Series")

        # Handle labels
        if labels is not None:
            if (isinstance(labels, str) and
                isinstance(self.data, pd.DataFrame) and
                    labels in self.data.columns):
                labels = self.data[labels]
            else:
                labels = pd.Series(labels, index=data.index)

        return self.chart.treemap(data, labels, **kwargs)

    def boxplot(self, **kwargs) -> Any:
        """
        Create a boxplot.

        Args:
            **kwargs: Arguments passed to plot function

        Returns:
            Chart figure object
        """
        return self.chart.boxplot(self.data, **kwargs)

    def pairplot(self, **kwargs) -> Any:
        """
        Create a pair plot.

        Args:
            **kwargs: Arguments passed to plot function

        Returns:
            Chart figure object
        """
        return self.chart.pairplot(self.data, **kwargs)

    def wordcloud(self, show_log: bool = False, **kwargs) -> Any:
        """
        Create a word cloud.

        Args:
            show_log: Whether to log the processed text
            **kwargs: Arguments passed to plot function

        Returns:
            Chart figure object
        """
        # Convert DataFrame to text
        if isinstance(self.data, pd.DataFrame):
            text = (self.data
                    .apply(lambda x: ' '.join(x.dropna().astype(str)),
                           axis=1)
                    .str.cat(sep=' '))
        elif isinstance(self.data, pd.Series):
            text = self.data.str.cat(sep=' ')
        else:
            raise ValueError("Data must be a pandas DataFrame or Series")

        if show_log:
            logger.info(f"Word cloud text: {text[:200]}...")

        return self.chart.wordcloud(text, **kwargs)

    def table(self, **kwargs) -> Any:
        """
        Create a table visualization.

        Args:
            **kwargs: Arguments passed to plot function

        Returns:
            Chart figure object
        """
        return self.chart.table(self.data, **kwargs)

    def combo(self, bar_data, line_data, **kwargs) -> Any:
        """
        Create a combo chart with bar and line data.

        Args:
            bar_data: Column name(s) for bar chart data
            line_data: Column name(s) for line chart data
            **kwargs: Arguments passed to plot function

        Returns:
            Chart figure object

        Raises:
            ValueError: If data is not DataFrame or Series
        """
        if isinstance(self.data, pd.DataFrame):
            bar_df = self.data[bar_data]
            line_df = self.data[line_data]
        elif isinstance(self.data, pd.Series):
            bar_df = self.data
            line_df = self.data
        else:
            raise ValueError("Data must be a pandas DataFrame or Series")

        return self.chart.combo_chart(bar_df, line_df, **kwargs)


def _add_viz_property(cls):
    """
    Add .viz property to pandas DataFrame and Series.

    This enables convenient chart access: df.viz.bar()

    Args:
        cls: pandas DataFrame or Series class
    """
    @property
    def viz(self):
        return Chart(self)

    cls.viz = viz


# Add .viz property to pandas classes
_add_viz_property(pd.DataFrame)
_add_viz_property(pd.Series)
