"""
News Feed UI Components for Streamlit
Displays stock-related news articles in a Bloomberg-style feed.
"""

import streamlit as st
from datetime import datetime
from data_processor import StockDataProcessor
from typing import List, Dict, Any


def render_news_feed(symbol: str, limit: int = 5):
    """
    Render news feed for a stock symbol.
    
    Args:
        symbol: Stock ticker symbol
        limit: Maximum number of articles to display
    """
    processor = StockDataProcessor()
    
    try:
        news_articles = processor.get_news_data(symbol, limit=limit)
        
        if not news_articles:
            st.info(f"📰 No news available for {symbol}. NewsAPI key may not be configured.")
            return
        
        st.markdown("### 📰 News Feed")
        
        for i, article in enumerate(news_articles):
            title = article.get("title", "No title")
            description = article.get("description", "")
            url = article.get("url", "")
            published_at = article.get("publishedAt", "")
            source = article.get("source", "")
            
            # Format date
            try:
                if published_at:
                    pub_date = datetime.fromisoformat(published_at.replace('Z', '+00:00'))
                    date_str = pub_date.strftime("%b %d, %Y %H:%M")
                else:
                    date_str = "Recent"
            except:
                date_str = "Recent"
            
            # News card
            with st.container():
                st.markdown(
                    f"""
                    <div style="
                        background-color: #1e1e1e;
                        border: 1px solid #333333;
                        border-radius: 8px;
                        padding: 1rem;
                        margin-bottom: 0.75rem;
                    ">
                        <div style="display: flex; justify-content: space-between; margin-bottom: 0.5rem;">
                            <span style="color: #888888; font-size: 0.85rem;">{source}</span>
                            <span style="color: #888888; font-size: 0.85rem;">{date_str}</span>
                        </div>
                        <h4 style="color: #ffffff; margin: 0.5rem 0;">
                            {title}
                        </h4>
                        <p style="color: #aaaaaa; font-size: 0.9rem; margin: 0.5rem 0;">
                            {description[:200]}{'...' if len(description) > 200 else ''}
                        </p>
                    </div>
                    """,
                    unsafe_allow_html=True
                )
                
                # Link button
                if url:
                    st.markdown(f"[Read more →]({url})")
                
                if i < len(news_articles) - 1:
                    st.markdown("---")
        
    except Exception as e:
        st.warning(f"Could not load news for {symbol}: {str(e)}")


def render_news_summary(symbol: str):
    """
    Render a compact news summary (just headlines).
    
    Args:
        symbol: Stock ticker symbol
    """
    processor = StockDataProcessor()
    
    try:
        news_articles = processor.get_news_data(symbol, limit=3)
        
        if not news_articles:
            return
        
        st.markdown("**Latest News**")
        for article in news_articles[:3]:
            title = article.get("title", "")
            url = article.get("url", "")
            
            if url:
                st.markdown(f"• [{title[:60]}{'...' if len(title) > 60 else ''}]({url})")
            else:
                st.markdown(f"• {title[:60]}{'...' if len(title) > 60 else ''}")
        
    except Exception as e:
        pass  # Silently fail for summary

