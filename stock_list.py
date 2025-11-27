"""
Stock list loader for NASDAQ stocks.
Loads stock symbols and company names for autocomplete search.
"""

import pandas as pd
import json
import os
from typing import List, Dict, Tuple
import streamlit as st


@st.cache_data
def load_nasdaq_stocks() -> List[Dict[str, str]]:
    """
    Load NASDAQ stock list with symbols and company names.
    Returns list of dicts with 'symbol' and 'name' keys.
    
    Returns:
        List of stock dictionaries
    """
    # Try to load from CSV file first
    csv_path = "nasdaq_stocks.csv"
    if os.path.exists(csv_path):
        try:
            df = pd.read_csv(csv_path)
            # Expected columns: symbol, name (or similar)
            if 'symbol' in df.columns and 'name' in df.columns:
                return df[['symbol', 'name']].to_dict('records')
            elif 'Symbol' in df.columns and 'Name' in df.columns:
                df.columns = df.columns.str.lower()
                return df[['symbol', 'name']].to_dict('records')
        except Exception as e:
            st.warning(f"Could not load CSV: {str(e)}")
    
    # Fallback: Return comprehensive list of major NASDAQ stocks
    # This is a curated list - user can add full CSV later
    major_stocks = [
        {"symbol": "AAPL", "name": "Apple Inc."},
        {"symbol": "MSFT", "name": "Microsoft Corporation"},
        {"symbol": "GOOGL", "name": "Alphabet Inc. (Class A)"},
        {"symbol": "GOOG", "name": "Alphabet Inc. (Class C)"},
        {"symbol": "AMZN", "name": "Amazon.com Inc."},
        {"symbol": "NVDA", "name": "NVIDIA Corporation"},
        {"symbol": "META", "name": "Meta Platforms Inc."},
        {"symbol": "TSLA", "name": "Tesla Inc."},
        {"symbol": "NFLX", "name": "Netflix Inc."},
        {"symbol": "AMD", "name": "Advanced Micro Devices"},
        {"symbol": "INTC", "name": "Intel Corporation"},
        {"symbol": "PYPL", "name": "PayPal Holdings Inc."},
        {"symbol": "ADBE", "name": "Adobe Inc."},
        {"symbol": "CMCSA", "name": "Comcast Corporation"},
        {"symbol": "COST", "name": "Costco Wholesale Corporation"},
        {"symbol": "AVGO", "name": "Broadcom Inc."},
        {"symbol": "PEP", "name": "PepsiCo Inc."},
        {"symbol": "CSCO", "name": "Cisco Systems Inc."},
        {"symbol": "TXN", "name": "Texas Instruments Inc."},
        {"symbol": "QCOM", "name": "QUALCOMM Incorporated"},
        {"symbol": "AMGN", "name": "Amgen Inc."},
        {"symbol": "ISRG", "name": "Intuitive Surgical Inc."},
        {"symbol": "BKNG", "name": "Booking Holdings Inc."},
        {"symbol": "VRTX", "name": "Vertex Pharmaceuticals Inc."},
        {"symbol": "REGN", "name": "Regeneron Pharmaceuticals Inc."},
        {"symbol": "GILD", "name": "Gilead Sciences Inc."},
        {"symbol": "ADI", "name": "Analog Devices Inc."},
        {"symbol": "ANSS", "name": "ANSYS Inc."},
        {"symbol": "CDNS", "name": "Cadence Design Systems Inc."},
        {"symbol": "SNPS", "name": "Synopsys Inc."},
        {"symbol": "KLAC", "name": "KLA Corporation"},
        {"symbol": "LRCX", "name": "Lam Research Corporation"},
        {"symbol": "MCHP", "name": "Microchip Technology Inc."},
        {"symbol": "MRVL", "name": "Marvell Technology Inc."},
        {"symbol": "NXPI", "name": "NXP Semiconductors N.V."},
        {"symbol": "ON", "name": "ON Semiconductor Corporation"},
        {"symbol": "SWKS", "name": "Skyworks Solutions Inc."},
        {"symbol": "CRWD", "name": "CrowdStrike Holdings Inc."},
        {"symbol": "ZS", "name": "Zscaler Inc."},
        {"symbol": "FTNT", "name": "Fortinet Inc."},
        {"symbol": "PANW", "name": "Palo Alto Networks Inc."},
        {"symbol": "OKTA", "name": "Okta Inc."},
        {"symbol": "DOCN", "name": "DigitalOcean Holdings Inc."},
        {"symbol": "NET", "name": "Cloudflare Inc."},
        {"symbol": "DDOG", "name": "Datadog Inc."},
        {"symbol": "SPLK", "name": "Splunk Inc."},
        {"symbol": "TEAM", "name": "Atlassian Corporation"},
        {"symbol": "ZM", "name": "Zoom Video Communications Inc."},
        {"symbol": "DOCU", "name": "DocuSign Inc."},
        {"symbol": "NOW", "name": "ServiceNow Inc."},
        {"symbol": "WDAY", "name": "Workday Inc."},
        {"symbol": "VEEV", "name": "Veeva Systems Inc."},
        {"symbol": "HUBS", "name": "HubSpot Inc."},
        {"symbol": "BILL", "name": "Bill.com Holdings Inc."},
        {"symbol": "FRSH", "name": "Freshworks Inc."},
        {"symbol": "ASAN", "name": "Asana Inc."},
        {"symbol": "ESTC", "name": "Elastic N.V."},
        {"symbol": "MDB", "name": "MongoDB Inc."},
        {"symbol": "COUP", "name": "Coupa Software Inc."},
        {"symbol": "RPD", "name": "Rapid7 Inc."},
        {"symbol": "QLYS", "name": "Qualys Inc."},
        {"symbol": "TENB", "name": "Tenable Holdings Inc."},
        {"symbol": "VRNS", "name": "Varonis Systems Inc."},
        {"symbol": "ALRM", "name": "Alarm.com Holdings Inc."},
        {"symbol": "RDWR", "name": "Radware Ltd."},
    ]
    
    # Add more stocks - expand this list or load from CSV
    # For full NASDAQ list, download from:
    # https://www.nasdaq.com/market-activity/stocks/screener
    # Or use: https://old.nasdaq.com/screening/companies-by-name.aspx
    
    return major_stocks


