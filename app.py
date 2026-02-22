"""
Income Strategy Engine - AI Powered
Main application file
"""

import streamlit as st
from datetime import datetime, timedelta
import numpy as np
from collections import defaultdict

# Import all utilities
from utils.helpers import (
    get_price,
    ETF_LIST,
    ETF_INFO,
    calculate_current_metrics
)

# Import all tab modules
from tabs import (
    ai_command_center,
    weekly_advisor,
    dashboard,
    safety_monitor,
    news_intelligence,
    compound_projections,
    portfolio_editor,
    performance_tracking,
    snapshots
)

# =====================================================
# PAGE CONFIG
# =====================================================
st.set_page_config(
    page_title="Income Strategy Engine - AI Powered",
    layout="wide",
    initial_sidebar_state="expanded"
)

# =====================================================
# CUSTOM CSS
# =====================================================
st.markdown("""
<style>
    /* Base styles */
    .main {padding: 0rem 0.5rem;}
    h1 {font-size: 1.5rem !important; font-weight: 700 !important; word-wrap: break-word !important;}
    h2 {font-size: 1.2rem !important; font-weight: 600 !important; margin-top: 1.5rem !important; word-wrap: break-word !important;}
    h3 {font-size: 1rem !important; word-wrap: break-word !important;}
    
    [data-testid="stMetricValue"] {font-size: 1.5rem !important; font-weight: 700 !important;}
    [data-testid="stMetricLabel"] {font-size: 0.85rem !important; word-wrap: break-word !important;}
    
    /* Mobile-specific styles */
    @media (max-width: 768px) {
        .main {padding: 0rem 0.25rem;}
        h1 {font-size: 1.2rem !important;}
        h2 {font-size: 1rem !important;}
        h3 {font-size: 0.9rem !important;}
        [data-testid="stMetricValue"] {font-size: 1.2rem !important;}
        [data-testid="stMetricLabel"] {font-size: 0.75rem !important;}
        [data-testid="column"] {width: 100% !important; flex: 100% !important; max-width: 100% !important;}
        .stButton > button {width: 100%; font-size: 0.9rem !important;}
        input {font-size: 0.9rem !important;}
    }
    
    .status-locked {
        background: linear-gradient(90deg, #059669 0%, #10b981 100%);
        color: white;
        padding: 0.5rem 1rem;
        border-radius: 0.5rem;
        font-weight: 600;
        display: inline-block;
        margin: 1rem 0;
        font-size: 0.9rem;
    }
    
    .status-unlocked {
        background: linear-gradient(90deg, #dc2626 0%, #ef4444 100%);
        color: white;
        padding: 0.5rem 1rem;
        border-radius: 0.5rem;
        font-weight: 600;
        display: inline-block;
        margin: 1rem 0;
        font-size: 0.9rem;
    }
    
    .autopilot-active {
        background: linear-gradient(90deg, #3b82f6 0%, #1e88e5 100%);
        color: white;
        padding: 0.75rem 1.5rem;
        border-radius: 0.75rem;
        font-weight: 700;
        display: inline-block;
        margin: 1rem 0;
        font-size: 0.95rem;
        animation: pulse 2s infinite;
    }
    
    @keyframes pulse {
        0%, 100% { opacity: 1; }
        50% { opacity: 0.7; }
    }
    
    .risk-score-low {
        background: linear-gradient(135deg, #059669 0%, #10b981 100%);
        color: white;
        padding: 2rem;
        border-radius: 1rem;
        text-align: center;
        font-size: 3rem;
        font-weight: 700;
    }
    
    .risk-score-medium {
        background: linear-gradient(135deg, #d97706 0%, #f59e0b 100%);
        color: white;
        padding: 2rem;
        border-radius: 1rem;
        text-align: center;
        font-size: 3rem;
        font-weight: 700;
    }
    
    .risk-score-high {
        background: linear-gradient(135deg, #dc2626 0%, #ef4444 100%);
        color: white;
        padding: 2rem;
        border-radius: 1rem;
        text-align: center;
        font-size: 3rem;
        font-weight: 700;
    }
    
    @media (max-width: 768px) {
        .risk-score-low, .risk-score-medium, .risk-score-high {
            font-size: 2rem;
            padding: 1.5rem;
        }
    }
    
    .alert-critical {
        background: rgba(239, 68, 68, 0.15);
        border-left: 4px solid #ef4444;
        padding: 1.25rem;
        border-radius: 0.75rem;
        margin: 1rem 0;
    }
    
    .alert-warning {
        background: rgba(234, 179, 8, 0.15);
        border-left: 4px solid #eab308;
        padding: 1.25rem;
        border-radius: 0.75rem;
        margin: 1rem 0;
    }
    
    .alert-info {
        background: rgba(59, 130, 246, 0.15);
        border-left: 4px solid #3b82f6;
        padding: 1.25rem;
        border-radius: 0.75rem;
        margin: 1rem 0;
    }
    
    .alert-success {
        background: rgba(34, 197, 94, 0.15);
        border-left: 4px solid #22c55e;
        padding: 1.25rem;
        border-radius: 0.75rem;
        margin: 1rem 0;
    }
    
    .news-card {
        background: #1e293b;
        border-radius: 0.75rem;
        padding: 1.25rem;
        margin-bottom: 1rem;
        border: 1px solid #334155;
        transition: all 0.3s;
    }
    
    .news-card:hover {
        border-color: #3b82f6;
        transform: translateY(-2px);
    }
    
    .sentiment-positive {
        background: #22c55e;
        color: white;
        padding: 0.25rem 0.75rem;
        border-radius: 0.5rem;
        font-weight: 600;
        font-size: 0.85rem;
    }
    
    .sentiment-negative {
        background: #ef4444;
        color: white;
        padding: 0.25rem 0.75rem;
        border-radius: 0.5rem;
        font-weight: 600;
        font-size: 0.85rem;
    }
    
    .sentiment-neutral {
        background: #94a3b8;
        color: white;
        padding: 0.25rem 0.75rem;
        border-radius: 0.5rem;
        font-weight: 600;
        font-size: 0.85rem;
    }
</style>
""", unsafe_allow_html=True)

