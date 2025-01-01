# vnstock/common/chart_wrapper.py

import pandas as pd
from vnstock_ezchart.mplot import MPlot, Utils
from vnstock.core.utils.logger import get_logger

logger = get_logger(__name__)

class Chart:
    """
    A wrapper class for creating various types of charts using data from a pandas DataFrame or Series.

    This class integrates the MPlot library for plotting and Utils for additional utilities.
    """

    def __init__(self, data):
        """
        Initialize the Chart instance with the provided data.

        Args:
            data (pd.DataFrame or pd.Series): The data to be visualized.
        """
        self.data = data
        self.chart = MPlot()
        self.utils = Utils()
        self.validate_data()
        self._add_utils_methods()

    def validate_data(self):
        """
        Validate the input data to ensure it is a pandas DataFrame or Series.

        Raises:
            ValueError: If the data is not a pandas DataFrame or Series.
        """
        if not isinstance(self.data, (pd.DataFrame, pd.Series)):
            raise ValueError("Data must be a pandas DataFrame or Series")
        # Ensure datetime index
        if isinstance(self.data.index, pd.DatetimeIndex):
            self.data.index = pd.to_datetime(self.data.index)

    def _add_utils_methods(self):
        """
        Dynamically add methods from the Utils class to the Chart instance.
        """
        for method_name in dir(self.utils):
            if not method_name.startswith("__"):
                method = getattr(self.utils, method_name)
                if callable(method):
                    setattr(self, method_name, method)

    def help(self, func_name):
        """
        Display the docstring for a specified function.

        Args:
            func_name (str): The name of the function to display the docstring for.
        """
        return self.chart.help(func_name)

    def bar(self, **kwargs):
        """
        Plot a bar chart.

        Args:
            **kwargs: Additional arguments to pass to the plot function.
        """
        return self.chart.bar(self.data, **kwargs)

    def hist(self, **kwargs):
        """
        Plot a histogram.

        Args:
            **kwargs: Additional arguments to pass to the plot function.
        """
        return self.chart.hist(self.data, **kwargs)

    def pie(self, labels=None, values=None, **kwargs):
        """
        Plot a pie chart.

        Args:
            labels (str, list, pd.Series, optional): Labels for each slice.
                - If str, it should be a column name in the DataFrame.
                - If list or pd.Series, it will be used directly as labels.
            values (str, optional): A column name to use as values for each slice.
                If you are plotting on a Series, this argument is not required,
                instead the index is used.
            **kwargs: Additional arguments to pass to the plot function.

        Raises:
            ValueError: If the data is not a pandas DataFrame or Series.
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
            if isinstance(labels, str) and isinstance(self.data, pd.DataFrame) and labels in self.data.columns:
                labels = self.data[labels]
            else:
                labels = pd.Series(labels, index=data.index)

        return self.chart.pie(data, labels, **kwargs)

    def timeseries(self, **kwargs):
        """
        Plot a time series chart.

        Args:
            **kwargs: Additional arguments to pass to the plot function.
        """
        return self.chart.timeseries(self.data, **kwargs)

    def heatmap(self, **kwargs):
        """
        Plot a heatmap.

        Args:
            **kwargs: Additional arguments to pass to the plot function.
        """
        return self.chart.heatmap(self.data, **kwargs)

    def scatter(self, x, y, **kwargs):
        """
        Plot a scatter chart.

        Args:
            x (str): The column name for the x-axis data.
            y (str): The column name for the y-axis data.
            **kwargs: Additional arguments to pass to the plot function.
        """
        return self.chart.scatter(self.data, x, y, **kwargs)

    def treemap(self, values, labels, **kwargs):
        """
        Plot a treemap chart.

        Args:
            values (str or list): Values for the treemap slices.
            labels (str or list): Labels for the treemap slices.
            **kwargs: Additional arguments to pass to the plot function.
        """
        """
        Plot a pie chart.

        Args:
            labels (str, list, pd.Series, optional): Labels for each slice.
                - If str, it should be a column name in the DataFrame.
                - If list or pd.Series, it will be used directly as labels.
            values (str, optional): A column name to use as values for each slice.
                If you are plotting on a Series, this argument is not required,
                instead the index is used.
            **kwargs: Additional arguments to pass to the plot function.

        Raises:
            ValueError: If the data is not a pandas DataFrame or Series.
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
            if isinstance(labels, str) and isinstance(self.data, pd.DataFrame) and labels in self.data.columns:
                labels = self.data[labels]
            else:
                labels = pd.Series(labels, index=data.index)

        return self.chart.treemap(data, labels, **kwargs)

    def boxplot(self, **kwargs):
        """
        Plot a boxplot.

        Args:
            **kwargs: Additional arguments to pass to the plot function.
        """
        return self.chart.boxplot(self.data, **kwargs)

    def pairplot(self, **kwargs):
        """
        Plot a pairplot.

        Args:
            **kwargs: Additional arguments to pass to the plot function.
        """
        return self.chart.pairplot(self.data, **kwargs)

    def wordcloud(self, show_log=False, **kwargs):
        """
        Plot a word cloud.

        Args:
            show_log (bool, optional): Whether to log the text data.
            **kwargs: Additional arguments to pass to the plot function.
        """
        # if data is a DataFrame, concatenate all columns into a single string
        if isinstance(self.data, pd.DataFrame):
            text = self.data.apply(lambda x: ' '.join(x.dropna().astype(str)), axis=1).str.cat(sep=' ')
        elif isinstance(self.data, pd.Series):
            text = self.data.str.cat(sep=' ')
        # if show_log in kwargs and it is True, log the text
        if show_log:
            logger.info(text)
        return self.chart.wordcloud(text, **kwargs)

    def table(self, **kwargs):
        """
        Plot a table.

        Args:
            **kwargs: Additional arguments to pass to the plot function.
        """
        return self.chart.table(self.data, **kwargs)

    def combo(self, bar_data, line_data, **kwargs):
        """
        Plot a combo chart with both bar and line data.

        Args:
            bar_data (str or list): The column(s) for the bar data.
            line_data (str or list): The column(s) for the line data.
            **kwargs: Additional arguments to pass to the plot function.

        Raises:
            ValueError: If the data is not a pandas DataFrame or Series.
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
    Add the viz property to pandas DataFrame and Series classes.

    Args:
        cls (type): The class to add the viz property to.
    """
    @property
    def viz(self):
        return Chart(self)
    cls.viz = viz

_add_viz_property(pd.DataFrame)
_add_viz_property(pd.Series)
