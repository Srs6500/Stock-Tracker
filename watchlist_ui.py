"""
Watchlist UI Components for Streamlit
Simplified version using yfinance.
"""

import streamlit as st
from database import (
    get_session,
    add_to_watchlist,
    remove_from_watchlist,
    get_watchlist,
    is_in_watchlist
)
from utils import get_default_watchlist, format_stock_name, get_watchlist_stocks_data
from stock_list import load_nasdaq_stocks, search_stocks


def render_watchlist_panel(selected_symbol: str = "TSLA"):
    """
    Render the watchlist panel with stock cards.
    Shows live prices and allows selection.
    
    Args:
        selected_symbol: Currently selected stock symbol
    
    Returns:
        Selected symbol (if user clicked a stock)
    """
    session = get_session()
    
    try:
        # Get watchlist from database
        watchlist_items = get_watchlist(session)
        watchlist_symbols = [item.symbol for item in watchlist_items]
        
        # If watchlist is empty, initialize with default stocks
        if not watchlist_symbols:
            default_symbols = get_default_watchlist()
            for symbol in default_symbols:
                add_to_watchlist(session, symbol)
            watchlist_symbols = default_symbols
            session.commit()
        
        # Get live data for all watchlist stocks
        live_data = {}
        try:
            live_data = get_watchlist_stocks_data(watchlist_symbols)
        except Exception as e:
            # If API fails, show placeholder data
            pass
        
        # Add stock input with autocomplete
        st.markdown("**Add Stock to Watchlist**")
        
        # Load all NASDAQ stocks
        all_stocks = load_nasdaq_stocks()
        
        # Search input
        search_query = st.text_input(
            "🔍 Search stocks",
            placeholder="Start typing...",
            key="stock_search_input",
            label_visibility="visible"
        )
        
        # Show suggestions as you type (like Google) - appears when you type
        if search_query and len(search_query.strip()) > 0:
            filtered_stocks = search_stocks(search_query.strip(), all_stocks, limit=10)
            
            if filtered_stocks:
                # Simple clickable suggestions (Google-like)
                for stock in filtered_stocks:
                    symbol = stock['symbol']
                    name = stock['name']
                    already_added = is_in_watchlist(session, symbol)
                    
                    if already_added:
                        st.markdown(f"**{symbol}** - {name} ✓ Added")
                    else:
                        if st.button(f"**{symbol}** - {name}", key=f"add_{symbol}", use_container_width=True):
                            add_to_watchlist(session, symbol)
                            st.rerun()
            else:
                st.info("No stocks found")
        
        st.markdown('<div style="margin: 0.75rem 0;"></div>', unsafe_allow_html=True)
        
        # Display watchlist stocks
        for symbol in watchlist_symbols:
            if not symbol or not isinstance(symbol, str):
                continue
                
            stock_data = live_data.get(symbol, {})
            current_price = stock_data.get("current_price")
            prev_close = stock_data.get("prev_close")
            
            # Calculate change
            change_amount = 0.0
            change_percent = 0.0
            if current_price and prev_close:
                change_amount = current_price - prev_close
                change_percent = (change_amount / prev_close) * 100
            
            # Determine if selected
            is_selected = (symbol == selected_symbol)
            border_color = "#007bff" if is_selected else "#e0e0e0"
            bg_color = "#f0f8ff" if is_selected else "#ffffff"
            
            # Format stock name
            formatted_name = format_stock_name(symbol) if symbol else symbol.upper()
            
            # Format price and change
            price_display = f"${current_price:,.2f}" if current_price else "N/A"
            change_display = "N/A"
            change_color = "#888888"
            if current_price and prev_close:
                change_sign = "+" if change_amount >= 0 else ""
                change_display = f"{change_sign}{change_percent:.2f}%"
                change_color = "#28a745" if change_amount >= 0 else "#dc3545"
            
            # Stock card
            with st.container():
                st.markdown(
                    f"""
                    <div style="
                        background-color: {bg_color};
                        border: 2px solid {border_color};
                        border-radius: 6px;
                        padding: 0.75rem;
                        margin-bottom: 0.75rem;
                    ">
                        <div style="display: flex; justify-content: space-between; align-items: center;">
                            <div>
                                <strong style="font-size: 1rem; color: #333333;">{symbol}</strong>
                            </div>
                            <div style="text-align: right;">
                                <div style="font-size: 1rem; font-weight: 600; color: #333333;">
                                    {price_display}
                                </div>
                                <div style="color: {change_color}; font-size: 0.8rem; font-weight: 500;">
                                    {change_display}
                                </div>
                            </div>
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True
                )
                
                # Action buttons
                col1, col2 = st.columns([3, 1])
                with col1:
                    if st.button(f"📈 View", key=f"view_{symbol}", use_container_width=True):
                        st.session_state.selected_symbol = symbol
                        st.rerun()
                with col2:
                    if st.button("🗑️", key=f"remove_{symbol}"):
                        remove_from_watchlist(session, symbol)
                        st.rerun()
        
        return st.session_state.get("selected_symbol", selected_symbol)
        
    except Exception as e:
        st.error(f"Error loading watchlist: {str(e)}")
        return selected_symbol
    finally:
        session.close()


def get_selected_symbol() -> str:
    """
    Get the currently selected stock symbol from session state.
    Defaults to TSLA if not set.
    
    Returns:
        Selected stock symbol
    """
    if "selected_symbol" not in st.session_state:
        st.session_state.selected_symbol = "TSLA"
    return st.session_state.selected_symbol


def set_selected_symbol(symbol: str):
    """Set the selected stock symbol in session state."""
    st.session_state.selected_symbol = symbol.upper()
