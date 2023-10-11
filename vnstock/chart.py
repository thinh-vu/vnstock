from .config import *
from .technical import *

import plotly.graph_objs as go


# CANDLESTICK CHART
def candlestick_chart(df, title='Candlestick Chart with MA and Volume', x_label='Date', y_label='Price', ma_periods=None, show_volume=True, figure_size=(15, 8), reference_period=None, colors=('#00F4B0', '#FF3747'), reference_colors=('blue', 'black')):
    """
    Generate a candlestick chart with optional Moving Averages (MA) lines, volume data, and reference lines.

    Parameters:
    - df: DataFrame with candlestick data ('time', 'open', 'high', 'low', 'close', 'volume', 'ticker').
    - title: Title of the chart.
    - x_label: Label for the x-axis.
    - y_label: Label for the y-axis.
    - ma_periods: List of MA periods to calculate and plot (e.g., [10, 50, 200]).
    - show_volume: Boolean to indicate whether to display volume data.
    - figure_size: Tuple specifying the figure size (width, height).
    - reference_period: Number of days to consider for reference lines (e.g., 90).
    - colors: Tuple of color codes for up and down candles (e.g., ('#00F4B0', '#FF3747')).
    - reference_colors: Tuple of color codes for reference lines (e.g., ('black', 'blue')).

    Returns:
    - Plotly figure object.
    """
    # Create the base candlestick chart
    candlestick_trace = go.Candlestick(
        x=df['time'],
        open=df['open'],
        high=df['high'],
        low=df['low'],
        close=df['close'],
        name='Candlestick',
    )

    # Create a figure
    fig = go.Figure(data=[candlestick_trace])

    # Add volume data if specified
    if show_volume:
        volume_trace = go.Bar(
            x=df['time'],
            y=df['volume'],
            name='Volume',
            yaxis='y2',  # Use the secondary y-axis for volume
            marker=dict(color=[colors[0] if close >= open else colors[1] for close, open in zip(df['close'], df['open'])]),  # Match volume color to candle color
        )

        fig.add_trace(volume_trace)

    # Add Moving Averages (MA) lines if specified
    if ma_periods:
        for period in ma_periods:
            ma_name = f'{period}-day MA'
            df[ma_name] = df['close'].rolling(period).mean()

            ma_trace = go.Scatter(
                x=df['time'],
                y=df[ma_name],
                mode='lines',
                name=ma_name,
            )

            fig.add_trace(ma_trace)

    # Add straight reference lines for the highest high and lowest low
    if reference_period:
        df['lowest_low'] = df['low'].rolling(reference_period).min()
        df['highest_high'] = df['high'].rolling(reference_period).max()

        lowest_low_trace = go.Scatter(
            x=df['time'],
            y=[df['lowest_low'].iloc[-1]] * len(df),  # Create a straight line for lowest low
            mode='lines',
            name=f'Lowest Low ({reference_period} days)',
            line=dict(color=reference_colors[0], dash='dot'),
        )

        highest_high_trace = go.Scatter(
            x=df['time'],
            y=[df['highest_high'].iloc[-1]] * len(df),  # Create a straight line for highest high
            mode='lines',
            name=f'Highest High ({reference_period} days)',
            line=dict(color=reference_colors[1], dash='dot'),
        )

        fig.add_trace(lowest_low_trace)
        fig.add_trace(highest_high_trace)

    # Customize the chart appearance
    fig.update_layout(
        title=title,
        xaxis_title=x_label,
        yaxis_title=y_label,
        xaxis_rangeslider_visible=True,
        yaxis2=dict(
            title='Volume',
            overlaying='y',
            side='right',
        ),
        width=figure_size[0] * 100,  # Convert short form to a larger size for better readability
        height=figure_size[1] * 100,
        margin=dict(l=50, r=50, t=70, b=50),  # Adjust margins for space between title and legend
    )

    return fig

# BOLLINGER BANDS

