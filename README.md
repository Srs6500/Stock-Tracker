# StockTracker - Real-Time Stock Dashboard

A professional, multi-stock monitoring dashboard built with Streamlit. Track multiple stocks with real-time data, interactive charts, and portfolio management.

## Features

### Core Stock Monitoring
- 📊 **Live Stock Data**: Real-time price, daily high/low, previous close, volume for any stock
- 📈 **Interactive Charts**: 30-day candlestick charts with volume bars
- 🔄 **Real-Time Updates**: Fresh data on every page refresh
- 💾 **SQLite Database**: Local storage for watchlist and portfolio data
- 🎨 **Clean UI**: Professional, modern interface with centered design
- 📱 **Mobile Responsive**: Works beautifully on all devices

### Key Features
- 📋 **Multi-Stock Watchlist**: Track multiple stocks simultaneously with live price updates
- 🔍 **Google-like Search**: Dynamic autocomplete search for finding stocks quickly
- 💼 **Portfolio Tracker**: Manage holdings, track P&L, and monitor portfolio performance
- 📊 **Technical Indicators**: SMA (20, 50) overlays on charts
- 🔄 **Stock Comparison**: Compare multiple stocks with normalized percentage charts

## Setup Instructions

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Run the App

**No API keys required!** StockTracker uses yfinance, which provides free stock data without authentication.

```bash
streamlit run app.py
```

The app will open in your browser at `http://localhost:8501`

## How It Works

### Data Flow
1. **Data Source**: Uses yfinance to fetch real-time and historical stock data
2. **Fresh Data**: Fetches fresh data on every page refresh for up-to-date prices
3. **Local Storage**: SQLite database stores watchlist and portfolio data locally
4. **No API Keys**: Completely free - no authentication required

### Architecture
- **yfinance Client**: Simplified data fetching using Yahoo Finance
- **SQLite Database**: Local storage for watchlist and portfolio
- **Multi-Stock Support**: Generic database models support any stock symbol
- **Modular Design**: Separate UI components for watchlist, portfolio, and charts

## Project Structure

```
.
├── app.py                 # Main Streamlit application
├── database.py            # Database models (multi-stock support)
├── yfinance_client.py     # Yahoo Finance data fetching
├── utils.py               # Data processing utilities
├── charts.py              # Plotly candlestick charts with indicators
├── comparison_charts.py   # Stock comparison visualization
├── watchlist_ui.py        # Watchlist management UI component
├── portfolio_ui.py        # Portfolio tracker UI component
├── stock_list.py          # NASDAQ stock list for search
├── requirements.txt       # Python dependencies
└── tsla_data.db          # SQLite database (created automatically)
```

## Usage Tips

- **Watchlist**: Use the Google-like search to find stocks by symbol or company name, then click Add
- **Portfolio**: Track your holdings with purchase price and quantity for P&L calculations
- **Charts**: Use autoscale/reset buttons or double-click to reset chart view
- **Technical Indicators**: SMA (20, 50) lines appear automatically on charts
- **Search**: Start typing in the watchlist search box - suggestions appear as you type

## Notes

- Database file (`tsla_data.db`) is created automatically on first run
- Data is fetched fresh on every page refresh for real-time accuracy
- Market status shows: Open (green), Closed (red), After Hours (orange)
- No API keys required - completely free to use
- Search includes 65 major NASDAQ stocks (expandable via CSV - see STOCK_LIST_README.md)

## See Also

- [FEATURES.md](FEATURES.md) - Comprehensive feature list
- [DEMO_FOR_PROFESSOR.md](DEMO_FOR_PROFESSOR.md) - Demo guide for presentations