# =====================================================
# SESSION STATE INITIALIZATION
# =====================================================
if "holdings" not in st.session_state:
    st.session_state.holdings = {
        "QDTE": {"shares": 125, "div": 0.177, "cost_basis": 19.50},
        "CHPY": {"shares": 63,  "div": 0.52, "cost_basis": 25.80},
        "XDTE": {"shares": 84,  "div": 0.16, "cost_basis": 18.50},
    }

if "cash" not in st.session_state:
    st.session_state.cash = 0.0

if "monthly_deposit" not in st.session_state:
    st.session_state.monthly_deposit = 200.0

if "target_income" not in st.session_state:
    st.session_state.target_income = 1000.0

if "PORTFOLIO_LOCKED" not in st.session_state:
    st.session_state.PORTFOLIO_LOCKED = False

if "snapshots" not in st.session_state:
    st.session_state.snapshots = []

if "dividend_drop_threshold" not in st.session_state:
    st.session_state.dividend_drop_threshold = 10.0

if "dividend_history" not in st.session_state:
    st.session_state.dividend_history = defaultdict(list)
    for ticker in ETF_LIST:
        current_div = st.session_state.holdings[ticker]["div"]
        for i in range(12):
            variation = np.random.uniform(-0.02, 0.02)
            st.session_state.dividend_history[ticker].append({
                "date": datetime.now() - timedelta(weeks=12-i),
                "dividend": current_div + (current_div * variation),
                "verified": True
            })

if "price_alerts" not in st.session_state:
    st.session_state.price_alerts = {
        "QDTE": {"stop_loss_pct": 20, "target_price": None, "enabled": False},
        "CHPY": {"stop_loss_pct": 20, "target_price": None, "enabled": False},
        "XDTE": {"stop_loss_pct": 20, "target_price": None, "enabled": False},
    }

if "alert_settings" not in st.session_state:
    st.session_state.alert_settings = {
        "email": "",
        "sms": "",
        "enable_email": False,
        "enable_sms": False,
        "alert_on_dividend_drop": True,
        "alert_on_price_drop": True,
        "alert_on_news": True,
        "alert_frequency": "immediate"
    }

if "autopilot" not in st.session_state:
    st.session_state.autopilot = {
        "enabled": False,
        "auto_rebalance": False,
        "risk_tolerance": "moderate",
        "max_action_size": 10.0,
        "require_approval": True
    }

if "news_cache" not in st.session_state:
    st.session_state.news_cache = {
        "last_update": None,
        "articles": [],
        "sentiment_score": 0
    }

if "recommendations" not in st.session_state:
    st.session_state.recommendations = []

