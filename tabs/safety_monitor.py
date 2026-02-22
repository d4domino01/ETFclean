"""
TAB 4: SAFETY MONITOR
Comprehensive safety analysis and alerts
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime
from utils.helpers import (
    analyze_dividend_trends,
    check_price_alerts,
    trigger_alerts_if_needed
)


def render():
    """Render the Safety Monitor tab"""
    if not st.session_state.PORTFOLIO_LOCKED:
        st.warning("⚠️ Fix validation errors to view safety monitor")
    else:
        st.subheader("🛡️ Comprehensive Safety Analysis")
        
        col1, col2 = st.columns([1, 3])
        
        with col1:
            if st.button("🔍 Run Full Safety Check", type="primary", use_container_width=True):
                with st.spinner("Analyzing portfolio safety..."):
                    st.session_state.last_safety_check = datetime.now()
                    
                    if st.session_state.alert_settings.get("enable_email") or st.session_state.alert_settings.get("enable_sms"):
                        alerts_sent = trigger_alerts_if_needed()
                        if alerts_sent:
                            st.success(f"✅ Sent {len(alerts_sent)} alerts")
                            for alert in alerts_sent:
                                st.info(alert)
        
        with col2:
            if hasattr(st.session_state, 'last_safety_check'):
                st.info(f"Last check: {st.session_state.last_safety_check.strftime('%Y-%m-%d %H:%M:%S')}")
        
        div_alerts = analyze_dividend_trends()
        price_alerts_list = check_price_alerts()
        
        all_alerts = div_alerts + price_alerts_list
        
        if not all_alerts:
            st.success("✅ All safety checks passed! No concerns detected.")
        else:
            critical = [a for a in all_alerts if a.get("severity") == "critical"]
            warnings = [a for a in all_alerts if a.get("severity") == "warning"]
            
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Critical Alerts", len(critical), delta=None if len(critical) == 0 else "⚠️")
            with col2:
                st.metric("Warnings", len(warnings))
            with col3:
                st.metric("Info", len(all_alerts) - len(critical) - len(warnings))
            
            st.divider()
            
            for alert in all_alerts:
                severity_class = {
                    "critical": "alert-critical",
                    "warning": "alert-warning",
                    "success": "alert-success",
                    "info": "alert-info"
                }.get(alert.get("severity", "info"), "alert-info")
                
                st.markdown(f"""
                <div class="{severity_class}">
                    <div style="font-weight: 700; font-size: 1.1rem; margin-bottom: 0.5rem;">{alert['message']}</div>
                    <div style="margin-bottom: 0.5rem;"><strong>Recommended Action:</strong> {alert['action']}</div>
                    {f"<div><strong>Details:</strong> Change: {alert.get('change_pct', 0):.1f}%</div>" if 'change_pct' in alert else ""}
                </div>
                """, unsafe_allow_html=True)
        
        st.divider()
        
        st.subheader("📊 Dividend Trend Analysis")
        
        from utils.helpers import ETF_LIST
        
        selected_ticker = st.selectbox("Select ETF to analyze", ETF_LIST, key="div_trend_select")
        
        if st.session_state.dividend_history[selected_ticker]:
            df_div = pd.DataFrame(st.session_state.dividend_history[selected_ticker])
            
            fig = go.Figure()
            fig.add_trace(go.Scatter(
                x=df_div["date"],
                y=df_div["dividend"],
                mode='lines+markers',
                name='Dividend',
                line=dict(color='#22c55e', width=3)
            ))
            
            avg_div = df_div["dividend"].mean()
            fig.add_hline(y=avg_div, line_dash="dash", line_color="#94a3b8", 
                         annotation_text=f"Average: ${avg_div:.4f}")
            
            fig.update_layout(
                title=f"{selected_ticker} Dividend History (Last 12 Weeks)",
                xaxis_title="Date",
                yaxis_title="Dividend per Share ($)",
                hovermode='x unified',
                height=400
            )
            
            st.plotly_chart(fig, use_container_width=True)
            
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("Current", f"${df_div['dividend'].iloc[-1]:.4f}")
            with col2:
                st.metric("Average", f"${avg_div:.4f}")
            with col3:
                trend = ((df_div['dividend'].iloc[-1] / df_div['dividend'].iloc[0]) - 1) * 100
                st.metric("12-Week Trend", f"{trend:+.1f}%")
            with col4:
                volatility = df_div['dividend'].std() / avg_div * 100
                st.metric("Volatility", f"{volatility:.1f}%")
