"""
TAB 6: COMPOUND PROJECTIONS
Portfolio growth projections with dividend reinvestment
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from utils.helpers import calculate_current_metrics, ETF_LIST


def project_compound_growth():
    """Project portfolio growth with dividend reinvestment + monthly deposits"""
    current_metrics = calculate_current_metrics()
    target = st.session_state.target_income
    monthly_deposit = st.session_state.monthly_deposit
    
    portfolio = {ticker: st.session_state.holdings[ticker]["shares"] for ticker in ETF_LIST}
    cash = st.session_state.cash
    
    projection_data = []
    month = 0
    max_months = 360
    
    while month < max_months:
        monthly_income = 0
        portfolio_value = cash
        
        for ticker in ETF_LIST:
            shares = portfolio[ticker]
            div = st.session_state.holdings[ticker]["div"]
            price = current_metrics["prices"][ticker]
            
            weekly_income = shares * div
            monthly_income += weekly_income * 52 / 12
            portfolio_value += shares * price
        
        projection_data.append({
            "month": month,
            "portfolio_value": portfolio_value,
            "monthly_income": monthly_income,
            "portfolio": portfolio.copy()
        })
        
        if monthly_income >= target:
            return {
                "months_to_target": month,
                "years_to_target": month / 12,
                "projection_data": projection_data,
                "final_portfolio": portfolio,
                "final_value": portfolio_value,
                "final_income": monthly_income,
                "reached": True
            }
        
        monthly_dividends = monthly_income
        available_cash = monthly_dividends + monthly_deposit
        
        total_shares_value = sum(portfolio[t] * current_metrics["prices"][t] for t in ETF_LIST)
        
        for ticker in ETF_LIST:
            if total_shares_value > 0:
                ticker_weight = (portfolio[ticker] * current_metrics["prices"][ticker]) / total_shares_value
                ticker_investment = available_cash * ticker_weight
                shares_to_buy = ticker_investment / current_metrics["prices"][ticker]
                portfolio[ticker] += shares_to_buy
        
        month += 1
    
    return {
        "months_to_target": max_months,
        "years_to_target": max_months / 12,
        "projection_data": projection_data,
        "final_portfolio": portfolio,
        "final_value": projection_data[-1]["portfolio_value"],
        "final_income": projection_data[-1]["monthly_income"],
        "reached": False
    }


def render():
    """Render the Compound Projections tab"""
    st.subheader("🚀 Compound Growth Projections")
    
    if not st.session_state.PORTFOLIO_LOCKED:
        st.warning("⚠️ Fix validation errors to view projections")
    else:
        col1, col2 = st.columns([1, 2])
        
        with col1:
            st.markdown("### Settings")
            
            st.session_state.target_income = st.number_input(
                "Monthly Income Target ($)",
                min_value=0.0,
                step=100.0,
                value=st.session_state.target_income,
                key="target_proj"
            )
            
            st.session_state.monthly_deposit = st.number_input(
                "Monthly Additional Deposit ($)",
                min_value=0.0,
                step=50.0,
                value=st.session_state.monthly_deposit,
                key="deposit_proj"
            )
            
            if st.button("🔄 Run Projection", type="primary"):
                with st.spinner("Calculating compound growth..."):
                    projection = project_compound_growth()
                    st.session_state.projection = projection
        
        with col2:
            if "projection" in st.session_state:
                proj = st.session_state.projection
                
                if proj["reached"]:
                    st.markdown(f"""
                    <div style="background: linear-gradient(135deg, #1e293b 0%, #0f172a 100%); border: 2px solid #3b82f6; border-radius: 1rem; padding: 2rem;">
                        <div style="text-align: center; font-size: 1.1rem; opacity: 0.8; margin-bottom: 0.5rem;">Time to Reach ${st.session_state.target_income:,.0f}/month</div>
                        <div style="text-align: center; font-size: 3.5rem; font-weight: 700; color: #22c55e; margin: 1rem 0;">{proj['years_to_target']:.1f} years</div>
                        <div style="text-align: center; font-size: 1.2rem; color: #94a3b8; margin-bottom: 2rem;">({proj['months_to_target']} months)</div>
                        <div style="display: grid; grid-template-columns: repeat(3, 1fr); gap: 1rem; text-align: center; padding-top: 1.5rem; border-top: 1px solid #334155;">
                            <div>
                                <div style="font-size: 0.75rem; color: #94a3b8; text-transform: uppercase; margin-bottom: 0.25rem;">Final Portfolio Value</div>
                                <div style="font-size: 1.1rem; font-weight: 700; color: #3b82f6;">${proj['final_value']:,.0f}</div>
                            </div>
                            <div>
                                <div style="font-size: 0.75rem; color: #94a3b8; text-transform: uppercase; margin-bottom: 0.25rem;">Final Monthly Income</div>
                                <div style="font-size: 1.1rem; font-weight: 700; color: #22c55e;">${proj['final_income']:,.0f}</div>
                            </div>
                            <div>
                                <div style="font-size: 0.75rem; color: #94a3b8; text-transform: uppercase; margin-bottom: 0.25rem;">Total Contributed</div>
                                <div style="font-size: 1.1rem; font-weight: 700; color: #eab308;">${proj['months_to_target'] * st.session_state.monthly_deposit:,.0f}</div>
                            </div>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                else:
                    st.error(f"⚠️ Target not reachable within 30 years with current settings")
        
        if "projection" in st.session_state and st.session_state.projection["reached"]:
            st.divider()
            st.subheader("Growth Timeline")
            
            proj_df = pd.DataFrame(st.session_state.projection["projection_data"])
            
            fig = go.Figure()
            
            fig.add_trace(go.Scatter(
                x=proj_df["month"] / 12,
                y=proj_df["portfolio_value"],
                mode='lines',
                name='Portfolio Value',
                line=dict(color='#3b82f6', width=3),
                fill='tozeroy',
                fillcolor='rgba(59, 130, 246, 0.1)'
            ))
            
            fig.add_trace(go.Scatter(
                x=proj_df["month"] / 12,
                y=proj_df["monthly_income"],
                mode='lines',
                name='Monthly Income',
                line=dict(color='#22c55e', width=3),
                yaxis='y2'
            ))
            
            fig.add_hline(y=st.session_state.target_income, line_dash="dash",
                         line_color="#eab308", annotation_text="Target Income",
                         yref='y2')
            
            fig.update_layout(
                xaxis_title="Years",
                yaxis_title="Portfolio Value ($)",
                yaxis2=dict(title="Monthly Income ($)", overlaying='y', side='right'),
                hovermode='x unified',
                height=500,
                legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
            )
            
            st.plotly_chart(fig, use_container_width=True)
            
            st.divider()
            st.subheader("Final Portfolio Composition")
            
            col1, col2, col3 = st.columns(3)
            for idx, ticker in enumerate(ETF_LIST):
                final_shares = st.session_state.projection["final_portfolio"][ticker]
                current_shares = st.session_state.holdings[ticker]["shares"]
                shares_added = final_shares - current_shares
                
                with [col1, col2, col3][idx]:
                    st.markdown(f"""
                    <div style="background: linear-gradient(135deg, #1e293b 0%, #0f172a 100%); border: 1px solid #334155; border-radius: 1rem; padding: 1.5rem;">
                        <div style="font-size: 1.5rem; font-weight: 700; color: #3b82f6; margin-bottom: 0.5rem;">{ticker}</div>
                        <div style="font-size: 0.75rem; color: #94a3b8; text-transform: uppercase; margin-bottom: 0.25rem;">Current Shares</div>
                        <div style="font-size: 1.1rem; font-weight: 700; color: #94a3b8; margin-bottom: 0.75rem;">{current_shares:.0f}</div>
                        <div style="font-size: 0.75rem; color: #94a3b8; text-transform: uppercase; margin-bottom: 0.25rem;">Final Shares</div>
                        <div style="font-size: 1.1rem; font-weight: 700; color: #22c55e; margin-bottom: 0.75rem;">{final_shares:.0f}</div>
                        <div style="font-size: 0.75rem; color: #94a3b8; text-transform: uppercase; margin-bottom: 0.25rem;">Shares Added</div>
                        <div style="font-size: 1.1rem; font-weight: 700; color: #22c55e;">+{shares_added:.0f}</div>
                    </div>
                    """, unsafe_allow_html=True)
