"""
Stock Pulse - Real-Time Stock Dashboard (Bloomberg-lite)
Main Streamlit application entry point.
Supports multi-stock watchlist with TSLA as primary focus.
"""

import streamlit as st
import pandas as pd
from utils import (
    get_historical_and_live,  # Legacy TSLA function (backward compatible)
    get_stock_data,  # New multi-stock function
    format_currency,
    format_volume,
    calculate_change,
    get_market_status_color,
    format_stock_name
)
from charts import create_candlestick_chart
from watchlist_ui import render_watchlist_panel, get_selected_symbol, set_selected_symbol
from news_ui import render_news_feed
from portfolio_ui import render_portfolio_panel

# Page configuration
st.set_page_config(
    page_title="TSLA Pulse",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Custom CSS for dark mode and Tesla-red accents
st.markdown("""
<style>
    /* Main background */
    .stApp {
        background-color: #0e1117;
        color: #ffffff;
    }
    
    /* Title styling */
    .main-title {
        font-size: 3.5rem;
        font-weight: 700;
        text-align: center;
        background: linear-gradient(90deg, #ff0000, #ff4444);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        margin-bottom: 0.5rem;
        text-shadow: 0 0 20px rgba(255, 0, 0, 0.3);
    }
    
    /* Price display */
    .price-display {
        font-size: 4rem;
        font-weight: 700;
        text-align: center;
        color: #ffffff;
        margin: 1rem 0;
        text-shadow: 0 0 10px rgba(255, 255, 255, 0.2);
    }
    
    /* Change indicator */
    .change-positive {
        color: #00ff00;
        font-size: 1.5rem;
        font-weight: 600;
    }
    
    .change-negative {
        color: #ff0000;
        font-size: 1.5rem;
        font-weight: 600;
    }
    
    /* Metric boxes */
    .metric-box {
        background-color: #1e1e1e;
        padding: 1rem;
        border-radius: 10px;
        border: 1px solid #333333;
        text-align: center;
    }
    
    .metric-label {
        color: #888888;
        font-size: 0.9rem;
        margin-bottom: 0.5rem;
    }
    
    .metric-value {
        color: #ffffff;
        font-size: 1.5rem;
        font-weight: 600;
    }
    
    /* Market status badge */
    .market-badge {
        display: inline-block;
        padding: 0.5rem 1rem;
        border-radius: 20px;
        font-weight: 600;
        font-size: 0.9rem;
        margin: 0.5rem 0;
    }
    
    /* Status message */
    .status-message {
        text-align: center;
        color: #888888;
        font-size: 0.9rem;
        margin: 0.5rem 0;
    }
    
    /* Hide Streamlit default elements */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    /* Hide sidebar */
    section[data-testid="stSidebar"] {
        display: none;
    }
    
    /* Settings expander styling */
    .streamlit-expanderHeader {
        background-color: #1e1e1e;
        border: 1px solid #333333;
        border-radius: 8px;
        padding: 0.5rem;
    }
    
    .streamlit-expanderContent {
        background-color: #1e1e1e;
        border: 1px solid #333333;
        border-radius: 8px;
        padding: 1rem;
        margin-top: 0.5rem;
    }
</style>
""", unsafe_allow_html=True)


def display_price_and_change(current_price: float, prev_close: float):
    """Display the main price with change indicator."""
    if current_price is None or prev_close is None:
        st.markdown('<div class="price-display">N/A</div>', unsafe_allow_html=True)
        return
    
    change_amount, change_percent = calculate_change(current_price, prev_close)
    arrow = "↑" if change_amount >= 0 else "↓"
    color_class = "change-positive" if change_amount >= 0 else "change-negative"
    
    st.markdown(f'<div class="price-display">{format_currency(current_price)}</div>', unsafe_allow_html=True)
    st.markdown(
        f'<div class="{color_class}" style="text-align: center;">'
        f'{arrow} {format_currency(abs(change_amount))} ({change_percent:+.2f}%)'
        f'</div>',
        unsafe_allow_html=True
    )


def display_metrics(live_data: dict):
    """Display metric boxes for High, Low, Prev Close, Volume."""
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown(
            f'<div class="metric-box">'
            f'<div class="metric-label">Today\'s High</div>'
            f'<div class="metric-value">{format_currency(live_data.get("today_high"))}</div>'
            f'</div>',
            unsafe_allow_html=True
        )
    
    with col2:
        st.markdown(
            f'<div class="metric-box">'
            f'<div class="metric-label">Today\'s Low</div>'
            f'<div class="metric-value">{format_currency(live_data.get("today_low"))}</div>'
            f'</div>',
            unsafe_allow_html=True
        )
    
    with col3:
        st.markdown(
            f'<div class="metric-box">'
            f'<div class="metric-label">Prev Close</div>'
            f'<div class="metric-value">{format_currency(live_data.get("prev_close"))}</div>'
            f'</div>',
            unsafe_allow_html=True
        )
    
    with col4:
        st.markdown(
            f'<div class="metric-box">'
            f'<div class="metric-label">Volume</div>'
            f'<div class="metric-value">{format_volume(live_data.get("today_volume"))}</div>'
            f'</div>',
            unsafe_allow_html=True
        )


def display_market_status(status: str):
    """Display market status badge."""
    status_lower = status.lower()
    
    if "open" in status_lower:
        status_text = "Market: ● Open"
        color = "#00ff00"
    elif "closed" in status_lower or "close" in status_lower:
        status_text = "Market: ● Closed"
        color = "#ff0000"
    elif "after" in status_lower or "extended" in status_lower:
        status_text = "Market: ● After Hours"
        color = "#ff8800"
    else:
        status_text = "Market: ● Unknown"
        color = "#888888"
    
    st.markdown(
        f'<div style="text-align: center;">'
        f'<span class="market-badge" style="background-color: {color}20; color: {color}; border: 1px solid {color};">'
        f'{status_text}'
        f'</span>'
        f'</div>',
        unsafe_allow_html=True
    )


def main():
    """Main application function with Bloomberg-lite multi-panel layout."""
    # Title - Update to reflect multi-stock support
    selected_symbol = get_selected_symbol()
    title_symbol = format_stock_name(selected_symbol) if selected_symbol != "TSLA" else "TSLA"
    st.markdown(f'<h1 class="main-title">⚡ {title_symbol} Pulse</h1>', unsafe_allow_html=True)
    
    # Settings - Integrated into main UI (top right)
    col_left, col_right = st.columns([4, 1])
    with col_right:
        with st.expander("⚙️", expanded=False):
            auto_refresh = st.checkbox("Auto-refresh (15s)", value=True, key="auto_refresh")
            if auto_refresh:
                st.rerun_interval = 15  # Refresh every 15 seconds
            st.caption("Updates every 15 seconds")
    
    # Bloomberg-lite Multi-Panel Layout
    # Left: Watchlist + Portfolio | Right: Main Chart + News
    col_watchlist, col_main = st.columns([1, 3])
    
    with col_watchlist:
        # Watchlist Panel
        selected_symbol = render_watchlist_panel(selected_symbol)
        set_selected_symbol(selected_symbol)
        
        # Portfolio Panel (tabbed or expandable)
        st.markdown("<br>")
        with st.expander("💼 Portfolio", expanded=False):
            render_portfolio_panel()
        
        # News Feed (compact in watchlist column)
        st.markdown("<br>")
        render_news_feed(selected_symbol, limit=3)
    
    with col_main:
        # Main Chart Area
        try:
            # Use new multi-stock function (works for any symbol, defaults to TSLA)
            df, live_data, status_msg = get_stock_data(selected_symbol)
            
            # Display status message
            st.markdown(f'<div class="status-message">{status_msg}</div>', unsafe_allow_html=True)
            
            # Check if we have data
            if df.empty or not live_data:
                st.warning(f"⚠️ No data available for {selected_symbol}. Please check your API key configuration.")
                return
            
            # Display price and change
            current_price = live_data.get("current_price")
            prev_close = live_data.get("prev_close")
            display_price_and_change(current_price, prev_close)
            
            # Display market status
            market_status = live_data.get("market_status", "unknown")
            display_market_status(market_status)
            
            # Spacer
            st.markdown("<br>", unsafe_allow_html=True)
            
            # Display metrics
            display_metrics(live_data)
            
            # Spacer
            st.markdown("<br><br>", unsafe_allow_html=True)
            
            # Chart with technical indicators
            if not df.empty:
                # Get technical indicators if available
                from data_processor import StockDataProcessor
                processor = StockDataProcessor()
                indicators = processor.get_technical_indicators_data(selected_symbol, ['RSI', 'MACD'])
                
                fig = create_candlestick_chart(df, days=30, symbol=selected_symbol, indicators=indicators)
                chart_filename = f"{selected_symbol.lower()}_chart"
                st.plotly_chart(
                    fig, 
                    use_container_width=True,
                    config={
                        "displayModeBar": True,
                        "displaylogo": False,
                        "modeBarButtonsToRemove": ["lasso2d", "select2d"],
                        "modeBarButtonsToAdd": ["resetScale2d"],
                        "toImageButtonOptions": {
                            "format": "png",
                            "filename": chart_filename,
                            "height": 600,
                            "width": 1200,
                            "scale": 1
                        },
                        "doubleClick": "reset",
                        "doubleClickDelay": 300,
                        "showTips": True,
                        "responsive": True,
                        "editable": False
                    }
                )
            else:
                st.info("📊 Chart data will appear once historical data is loaded.")
        
        except KeyError as e:
            st.error(f"🔑 Configuration Error: {str(e)}")
            st.info("""
            **Setup Instructions:**
            1. Create a `.streamlit` folder in your project directory
            2. Create `secrets.toml` inside `.streamlit`
            3. Add your Polygon API key:
               ```
               POLYGON_API_KEY = "your_api_key_here"
               ```
            4. Get your free API key at: https://polygon.io/
            """)
        
        except Exception as e:
            st.error(f"❌ Error: {str(e)}")
            st.info("The app encountered an error. Please check your API key and internet connection.")


if __name__ == "__main__":
    main()

