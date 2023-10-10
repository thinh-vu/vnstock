from .config import *
from .technical import *

def candlestick_chart(symbol='TCB', start_date='2022-01-01', end_date='2023-10-10', resolution='1D', type='stock', title='Candlestick Chart with MA and Volume', x_label='Date', y_label='Price', ma_periods=None, show_volume=True, figure_size=(15, 8), reference_period=None, up_color='#00F4B0', down_color='#FF3747'):
    """
    Generate a candlestick chart with optional Moving Averages (MA) lines, volume data, and reference lines.

    Parameters:
    - symbol: Stock symbol
    - start_date: Start date of the chart (e.g., '2022-01-01').
    - end_date: End date of the chart (e.g., '2023-10-10').
    - resolution: Resolution of the data (e.g., '1D' for daily data). Other values are: 1, 15, 30, 60
    - type: Type of the data (e.g., 'stock' for stock data).
    - title: Title of the chart.
    - x_label: Label for the x-axis.
    - y_label: Label for the y-axis.
    - ma_periods: List of MA periods to calculate and plot (e.g., [10, 50, 200]).
    - show_volume: Boolean to indicate whether to display volume data.
    - figure_size: Tuple specifying the figure size (width, height).
    - reference_period: Number of days to consider for reference lines (e.g., 90).

    Returns:
    - Plotly figure object.
    """
    df = stock_historical_data(symbol, start_date, end_date, resolution, type)
    # Create the base candlestick chart
    candlestick_trace = go.Candlestick(
        x=df['time'],
        open=df['open'],
        high=df['high'],
        low=df['low'],
        close=df['close'],
        name='Candlestick',
        increasing=dict(line=dict(color=up_color)),  # Green color for increasing candles
        decreasing=dict(line=dict(color=down_color)),  # Red color for decreasing candles
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
            marker=dict(color=[up_color if close >= open else down_color for close, open in zip(df['close'], df['open'])]),  # Match volume color to candle color
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
            line=dict(color='red', dash='dot'),
        )

        highest_high_trace = go.Scatter(
            x=df['time'],
            y=[df['highest_high'].iloc[-1]] * len(df),  # Create a straight line for highest high
            mode='lines',
            name=f'Highest High ({reference_period} days)',
            line=dict(color='green', dash='dot'),
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
        # legend=dict(orientation="h", y=1.05),  # Place legend at the top
    )

    return fig
