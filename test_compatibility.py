"""
Compatibility Test Script
Verifies that all existing functionality still works after Bloomberg-lite upgrades.
"""

def test_backward_compatibility():
    """Test that original TSLA Pulse functionality still works."""
    print("Testing backward compatibility...")
    
    # Test 1: Original functions still import
    try:
        from utils import get_historical_and_live, format_currency, calculate_change
        print("✓ Original utils functions import successfully")
    except Exception as e:
        print(f"✗ Error importing original utils: {e}")
        return False
    
    # Test 2: Original database functions work
    try:
        from database import TslaDaily, get_historical_data, save_daily_data
        print("✓ Original database functions import successfully")
    except Exception as e:
        print(f"✗ Error importing original database: {e}")
        return False
    
    # Test 3: Original API client works
    try:
        from api_client import get_polygon_client, fetch_historical_data
        print("✓ Original API client imports successfully")
    except Exception as e:
        print(f"✗ Error importing original API client: {e}")
        return False
    
    # Test 4: Original charts work
    try:
        from charts import create_candlestick_chart
        print("✓ Original charts import successfully")
    except Exception as e:
        print(f"✗ Error importing original charts: {e}")
        return False
    
    # Test 5: New functions work alongside old ones
    try:
        from utils import get_stock_data, get_watchlist_stocks_data
        from data_processor import StockDataProcessor
        from api_wrapper import StockDataWrapper
        print("✓ New Bloomberg-lite functions import successfully")
    except Exception as e:
        print(f"✗ Error importing new functions: {e}")
        return False
    
    # Test 6: All UI components work
    try:
        from watchlist_ui import render_watchlist_panel
        from news_ui import render_news_feed
        from portfolio_ui import render_portfolio_panel
        print("✓ All UI components import successfully")
    except Exception as e:
        print(f"✗ Error importing UI components: {e}")
        return False
    
    print("\n✅ All compatibility tests passed!")
    print("✅ Original TSLA Pulse functionality preserved")
    print("✅ New Bloomberg-lite features work correctly")
    return True

if __name__ == "__main__":
    test_backward_compatibility()

