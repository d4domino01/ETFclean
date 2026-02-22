"""
TAB 2: WEEKLY INVESTMENT ADVISOR
Smart investment guidance for the current week
"""

import streamlit as st
import pandas as pd
from utils.helpers import (
    get_price,
    generate_weekly_investment_recommendation,
)


def generate_auto_rebalance_plan():
    """Generate automatic rebalancing plan based on current conditions"""
    from utils.helpers import calculate_current_metrics, calculate_portfolio_risk_score, ETF_LIST, ETF_INFO
    
    metrics = calculate_current_metrics()
    risk_score = calculate_portfolio_risk_score()
    
    rebalance_actions = []
    
    # Check 1: Concentration risk
    for holding in metrics["holdings"]:
        concentration = (holding["value"] / metrics["total_value"] * 100) if metrics["total_value"] > 0 else 0
        
        if concentration > 45:
            target_concentration = 35
            excess_pct = concentration - target_concentration
            shares_to_sell = int(holding["shares"] * (excess_pct / concentration))
            proceeds = shares_to_sell * holding["price"]
            
            rebalance_actions.append({
                "type": "SELL",
                "ticker": holding["ticker"],
                "shares": shares_to_sell,
                "proceeds": proceeds,
                "reason": f"Reduce concentration from {concentration:.1f}% to ~{target_concentration}%",
                "priority": "HIGH"
            })
    
    # Check 2: Weak performers
    weekly_rec = generate_weekly_investment_recommendation()
    
    for ticker, score_data in weekly_rec["all_scores"].items():
        if score_data["total_score"] < 40 and score_data["warnings"]:
            holding = next((h for h in metrics["holdings"] if h["ticker"] == ticker), None)
            
            if holding and holding["shares"] > 0:
                shares_to_sell = int(holding["shares"] * 0.2)
                proceeds = shares_to_sell * holding["price"]
                
                rebalance_actions.append({
                    "type": "SELL",
                    "ticker": ticker,
                    "shares": shares_to_sell,
                    "proceeds": proceeds,
                    "reason": f"Weak performance (score: {score_data['total_score']:.1f}/100) + warnings",
                    "priority": "MEDIUM"
                })
    
    # Check 3: Where to reinvest proceeds
    if rebalance_actions:
        total_proceeds = sum(a["proceeds"] for a in rebalance_actions if a["type"] == "SELL")
        
        best_ticker = weekly_rec["recommended_ticker"]
        best_price = metrics["prices"][best_ticker]
        shares_to_buy = int(total_proceeds / best_price)
        
        rebalance_actions.append({
            "type": "BUY",
            "ticker": best_ticker,
            "shares": shares_to_buy,
            "cost": shares_to_buy * best_price,
            "reason": f"Highest score ({weekly_rec['all_scores'][best_ticker]['total_score']:.1f}/100)",
            "priority": "HIGH"
        })
    
    # Calculate income impact
    income_before = metrics["monthly_income"]
    income_after = income_before
    
    for action in rebalance_actions:
        ticker = action["ticker"]
        div = st.session_state.holdings[ticker]["div"]
        
        if action["type"] == "SELL":
            income_after -= action["shares"] * div * 52 / 12
        else:
            income_after += action["shares"] * div * 52 / 12
    
    income_change = income_after - income_before
    
    return {
        "needs_rebalancing": len(rebalance_actions) > 0,
        "actions": rebalance_actions,
        "income_before": income_before,
        "income_after": income_after,
        "income_change": income_change,
        "risk_improvement": "Reduces concentration risk" if any(a["type"] == "SELL" for a in rebalance_actions) else "Maintains balance"
    }


