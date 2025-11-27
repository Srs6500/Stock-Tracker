# NASDAQ Stock List

## Current Setup

The app includes a curated list of ~65 major NASDAQ stocks for autocomplete search.

## To Expand to Full NASDAQ List (~3,000+ stocks)

### Option 1: Download from NASDAQ Website
1. Visit: https://www.nasdaq.com/market-activity/stocks/screener
2. Export the list as CSV
3. Save as `nasdaq_stocks.csv` in the project root
4. Ensure CSV has columns: `symbol` and `name` (or `Symbol` and `Name`)

### Option 2: Use NASDAQ API
- Download from: https://old.nasdaq.com/screening/companies-by-name.aspx
- Export as CSV

### Option 3: Use Python Script
You can create a script to fetch all NASDAQ stocks from various sources.

## File Format

The CSV should have this structure:
```csv
symbol,name
AAPL,Apple Inc.
MSFT,Microsoft Corporation
TSLA,Tesla Inc.
```

Or with capitalized headers:
```csv
Symbol,Name
AAPL,Apple Inc.
MSFT,Microsoft Corporation
```

The app will automatically detect and load the CSV file if it exists in the project root.

## Notes

- The app will use the CSV file if available, otherwise falls back to the curated list
- Update the CSV file periodically (every 3-6 months) to include new IPOs
- The file is cached by Streamlit for performance

