"""
Unified Data Processing Layer
Normalizes data from multiple APIs into consistent formats.
Handles data transformation, caching, and error handling.
"""

import pandas as pd
from datetime import date, datetime, timedelta
from typing import Dict, Any, Optional, List, Tuple
import streamlit as st
from api_wrapper import StockDataWrapper
from database import (
    get_session, 
    save_stock_daily_data, 
    get_stock_historical_data,
    get_latest_stock_date,
    StockDaily
)


class StockDataProcessor:
    """
    Processes and normalizes stock data from multiple sources.
    Handles caching, data transformation, and unified data format.
    """
    
    def __init__(self):
        """Initialize the data processor with API wrapper."""
        self.api_wrapper = StockDataWrapper()
    
    @st.cache_data(ttl=60)
    def get_stock_data_with_cache(self, symbol: str, days: int = 45) -> Tuple[pd.DataFrame, Dict[str, Any], str]:
        """
        Get stock data with intelligent caching (database-first strategy).
        Similar to get_historical_and_live() but works for any symbol.
        
        Args:
            symbol: Stock ticker symbol
            days: Number of days of historical data
        
        Returns:
            Tuple of (DataFrame, live_data_dict, status_message)
        """
        session = get_session()
        status_msg = "⚡ Loaded from local database"
        
        try:
            # Step 1: Check database for existing data
            db_data = get_stock_historical_data(session, symbol, days=days)
            latest_db_date = get_latest_stock_date(session, symbol)
            today = date.today()
            
            # Step 2: Determine if we need to fetch from API
            needs_fetch = False
            
            if not db_data or len(db_data) == 0:
                needs_fetch = True
                status_msg = f"🔄 Fetching {symbol} from API (first time)"
            elif latest_db_date:
                days_since_update = (today - latest_db_date).days
                if days_since_update > 1:
                    needs_fetch = True
                    status_msg = f"🔄 Fetching fresh {symbol} data (last update: {latest_db_date})"
            
            # Step 3: Fetch from API if needed
            if needs_fetch:
                api_data = self.api_wrapper.get_stock_data(symbol, days=days)
                
                if api_data:
                    # Save to database
                    for row in api_data:
                        save_stock_daily_data(
                            session=session,
                            symbol=symbol,
                            date=row["date"],
                            open=row["open"],
                            high=row["high"],
                            low=row["low"],
                            close=row["close"],
                            volume=row["volume"]
                        )
                    
                    # Refresh from database
                    db_data = get_stock_historical_data(session, symbol, days=days)
                    status_msg = f"✅ Fetched and saved {symbol} to database"
            
            # Step 4: Convert to DataFrame
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
                df = pd.DataFrame(columns=["open", "high", "low", "close", "volume"])
                df.index.name = "date"
            
            # Step 5: Fetch live data
            live_data = {}
            try:
                snapshot = self.api_wrapper.get_live_price(symbol)
                
                if snapshot:
                    live_data = snapshot
                else:
                    # Fallback to latest historical data
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
                # Silently fallback
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
            
            # Ensure prev_close is set
            if live_data.get("prev_close") is None and len(df) >= 2:
                live_data["prev_close"] = float(df.iloc[-2]["close"])
            
            return df, live_data, status_msg
            
        except Exception as e:
            st.error(f"Error processing {symbol}: {str(e)}")
            return pd.DataFrame(), {}, f"❌ Error: {str(e)}"
        
        finally:
            session.close()
    
    def get_multiple_stocks_live(self, symbols: List[str]) -> Dict[str, Dict[str, Any]]:
        """
        Get live data for multiple stocks simultaneously.
        
        Args:
            symbols: List of stock ticker symbols
        
        Returns:
            Dictionary mapping symbol to its live data
        """
        return self.api_wrapper.get_multiple_stocks_data(symbols)
    
    def get_technical_indicators_data(self, symbol: str, indicators: List[str] = None) -> Dict[str, Any]:
        """
        Get technical indicators for a stock.
        
        Args:
            symbol: Stock ticker symbol
            indicators: List of indicators to fetch (default: ['RSI', 'MACD', 'SMA'])
        
        Returns:
            Dictionary with indicator data
        """
        if indicators is None:
            indicators = ['RSI', 'MACD', 'SMA']
        
        result = {}
        for indicator in indicators:
            data = self.api_wrapper.get_technical_indicators(symbol, indicator)
            if data:
                result[indicator] = data
        
        return result
    
    def get_news_data(self, symbol: str, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Get news articles for a stock.
        
        Args:
            symbol: Stock ticker symbol
            limit: Maximum number of articles
        
        Returns:
            List of news article dictionaries
        """
        news = self.api_wrapper.get_news(symbol, limit=limit)
        return news if news else []
    
    def normalize_price_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Normalize price data from different API sources to unified format.
        
        Args:
            data: Raw data from API
        
        Returns:
            Normalized data dictionary
        """
        normalized = {
            "current_price": data.get("current_price") or data.get("price") or data.get("close"),
            "today_high": data.get("today_high") or data.get("high"),
            "today_low": data.get("today_low") or data.get("low"),
            "today_volume": data.get("today_volume") or data.get("volume"),
            "prev_close": data.get("prev_close") or data.get("previous_close"),
            "market_status": data.get("market_status", "unknown")
        }
        
        return normalized
    
    def calculate_portfolio_value(self, portfolio: List[Dict], current_prices: Dict[str, float]) -> Dict[str, Any]:
        """
        Calculate portfolio value and P&L.
        
        Args:
            portfolio: List of portfolio items with symbol, quantity, purchase_price
            current_prices: Dictionary mapping symbol to current price
        
        Returns:
            Dictionary with total_value, total_cost, pnl, pnl_percent
        """
        total_cost = 0.0
        total_value = 0.0
        
        for item in portfolio:
            symbol = item.get("symbol", "").upper()
            quantity = item.get("quantity", 0.0)
            purchase_price = item.get("purchase_price", 0.0)
            current_price = current_prices.get(symbol, 0.0)
            
            cost = quantity * purchase_price
            value = quantity * current_price
            
            total_cost += cost
            total_value += value
        
        pnl = total_value - total_cost
        pnl_percent = (pnl / total_cost * 100) if total_cost > 0 else 0.0
        
        return {
            "total_cost": total_cost,
            "total_value": total_value,
            "pnl": pnl,
            "pnl_percent": pnl_percent
        }

