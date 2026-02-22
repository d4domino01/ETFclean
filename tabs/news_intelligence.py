"""
TAB 5: NEWS & INTELLIGENCE
Real-time news and market intelligence
"""

import streamlit as st
from utils.helpers import fetch_real_news_sentiment, ETF_LIST, ETF_INFO


def render():
    """Render the News & Intelligence tab"""
    if not st.session_state.PORTFOLIO_LOCKED:
        st.warning("⚠️ Fix validation errors to view news intelligence")
    else:
        st.subheader("📰 Real-Time News & Market Intelligence")
        
        st.info("ℹ️ **News Sources:** Searches news for ETFs and underlying stocks. When live news is unavailable, shows market data & price trends.")
        
        col1, col2, col3 = st.columns([2, 1, 1])
        
        with col1:
            selected_etf = st.selectbox("Select ETF for Deep Analysis", ["ALL"] + ETF_LIST)
        
        with col2:
            sort_by = st.selectbox("Sort by", ["Latest", "Sentiment"])
        
        with col3:
            if st.button("🔄 Refresh News", type="primary", use_container_width=True):
                with st.spinner("Fetching latest news..."):
                    st.session_state.news_cache = fetch_real_news_sentiment()
                    st.success("✅ News updated!")
        
        if not st.session_state.news_cache.get("articles"):
            with st.spinner("Loading news for your portfolio..."):
                st.session_state.news_cache = fetch_real_news_sentiment()
        
        news_data = st.session_state.news_cache
        articles = news_data.get("articles", [])
        
        if not articles:
            st.warning("No news data available. Please try refreshing.")
            articles = []
        
        st.markdown("### 📊 Market Sentiment Overview")
        
        col1, col2, col3, col4 = st.columns(4)
        
        sentiment_counts = {"POSITIVE": 0, "NEUTRAL": 0, "NEGATIVE": 0}
        for article in articles:
            sentiment = article.get("sentiment", "NEUTRAL")
            sentiment_counts[sentiment] += 1
        
        total_articles = len(articles)
        
        with col1:
            pct = (sentiment_counts["POSITIVE"] / total_articles * 100) if total_articles > 0 else 0
            st.metric("🟢 Positive", f"{pct:.0f}%", delta=f"{sentiment_counts['POSITIVE']}")
        
        with col2:
            pct = (sentiment_counts["NEUTRAL"] / total_articles * 100) if total_articles > 0 else 0
            st.metric("🟡 Neutral", f"{pct:.0f}%", delta=f"{sentiment_counts['NEUTRAL']}")
        
        with col3:
            pct = (sentiment_counts["NEGATIVE"] / total_articles * 100) if total_articles > 0 else 0
            st.metric("🔴 Negative", f"{pct:.0f}%", delta=f"{sentiment_counts['NEGATIVE']}")
        
        with col4:
            overall = news_data.get("overall_sentiment", 0)
            overall_pct = (overall + 1) / 2 * 100
            st.metric("Overall Score", f"{overall_pct:.0f}/100")
        
        st.divider()
        
        st.markdown("### 📰 Latest News & Analysis")
        
        articles_to_show = articles
        if selected_etf != "ALL":
            articles_to_show = [a for a in articles_to_show if selected_etf in a.get("ticker", "")]
        
        if sort_by == "Sentiment":
            articles_to_show = sorted(articles_to_show, 
                                     key=lambda x: x.get("sentiment_score", 0), 
                                     reverse=True)
        
        if not articles_to_show:
            st.info(f"No news found for {selected_etf}. Try selecting 'ALL' to see all news.")
        else:
            for idx, article in enumerate(articles_to_show):
                sentiment = article.get("sentiment", "NEUTRAL")
                sentiment_emoji = "🟢" if sentiment == "POSITIVE" else "🔴" if sentiment == "NEGATIVE" else "🟡"
                
                with st.container(border=True):
                    col1, col2 = st.columns([0.9, 0.1])
                    
                    with col1:
                        st.markdown(f"**{sentiment_emoji} {article.get('title', 'Untitled')}**")
                        st.caption(f"{article.get('source', 'News')} • {article.get('time', 'Recent')} • {article.get('ticker', 'ETF')}")
                        st.write(article.get('summary', 'No summary available'))
                    
                    with col2:
                        st.metric("Sentiment", sentiment)
        
        st.divider()
        
        st.markdown("### 📌 Underlying Holdings Monitor")
        
        selected_for_underlying = st.selectbox(
            "Select ETF to view underlying stocks",
            ETF_LIST,
            key="underlying_select"
        )
        
        underlying_stocks = ETF_INFO[selected_for_underlying]["top_holdings"]
        
        st.info(f"**{selected_for_underlying}** tracks: {ETF_INFO[selected_for_underlying]['underlying_index']}")
        st.write(f"**Top Holdings:** {', '.join(underlying_stocks)}")