# =====================================================
# SIDEBAR - AI CONTROL CENTER
# =====================================================
with st.sidebar:
    st.title("⚙️ AI Control Center")
    
    st.subheader("🤖 AI Autopilot")
    st.session_state.autopilot["enabled"] = st.toggle(
        "Enable AI Autopilot",
        value=st.session_state.autopilot["enabled"],
        help="AI will monitor your portfolio 24/7 and provide real-time recommendations"
    )
    
    if st.session_state.autopilot["enabled"]:
        st.markdown('<div class="autopilot-active">✓ AUTOPILOT ACTIVE</div>', unsafe_allow_html=True)
        
        st.session_state.autopilot["risk_tolerance"] = st.select_slider(
            "Risk Tolerance",
            options=["conservative", "moderate", "aggressive"],
            value=st.session_state.autopilot["risk_tolerance"]
        )
        
        st.session_state.autopilot["require_approval"] = st.checkbox(
            "Require approval for actions",
            value=st.session_state.autopilot["require_approval"]
        )
        
        st.session_state.autopilot["auto_rebalance"] = st.checkbox(
            "Auto-rebalance when needed",
            value=st.session_state.autopilot["auto_rebalance"]
        )
    
    st.divider()
    
    st.subheader("📧 Alert Settings")
    st.session_state.alert_settings["enable_email"] = st.checkbox(
        "Enable Email Alerts",
        value=st.session_state.alert_settings["enable_email"]
    )
    
    if st.session_state.alert_settings["enable_email"]:
        st.session_state.alert_settings["email"] = st.text_input(
            "Email Address",
            value=st.session_state.alert_settings["email"],
            placeholder="your@email.com"
        )
    
    st.session_state.alert_settings["enable_sms"] = st.checkbox(
        "Enable SMS Alerts",
        value=st.session_state.alert_settings["enable_sms"]
    )
    
    if st.session_state.alert_settings["enable_sms"]:
        st.session_state.alert_settings["sms"] = st.text_input(
            "Phone Number",
            value=st.session_state.alert_settings["sms"],
            placeholder="+1234567890"
        )
    
    st.divider()
    
    st.subheader("🎯 Price Alerts")
    for ticker in ETF_LIST:
        with st.expander(f"{ticker} Alerts"):
            st.session_state.price_alerts[ticker]["enabled"] = st.checkbox(
                f"Enable {ticker} alerts",
                value=st.session_state.price_alerts[ticker]["enabled"],
                key=f"alert_enable_{ticker}"
            )
            
            if st.session_state.price_alerts[ticker]["enabled"]:
                st.session_state.price_alerts[ticker]["stop_loss_pct"] = st.slider(
                    "Stop Loss %",
                    min_value=5,
                    max_value=50,
                    value=st.session_state.price_alerts[ticker]["stop_loss_pct"],
                    key=f"stop_loss_{ticker}"
                )
                
                current_price = get_price(ticker)
                st.session_state.price_alerts[ticker]["target_price"] = st.number_input(
                    "Target Price ($)",
                    min_value=0.0,
                    value=st.session_state.price_alerts[ticker]["target_price"] or 0.0,
                    step=0.50,
                    key=f"target_{ticker}"
                )
                
                if st.session_state.price_alerts[ticker]["target_price"]:
                    if current_price:
                        st.caption(f"Current: ${current_price:.2f}")
                    else:
                        st.caption("Current: N/A")

# =====================================================
# MAIN HEADER
# =====================================================
st.title("💼 Income Strategy Engine - AI Powered")

col1, col2, col3 = st.columns([2, 1, 1])
with col1:
    st.markdown("**AI-powered dividend portfolio with real-time intelligence & safety monitoring**")
with col2:
    # Validate portfolio
    validation_errors = []
    for ticker in ETF_LIST:
        if st.session_state.holdings[ticker]["shares"] < 0:
            validation_errors.append(f"{ticker}: Invalid shares")
        if st.session_state.holdings[ticker]["div"] < 0:
            validation_errors.append(f"{ticker}: Invalid dividend")
    
    if validation_errors:
        st.session_state.PORTFOLIO_LOCKED = False
        st.markdown('<div class="status-unlocked">🔴 Portfolio Unlocked</div>', unsafe_allow_html=True)
    else:
        st.session_state.PORTFOLIO_LOCKED = True
        st.markdown('<div class="status-locked">🟢 Portfolio Locked</div>', unsafe_allow_html=True)

with col3:
    if st.session_state.autopilot["enabled"]:
        st.markdown('<div class="autopilot-active">🤖 AI ACTIVE</div>', unsafe_allow_html=True)

st.divider()

# =====================================================
# TABS
# =====================================================
tab1, tab2, tab3, tab4, tab5, tab6, tab7, tab8, tab9 = st.tabs([
    "🎯 AI Command Center",
    "💡 Weekly Advisor",
    "📊 Dashboard",
    "🛡️ Safety Monitor",
    "📰 News & Intelligence",
    "🚀 Compound Projections",
    "📁 Portfolio Editor",
    "📈 Performance Tracking",
    "📸 Snapshots"
])

with tab1:
    ai_command_center.render()

with tab2:
    weekly_advisor.render()

with tab3:
    dashboard.render()

with tab4:
    safety_monitor.render()

with tab5:
    news_intelligence.render()

with tab6:
    compound_projections.render()

with tab7:
    portfolio_editor.render()

with tab8:
    performance_tracking.render()

with tab9:
    snapshots.render()

st.divider()
st.caption("Income Strategy Engine v4.0 - AI Powered Edition • " + datetime.now().strftime("%b %d, %Y %I:%M %p"))
