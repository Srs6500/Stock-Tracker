"""
Watchlist UI Components for Streamlit
Provides watchlist management interface with add/remove functionality.
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
        live_data = get_watchlist_stocks_data(watchlist_symbols)
        
        # Display watchlist header
        st.markdown("### 📊 Watchlist")
        
        # Add stock input
        col1, col2 = st.columns([3, 1])
        with col1:
            new_symbol = st.text_input(
                "Add Stock",
                placeholder="e.g., AAPL, MSFT",
                key="add_stock_input",
                label_visibility="collapsed"
            )
        with col2:
            if st.button("➕", key="add_stock_btn", help="Add stock to watchlist"):
                if new_symbol and len(new_symbol.strip()) > 0:
                    symbol_upper = new_symbol.strip().upper()
                    if not is_in_watchlist(session, symbol_upper):
                        add_to_watchlist(session, symbol_upper)
                        st.rerun()
                    else:
                        st.warning(f"{symbol_upper} is already in watchlist")
        
        st.markdown("---")
        
        # Display watchlist stocks
        for symbol in watchlist_symbols:
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
            border_color = "#ff0000" if is_selected else "#333333"
            bg_color = "#1e2e1e" if is_selected else "#1e1e1e"
            
            # Stock card
            with st.container():
                st.markdown(
                    f"""
                    <div style="
                        background-color: {bg_color};
                        border: 2px solid {border_color};
                        border-radius: 8px;
                        padding: 0.75rem;
                        margin-bottom: 0.5rem;
                        cursor: pointer;
                    ">
                        <div style="display: flex; justify-content: space-between; align-items: center;">
                            <div>
                                <strong style="font-size: 1.1rem;">{format_stock_name(symbol)}</strong>
                                <br>
                                <span style="color: #888888; font-size: 0.9rem;">{symbol}</span>
                            </div>
                            <div style="text-align: right;">
                                <div style="font-size: 1.1rem; font-weight: 600;">
                                    ${current_price:,.2f if current_price else 'N/A'}
                                </div>
                                <div style="color: {'#00ff00' if change_amount >= 0 else '#ff0000'}; font-size: 0.85rem;">
                                    {('+' if change_amount >= 0 else '') + f'{change_percent:.2f}%' if current_price and prev_close else 'N/A'}
                                </div>
                            </div>
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True
                )
                
                # Click handler - use button for selection
                col1, col2 = st.columns([4, 1])
                with col1:
                    if st.button(f"View {symbol}", key=f"view_{symbol}", use_container_width=True):
                        st.session_state.selected_symbol = symbol
                        st.rerun()
                with col2:
                    if st.button("❌", key=f"remove_{symbol}", help=f"Remove {symbol}"):
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

