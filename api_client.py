"""
Polygon.io API client for fetching TSLA stock data.
Handles both historical OHLCV data and live snapshot data.
"""

from polygon import RESTClient
from datetime import datetime, date, timedelta
from typing import Optional, Dict, Any
import streamlit as st


def get_polygon_client() -> RESTClient:
    """
    Initialize and return Polygon REST client.
    Reads API key from Streamlit secrets.
    
    Returns:
        Polygon RESTClient instance
        
    Raises:
        KeyError: If POLYGON_API_KEY is not found in secrets
    """
    try:
        api_key = st.secrets["POLYGON_API_KEY"]
        if not api_key or api_key == "your_polygon_api_key_here":
            raise ValueError("Please configure your Polygon API key in .streamlit/secrets.toml")
        return RESTClient(api_key)
    except KeyError:
        raise KeyError(
            "POLYGON_API_KEY not found in secrets. "
            "Please create .streamlit/secrets.toml with your API key."
        )


def fetch_historical_data(client: RESTClient, days: int = 45) -> list:
    """
    Fetch historical daily OHLCV data for TSLA from Polygon API.
    
    Args:
        client: Polygon RESTClient instance
        days: Number of days to fetch (default: 45 to account for weekends/holidays)
    
    Returns:
        List of dictionaries with date, open, high, low, close, volume
    """
    # Calculate start date (days back from today)
    end_date = datetime.now().date()
    start_date = end_date - timedelta(days=days)
    
    # Convert to timestamps (milliseconds)
    start_timestamp = int(datetime.combine(start_date, datetime.min.time()).timestamp() * 1000)
    end_timestamp = int(datetime.combine(end_date, datetime.max.time()).timestamp() * 1000)
    
    try:
        # Fetch aggregates (daily bars)
        aggs = client.get_aggs(
            ticker="TSLA",
            multiplier=1,
            timespan="day",
            from_=start_timestamp,
            to=end_timestamp,
            limit=50000  # Max limit
        )
        
        # Convert to list of dicts
        historical_data = []
        for agg in aggs:
            # Convert timestamp to date
            agg_date = datetime.fromtimestamp(agg.timestamp / 1000).date()
            
            historical_data.append({
                "date": agg_date,
                "open": float(agg.open),
                "high": float(agg.high),
                "low": float(agg.low),
                "close": float(agg.close),
                "volume": int(agg.volume)
            })
        
        # Sort by date (oldest first)
        historical_data.sort(key=lambda x: x["date"])
        
        return historical_data
        
    except Exception as e:
        st.error(f"Error fetching historical data from Polygon API: {str(e)}")
        return []


def fetch_today_data(client: RESTClient) -> Optional[Dict[str, Any]]:
    """
    Fetch today's data for TSLA from Polygon API using aggregates (free tier compatible).
    Falls back to snapshot if available (paid tier).
    
    Args:
        client: Polygon RESTClient instance
    
    Returns:
        Dictionary with today's data, or None if error
    """
    from datetime import datetime, date
    
    try:
        # Try to get today's data from aggregates (free tier compatible)
        today = date.today()
        start_timestamp = int(datetime.combine(today, datetime.min.time()).timestamp() * 1000)
        end_timestamp = int(datetime.combine(today, datetime.max.time()).timestamp() * 1000)
        
        # Get today's aggregate data
        aggs = client.get_aggs(
            ticker="TSLA",
            multiplier=1,
            timespan="day",
            from_=start_timestamp,
            to=end_timestamp,
            limit=1
        )
        
        if aggs and len(aggs) > 0:
            agg = aggs[0]
            return {
                "current_price": float(agg.close) if agg.close else None,
                "today_high": float(agg.high) if agg.high else None,
                "today_low": float(agg.low) if agg.low else None,
                "today_volume": int(agg.volume) if agg.volume else None,
                "prev_close": None,  # Will be filled from historical data
                "market_status": "closed"  # Default, can't determine from aggregates
            }
        
        return None
        
    except Exception as e:
        # Silently fail - we'll use historical data as fallback
        return None


def fetch_live_snapshot(client: RESTClient) -> Optional[Dict[str, Any]]:
    """
    Fetch live snapshot data for TSLA from Polygon API (paid tier only).
    Falls back to today's aggregates if snapshot is not available.
    
    Args:
        client: Polygon RESTClient instance
    
    Returns:
        Dictionary with live data, or None if error
    """
    try:
        # Try snapshot first (paid tier)
        snapshots = client.get_snapshot_all(market_type='stocks', tickers=['TSLA'])
        
        if not snapshots or len(snapshots) == 0:
            return None
        
        snapshot = snapshots[0]
        ticker_data = snapshot.ticker
        
        # Extract current price (last trade)
        current_price = None
        if ticker_data.day:
            current_price = float(ticker_data.day.c) if ticker_data.day.c else None
        
        # Extract today's high/low
        today_high = None
        today_low = None
        today_volume = None
        if ticker_data.day:
            today_high = float(ticker_data.day.h) if ticker_data.day.h else None
            today_low = float(ticker_data.day.l) if ticker_data.day.l else None
            today_volume = int(ticker_data.day.v) if ticker_data.day.v else None
        
        # Get previous close
        prev_close = None
        if ticker_data.prev_day:
            prev_close = float(ticker_data.prev_day.c) if ticker_data.prev_day.c else None
        
        # Market status
        market_status = "unknown"
        if ticker_data.market_status:
            market_status = ticker_data.market_status.lower()
        
        # If no current price from day, try last quote
        if current_price is None and ticker_data.last_quote:
            if ticker_data.last_quote.bp:  # bid price
                current_price = float(ticker_data.last_quote.bp)
            elif ticker_data.last_quote.ap:  # ask price
                current_price = float(ticker_data.last_quote.ap)
        
        return {
            "current_price": current_price,
            "today_high": today_high,
            "today_low": today_low,
            "today_volume": today_volume,
            "prev_close": prev_close,
            "market_status": market_status
        }
        
    except Exception as e:
        # If snapshot fails (free tier), try today's aggregates instead
        error_str = str(e)
        if "NOT_AUTHORIZED" in error_str or "not entitled" in error_str.lower():
            # Free tier - use aggregates instead
            return fetch_today_data(client)
        # Other errors - return None silently
        return None

