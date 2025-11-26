"""
Stock Comparison Chart Functions
Create charts comparing multiple stocks side-by-side.
"""

import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
from typing import List, Dict
from charts import calculate_sma


def create_comparison_chart(symbols_data: Dict[str, pd.DataFrame], days: int = 30) -> go.Figure:
    """
    Create a comparison chart showing multiple stocks' price movements.
    
    Args:
        symbols_data: Dictionary mapping symbol to DataFrame with OHLCV data
        days: Number of days to display
    
    Returns:
        Plotly Figure object with multiple stock price lines
    """
    if not symbols_data or len(symbols_data) == 0:
        fig = go.Figure()
        fig.add_annotation(
            text="No data available for comparison",
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
    
    # Create figure
    fig = go.Figure()
    
    # Color palette for different stocks
    colors = ["#ff0000", "#00ff00", "#00aaff", "#ffaa00", "#ff00ff", "#00ffff", "#ffffff"]
    
    # Normalize prices to percentage change for fair comparison
    for idx, (symbol, df) in enumerate(symbols_data.items()):
        if df.empty:
            continue
        
        # Filter to last N days
        if len(df) > days:
            chart_df = df.tail(days).copy()
        else:
            chart_df = df.copy()
        
        dates = chart_df.index
        
        # Calculate percentage change from first day (normalized)
        if len(chart_df) > 0:
            first_close = chart_df.iloc[0]["close"]
            if first_close > 0:
                normalized_prices = ((chart_df["close"] - first_close) / first_close) * 100
            else:
                normalized_prices = chart_df["close"]
            
            color = colors[idx % len(colors)]
            
            fig.add_trace(
                go.Scatter(
                    x=dates,
                    y=normalized_prices,
                    name=symbol.upper(),
                    line=dict(color=color, width=2),
                    mode='lines',
                    hovertemplate=f'{symbol}<br>Date: %{{x}}<br>Change: %{{y:.2f}}%<extra></extra>'
                )
            )
    
    # Update layout
    fig.update_layout(
        template="plotly_dark",
        paper_bgcolor="#0e1117",
        plot_bgcolor="#0e1117",
        height=500,
        title=dict(
            text="Stock Comparison (Normalized % Change)",
            font=dict(size=18, color="#ffffff"),
            x=0.5,
            xanchor="center"
        ),
        xaxis=dict(
            showgrid=True,
            gridcolor="#1e1e1e",
            title="Date"
        ),
        yaxis=dict(
            showgrid=True,
            gridcolor="#1e1e1e",
            title="% Change from Start",
            autorange=True,
            fixedrange=False
        ),
        hovermode="x unified",
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        ),
        margin=dict(l=50, r=50, t=80, b=50),
        dragmode="zoom"
    )
    
    return fig


def create_price_comparison_chart(symbols_data: Dict[str, pd.DataFrame], days: int = 30) -> go.Figure:
    """
    Create a comparison chart showing absolute prices (not normalized).
    Useful for stocks in similar price ranges.
    
    Args:
        symbols_data: Dictionary mapping symbol to DataFrame
        days: Number of days to display
    
    Returns:
        Plotly Figure object
    """
    if not symbols_data or len(symbols_data) == 0:
        fig = go.Figure()
        fig.add_annotation(
            text="No data available",
            xref="paper", yref="paper",
            x=0.5, y=0.5,
            showarrow=False,
            font=dict(size=20, color="#888888")
        )
        fig.update_layout(template="plotly_dark", paper_bgcolor="#0e1117", plot_bgcolor="#0e1117", height=500)
        return fig
    
    fig = go.Figure()
    colors = ["#ff0000", "#00ff00", "#00aaff", "#ffaa00", "#ff00ff", "#00ffff", "#ffffff"]
    
    for idx, (symbol, df) in enumerate(symbols_data.items()):
        if df.empty:
            continue
        
        if len(df) > days:
            chart_df = df.tail(days).copy()
        else:
            chart_df = df.copy()
        
        dates = chart_df.index
        color = colors[idx % len(colors)]
        
        fig.add_trace(
            go.Scatter(
                x=dates,
                y=chart_df["close"],
                name=symbol.upper(),
                line=dict(color=color, width=2),
                mode='lines',
                hovertemplate=f'{symbol}<br>Date: %{{x}}<br>Price: $%{{y:.2f}}<extra></extra>'
            )
        )
    
    fig.update_layout(
        template="plotly_dark",
        paper_bgcolor="#0e1117",
        plot_bgcolor="#0e1117",
        height=500,
        title=dict(
            text="Stock Price Comparison",
            font=dict(size=18, color="#ffffff"),
            x=0.5,
            xanchor="center"
        ),
        xaxis=dict(showgrid=True, gridcolor="#1e1e1e", title="Date"),
        yaxis=dict(showgrid=True, gridcolor="#1e1e1e", title="Price ($)", autorange=True, fixedrange=False),
        hovermode="x unified",
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        margin=dict(l=50, r=50, t=80, b=50),
        dragmode="zoom"
    )
    
    return fig