def bollinger_bands(df, window=20, num_std_dev=2):
    """
    Calculate Bollinger Bands for a DataFrame.

    Parameters:
    - df: DataFrame with OHLC data ('time', 'open', 'high', 'low', 'close', 'volume', 'ticker').
    - window: The rolling window size for calculating the moving average and standard deviation.
    - num_std_dev: The number of standard deviations to use for the Bollinger Bands.

    Returns:
    - DataFrame with Bollinger Bands ('time', 'upper_band', 'middle_band', 'lower_band').
    """
    df['middle_band'] = df['close'].rolling(window=window).mean()
    df['rolling_std'] = df['close'].rolling(window=window).std()
    df['upper_band'] = df['middle_band'] + (num_std_dev * df['rolling_std'])
    df['lower_band'] = df['middle_band'] - (num_std_dev * df['rolling_std'])
    df.drop(columns=['rolling_std'], inplace=True)
    return df

def bollinger_bands_chart(df, use_candlestick=True, show_volume=True, fig_size=(15, 8), chart_title='Bollinger Bands Chart', xaxis_title='Date', yaxis_title='Price', bollinger_band_colors=('gray', 'orange', 'gray'), volume_colors=('#00F4B0', '#FF3747')):
    """
    Visualize a candlestick chart or close price chart with Bollinger Bands and volume using Plotly.

    Parameters:
    - df: DataFrame with Bollinger Bands data ('time', 'open', 'high', 'low', 'close', 'volume', 'ticker', 'upper_band', 'middle_band', 'lower_band').
    - use_candlestick: Boolean to indicate whether to use candlestick chart (default) or close price chart.
    - show_volume: Boolean to indicate whether to display volume data on the main chart.
    - fig_size: Tuple specifying the figure size in short form, e.g., (15, 8) equals to (1500, 800) in actual.
    - chart_title: Title for the chart.
    - xaxis_title: Title for the x-axis.
    - yaxis_title: Title for the y-axis.
    - bollinger_band_colors: Tuple of color codes for the Bollinger Bands (upper, middle, lower).
    - volume_colors: Tuple of color codes for volume bars on up and down days.

    Returns:
    - Plotly figure object.
    """
    fig = go.Figure()

    if use_candlestick:
        # Create the candlestick chart
        candlestick_trace = go.Candlestick(
            x=df['time'],
            open=df['open'],
            high=df['high'],
            low=df['low'],
            close=df['close'],
            name='Candlestick',
        )

        fig.add_trace(candlestick_trace)
    else:
        # Create a chart using close prices
        close_price_trace = go.Scatter(
            x=df['time'],
            y=df['close'],
            mode='lines',
            name='Close Price',
        )

        fig.add_trace(close_price_trace)

    # Create the Bollinger Bands traces
    upper_band_trace = go.Scatter(
        x=df['time'],
        y=df['upper_band'],
        mode='lines',
        line=dict(color=bollinger_band_colors[0]),
        name='Upper Bollinger Band',
    )

    middle_band_trace = go.Scatter(
        x=df['time'],
        y=df['middle_band'],
        mode='lines',
        line=dict(color=bollinger_band_colors[1]),
        name='Middle Bollinger Band',
    )

    lower_band_trace = go.Scatter(
        x=df['time'],
        y=df['lower_band'],
        mode='lines',
        line=dict(color=bollinger_band_colors[2]),
        name='Lower Bollinger Band',
    )

    fig.add_trace(upper_band_trace)
    fig.add_trace(middle_band_trace)
    fig.add_trace(lower_band_trace)

    if show_volume:
        # Create the volume bars with different colors for up and down days
        volume_color = [volume_colors[0] if close >= open else volume_colors[1] for close, open in zip(df['close'], df['open'])]

        volume_trace = go.Bar(
            x=df['time'],
            y=df['volume'],
            name='Volume',
            marker=dict(color=volume_color),
            yaxis='y2',
        )

        fig.add_trace(volume_trace)

    # Customize the chart appearance
    fig.update_layout(
        title=chart_title,
        xaxis_title=xaxis_title,
        yaxis_title=yaxis_title,
        xaxis_rangeslider_visible=True,
        # legend=dict(orientation="h", y=1.05),
        yaxis2=dict(title='Volume', overlaying='y', side='right'),
        width=fig_size[0] * 100,  # Convert short form width to full width
        height=fig_size[1] * 100,  # Convert short form height to full height
    )

    return fig
