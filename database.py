"""
Database models and connection utilities for stock data storage.
Uses SQLModel for type-safe database operations with SQLite.
Supports both single-stock (TSLA) and multi-stock operations.
"""

from datetime import date as date_type
from sqlmodel import SQLModel, Field, create_engine, Session, select
from typing import Optional
import os

# Database file path
DB_PATH = "tsla_data.db"
DATABASE_URL = f"sqlite:///{DB_PATH}"


class TslaDaily(SQLModel, table=True):
    """
    SQLModel table for storing TSLA daily OHLCV (Open/High/Low/Close/Volume) data.
    Date is the primary key to prevent duplicates.
    """
    __tablename__ = "tsla_daily"
    __table_args__ = {"extend_existing": True}
    
    date: date_type = Field(primary_key=True, description="Trading date")
    open: float = Field(description="Opening price")
    high: float = Field(description="Daily high price")
    low: float = Field(description="Daily low price")
    close: float = Field(description="Closing price")
    volume: int = Field(description="Trading volume")


def get_engine():
    """Create and return SQLite database engine."""
    engine = create_engine(DATABASE_URL, echo=False)
    return engine


def init_database():
    """
    Initialize the database by creating all tables.
    This is safe to call multiple times - it won't recreate existing tables.
    """
    engine = get_engine()
    SQLModel.metadata.create_all(engine)
    return engine


def get_session():
    """Get a database session for querying/inserting data."""
    engine = init_database()
    return Session(engine)


def save_daily_data(session: Session, date: date_type, open: float, high: float, 
                    low: float, close: float, volume: int):
    """
    Save or update daily TSLA data for a specific date.
    Uses INSERT OR REPLACE to handle duplicates gracefully.
    
    Args:
        session: Database session
        date: Trading date
        open: Opening price
        high: Daily high
        low: Daily low
        close: Closing price
        volume: Trading volume
    """
    daily_data = TslaDaily(
        date=date,
        open=open,
        high=high,
        low=low,
        close=close,
        volume=volume
    )
    session.merge(daily_data)  # Insert or update if exists
    session.commit()


def get_historical_data(session: Session, days: int = 30):
    """
    Retrieve the last N days of TSLA data from database.
    
    Args:
        session: Database session
        days: Number of days to retrieve (default: 30)
    
    Returns:
        List of TslaDaily objects, ordered by date (oldest first)
    """
    statement = select(TslaDaily).order_by(TslaDaily.date.desc()).limit(days)
    results = session.exec(statement).all()
    return list(reversed(results))  # Return oldest first for chronological order


def get_latest_date(session: Session) -> Optional[date_type]:
    """
    Get the most recent date in the database.
    
    Returns:
        Most recent date, or None if database is empty
    """
    statement = select(TslaDaily.date).order_by(TslaDaily.date.desc()).limit(1)
    result = session.exec(statement).first()
    return result


# ============================================================================
# Multi-Stock Database Models (Bloomberg-lite features)
# ============================================================================

class StockDaily(SQLModel, table=True):
    """
    Generic table for storing daily OHLCV data for any stock.
    Supports multiple stocks with symbol as part of composite key.
    """
    __tablename__ = "stock_daily"
    __table_args__ = {"extend_existing": True}
    
    symbol: str = Field(primary_key=True, description="Stock ticker symbol")
    date: date_type = Field(primary_key=True, description="Trading date")
    open: float = Field(description="Opening price")
    high: float = Field(description="Daily high price")
    low: float = Field(description="Daily low price")
    close: float = Field(description="Closing price")
    volume: int = Field(description="Trading volume")


class Watchlist(SQLModel, table=True):
    """
    User's stock watchlist - stores selected stocks to monitor.
    """
    __tablename__ = "watchlist"
    __table_args__ = {"extend_existing": True}
    
    symbol: str = Field(primary_key=True, description="Stock ticker symbol")
    added_date: date_type = Field(default_factory=date_type.today, description="Date added to watchlist")
    display_order: int = Field(default=0, description="Display order in watchlist")


