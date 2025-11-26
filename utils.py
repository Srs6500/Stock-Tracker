"""
Data processing utilities and main data fetching function.
Combines database caching with Polygon API calls for optimal performance.
Supports both TSLA-specific (legacy) and multi-stock operations.
"""

import pandas as pd
from datetime import date, datetime, timedelta
from typing import Dict, Any, Optional, Tuple, List
import streamlit as st
from database import (
    get_session, 
    save_daily_data, 
    get_historical_data, 
    get_latest_date,
    save_stock_daily_data,
    get_stock_historical_data,
    get_latest_stock_date
)
from api_client import get_polygon_client, fetch_historical_data, fetch_live_snapshot
from data_processor import StockDataProcessor


@st.cache_data(ttl=60)  # Cache for 60 seconds to prevent API spam
def get_historical_and_live() -> Tuple[pd.DataFrame, Dict[str, Any], str]:
    """
    Main data fetching function with intelligent caching.
    
    Strategy:
    1. Check database for existing historical data
    2. If missing or stale, fetch from Polygon API
    3. Save new data to database
    4. Fetch live snapshot for current day data
    5. Return combined DataFrame and live metrics
    
    Returns:
        Tuple of:
        - DataFrame: Historical OHLCV data (last 30+ days)
        - Dict: Live metrics (current price, high, low, volume, prev_close, market_status)
        - Str: Status message (e.g., "Loaded from database" or "Fetched from API")
    """
    session = get_session()
    status_msg = "⚡ Loaded from local database"
    
    try:
        # Step 1: Check what we have in database
        db_data = get_historical_data(session, days=45)
        latest_db_date = get_latest_date(session)
        today = date.today()
        
        # Step 2: Determine if we need to fetch from API
        needs_fetch = False
        
        if not db_data or len(db_data) == 0:
            # Empty database - need to fetch
            needs_fetch = True
            status_msg = "🔄 Fetching from Polygon API (first time)"
        elif latest_db_date:
            # Check if we have today's data or if it's stale
            days_since_update = (today - latest_db_date).days
            
            # Fetch if:
            # - We don't have today's data (and it's a trading day)
            # - Data is more than 1 day old (to catch weekends/holidays)
            if days_since_update > 1:
                needs_fetch = True
                status_msg = f"🔄 Fetching fresh data (last update: {latest_db_date})"
        
        # Step 3: Fetch from API if needed
        if needs_fetch:
            client = get_polygon_client()
            api_data = fetch_historical_data(client, days=45)
            
            if api_data:
                # Save to database
                for row in api_data:
                    save_daily_data(
                        session=session,
                        date=row["date"],
                        open=row["open"],
                        high=row["high"],
                        low=row["low"],
                        close=row["close"],
                        volume=row["volume"]
                    )
                
                # Refresh from database
                db_data = get_historical_data(session, days=45)
                status_msg = "✅ Fetched and saved to database"
        
        # Step 4: Convert database records to DataFrame
        if db_data and len(db_data) > 0:
            df_data = []
            for record in db_data:
                df_data.append({
                    "date": record.date,
                    "open": record.open,
                    "high": record.high,
                    "low": record.low,
                    "close": record.close,
                    "volume": record.volume
                })
            
            df = pd.DataFrame(df_data)
            df.set_index("date", inplace=True)
        else:
            # Fallback: empty DataFrame
            df = pd.DataFrame(columns=["open", "high", "low", "close", "volume"])
            df.index.name = "date"
        
        # Step 5: Fetch live/today's data
        live_data = {}
        try:
            client = get_polygon_client()
            # Try snapshot first (paid tier), falls back to today's aggregates (free tier)
            snapshot = fetch_live_snapshot(client)
            
            if snapshot:
                live_data = snapshot
            else:
                # Fallback: use most recent close from historical data
                if not df.empty:
                    latest_row = df.iloc[-1]
                    live_data = {
                        "current_price": float(latest_row["close"]),
                        "today_high": float(latest_row["high"]),
                        "today_low": float(latest_row["low"]),
                        "today_volume": int(latest_row["volume"]),
                        "prev_close": float(latest_row["close"]) if len(df) > 1 else None,
                        "market_status": "closed"
                    }
        except Exception as e:
            # Silently fallback to latest historical data
            if not df.empty:
                latest_row = df.iloc[-1]
                live_data = {
                    "current_price": float(latest_row["close"]),
                    "today_high": float(latest_row["high"]),
                    "today_low": float(latest_row["low"]),
                    "today_volume": int(latest_row["volume"]),
                    "prev_close": float(latest_row["close"]) if len(df) > 1 else None,
                    "market_status": "closed"
                }
        
        # Ensure prev_close is set (use second-to-last day if not available)
        if live_data.get("prev_close") is None and len(df) >= 2:
            live_data["prev_close"] = float(df.iloc[-2]["close"])
        
        return df, live_data, status_msg
        
    except Exception as e:
        st.error(f"Error in data fetching: {str(e)}")
        # Return empty data with error message
        return pd.DataFrame(), {}, f"❌ Error: {str(e)}"
    
    finally:
        session.close()


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


# ============================================================================
# Multi-Stock Support Functions (Bloomberg-lite features)
# ============================================================================

def get_stock_data(symbol: str = "TSLA", days: int = 45) -> Tuple[pd.DataFrame, Dict[str, Any], str]:
    """
    Get stock data for any symbol (multi-stock support).
    Uses the new data processor for unified handling.
    Defaults to TSLA for backward compatibility.
    
    Args:
        symbol: Stock ticker symbol (default: "TSLA")
        days: Number of days of historical data
    
    Returns:
        Tuple of (DataFrame, live_data_dict, status_message)
    """
    processor = StockDataProcessor()
    return processor.get_stock_data_with_cache(symbol.upper(), days=days)


def get_watchlist_stocks_data(symbols: List[str]) -> Dict[str, Dict[str, Any]]:
    """
    Get live data for multiple stocks in watchlist.
    
    Args:
        symbols: List of stock ticker symbols
    
    Returns:
        Dictionary mapping symbol to its live data
    """
    processor = StockDataProcessor()
    return processor.get_multiple_stocks_live(symbols)


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
    
    name = stock_names.get(symbol.upper(), "")
    if name:
        return f"{symbol.upper()} ({name})"
    return symbol.upper()

