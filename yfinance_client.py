"""
Simple Yahoo Finance client for stock data.
No API key needed - free and reliable.
"""

import yfinance as yf
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, List
import pandas as pd


def get_stock_data(symbol: str, days: int = 45) -> Optional[pd.DataFrame]:
    """
    Get historical stock data from Yahoo Finance.
    
    Args:
        symbol: Stock ticker symbol (e.g., 'TSLA', 'AAPL')
        days: Number of days of historical data
    
    Returns:
        DataFrame with OHLCV data, or None if error
    """
    try:
        ticker = yf.Ticker(symbol.upper())
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)
        
        # Fetch historical data
        df = ticker.history(start=start_date, end=end_date)
        
        if df.empty:
            return None
        
        # Reset index to get date as column
        df.reset_index(inplace=True)
        df['Date'] = pd.to_datetime(df['Date']).dt.date
        
        # Rename columns to match our format
        df.rename(columns={
            'Date': 'date',
            'Open': 'open',
            'High': 'high',
            'Low': 'low',
            'Close': 'close',
            'Volume': 'volume'
        }, inplace=True)
        
        # Select only needed columns
        df = df[['date', 'open', 'high', 'low', 'close', 'volume']]
        
        return df
        
    except Exception as e:
        print(f"Error fetching {symbol}: {str(e)}")
        return None


def get_live_price(symbol: str) -> Optional[Dict[str, Any]]:
    """
    Get live/current price data from Yahoo Finance.
    
    Args:
        symbol: Stock ticker symbol
    
    Returns:
        Dictionary with current price, high, low, volume, prev_close, market_status
    """
    try:
        ticker = yf.Ticker(symbol.upper())
        info = ticker.info
        
        # Get current price
        current_price = info.get('currentPrice') or info.get('regularMarketPrice')
        
        # Get today's data
        today_data = ticker.history(period='1d', interval='1m')
        
        today_high = None
        today_low = None
        today_volume = None
        
        if not today_data.empty:
            today_high = float(today_data['High'].max())
            today_low = float(today_data['Low'].min())
            today_volume = int(today_data['Volume'].sum())
        
        # Get previous close
        prev_close = info.get('previousClose') or info.get('regularMarketPreviousClose')
        
        # Market status
        market_status = "closed"
        if info.get('marketState') == 'REGULAR':
            market_status = "open"
        elif info.get('marketState') == 'CLOSED':
            market_status = "closed"
        elif info.get('marketState'):
            market_status = info.get('marketState', 'unknown').lower()
        
        return {
            "current_price": float(current_price) if current_price else None,
            "today_high": today_high,
            "today_low": today_low,
            "today_volume": today_volume,
            "prev_close": float(prev_close) if prev_close else None,
            "market_status": market_status
        }
        
    except Exception as e:
        print(f"Error fetching live price for {symbol}: {str(e)}")
        return None


def get_multiple_stocks_data(symbols: List[str]) -> Dict[str, Dict[str, Any]]:
    """
    Get live data for multiple stocks simultaneously.
    
    Args:
        symbols: List of stock ticker symbols
    
    Returns:
        Dictionary mapping symbol to its live data
    """
    results = {}
    for symbol in symbols:
        try:
            data = get_live_price(symbol)
            if data:
                results[symbol.upper()] = data
        except:
            continue
    
    return results

