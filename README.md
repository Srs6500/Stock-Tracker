# Stock Pulse - Real-Time Stock Dashboard (Bloomberg-lite)

A professional, multi-stock monitoring dashboard built with Streamlit. Originally focused on Tesla (TSLA), now expanded to support multiple stocks with Bloomberg Terminal-inspired features.

## Features

### Core Stock Monitoring
- 📊 **Live Stock Data**: Real-time price, daily high/low, previous close, volume for any stock
- 📈 **Interactive Charts**: 30-day candlestick charts with volume bars and technical indicators
- 🔄 **Auto-Refresh**: Optional 15-second auto-refresh for live market updates
- 💾 **Local Caching**: SQLite database for offline capability and API call optimization
- 🎨 **Dark Mode UI**: Professional fintech-style interface with customizable accents
- 📱 **Mobile Responsive**: Works beautifully on all devices

### Bloomberg-lite Features
- 📋 **Multi-Stock Watchlist**: Track multiple stocks simultaneously with live price updates
- 💼 **Portfolio Tracker**: Manage holdings, track P&L, and monitor portfolio performance
- 📰 **News Feed**: Real-time financial news for tracked stocks
- 📊 **Technical Indicators**: SMA (20, 50), RSI, MACD overlays on charts
- 🔄 **Stock Comparison**: Compare multiple stocks with normalized percentage charts
- 🔌 **Multi-API Support**: Unified wrapper supporting Polygon.io, Alpha Vantage, and NewsAPI

## Setup Instructions

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Get API Keys

**Required:**
- **Polygon.io**: Sign up for a free account at [polygon.io](https://polygon.io/) and get your API key

**Optional (for enhanced features):**
- **Alpha Vantage**: Get free API key at [alphavantage.co](https://www.alphavantage.co/support/#api-key) (for technical indicators)
- **NewsAPI**: Get free API key at [newsapi.org](https://newsapi.org/register) (for news feed)

### 3. Configure API Keys

Create a `.streamlit` folder in the project root, then create `secrets.toml`:

```bash
mkdir .streamlit
```

Copy `secrets.toml.example` to `.streamlit/secrets.toml` and add your API keys:

```toml
# Required
POLYGON_API_KEY = "your_polygon_api_key_here"

# Optional (for enhanced features)
ALPHA_VANTAGE_API_KEY = "your_alpha_vantage_key_here"
NEWSAPI_KEY = "your_newsapi_key_here"
```

### 4. Run the App

```bash
streamlit run app.py
```

The app will open in your browser at `http://localhost:8501`

## How It Works

### Data Flow
1. **First Launch**: Fetches historical data from Polygon API and stores in SQLite database
2. **Subsequent Launches**: Loads from local database (fast!) and only fetches fresh data when needed
3. **Auto-Refresh**: When enabled, updates live data every 15 seconds during market hours
4. **Offline Mode**: Works with cached data if API is unavailable

### Architecture
- **API Wrapper**: Unified interface for multiple data sources (Polygon, Alpha Vantage, NewsAPI)
- **Data Processor**: Intelligent caching layer with database-first strategy
- **Multi-Stock Support**: Generic database models support any stock symbol
- **Modular Design**: Separate UI components for watchlist, portfolio, news, and charts

## Project Structure

```
.
├── app.py                 # Main Streamlit application (Bloomberg-lite layout)
├── database.py            # Database models (multi-stock support)
├── api_client.py          # Polygon API integration
├── api_wrapper.py         # Multi-API wrapper (Polygon, Alpha Vantage, NewsAPI)
├── data_processor.py      # Unified data processing and caching layer
├── utils.py               # Data processing utilities
├── charts.py              # Plotly candlestick charts with indicators
├── comparison_charts.py   # Stock comparison visualization
├── watchlist_ui.py        # Watchlist management UI component
├── portfolio_ui.py        # Portfolio tracker UI component
├── news_ui.py             # News feed UI component
├── test_compatibility.py  # Backward compatibility test suite
├── requirements.txt       # Python dependencies
├── secrets.toml.example   # API key template
└── tsla_data.db          # SQLite database (created automatically)
```

## Usage Tips

- **Watchlist**: Add stocks by typing symbol (e.g., AAPL, MSFT) and clicking Add
- **Portfolio**: Track your holdings with purchase price and quantity for P&L calculations
- **Charts**: Use autoscale/reset buttons or double-click to reset chart view
- **Technical Indicators**: SMA lines appear automatically; RSI/MACD available with Alpha Vantage API key
- **News Feed**: Shows latest financial news for selected stock (requires NewsAPI key)

## Notes

- Database file (`tsla_data.db`) is created automatically on first run
- Free Polygon tier has rate limits; the app caches data to minimize API calls
- Market status shows: Open (green), Closed (red), After Hours (orange)
- All features work with Polygon API alone; optional APIs enhance functionality
- Backward compatible: Original TSLA-focused functions still work

## See Also

- [FEATURES.md](FEATURES.md) - Comprehensive feature list
- [DEMO_FOR_PROFESSOR.md](DEMO_FOR_PROFESSOR.md) - Demo guide for presentations
