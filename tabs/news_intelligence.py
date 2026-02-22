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
        
        st.info("ℹ️ **News Sources:** Searches news for (1) The ETF itself, (2) Underlying stocks, and (3) Connected markets. This provides comprehensive market intelligence.")
        
        col1, col2 = st.columns([3, 1])
        
        with col1:
            selected_etf = st.selectbox("Select ETF for Deep Analysis", ["ALL"] + ETF_LIST)
        
        with col2:
            if st.button("🔄 Refresh News", type="primary", use_container_width=True):
                with st.spinner("Fetching latest news..."):
                    st.session_state.news_cache = fetch_real_news_sentiment()
                    st.success("News updated!")
        
        if not st.session_state.news_cache.get("articles"):
            with st.spinner("Loading news..."):
                st.session_state.news_cache = fetch_real_news_sentiment()
        
        news_data = st.session_state.news_cache
        
        st.markdown("### Market Sentiment Overview")
        
        col1, col2, col3, col4 = st.columns(4)
        
        sentiment_counts = {"POSITIVE": 0, "NEUTRAL": 0, "NEGATIVE": 0}
        for article in news_data["articles"]:
            sentiment_counts[article["sentiment"]] += 1
        
        total_articles = len(news_data["articles"])
        
        with col1:
            pct = (sentiment_counts["POSITIVE"] / total_articles * 100) if total_articles > 0 else 0
            st.metric("🟢 Positive", f"{pct:.0f}%", delta=f"{sentiment_counts['POSITIVE']} articles")
        
        with col2:
            pct = (sentiment_counts["NEUTRAL"] / total_articles * 100) if total_articles > 0 else 0
            st.metric("🟡 Neutral", f"{pct:.0f}%", delta=f"{sentiment_counts['NEUTRAL']} articles")
        
        with col3:
            pct = (sentiment_counts["NEGATIVE"] / total_articles * 100) if total_articles > 0 else 0
            st.metric("🔴 Negative", f"{pct:.0f}%", delta=f"{sentiment_counts['NEGATIVE']} articles")
        
        with col4:
            overall = news_data["overall_sentiment"]
            overall_pct = (overall + 1) / 2 * 100
            st.metric("Overall Score", f"{overall_pct:.0f}/100")
        
        st.divider()
        
        st.markdown("### Latest News & Analysis")
        
        articles_to_show = news_data["articles"]
        if selected_etf != "ALL":
            articles_to_show = [a for a in articles_to_show if selected_etf in a["ticker"]]
        
        for article in articles_to_show:
            st.markdown(f"""
            <div class="news-card">
                <div style="display: flex; justify-content: space-between; align-items: start; margin-bottom: 0.75rem;">
                    <div style="flex: 1;">
                        <div style="font-size: 1.1rem; font-weight: 700; margin-bottom: 0.25rem;">{article['title']}</div>
                        <div style="font-size: 0.85rem; color: #64748b;">{article['source']} • {article['time']}</div>
                    </div>
                    <div style="display: flex; gap: 0.5rem; align-items: center;">
                        <span class="{article['sentiment_class']}">{article['sentiment']}</span>
                        <span style="background: #334155; padding: 0.5rem; border-radius: 0.5rem; font-weight: 700;">{article['ticker']}</span>
                    </div>
                </div>
                <div style="color: #94a3b8; line-height: 1.6;">{article['summary']}</div>
            </div>
            """, unsafe_allow_html=True)
        
        st.divider()
        
        st.markdown("### Underlying Holdings Monitor")
        
        selected_for_underlying = st.selectbox(
            "Select ETF to view underlying stocks",
            ETF_LIST,
            key="underlying_select"
        )
        
        underlying_stocks = ETF_INFO[selected_for_underlying]["top_holdings"]
        
        st.info(f"**{selected_for_underlying}** tracks: {ETF_INFO[selected_for_underlying]['underlying_index']}")
        st.write(f"**Top Holdings:** {', '.join(underlying_stocks)}")
