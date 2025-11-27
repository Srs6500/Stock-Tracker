"""
Portfolio Tracker UI Components for Streamlit
Manages stock portfolio with holdings, P&L calculations, and performance metrics.
"""

import streamlit as st
from database import (
    get_session,
    add_to_portfolio,
    remove_from_portfolio,
    get_portfolio,
    update_portfolio_quantity
)
from utils import format_currency, calculate_change, get_watchlist_stocks_data


def render_portfolio_panel():
    """
    Render portfolio management panel with holdings and P&L.
    
    Returns:
        None (updates session state)
    """
    session = get_session()
    
    try:
        portfolio_items = get_portfolio(session)
        
        st.markdown("### 💼 Portfolio")
        
        if not portfolio_items:
            st.info("No stocks in portfolio. Add stocks below.")
            
            # Add stock form
            with st.form("add_to_portfolio", clear_on_submit=True):
                col1, col2, col3 = st.columns(3)
                with col1:
                    symbol = st.text_input("Symbol", placeholder="AAPL", key="portfolio_symbol")
                with col2:
                    quantity = st.number_input("Quantity", min_value=0.0, value=0.0, step=0.01, key="portfolio_quantity")
                with col3:
                    purchase_price = st.number_input("Purchase Price", min_value=0.0, value=0.0, step=0.01, key="portfolio_price")
                
                if st.form_submit_button("➕ Add to Portfolio"):
                    if symbol and quantity > 0 and purchase_price > 0:
                        add_to_portfolio(session, symbol.upper(), quantity, purchase_price)
                        st.rerun()
                    else:
                        st.warning("Please fill all fields with valid values")
        else:
            # Get current prices for all portfolio stocks
            symbols = [item.symbol for item in portfolio_items]
            current_prices = get_watchlist_stocks_data(symbols)
            
            # Calculate portfolio metrics
            total_cost = 0.0
            total_value = 0.0
            holdings_data = []
            
            for item in portfolio_items:
                symbol = item.symbol
                quantity = item.quantity
                purchase_price = item.purchase_price
                current_price_data = current_prices.get(symbol, {})
                current_price = current_prices.get(symbol, {}).get("current_price", 0.0)
                
                cost = quantity * purchase_price
                value = quantity * current_price if current_price else 0.0
                pnl = value - cost
                pnl_percent = (pnl / cost * 100) if cost > 0 else 0.0
                
                total_cost += cost
                total_value += value
                
                holdings_data.append({
                    "symbol": symbol,
                    "quantity": quantity,
                    "purchase_price": purchase_price,
                    "current_price": current_price,
                    "cost": cost,
                    "value": value,
                    "pnl": pnl,
                    "pnl_percent": pnl_percent
                })
            
            # Portfolio summary
            portfolio_pnl = total_value - total_cost
            portfolio_pnl_percent = (portfolio_pnl / total_cost * 100) if total_cost > 0 else 0.0
            
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("Total Cost", format_currency(total_cost))
            with col2:
                st.metric("Current Value", format_currency(total_value))
            with col3:
                st.metric(
                    "Total P&L", 
                    format_currency(portfolio_pnl),
                    f"{portfolio_pnl_percent:+.2f}%"
                )
            with col4:
                st.metric(
                    "Return %",
                    f"{portfolio_pnl_percent:+.2f}%",
                    delta=None
                )
            
            st.markdown("---")
            
            # Holdings table
            st.markdown("**Holdings**")
            for holding in holdings_data:
                pnl_color = "#00ff00" if holding["pnl"] >= 0 else "#ff0000"
                
                with st.container():
                    col1, col2, col3, col4, col5, col6 = st.columns(6)
                    with col1:
                        st.write(f"**{holding['symbol']}**")
                    with col2:
                        st.write(f"{holding['quantity']:.2f} shares")
                    with col3:
                        st.write(format_currency(holding['purchase_price']))
                    with col4:
                        st.write(format_currency(holding['current_price']) if holding['current_price'] else "N/A")
                    with col5:
                        st.write(format_currency(holding['value']))
                    with col6:
                        st.markdown(
                            f"<span style='color: {pnl_color}; font-weight: 600;'>"
                            f"{format_currency(holding['pnl'])} ({holding['pnl_percent']:+.2f}%)"
                            f"</span>",
                            unsafe_allow_html=True
                        )
                    
                    # Edit/Remove buttons
                    col_edit, col_remove = st.columns([1, 1])
                    with col_edit:
                        if st.button("✏️ Edit", key=f"edit_{holding['symbol']}"):
                            st.session_state[f"editing_{holding['symbol']}"] = True
                    with col_remove:
                        if st.button("🗑️ Remove", key=f"remove_{holding['symbol']}"):
                            remove_from_portfolio(session, holding['symbol'])
                            st.rerun()
                    
                    # Edit form
                    if st.session_state.get(f"editing_{holding['symbol']}", False):
                        with st.form(f"edit_{holding['symbol']}"):
                            new_quantity = st.number_input(
                                "Quantity", 
                                value=float(holding['quantity']), 
                                min_value=0.0,
                                key=f"edit_qty_{holding['symbol']}"
                            )
                            if st.form_submit_button("Save"):
                                update_portfolio_quantity(session, holding['symbol'], new_quantity)
                                st.session_state[f"editing_{holding['symbol']}"] = False
                                st.rerun()
                    
                    st.markdown("---")
            
            # Add new stock form
            with st.expander("➕ Add Stock to Portfolio", expanded=False):
                with st.form("add_to_portfolio", clear_on_submit=True):
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        new_symbol = st.text_input("Symbol", placeholder="AAPL", key="new_portfolio_symbol")
                    with col2:
                        new_quantity = st.number_input("Quantity", min_value=0.0, value=0.0, step=0.01, key="new_portfolio_quantity")
                    with col3:
                        new_price = st.number_input("Purchase Price", min_value=0.0, value=0.0, step=0.01, key="new_portfolio_price")
                    
                    if st.form_submit_button("Add"):
                        if new_symbol and new_quantity > 0 and new_price > 0:
                            add_to_portfolio(session, new_symbol.upper(), new_quantity, new_price)
                            st.rerun()
                        else:
                            st.warning("Please fill all fields with valid values")
        
    except Exception as e:
        st.error(f"Error loading portfolio: {str(e)}")
    finally:
        session.close()

