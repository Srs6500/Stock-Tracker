"""
Stock Pulse - Real-Time Stock Dashboard
Clean, simplified version using only yfinance.
"""

import streamlit as st
import pandas as pd
from utils import (
    get_stock_data,
    format_currency,
    format_volume,
    calculate_change,
    get_market_status_color,
    format_stock_name
)
from charts import create_candlestick_chart
from watchlist_ui import render_watchlist_panel, get_selected_symbol, set_selected_symbol

# Page configuration
st.set_page_config(
    page_title="StockTracker",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Custom CSS for Clean Dashboard Design
st.markdown("""
<style>
    /* Main background - Clean light gray */
    .stApp {
        background-color: #f5f5f5;
        color: #333333;
        font-family: 'Segoe UI', 'Arial', sans-serif;
    }
    
    /* Clean Dashboard Header */
    .dashboard-header {
        background-color: #ffffff;
        border: 1px solid #e0e0e0;
        border-radius: 8px;
        padding: 1rem;
        margin-bottom: 0.5rem;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
    }
    
    .ticker-info {
        display: flex;
        align-items: center;
        gap: 1.5rem;
        flex-wrap: wrap;
    }
    
    .ticker-symbol {
        font-size: 2rem;
        font-weight: 700;
        color: #333333;
        letter-spacing: 0.5px;
    }
    
    .ticker-price {
        font-size: 2rem;
        font-weight: 600;
        color: #333333;
    }
    
    .ticker-change {
        font-size: 1.1rem;
        font-weight: 600;
        padding: 0.5rem 1rem;
        border-radius: 6px;
    }
    
    .change-positive {
        color: #28a745;
        background-color: #d4edda;
    }
    
    .change-negative {
        color: #dc3545;
        background-color: #f8d7da;
    }
    
    .header-metric {
        display: flex;
        flex-direction: column;
        gap: 0.5rem;
        padding: 0 1rem;
    }
    
    .header-metric-label {
        font-size: 0.85rem;
        color: #666666;
        font-weight: 500;
    }
    
    .header-metric-value {
        font-size: 1.2rem;
        font-weight: 600;
        color: #333333;
    }
    
    /* Clean Dashboard Title */
    .main-title {
        font-size: 2.5rem;
        font-weight: 700;
        color: #333333;
        margin: 0 auto 1.5rem auto;
        padding: 0;
        text-align: center;
        letter-spacing: 1px;
        width: 100%;
        display: block;
    }
    
    /* Status message - subtle */
    .status-message {
        color: #666666;
        font-size: 0.85rem;
        padding: 0.5rem 0;
        text-align: left;
    }
    
    /* Clean Dashboard Panel */
    .dashboard-panel {
        background-color: #ffffff;
        border: 1px solid #e0e0e0;
        border-radius: 10px;
        padding: 1rem;
        margin-bottom: 0.5rem;
        box-shadow: 0 2px 8px rgba(0,0,0,0.08);
        transition: box-shadow 0.3s ease;
    }
    
    .dashboard-panel:hover {
        box-shadow: 0 4px 12px rgba(0,0,0,0.12);
    }
    
    .panel-title {
        font-size: 1.25rem;
        font-weight: 700;
        color: #2c3e50;
        margin-bottom: 0.75rem;
        padding-bottom: 0.25rem;
        letter-spacing: 0.3px;
    }
    
    /* Hide Streamlit default elements */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    /* Hide sidebar */
    section[data-testid="stSidebar"] {
        display: none;
    }
    
    /* Hide Streamlit's default search bar */
    div[data-testid="stToolbar"] { display: none; }
    
    /* Remove any default Streamlit dividers */
    hr { display: none; }
    .stHorizontalBlock hr { display: none; }
</style>
""", unsafe_allow_html=True)


def display_dashboard_header(symbol: str, live_data: dict):
    """Display clean dashboard header with ticker, price, and key metrics."""
    if not live_data:
        return
    
    current_price = live_data.get("current_price")
    prev_close = live_data.get("prev_close")
    today_high = live_data.get("today_high")
    today_low = live_data.get("today_low")
    today_volume = live_data.get("today_volume")
    market_status = live_data.get("market_status", "unknown")
    
    if current_price is None or prev_close is None:
        return
    
    change_amount, change_percent = calculate_change(current_price, prev_close)
    arrow = "▲" if change_amount >= 0 else "▼"
    change_class = "change-positive" if change_amount >= 0 else "change-negative"
    
    header_html = f"""
    <div class="dashboard-header">
        <div style="display: flex; align-items: center; justify-content: space-between; flex-wrap: wrap; gap: 1rem;">
            <div style="display: flex; align-items: center; gap: 1rem; flex-wrap: wrap;">
                <div class="ticker-symbol">{symbol.upper()}</div>
                <div class="ticker-price">{format_currency(current_price)}</div>
                <div class="ticker-change {change_class}">
                    {arrow} {format_currency(abs(change_amount))} ({change_percent:+.2f}%)
                </div>
            </div>
            <div style="display: flex; gap: 1rem; align-items: center; flex-wrap: wrap;">
                <div class="header-metric">
                    <div class="header-metric-label">High</div>
                    <div class="header-metric-value" style="color: #28a745;">{format_currency(today_high) if today_high else "N/A"}</div>
                </div>
                <div class="header-metric">
                    <div class="header-metric-label">Low</div>
                    <div class="header-metric-value" style="color: #dc3545;">{format_currency(today_low) if today_low else "N/A"}</div>
                </div>
                <div class="header-metric">
                    <div class="header-metric-label">Volume</div>
                    <div class="header-metric-value">{format_volume(today_volume) if today_volume else "N/A"}</div>
                </div>
                <div class="header-metric">
                    <div class="header-metric-label">Prev Close</div>
                    <div class="header-metric-value">{format_currency(prev_close)}</div>
                </div>
            </div>
        </div>
    </div>
    """
    st.markdown(header_html, unsafe_allow_html=True)


def main():
    """Main application function with clean dashboard layout."""
    selected_symbol = get_selected_symbol()
    st.markdown(f'<div class="main-title">📊 StockTracker</div>', unsafe_allow_html=True)
    
    # Clean Dashboard Layout
    col_watchlist, col_main = st.columns([1.3, 3.7])
    
    with col_watchlist:
        # Watchlist Panel
        st.markdown('<div class="dashboard-panel">', unsafe_allow_html=True)
        st.markdown('<div class="panel-title">📊 Watchlist</div>', unsafe_allow_html=True)
        selected_symbol = render_watchlist_panel(selected_symbol)
        set_selected_symbol(selected_symbol)
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col_main:
        # Main Chart Area
        try:
            df, live_data, status_msg = get_stock_data(selected_symbol)
            
            # Display clean dashboard header
            if live_data:
                display_dashboard_header(selected_symbol, live_data)
            
            # Display status message
            st.markdown(f'<div class="status-message">{status_msg}</div>', unsafe_allow_html=True)
            
            # Check if we have data
            if df.empty and not live_data:
                st.warning(f"⚠️ No data available for {selected_symbol}.")
                st.info("Please check your internet connection and try again.")
                return
            elif df.empty:
                st.info(f"📊 Loading historical data for {selected_symbol}...")
            elif not live_data:
                st.info(f"📊 Using historical data for {selected_symbol}.")
            
            # Chart Panel
            st.markdown('<div class="dashboard-panel">', unsafe_allow_html=True)
            st.markdown(f'<div class="panel-title">📈 Historical Candlestick Chart - {selected_symbol}</div>', unsafe_allow_html=True)
            
            # Chart
            if not df.empty:
                fig = create_candlestick_chart(df, days=30, symbol=selected_symbol)
                chart_filename = f"{selected_symbol.lower()}_chart"
                st.plotly_chart(
                    fig, 
                    use_container_width=True,
                    config={
                        "displayModeBar": True,
                        "displaylogo": False,
                        "modeBarButtonsToRemove": ["lasso2d", "select2d"],
                        "toImageButtonOptions": {
                            "format": "png",
                            "filename": chart_filename,
                            "height": 600,
                            "width": 1200,
                            "scale": 1
                        }
                    }
                )
            else:
                st.info("📊 Chart data will appear once historical data is loaded.")
            
            st.markdown('</div>', unsafe_allow_html=True)
        
        except Exception as e:
            error_str = str(e)
            st.error(f"❌ Error: {error_str}")
            st.info("Please check your internet connection and try again.")


if __name__ == "__main__":
    main()
