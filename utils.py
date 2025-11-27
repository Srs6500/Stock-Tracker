"""
Data processing utilities using yfinance.
Simple and clean - no complex dependencies.
"""

import pandas as pd
from datetime import date, datetime, timedelta
from typing import Dict, Any, Optional, Tuple, List
import streamlit as st
from yfinance_client import get_stock_data as yf_get_data, get_live_price as yf_get_live, get_multiple_stocks_data as yf_get_multiple


def get_stock_data(symbol: str = "TSLA", days: int = 45) -> Tuple[pd.DataFrame, Dict[str, Any], str]:
    """
    Get stock data for any symbol using yfinance.
    
    Args:
        symbol: Stock ticker symbol (default: "TSLA")
        days: Number of days of historical data
    
    Returns:
        Tuple of (DataFrame, live_data_dict, status_message)
    """
    try:
        # Get historical data
        df = yf_get_data(symbol, days=days)
        
        if df is None or df.empty:
            return pd.DataFrame(), {}, f"❌ No data available for {symbol}"
        
        # Set date as index if not already
        if 'date' in df.columns:
            df.set_index('date', inplace=True)
        
        # Get live data
        live_data = yf_get_live(symbol)
        
        if not live_data:
            # Fallback to latest historical data
            if not df.empty:
                latest_row = df.iloc[-1]
                live_data = {
                    "current_price": float(latest_row["close"]),
                    "today_high": float(latest_row["high"]),
                    "today_low": float(latest_row["low"]),
                    "today_volume": int(latest_row["volume"]),
                    "prev_close": float(df.iloc[-2]["close"]) if len(df) >= 2 else None,
                    "market_status": "closed"
                }
        
        # Ensure prev_close is set
        if live_data.get("prev_close") is None and len(df) >= 2:
            live_data["prev_close"] = float(df.iloc[-2]["close"])
        
        status_msg = f"✅ Data loaded for {symbol}"
        return df, live_data, status_msg
        
    except Exception as e:
        error_msg = str(e)
        return pd.DataFrame(), {}, f"❌ Error: {error_msg}"


def format_currency(value: float, decimals: int = 2) -> str:
    """Format a number as currency string."""
    if value is None:
        return "N/A"
    return f"${value:,.{decimals}f}"


def format_volume(value: int) -> str:
    """Format volume number with M/B/K suffixes."""
    if value is None:
        return "N/A"
    if value >= 1_000_000_000:
        return f"{value / 1_000_000_000:.2f}B"
    elif value >= 1_000_000:
        return f"{value / 1_000_000:.2f}M"
    elif value >= 1_000:
        return f"{value / 1_000:.2f}K"
    return str(value)


def calculate_change(current: float, previous: float) -> Tuple[float, float]:
    """
    Calculate price change amount and percentage.
    
    Returns:
        Tuple of (change_amount, change_percentage)
    """
    if previous is None or previous == 0:
        return 0.0, 0.0
    
    change_amount = current - previous
    change_percent = (change_amount / previous) * 100
    
    return change_amount, change_percent


def get_market_status_color(status: str) -> str:
    """Get color code for market status badge."""
    status_lower = status.lower()
    if "open" in status_lower:
        return "#00ff00"  # Green
    elif "closed" in status_lower or "close" in status_lower:
        return "#ff0000"  # Red
    elif "after" in status_lower or "extended" in status_lower:
        return "#ff8800"  # Orange
    return "#888888"  # Gray (unknown)


def get_watchlist_stocks_data(symbols: List[str]) -> Dict[str, Dict[str, Any]]:
    """
    Get live data for multiple stocks in watchlist.
    Uses Yahoo Finance - simple and reliable.
    
    Args:
        symbols: List of stock ticker symbols
    
    Returns:
        Dictionary mapping symbol to its live data
    """
    return yf_get_multiple(symbols)


def get_default_watchlist() -> List[str]:
    """
    Get default watchlist stocks.
    TSLA is always first (primary focus).
    
    Returns:
        List of default stock symbols
    """
    return ["TSLA", "AAPL", "MSFT", "GOOGL", "AMZN", "NVDA", "META"]


def format_stock_name(symbol: str) -> str:
    """
    Format stock symbol with company name (if known).
    
    Args:
        symbol: Stock ticker symbol
    
    Returns:
        Formatted string with symbol and name
    """
    if not symbol or not isinstance(symbol, str):
        return "Unknown"
    
    stock_names = {
        "TSLA": "Tesla",
        "AAPL": "Apple",
        "MSFT": "Microsoft",
        "GOOGL": "Google",
        "AMZN": "Amazon",
        "NVDA": "NVIDIA",
        "META": "Meta",
        "NFLX": "Netflix",
        "AMD": "AMD",
        "INTC": "Intel"
    }
    
    symbol_upper = symbol.upper().strip()
    name = stock_names.get(symbol_upper, "")
    if name:
        return f"{symbol_upper} ({name})"
    return symbol_upper
