"""
TAB 1: AI COMMAND CENTER
Displays AI-powered recommendations and portfolio risk assessment
"""

import streamlit as st
from utils.helpers import (
    calculate_portfolio_risk_score, 
    generate_ai_recommendations
)


def render():
    """Render the AI Command Center tab"""
    if not st.session_state.PORTFOLIO_LOCKED:
        st.warning("⚠️ Fix validation errors in Portfolio Editor to unlock AI features")
    else:
        st.subheader("🤖 AI Recommendations & Actions")
        
        # Generate recommendations
        if st.button("🔄 Refresh AI Analysis", type="primary"):
            with st.spinner("AI analyzing portfolio..."):
                st.session_state.recommendations = generate_ai_recommendations()
                st.success("Analysis complete!")
        
        if not st.session_state.recommendations:
            st.session_state.recommendations = generate_ai_recommendations()
        
        # Display recommendations
        if st.session_state.recommendations:
            st.markdown(f"**Found {len(st.session_state.recommendations)} recommendations**")
            
            for idx, rec in enumerate(st.session_state.recommendations):
                priority_colors = {
                    "CRITICAL": "alert-critical",
                    "HIGH": "alert-warning",
                    "MEDIUM": "alert-info",
                    "LOW": "alert-success"
                }
                
                alert_class = priority_colors[rec["priority"]]
                
                st.markdown(f"""
                <div class="{alert_class}">
                    <div style="display: flex; justify-content: space-between; align-items: start; margin-bottom: 0.75rem;">
                        <div>
                            <div style="font-size: 1.1rem; font-weight: 700; margin-bottom: 0.25rem;">{rec['title']}</div>
                            <div style="font-size: 0.85rem; opacity: 0.8;">Priority: {rec['priority']} | Confidence: {rec['confidence']}%</div>
                        </div>
                        <div style="background: rgba(255,255,255,0.1); padding: 0.5rem 1rem; border-radius: 0.5rem; font-weight: 700;">
                            {rec['ticker']}
                        </div>
                    </div>
                    <div style="margin-bottom: 0.75rem;">
                        <strong>Analysis:</strong> {rec['description']}
                    </div>
                    <div style="margin-bottom: 0.75rem;">
                        <strong>Recommended Action:</strong> {rec['action']}
                    </div>
                    <div style="font-size: 0.9rem; opacity: 0.9;">
                        <strong>Expected Impact:</strong> {rec['impact']}
                    </div>
                </div>
                """, unsafe_allow_html=True)
                
                if st.session_state.autopilot["enabled"] and st.session_state.autopilot["require_approval"]:
                    col1, col2, col3 = st.columns([1, 1, 4])
                    with col1:
                        if st.button("✓ Execute", key=f"exec_{idx}"):
                            st.success(f"Action approved! (Demo mode - no actual trades executed)")
                    with col2:
                        if st.button("✗ Dismiss", key=f"dismiss_{idx}"):
                            st.info("Recommendation dismissed")
                
                st.markdown("<br>", unsafe_allow_html=True)
        else:
            st.success("✅ No critical actions needed right now. Portfolio looking good!")
        
        st.divider()
        
        # Portfolio Risk Score
        st.subheader("🛡️ Portfolio Risk Assessment")
        
        risk_data = calculate_portfolio_risk_score()
        
        col1, col2 = st.columns([1, 2])
        
        with col1:
            st.markdown(f"""
            <div class="{risk_data['risk_class']}">
                {risk_data['total_score']:.0f}/100
                <div style="font-size: 1.2rem; margin-top: 0.5rem;">{risk_data['risk_level']} RISK</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown("### Risk Breakdown")
            for category, score in risk_data["scores"].items():
                max_score = {
                    "diversification": 20,
                    "dividend_stability": 25,
                    "price_performance": 20,
                    "yield_sustainability": 20,
                    "risk_exposure": 15
                }[category]
                
                pct = (score / max_score) * 100
                color = "#22c55e" if pct >= 70 else "#f59e0b" if pct >= 40 else "#ef4444"
                
                st.markdown(f"""
                <div style="margin-bottom: 1rem;">
                    <div style="display: flex; justify-content: space-between; margin-bottom: 0.25rem;">
                        <span style="text-transform: capitalize;">{category.replace('_', ' ')}</span>
                        <span style="font-weight: 700;">{score:.1f}/{max_score}</span>
                    </div>
                    <div style="background: #1e293b; border-radius: 0.5rem; height: 0.75rem; overflow: hidden;">
                        <div style="background: {color}; height: 100%; width: {pct}%; transition: width 0.5s;"></div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