def render():
    """Render the Weekly Advisor tab"""
    st.subheader("💡 This Week's Investment Recommendation")
    
    if not st.session_state.PORTFOLIO_LOCKED:
        st.warning("⚠️ Fix validation errors to get investment recommendations")
    else:
        col1, col2 = st.columns([3, 1])
        
        with col1:
            st.markdown("""
            **Smart investment guidance based on:**
            - 📰 News sentiment & market conditions
            - 📈 Price trends (buying dips = opportunities!)
            - 💰 Dividend stability & yield
            - ⚖️ Portfolio balance & concentration
            - 🎯 Risk level assessment
            """)
        
        with col2:
            if st.button("🔄 Get Recommendation", type="primary", use_container_width=True):
                with st.spinner("Analyzing all factors..."):
                    st.session_state.weekly_rec = generate_weekly_investment_recommendation()
        
        if "weekly_rec" not in st.session_state:
            with st.spinner("Analyzing markets..."):
                st.session_state.weekly_rec = generate_weekly_investment_recommendation()
        
        rec = st.session_state.weekly_rec
        
        st.markdown("---")
        
        st.markdown(f"""
        <div style="background: linear-gradient(135deg, #1e293b 0%, #0f172a 100%); border: 3px solid {rec['confidence_color']}; border-radius: 1rem; padding: 2rem; margin: 1rem 0;">
            <div style="text-align: center; margin-bottom: 1.5rem;">
                <div style="font-size: 1rem; opacity: 0.8; margin-bottom: 0.5rem;">💡 THIS WEEK, INVEST IN:</div>
                <div style="font-size: 3.5rem; font-weight: 700; color: {rec['confidence_color']}; margin: 0.5rem 0;">
                    {rec['recommended_ticker']}
                </div>
                <div style="font-size: 1.2rem; font-weight: 600; color: {rec['confidence_color']};">
                    Confidence: {rec['confidence']}
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("**📊 Analysis Breakdown:**")
        for reason in rec['reasoning']:
            st.markdown(f"- {reason}")
        
        if rec['warnings']:
            st.warning("**⚠️ Warnings:**")
            for warning in rec['warnings']:
                st.markdown(f"- {warning}")
        
        st.info(f"**Alternative option:** {rec['alternative']} (if diversifying this week)")
        
        st.divider()
        st.markdown("### 📊 All ETF Scores (This Week)")
        
        cols = st.columns(3)
        for idx, (ticker, score_data) in enumerate(sorted(rec["all_scores"].items(), key=lambda x: x[1]["total_score"], reverse=True)):
            with cols[idx]:
                rank_emoji = ["🥇", "🥈", "🥉"][idx]
                rank_color = ["#ffd700", "#c0c0c0", "#cd7f32"][idx]
                
                st.markdown(f"""
                <div style="background: #1e293b; border-radius: 1rem; padding: 1.5rem; border: 2px solid {rank_color if idx == 0 else '#334155'}; text-align: center;">
                    <div style="font-size: 2rem;">{rank_emoji}</div>
                    <div style="font-size: 1.8rem; font-weight: 700; color: #3b82f6; margin: 0.5rem 0;">{ticker}</div>
                    <div style="font-size: 2.5rem; font-weight: 700; color: {rank_color if idx == 0 else '#94a3b8'};">
                        {score_data['total_score']}/100
                    </div>
                </div>
                """, unsafe_allow_html=True)
                
                st.markdown("**Factors:**")
                for factor in score_data['factors'][:4]:
                    st.caption(factor)
                
                st.caption("_Yield = annual dividend income / current market value_")
                
                if score_data['warnings']:
                    st.warning(f"⚠️ {score_data['warnings'][0]}", icon="⚠️")
        
        st.divider()
        st.markdown("### 💰 Suggested Investment Amount")
        
        col1, col2 = st.columns(2)
        
        with col1:
            investment_amount = st.number_input(
                "How much are you investing this week?",
                min_value=0.0,
                value=st.session_state.monthly_deposit / 4.33,
                step=50.0,
                help="Your regular $200/month = ~$46/week"
            )
        
        with col2:
            if investment_amount > 0:
                best_ticker = rec["recommended_ticker"]
                best_price = get_price(best_ticker)
                shares_to_buy = int(investment_amount / best_price) if best_price > 0 else 0
                leftover = investment_amount - (shares_to_buy * best_price)
                
                weekly_div_income = shares_to_buy * st.session_state.holdings[best_ticker]["div"]
                monthly_div_income = weekly_div_income * 52 / 12
                annual_div_income = weekly_div_income * 52
                
                st.markdown(f"""
                <div style="background: #1e293b; padding: 1.5rem; border-radius: 1rem; border: 2px solid #22c55e;">
                    <div style="font-weight: 700; margin-bottom: 1rem;">💵 Investment Breakdown:</div>
                    <div style="line-height: 2;">
                        <strong>Buy:</strong> {shares_to_buy} shares of {best_ticker}<br>
                        <strong>Cost:</strong> ${shares_to_buy * best_price:.2f}<br>
                        <strong>Leftover:</strong> ${leftover:.2f}<br>
                        <hr style="margin: 1rem 0; opacity: 0.3;">
                        <strong>Weekly income added:</strong> <span style="color: #22c55e;">${weekly_div_income:.2f}</span><br>
                        <strong>Monthly income added:</strong> <span style="color: #22c55e;">${monthly_div_income:.2f}</span><br>
                        <strong>Annual income added:</strong> <span style="color: #22c55e;">${annual_div_income:.2f}</span>
                    </div>
                </div>
                """, unsafe_allow_html=True)
        
        st.divider()
        st.markdown("### 🔄 Auto-Rebalancer Analysis")
        
        if st.button("🤖 Generate Rebalancing Plan", use_container_width=True):
            with st.spinner("Analyzing portfolio balance..."):
                st.session_state.rebalance_plan = generate_auto_rebalance_plan()
        
        if "rebalance_plan" in st.session_state:
            plan = st.session_state.rebalance_plan
            
            if plan["needs_rebalancing"]:
                st.warning(f"⚠️ Rebalancing recommended - Portfolio needs adjustment")
                
                st.markdown("#### Recommended Actions:")
                
                for idx, action in enumerate(plan["actions"]):
                    if action["type"] == "SELL":
                        st.markdown(f"""
                        <div style="background: rgba(239, 68, 68, 0.1); border-left: 4px solid #ef4444; padding: 1rem; border-radius: 0.5rem; margin-bottom: 0.5rem;">
                            <strong>📉 SELL {action['shares']} shares of {action['ticker']}</strong><br>
                            <em>Proceeds: ${action['proceeds']:.2f}</em><br>
                            <small>Reason: {action['reason']}</small>
                        </div>
                        """, unsafe_allow_html=True)
                    else:
                        st.markdown(f"""
                        <div style="background: rgba(34, 197, 94, 0.1); border-left: 4px solid #22c55e; padding: 1rem; border-radius: 0.5rem; margin-bottom: 0.5rem;">
                            <strong>📈 BUY {action['shares']} shares of {action['ticker']}</strong><br>
                            <em>Cost: ${action['cost']:.2f}</em><br>
                            <small>Reason: {action['reason']}</small>
                        </div>
                        """, unsafe_allow_html=True)
                
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Income Before", f"${plan['income_before']:.2f}")
                with col2:
                    st.metric("Income After", f"${plan['income_after']:.2f}")
                with col3:
                    st.metric("Income Change", f"${plan['income_change']:+.2f}", 
                             delta=f"{(plan['income_change']/plan['income_before']*100):+.1f}%" if plan['income_before'] > 0 else "N/A")
                
                st.info(f"ℹ️ {plan['risk_improvement']}")
                
                if st.session_state.autopilot.get("auto_rebalance") and st.session_state.autopilot.get("require_approval"):
                    col1, col2 = st.columns(2)
                    with col1:
                        if st.button("✅ Execute Rebalance", type="primary", use_container_width=True):
                            st.success("✅ Rebalancing plan approved! (Demo mode - no actual trades)")
                    with col2:
                        if st.button("❌ Dismiss", use_container_width=True):
                            del st.session_state.rebalance_plan
                            st.rerun()
            else:
                st.success("✅ Portfolio is well-balanced! No rebalancing needed this week.")
                st.info("Your holdings are optimally distributed. Continue with regular investments.")
