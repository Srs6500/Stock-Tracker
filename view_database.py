"""
Database Viewer - Show database contents to professor
Run this to demonstrate where and how data is stored.
"""

from database import get_session, get_historical_data, TslaDaily
from sqlmodel import select
from datetime import date

def view_database():
    """Display database contents in a readable format."""
    print("=" * 80)
    print("TSLA STOCK DATABASE - DATA STORAGE DEMONSTRATION")
    print("=" * 80)
    print()
    
    session = get_session()
    
    try:
        # Get all records
        statement = select(TslaDaily).order_by(TslaDaily.date)
        all_records = session.exec(statement).all()
        
        if not all_records:
            print("⚠️  Database is empty. Run the app first to fetch and store data.")
            print("   Database file location: tsla_data.db (in project root)")
            return
        
        print(f"📊 Database File: tsla_data.db")
        print(f"📁 Location: {session.bind.url}")
        print(f"📈 Total Records: {len(all_records)}")
        print()
        print("=" * 80)
        print("DATABASE SCHEMA:")
        print("=" * 80)
        print("Table Name: tsla_daily")
        print("Columns:")
        print("  - date (PRIMARY KEY): Trading date")
        print("  - open: Opening price")
        print("  - high: Daily high price")
        print("  - low: Daily low price")
        print("  - close: Closing price")
        print("  - volume: Trading volume")
        print()
        print("=" * 80)
        print("SAMPLE DATA (First 10 records):")
        print("=" * 80)
        print(f"{'Date':<12} {'Open':<10} {'High':<10} {'Low':<10} {'Close':<10} {'Volume':<15}")
        print("-" * 80)
        
        for record in all_records[:10]:
            print(f"{str(record.date):<12} ${record.open:<9.2f} ${record.high:<9.2f} ${record.low:<9.2f} ${record.close:<9.2f} {record.volume:,}")
        
        if len(all_records) > 10:
            print(f"\n... and {len(all_records) - 10} more records")
        
        print()
        print("=" * 80)
        print("LATEST RECORD:")
        print("=" * 80)
        latest = all_records[-1]
        print(f"Date: {latest.date}")
        print(f"Open: ${latest.open:.2f}")
        print(f"High: ${latest.high:.2f}")
        print(f"Low: ${latest.low:.2f}")
        print(f"Close: ${latest.close:.2f}")
        print(f"Volume: {latest.volume:,}")
        print()
        print("=" * 80)
        print("HOW TO DEMONSTRATE TO PROFESSOR:")
        print("=" * 80)
        print("1. Show this output (run: python view_database.py)")
        print("2. Show the database file: tsla_data.db in project folder")
        print("3. Explain: SQLite is a REAL database (used by millions of apps)")
        print("4. Show database.py - the schema/model definition")
        print("5. Show how data is saved in utils.py (save_daily_data function)")
        print("6. Use a SQLite browser tool to view the .db file visually")
        print()
        print("SQLite Browser Tools:")
        print("  - DB Browser for SQLite (free): https://sqlitebrowser.org/")
        print("  - VS Code extension: SQLite Viewer")
        print()
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
    finally:
        session.close()

if __name__ == "__main__":
    view_database()

