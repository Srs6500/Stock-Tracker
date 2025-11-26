"""
Plotly chart generation for stock visualization.
Creates candlestick charts with volume bars and technical indicators.
Supports any stock symbol (not just TSLA).
"""

import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
from typing import Optional, Dict, Any


def calculate_sma(data: pd.Series, window: int) -> pd.Series:
    """Calculate Simple Moving Average."""
    return data.rolling(window=window).mean()


def calculate_ema(data: pd.Series, window: int) -> pd.Series:
    """Calculate Exponential Moving Average."""
    return data.ewm(span=window, adjust=False).mean()


def create_candlestick_chart(df: pd.DataFrame, days: int = 30, symbol: str = "TSLA", 
                            indicators: Optional[Dict[str, Any]] = None) -> go.Figure:
    """
    Create an interactive candlestick chart with volume bars for TSLA.
    
    Args:
        df: DataFrame with OHLCV data (indexed by date)
        days: Number of days to display (default: 30)
    
    Returns:
        Plotly Figure object
    """
    # Filter to last N days
    if len(df) > days:
        chart_df = df.tail(days).copy()
    else:
        chart_df = df.copy()
    
    if chart_df.empty:
        # Return empty chart with message
        fig = go.Figure()
        fig.add_annotation(
            text="No data available",
            xref="paper", yref="paper",
            x=0.5, y=0.5,
            showarrow=False,
            font=dict(size=20, color="#888888")
        )
        fig.update_layout(
            template="plotly_dark",
            paper_bgcolor="#0e1117",
            plot_bgcolor="#0e1117",
            height=500
        )
        return fig
    
    # Create subplots: price on top, volume on bottom
    # shared_xaxes=True means x-axes are linked (zoom/pan together)
    fig = make_subplots(
        rows=2, cols=1,
        shared_xaxes=True,
        vertical_spacing=0.03,
        row_heights=[0.7, 0.3],
        subplot_titles=("Price", "Volume"),
        specs=[[{"secondary_y": False}], [{"secondary_y": False}]]
    )
    
    # Format dates for x-axis
    dates = chart_df.index
    
    # Candlestick chart
    fig.add_trace(
        go.Candlestick(
            x=dates,
            open=chart_df["open"],
            high=chart_df["high"],
            low=chart_df["low"],
            close=chart_df["close"],
            name=symbol.upper(),
            increasing_line_color="#00ff00",  # Green for up days
            decreasing_line_color="#ff0000",   # Red for down days
            increasing_fillcolor="#00ff00",
            decreasing_fillcolor="#ff0000",
        ),
        row=1, col=1
    )
    
    # Technical Indicators - Moving Averages (calculated from data)
    if len(chart_df) >= 20:
        # SMA 20
        sma20 = calculate_sma(chart_df["close"], 20)
        fig.add_trace(
            go.Scatter(
                x=dates,
                y=sma20,
                name="SMA 20",
                line=dict(color="#ffaa00", width=1.5),
                opacity=0.8
            ),
            row=1, col=1
        )
    
    if len(chart_df) >= 50:
        # SMA 50
        sma50 = calculate_sma(chart_df["close"], 50)
        fig.add_trace(
            go.Scatter(
                x=dates,
                y=sma50,
                name="SMA 50",
                line=dict(color="#00aaff", width=1.5),
                opacity=0.8
            ),
            row=1, col=1
        )
    
    # Optional: Add RSI if available from API
    if indicators and "RSI" in indicators:
        try:
            rsi_data = indicators["RSI"]
            if "Technical Analysis: RSI" in rsi_data:
                rsi_values = rsi_data["Technical Analysis: RSI"]
                # Convert to DataFrame and plot (simplified - would need proper date matching)
                # For now, we'll skip RSI overlay as it requires date alignment
                pass
        except:
            pass  # Silently skip if RSI data is malformed
    
    # Volume bars
    colors = []
    for i in range(len(chart_df)):
        if i == 0:
            colors.append("#888888")
        else:
            # Green if close > previous close, red otherwise
            if chart_df.iloc[i]["close"] >= chart_df.iloc[i-1]["close"]:
                colors.append("#00ff00")
            else:
                colors.append("#ff0000")
    
    fig.add_trace(
        go.Bar(
            x=dates,
            y=chart_df["volume"],
            name="Volume",
            marker_color=colors,
            opacity=0.6
        ),
        row=2, col=1
    )
    
    # Update layout for dark theme
    fig.update_layout(
        template="plotly_dark",
        paper_bgcolor="#0e1117",
        plot_bgcolor="#0e1117",
        height=600,
        showlegend=True,
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        ),
        xaxis_rangeslider_visible=False,
        hovermode="x unified",
        dragmode="zoom",  # Enable zoom/pan
        title=dict(
            text=f"{symbol.upper()} – Last 30 Trading Days",
            font=dict(size=20, color="#ffffff"),
            x=0.5,
            xanchor="center"
        ),
        margin=dict(l=50, r=50, t=80, b=50),
        # Enable modebar (toolbar) with controls
        modebar=dict(
            bgcolor="rgba(30, 30, 30, 0.8)",
            color="#ffffff",
            activecolor="#ff0000"
        ),
        # Ensure all axes can be reset/autoscaled
        autosize=True
    )
    
    # Update axes - enable autoscaling and interaction for ALL axes
    # This ensures autoscale/reset buttons work on both subplots
    
    # X-axis for price chart (top) - linked to bottom via shared_xaxes=True
    fig.update_xaxes(
        showgrid=False,
        gridcolor="#333333",
        row=1, col=1,
        autorange=True,
        fixedrange=False,
        rangeslider=dict(visible=False)
    )
    # X-axis for volume chart (bottom) - this is the "master" x-axis
    fig.update_xaxes(
        showgrid=False,
        gridcolor="#333333",
        row=2, col=1,
        autorange=True,
        fixedrange=False
    )
    # Y-axis for price chart (top)
    fig.update_yaxes(
        showgrid=True,
        gridcolor="#1e1e1e",
        row=1, col=1,
        title_text="Price ($)",
        autorange=True,
        fixedrange=False,
        type="linear",
        automargin=True
    )
    # Y-axis for volume chart (bottom)
    fig.update_yaxes(
        showgrid=True,
        gridcolor="#1e1e1e",
        row=2, col=1,
        title_text="Volume",
        autorange=True,
        fixedrange=False,
        type="linear",
        automargin=True
    )
    
    return fig

