# TSLA Pulse - Real-Time Stock Dashboard

A beautiful, real-time Tesla (TSLA) stock monitoring dashboard built with Streamlit.

## Features

- 📊 **Live Stock Data**: Current price, daily high/low, previous close, volume
- 📈 **30-Day Chart**: Interactive candlestick chart with volume bars
- 🔄 **Auto-Refresh**: Optional 15-second auto-refresh for live updates
- 💾 **Local Caching**: SQLite database for offline capability and API call optimization
- 🎨 **Dark Mode UI**: Fintech-style interface with Tesla-red accents
- 📱 **Mobile Responsive**: Works beautifully on all devices

## Setup Instructions

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Get Polygon API Key

1. Sign up for a free account at [polygon.io](https://polygon.io/)
2. Get your API key from the dashboard

### 3. Configure API Key

Create a `.streamlit` folder in the project root, then create `secrets.toml`:

```bash
mkdir .streamlit
```

Copy `secrets.toml.example` to `.streamlit/secrets.toml` and add your API key:

```toml
POLYGON_API_KEY = "your_actual_api_key_here"
```

### 4. Run the App

```bash
streamlit run app.py
```

The app will open in your browser at `http://localhost:8501`

## How It Works

1. **First Launch**: Fetches historical data from Polygon API and stores in SQLite
2. **Subsequent Launches**: Loads from local database (fast!) and only fetches fresh data when needed
3. **Auto-Refresh**: When enabled, updates live data every 15 seconds during market hours
4. **Offline Mode**: Works with cached data if API is unavailable

## Project Structure

```
.
├── app.py                 # Main Streamlit application
├── database.py            # Database models and connection
├── api_client.py          # Polygon API integration
├── utils.py               # Data processing utilities
├── charts.py              # Plotly chart generation
├── requirements.txt       # Python dependencies
├── secrets.toml.example   # API key template
└── tsla_data.db          # SQLite database (created automatically)
```

## Notes

- Database file (`tsla_data.db`) is created automatically on first run
- Free Polygon tier has rate limits; the app caches data to minimize API calls
- Market status shows: Open (green), Closed (red), After Hours (orange)