def search_stocks(query: str, stocks: List[Dict[str, str]], limit: int = 20) -> List[Dict[str, str]]:
    """
    Search stocks by symbol or company name.
    
    Args:
        query: Search query (symbol or company name)
        stocks: List of stock dictionaries
        limit: Maximum number of results
    
    Returns:
        Filtered list of matching stocks
    """
    if not query or len(query.strip()) == 0:
        return stocks[:limit]
    
    query_upper = query.upper().strip()
    results = []
    exact_symbol_matches = []
    symbol_start_matches = []
    name_start_matches = []
    other_matches = []
    
    for stock in stocks:
        symbol = stock.get("symbol", "").upper()
        name = stock.get("name", "").upper()
        
        # Prioritize: exact symbol match > symbol starts with > name starts with > contains
        if symbol == query_upper:
            exact_symbol_matches.append(stock)
        elif symbol.startswith(query_upper):
            symbol_start_matches.append(stock)
        elif name.startswith(query_upper):
            name_start_matches.append(stock)
        elif query_upper in symbol or query_upper in name:
            other_matches.append(stock)
    
    # Combine results in priority order
    results = exact_symbol_matches + symbol_start_matches + name_start_matches + other_matches
    
    return results[:limit]


def get_stock_options_for_selectbox(stocks: List[Dict[str, str]]) -> List[str]:
    """
    Format stocks for Streamlit selectbox.
    Returns list of formatted strings like "AAPL - Apple Inc."
    
    Args:
        stocks: List of stock dictionaries
    
    Returns:
        List of formatted strings
    """
    return [f"{s['symbol']} - {s['name']}" for s in stocks]

