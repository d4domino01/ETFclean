"""
TAB 7: PORTFOLIO EDITOR
Edit portfolio holdings and positions
"""

import streamlit as st
from utils.helpers import get_price, calculate_current_metrics, ETF_LIST


def render():
    """Render the Portfolio Editor tab"""
    st.subheader("📁 Portfolio Editor")
    
    for ticker in ETF_LIST:
        price = get_price(ticker)
        price_display = f"${price:.2f}" if price else "N/A"
        
        st.markdown(f"""
        <div style="background: linear-gradient(135deg, #1e293b 0%, #0f172a 100%); border: 1px solid #334155; border-radius: 1rem; padding: 1.5rem; margin-bottom: 1rem;">
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 1rem; padding-bottom: 1rem; border-bottom: 1px solid #334155;">
                <div style="font-size: 1.8rem; font-weight: 700; color: #3b82f6;">{ticker}</div>
                <div style="font-size: 1.5rem; font-weight: 700; color: #22c55e;">{price_display}</div>
            </div>
        """, unsafe_allow_html=True)
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.session_state.holdings[ticker]["shares"] = st.number_input(
                "Number of Shares",
                min_value=0,
                value=st.session_state.holdings[ticker]["shares"],
                key=f"shares_{ticker}_edit"
            )
        
        with col2:
            st.session_state.holdings[ticker]["div"] = st.number_input(
                "Weekly Dividend per Share ($)",
                min_value=0.0,
                step=0.01,
                format="%.4f",
                value=st.session_state.holdings[ticker]["div"],
                key=f"div_{ticker}_edit"
            )
        
        with col3:
            # If price is None, use 0 as fallback
            price_for_default = price if price else 0.0
            st.session_state.holdings[ticker]["cost_basis"] = st.number_input(
                "Cost Basis per Share ($)",
                min_value=0.0,
                step=0.10,
                format="%.2f",
                value=st.session_state.holdings[ticker].get("cost_basis", price_for_default),
                key=f"cost_{ticker}_edit"
            )
        
        shares = st.session_state.holdings[ticker]["shares"]
        div = st.session_state.holdings[ticker]["div"]
        cost_basis = st.session_state.holdings[ticker].get("cost_basis", 0.0)
        
        # Use price if available, otherwise use cost_basis, otherwise 0
        current_price = price if price else (cost_basis if cost_basis > 0 else 0.0)
        
        weekly = shares * div
        monthly = weekly * 52 / 12
        annual = weekly * 52
        value = shares * current_price
        yield_pct = (annual / value * 100) if value > 0 else 0
        
        cost_total = shares * cost_basis
        gain_loss = value - cost_total
        gain_loss_pct = ((value / cost_total) - 1) * 100 if cost_total > 0 else 0
        
        metrics = calculate_current_metrics()
        portfolio_pct = (value / metrics['total_value'] * 100) if metrics['total_value'] > 0 else 0
        
        st.markdown(f"""
            <div style="display: grid; grid-template-columns: repeat(6, 1fr); gap: 1rem; margin-top: 1rem; padding-top: 1rem; border-top: 1px solid #334155;">
                <div style="text-align: center;">
                    <div style="font-size: 0.75rem; color: #94a3b8; text-transform: uppercase; margin-bottom: 0.25rem;">Weekly</div>
                    <div style="font-size: 1.1rem; font-weight: 700; color: #22c55e;">${weekly:.2f}</div>
                </div>
                <div style="text-align: center;">
                    <div style="font-size: 0.75rem; color: #94a3b8; text-transform: uppercase; margin-bottom: 0.25rem;">Monthly</div>
                    <div style="font-size: 1.1rem; font-weight: 700; color: #22c55e;">${monthly:.2f}</div>
                </div>
                <div style="text-align: center;">
                    <div style="font-size: 0.75rem; color: #94a3b8; text-transform: uppercase; margin-bottom: 0.25rem;">Annual</div>
                    <div style="font-size: 1.1rem; font-weight: 700; color: #22c55e;">${annual:,.0f}</div>
                </div>
                <div style="text-align: center;">
                    <div style="font-size: 0.75rem; color: #94a3b8; text-transform: uppercase; margin-bottom: 0.25rem;">Value</div>
                    <div style="font-size: 1.1rem; font-weight: 700; color: #3b82f6;">${value:,.0f}</div>
                </div>
                <div style="text-align: center;">
                    <div style="font-size: 0.75rem; color: #94a3b8; text-transform: uppercase; margin-bottom: 0.25rem;">Gain/Loss</div>
                    <div style="font-size: 1.1rem; font-weight: 700; color: {'#22c55e' if gain_loss >= 0 else '#ef4444'};">${gain_loss:,.0f} ({gain_loss_pct:+.1f}%)</div>
                </div>
                <div style="text-align: center;">
                    <div style="font-size: 0.75rem; color: #94a3b8; text-transform: uppercase; margin-bottom: 0.25rem;">% Portfolio</div>
                    <div style="font-size: 1.1rem; font-weight: 700; color: #eab308;">{portfolio_pct:.1f}%</div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("<br>", unsafe_allow_html=True)
    
    st.divider()
    
    st.subheader("💰 Cash Position")
    st.session_state.cash = st.number_input(
        "Cash Balance ($)",
        min_value=0.0,
        step=100.0,
        value=st.session_state.cash,
        key="cash_edit"
    )
