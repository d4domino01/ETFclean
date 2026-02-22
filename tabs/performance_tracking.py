"""
TAB 8: PERFORMANCE TRACKING
Track portfolio performance over time
"""

import streamlit as st


def render():
    """Render the Performance Tracking tab"""
    st.subheader("📈 Performance Tracking")
    st.info("Track your portfolio performance over time with detailed metrics and charts.")
    
    if st.session_state.snapshots:
        st.success(f"You have {len(st.session_state.snapshots)} saved snapshots to analyze")
    else:
        st.warning("No snapshots yet. Save snapshots to track performance over time.")
