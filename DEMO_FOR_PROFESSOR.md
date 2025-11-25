# Database Demonstration Guide for Professor

## Where Data is Stored

### Database File Location
- **File**: `tsla_data.db`
- **Location**: Project root directory (`C:\Users\Dell\CSCI 621 - Project\tsla_data.db`)
- **Type**: SQLite database (file-based relational database)

### Important: SQLite IS a Real Database
SQLite is a **full-featured SQL database engine** used by:
- Android (built-in)
- iOS (built-in)
- Firefox, Chrome browsers
- Millions of applications worldwide
- It's just file-based (no separate server needed)

## How to Show Database to Professor

### Method 1: View Database Contents (Command Line)
```bash
python view_database.py
```
This shows:
- Database schema (table structure)
- Sample data (first 10 records)
- Total record count
- Latest record

### Method 2: Visual Database Browser
1. **Download DB Browser for SQLite** (free): https://sqlitebrowser.org/
2. Open `tsla_data.db` in the browser
3. View tables, data, and run SQL queries

### Method 3: VS Code Extension
1. Install "SQLite Viewer" extension in VS Code
2. Right-click `tsla_data.db` → "Open Database"
3. View tables and data visually

### Method 4: Show the Code
Point to these files:
- **`database.py`**: Database models and schema definition
  - Shows `TslaDaily` table structure
  - Shows how data is stored (date, open, high, low, close, volume)
- **`utils.py`**: Data saving logic
  - `save_daily_data()` function saves to database
  - `get_historical_data()` function retrieves from database

## Database Schema

**Table Name**: `tsla_daily`

| Column | Type | Description |
|--------|------|-------------|
| date | DATE (PRIMARY KEY) | Trading date |
| open | FLOAT | Opening price |
| high | FLOAT | Daily high price |
| low | FLOAT | Daily low price |
| close | FLOAT | Closing price |
| volume | INTEGER | Trading volume |

## What Gets Stored

- **Historical Data**: Last 45 days of TSLA stock data (OHLCV)
- **Auto-updates**: When new trading day data is available
- **Persistent**: Data persists between app runs
- **Offline Capable**: App works with cached data if API is down

## Key Points to Explain

1. **SQLite is a real database** - Just file-based (no server setup needed)
2. **Data persistence** - Data saved in `tsla_data.db` file
3. **ORM (Object-Relational Mapping)** - Using SQLModel for type-safe database operations
4. **Caching strategy** - Reduces API calls by storing historical data locally
5. **Database operations** - INSERT, SELECT, UPDATE all handled in `database.py`

## Demonstration Script

Run this to show database contents:
```bash
python view_database.py
```

This will display:
- Database file location
- Total number of records
- Sample data
- Latest record
- Database schema

