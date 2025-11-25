"""
Database models and connection utilities for TSLA stock data storage.
Uses SQLModel for type-safe database operations with SQLite.
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

