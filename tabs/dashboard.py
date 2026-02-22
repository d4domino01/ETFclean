"""
TAB 3: DASHBOARD
Portfolio overview and key metrics
"""

import streamlit as st
import pandas as pd
import plotly.express as px
from utils.helpers import calculate_current_metrics


def render():
    """Render the Dashboard tab"""
    if not st.session_state.PORTFOLIO_LOCKED:
        st.warning("⚠️ Fix validation errors to view dashboard")
    else:
        metrics = calculate_current_metrics()
        
        st.subheader("Portfolio Overview")
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Total Value", f"${metrics['total_value']:,.0f}",
                     delta=f"{metrics['total_gain_loss_pct']:+.1f}%")
        
        with col2:
            st.metric("Monthly Income", f"${metrics['monthly_income']:,.0f}", 
                     delta=f"${metrics['total_weekly']:.0f}/week")
        
        with col3:
            st.metric("Annual Income", f"${metrics['annual_income']:,.0f}",
                     delta=f"{metrics['total_yield']:.1f}% yield")
        
        with col4:
            st.metric("Total Gain/Loss", f"${metrics['total_gain_loss']:,.0f}",
                     delta=f"{metrics['total_gain_loss_pct']:+.1f}%")
        
        st.divider()
        
        st.subheader("🎯 Income Goal Progress")
        
        current = metrics['monthly_income']
        target = st.session_state.target_income
        progress = min((current / target * 100), 100) if target > 0 else 0
        gap = target - current
        
        col1, col2 = st.columns([1, 2])
        
        with col1:
            st.metric("Monthly Target", f"${target:,.0f}")
            st.metric("Current Income", f"${current:,.0f}")
            st.metric("Gap to Target", f"${gap:,.0f}")
        
        with col2:
            progress_color = "#22c55e" if progress >= 80 else "#f59e0b" if progress >= 50 else "#ef4444"
            st.markdown(f"""
            <div style="background: linear-gradient(135deg, #1e293b 0%, #0f172a 100%); border: 2px solid {progress_color}; border-radius: 1rem; padding: 2rem;">
                <div style="display: flex; justify-content: space-between; margin-bottom: 0.5rem;">
                    <span style="font-weight: 600;">Progress to Goal</span>
                    <span style="font-weight: 700; color: {progress_color};">{progress:.1f}%</span>
                </div>
                <div style="background: #1e293b; border-radius: 1rem; height: 2.5rem; overflow: hidden;">
                    <div style="background: linear-gradient(90deg, {progress_color} 0%, {progress_color} 100%); height: 100%; width: {progress}%; display: flex; align-items: center; justify-content: flex-end; padding-right: 1rem; color: white; font-weight: 700; transition: width 0.5s;">
                        {progress:.0f}%
                    </div>
                </div>
                <div style="font-size: 0.85rem; color: #94a3b8; margin-top: 0.75rem;">
                    {'🎉 Goal reached! Consider increasing target.' if gap <= 0 else f'Need ${gap:,.0f}/month more (${gap*12/52:.0f}/week)'}
                </div>
            </div>
            """, unsafe_allow_html=True)
        
        st.divider()
        
        st.subheader("Portfolio Analysis")
        col1, col2 = st.columns(2)
        
        with col1:
            income_data = []
            for h in metrics["holdings"]:
                income_data.append({"ETF": h["ticker"], "Monthly Income": h["monthly"]})
            
            df_income = pd.DataFrame(income_data)
            fig_income = px.bar(df_income, x="ETF", y="Monthly Income",
                               title="Monthly Income by Holding",
                               color="Monthly Income", color_continuous_scale="Greens")
            fig_income.update_layout(showlegend=False, height=350, margin=dict(l=20, r=20, t=40, b=20))
            st.plotly_chart(fig_income, use_container_width=True)
        
        with col2:
            allocation_data = []
            for h in metrics["holdings"]:
                allocation_data.append({"ETF": h["ticker"], "Value": h["value"]})
            
            df_allocation = pd.DataFrame(allocation_data)
            fig_pie = px.pie(df_allocation, values="Value", names="ETF",
                            title="Portfolio Allocation by Value",
                            color_discrete_sequence=px.colors.sequential.Blues_r)
            fig_pie.update_layout(height=350, margin=dict(l=20, r=20, t=40, b=20))
            st.plotly_chart(fig_pie, use_container_width=True)
        
        st.divider()
        
        st.subheader("Holdings Detail")
        holdings_df = pd.DataFrame([{
            "Ticker": h["ticker"],
            "Shares": h["shares"],
            "Price": f"${h['price']:.2f}",
            "Cost Basis": f"${h['cost_basis']:.2f}",
            "Gain/Loss": f"${h['gain_loss']:,.0f}",
            "Gain/Loss %": f"{h['gain_loss_pct']:+.1f}%",
            "Div/Share": f"${h['div']:.4f}",
            "Monthly": f"${h['monthly']:.2f}",
            "Annual": f"${h['annual']:,.0f}",
            "Value": f"${h['value']:,.0f}",
            "Yield": f"{h['yield_pct']:.1f}%"
        } for h in metrics["holdings"]])
        
        st.dataframe(holdings_df, use_container_width=True, hide_index=True)
