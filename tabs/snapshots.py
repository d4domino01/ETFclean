"""
TAB 9: SNAPSHOTS
Save and manage portfolio snapshots
"""

import streamlit as st
from datetime import datetime
from utils.helpers import calculate_current_metrics


def render():
    """Render the Snapshots tab"""
    st.subheader("📸 Portfolio Snapshots")
    
    if not st.session_state.PORTFOLIO_LOCKED:
        st.warning("⚠️ Fix validation errors to save snapshots")
    else:
        col1, col2 = st.columns([3, 1])
        
        with col1:
            snapshot_name = st.text_input(
                "Snapshot Name",
                value=f"Snapshot {datetime.now().strftime('%Y-%m-%d %H:%M')}",
                key="snapshot_name"
            )
        
        with col2:
            if st.button("📸 Save Current State", use_container_width=True):
                metrics = calculate_current_metrics()
                
                st.session_state.snapshots.append({
                    "name": snapshot_name,
                    "timestamp": datetime.now(),
                    "holdings": st.session_state.holdings.copy(),
                    "cash": st.session_state.cash,
                    "value": metrics['total_value'],
                    "income": metrics['monthly_income'],
                    "monthly_deposit": st.session_state.monthly_deposit
                })
                st.success("Snapshot saved!")
                st.rerun()
        
        st.divider()
        
        if st.session_state.snapshots:
            st.markdown(f"**{len(st.session_state.snapshots)} saved snapshots**")
            
            for i, snap in enumerate(reversed(st.session_state.snapshots)):
                with st.expander(f"📊 {snap['name']} — {snap['timestamp'].strftime('%Y-%m-%d %H:%M')}"):
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.metric("Total Value", f"${snap['value']:,.0f}")
                    with col2:
                        st.metric("Monthly Income", f"${snap['income']:,.0f}")
                    with col3:
                        if st.button("Delete", key=f"del_{i}"):
                            st.session_state.snapshots.pop(-(i+1))
                            st.rerun()
                    
                    st.markdown("**Holdings:**")
                    for ticker, data in snap['holdings'].items():
                        st.write(f"**{ticker}:** {data['shares']} shares @ ${data['div']:.4f}/week")
                    st.write(f"**Cash:** ${snap['cash']:,.0f}")
                    st.write(f"**Monthly Deposit:** ${snap.get('monthly_deposit', 0):.0f}")
        else:
            st.info("No snapshots yet. Save your first one above!")
