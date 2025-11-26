"""
Multi-API Wrapper for Stock Data
Unified interface for multiple stock data APIs with fallback mechanisms.
Supports: Polygon.io, Alpha Vantage, NewsAPI, Yahoo Finance
"""

from typing import Optional, Dict, Any, List
from datetime import datetime, date, timedelta
import streamlit as st
import requests
import time

# Import existing Polygon client (keep backward compatibility)
from api_client import get_polygon_client, fetch_historical_data, fetch_live_snapshot, fetch_today_data


class StockDataWrapper:
    """
    Unified wrapper for multiple stock data APIs.
    Provides fallback mechanisms and unified data format.
    """
    
    def __init__(self):
        """Initialize all API clients."""
        self.polygon_client = None
        self.alpha_vantage_key = None
        self.newsapi_key = None
        self._init_clients()
    
    def _init_clients(self):
        """Initialize API clients from secrets."""
        try:
            # Polygon (existing - required)
            self.polygon_client = get_polygon_client()
        except Exception as e:
            st.warning(f"Polygon API not configured: {str(e)}")
        
        try:
            # Alpha Vantage (optional - for indicators)
            self.alpha_vantage_key = st.secrets.get("ALPHA_VANTAGE_API_KEY")
        except:
            pass  # Optional
        
        try:
            # NewsAPI (optional - for news)
            self.newsapi_key = st.secrets.get("NEWSAPI_KEY")
        except:
            pass  # Optional
    
    def get_stock_data(self, symbol: str, days: int = 45) -> Optional[List[Dict[str, Any]]]:
        """
        Get historical stock data for any symbol.
        Uses Polygon API (primary) with fallback options.
        
        Args:
            symbol: Stock ticker symbol (e.g., 'TSLA', 'AAPL')
            days: Number of days of historical data
        
        Returns:
            List of dictionaries with OHLCV data, or None if error
        """
        if not self.polygon_client:
            return None
        
        try:
            # Use existing Polygon function but for any symbol
            end_date = datetime.now().date()
            start_date = end_date - timedelta(days=days)
            
            start_timestamp = int(datetime.combine(start_date, datetime.min.time()).timestamp() * 1000)
            end_timestamp = int(datetime.combine(end_date, datetime.max.time()).timestamp() * 1000)
            
            aggs = self.polygon_client.get_aggs(
                ticker=symbol.upper(),
                multiplier=1,
                timespan="day",
                from_=start_timestamp,
                to=end_timestamp,
                limit=50000
            )
            
            historical_data = []
            for agg in aggs:
                agg_date = datetime.fromtimestamp(agg.timestamp / 1000).date()
                historical_data.append({
                    "date": agg_date,
                    "open": float(agg.open),
                    "high": float(agg.high),
                    "low": float(agg.low),
                    "close": float(agg.close),
                    "volume": int(agg.volume)
                })
            
            historical_data.sort(key=lambda x: x["date"])
            return historical_data
            
        except Exception as e:
            st.error(f"Error fetching data for {symbol}: {str(e)}")
            return None
    
    def get_live_price(self, symbol: str) -> Optional[Dict[str, Any]]:
        """
        Get live/current price data for any symbol.
        
        Args:
            symbol: Stock ticker symbol
        
        Returns:
            Dictionary with current price, high, low, volume, or None
        """
        if not self.polygon_client:
            return None
        
        try:
            # Try snapshot first
            snapshots = self.polygon_client.get_snapshot_all(
                market_type='stocks', 
                tickers=[symbol.upper()]
            )
            
            if snapshots and len(snapshots) > 0:
                snapshot = snapshots[0]
                ticker_data = snapshot.ticker
                
                current_price = None
                if ticker_data.day:
                    current_price = float(ticker_data.day.c) if ticker_data.day.c else None
                
                today_high = None
                today_low = None
                today_volume = None
                if ticker_data.day:
                    today_high = float(ticker_data.day.h) if ticker_data.day.h else None
                    today_low = float(ticker_data.day.l) if ticker_data.day.l else None
                    today_volume = int(ticker_data.day.v) if ticker_data.day.v else None
                
                prev_close = None
                if ticker_data.prev_day:
                    prev_close = float(ticker_data.prev_day.c) if ticker_data.prev_day.c else None
                
                market_status = "unknown"
                if ticker_data.market_status:
                    market_status = ticker_data.market_status.lower()
                
                return {
                    "current_price": current_price,
                    "today_high": today_high,
                    "today_low": today_low,
                    "today_volume": today_volume,
                    "prev_close": prev_close,
                    "market_status": market_status
                }
        except Exception as e:
            # Fallback to today's aggregate data
            try:
                today = date.today()
                start_timestamp = int(datetime.combine(today, datetime.min.time()).timestamp() * 1000)
                end_timestamp = int(datetime.combine(today, datetime.max.time()).timestamp() * 1000)
                
                aggs = self.polygon_client.get_aggs(
                    ticker=symbol.upper(),
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
                        "prev_close": None,
                        "market_status": "closed"
                    }
            except:
                pass
        
        return None
    
    def get_technical_indicators(self, symbol: str, function: str = "RSI") -> Optional[Dict[str, Any]]:
        """
        Get technical indicators using Alpha Vantage API.
        
        Args:
            symbol: Stock ticker symbol
            function: Indicator type ('RSI', 'MACD', 'SMA', 'EMA')
        
        Returns:
            Dictionary with indicator data, or None if error
        """
        if not self.alpha_vantage_key:
            return None
        
        try:
            base_url = "https://www.alphavantage.co/query"
            params = {
                "function": function,
                "symbol": symbol.upper(),
                "interval": "daily",
                "time_period": 14,
                "series_type": "close",
                "apikey": self.alpha_vantage_key
            }
            
            # Add function-specific parameters
            if function == "MACD":
                params.update({
                    "fastperiod": 12,
                    "slowperiod": 26,
                    "signalperiod": 9
                })
            elif function in ["SMA", "EMA"]:
                params["time_period"] = 20
            
            response = requests.get(base_url, params=params, timeout=10)
            data = response.json()
            
            # Handle rate limiting
            if "Note" in data or "Information" in data:
                return None
            
            return data
            
        except Exception as e:
            return None
    
    def get_news(self, symbol: str, limit: int = 10) -> Optional[List[Dict[str, Any]]]:
        """
        Get news articles for a stock symbol using NewsAPI.
        
        Args:
            symbol: Stock ticker symbol
            limit: Maximum number of articles to return
        
        Returns:
            List of news article dictionaries, or None if error
        """
        if not self.newsapi_key:
            return None
        
        try:
            # NewsAPI requires company name, so we'll search by symbol
            url = "https://newsapi.org/v2/everything"
            params = {
                "q": symbol,
                "sortBy": "publishedAt",
                "language": "en",
                "pageSize": limit,
                "apiKey": self.newsapi_key
            }
            
            response = requests.get(url, params=params, timeout=10)
            data = response.json()
            
            if data.get("status") == "ok":
                articles = []
                for article in data.get("articles", [])[:limit]:
                    articles.append({
                        "title": article.get("title", ""),
                        "description": article.get("description", ""),
                        "url": article.get("url", ""),
                        "publishedAt": article.get("publishedAt", ""),
                        "source": article.get("source", {}).get("name", "")
                    })
                return articles
            
            return None
            
        except Exception as e:
            return None
    
    def get_multiple_stocks_data(self, symbols: List[str]) -> Dict[str, Dict[str, Any]]:
        """
        Get live data for multiple stocks simultaneously.
        
        Args:
            symbols: List of stock ticker symbols
        
        Returns:
            Dictionary mapping symbol to its live data
        """
        results = {}
        for symbol in symbols:
            data = self.get_live_price(symbol)
            if data:
                results[symbol.upper()] = data
            # Small delay to avoid rate limits
            time.sleep(0.1)
        
        return results