class Portfolio(SQLModel, table=True):
    """
    User's portfolio - stores stock holdings with quantities and purchase prices.
    """
    __tablename__ = "portfolio"
    __table_args__ = {"extend_existing": True}
    
    symbol: str = Field(primary_key=True, description="Stock ticker symbol")
    quantity: float = Field(description="Number of shares owned")
    purchase_price: float = Field(description="Average purchase price per share")
    purchase_date: date_type = Field(default_factory=date_type.today, description="Purchase date")


# ============================================================================
# Multi-Stock Database Functions
# ============================================================================

def save_stock_daily_data(session: Session, symbol: str, date: date_type, 
                          open: float, high: float, low: float, close: float, volume: int):
    """
    Save or update daily stock data for any symbol.
    
    Args:
        session: Database session
        symbol: Stock ticker symbol (e.g., 'AAPL', 'MSFT')
        date: Trading date
        open: Opening price
        high: Daily high
        low: Daily low
        close: Closing price
        volume: Trading volume
    """
    stock_data = StockDaily(
        symbol=symbol.upper(),
        date=date,
        open=open,
        high=high,
        low=low,
        close=close,
        volume=volume
    )
    session.merge(stock_data)
    session.commit()


def get_stock_historical_data(session: Session, symbol: str, days: int = 30):
    """
    Retrieve historical data for a specific stock.
    
    Args:
        session: Database session
        symbol: Stock ticker symbol
        days: Number of days to retrieve
    
    Returns:
        List of StockDaily objects, ordered by date (oldest first)
    """
    statement = (
        select(StockDaily)
        .where(StockDaily.symbol == symbol.upper())
        .order_by(StockDaily.date.desc())
        .limit(days)
    )
    results = session.exec(statement).all()
    return list(reversed(results))


def get_latest_stock_date(session: Session, symbol: str) -> Optional[date_type]:
    """
    Get the most recent date for a specific stock in the database.
    
    Args:
        session: Database session
        symbol: Stock ticker symbol
    
    Returns:
        Most recent date, or None if no data exists
    """
    statement = (
        select(StockDaily.date)
        .where(StockDaily.symbol == symbol.upper())
        .order_by(StockDaily.date.desc())
        .limit(1)
    )
    result = session.exec(statement).first()
    return result


# Watchlist functions
def add_to_watchlist(session: Session, symbol: str):
    """Add a stock to the watchlist."""
    watchlist_item = Watchlist(
        symbol=symbol.upper(),
        added_date=date_type.today(),
        display_order=0
    )
    session.merge(watchlist_item)
    session.commit()


def remove_from_watchlist(session: Session, symbol: str):
    """Remove a stock from the watchlist."""
    statement = select(Watchlist).where(Watchlist.symbol == symbol.upper())
    item = session.exec(statement).first()
    if item:
        session.delete(item)
        session.commit()


def get_watchlist(session: Session) -> list:
    """Get all stocks in the watchlist."""
    statement = select(Watchlist).order_by(Watchlist.display_order, Watchlist.added_date)
    return list(session.exec(statement).all())


def is_in_watchlist(session: Session, symbol: str) -> bool:
    """Check if a stock is in the watchlist."""
    statement = select(Watchlist).where(Watchlist.symbol == symbol.upper())
    return session.exec(statement).first() is not None


# Portfolio functions
def add_to_portfolio(session: Session, symbol: str, quantity: float, purchase_price: float):
    """Add or update a stock in the portfolio."""
    portfolio_item = Portfolio(
        symbol=symbol.upper(),
        quantity=quantity,
        purchase_price=purchase_price,
        purchase_date=date_type.today()
    )
    session.merge(portfolio_item)
    session.commit()


def remove_from_portfolio(session: Session, symbol: str):
    """Remove a stock from the portfolio."""
    statement = select(Portfolio).where(Portfolio.symbol == symbol.upper())
    item = session.exec(statement).first()
    if item:
        session.delete(item)
        session.commit()


def get_portfolio(session: Session) -> list:
    """Get all stocks in the portfolio."""
    statement = select(Portfolio)
    return list(session.exec(statement).all())


def update_portfolio_quantity(session: Session, symbol: str, quantity: float):
    """Update the quantity of a stock in the portfolio."""
    statement = select(Portfolio).where(Portfolio.symbol == symbol.upper())
    item = session.exec(statement).first()
    if item:
        item.quantity = quantity
        session.add(item)
        session.commit()

