import streamlit as st
import pandas as pd
import yfinance as yf
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timedelta
import numpy as np
import json
from collections import defaultdict
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# =====================================================
# CONFIG
# =====================================================
st.set_page_config(
    page_title="Income Strategy Engine - AI Powered",
    layout="wide",
    initial_sidebar_state="expanded"
)

# =====================================================
# CUSTOM CSS - MOBILE FRIENDLY
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
        
        /* Make columns stack on mobile */
        [data-testid="column"] {
            width: 100% !important;
            flex: 100% !important;
            max-width: 100% !important;
        }
        
        /* Adjust button sizes */
        .stButton > button {
            width: 100%;
            font-size: 0.9rem !important;
        }
        
        /* Adjust input fields */
        input {
            font-size: 0.9rem !important;
        }
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
        word-wrap: break-word;
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
        word-wrap: break-word;
    }
    
    /* Mobile adjustments for status badges */
    @media (max-width: 768px) {
        .status-locked, .status-unlocked {
            font-size: 0.75rem;
            padding: 0.4rem 0.8rem;
        }
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
    
    /* Mobile risk scores */
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
        word-wrap: break-word;
        overflow-wrap: break-word;
    }
    
    .alert-warning {
        background: rgba(234, 179, 8, 0.15);
        border-left: 4px solid #eab308;
        padding: 1.25rem;
        border-radius: 0.75rem;
        margin: 1rem 0;
        word-wrap: break-word;
        overflow-wrap: break-word;
    }
    
    .alert-info {
        background: rgba(59, 130, 246, 0.15);
        border-left: 4px solid #3b82f6;
        padding: 1.25rem;
        border-radius: 0.75rem;
        margin: 1rem 0;
        word-wrap: break-word;
        overflow-wrap: break-word;
    }
    
    .alert-success {
        background: rgba(34, 197, 94, 0.15);
        border-left: 4px solid #22c55e;
        padding: 1.25rem;
        border-radius: 0.75rem;
        margin: 1rem 0;
        word-wrap: break-word;
        overflow-wrap: break-word;
    }
    
    /* Mobile alerts */
    @media (max-width: 768px) {
        .alert-critical, .alert-warning, .alert-info, .alert-success {
            padding: 1rem;
            font-size: 0.85rem;
        }
    }
    
    .news-card {
        background: #1e293b;
        border-radius: 0.75rem;
        padding: 1.25rem;
        margin-bottom: 1rem;
        border: 1px solid #334155;
        transition: all 0.3s;
        word-wrap: break-word;
        overflow-wrap: break-word;
    }
    
    .news-card:hover {
        border-color: #3b82f6;
        transform: translateY(-2px);
    }
    
    /* Mobile news cards */
    @media (max-width: 768px) {
        .news-card {
            padding: 1rem;
            font-size: 0.85rem;
        }
        .news-card:hover {
            transform: none;
        }
    }
    
    .sentiment-positive {
        color: #22c55e;
        font-weight: 700;
        word-wrap: break-word;
    }
    
    .sentiment-negative {
        color: #ef4444;
        font-weight: 700;
        word-wrap: break-word;
    }
    
    .sentiment-neutral {
        color: #94a3b8;
        font-weight: 700;
        word-wrap: break-word;
    }
    
    .action-button {
        background: linear-gradient(135deg, #3b82f6 0%, #8b5cf6 100%);
        color: white;
        padding: 0.75rem 1.5rem;
        border-radius: 0.5rem;
        font-weight: 600;
        border: none;
        cursor: pointer;
        transition: all 0.3s;
    }
    
    .action-button:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 24px rgba(59, 130, 246, 0.3);
    }
    
    /* Mobile buttons */
    @media (max-width: 768px) {
        .action-button {
            padding: 0.6rem 1rem;
            font-size: 0.85rem;
        }
        .action-button:hover {
            transform: none;
        }
    }
    
    /* Ensure all text wraps properly on mobile */
    @media (max-width: 768px) {
        * {
            word-wrap: break-word !important;
            overflow-wrap: break-word !important;
        }
        
        /* Prevent horizontal scroll */
        body {
            overflow-x: hidden !important;
        }
        
        .main .block-container {
            padding-left: 0.5rem !important;
            padding-right: 0.5rem !important;
            max-width: 100% !important;
        }
        
        /* Make tables scrollable on mobile */
        [data-testid="stDataFrame"] {
            overflow-x: auto !important;
        }
        
        /* Stack metrics vertically on mobile */
        [data-testid="stHorizontalBlock"] {
            flex-direction: column !important;
        }
        
        /* Adjust tabs for mobile */
        [data-testid="stTabs"] {
            overflow-x: auto !important;
        }
    }
    
    .autopilot-active {
        background: linear-gradient(90deg, #059669 0%, #10b981 100%);
        color: white;
        padding: 0.75rem 1.5rem;
        border-radius: 0.5rem;
        font-weight: 600;
        display: inline-block;
        animation: pulse 2s infinite;
        font-size: 0.9rem;
    }
    
    @keyframes pulse {
        0%, 100% { opacity: 1; }
        50% { opacity: 0.7; }
    }
    
    /* Mobile autopilot */
    @media (max-width: 768px) {
        .autopilot-active {
            font-size: 0.75rem;
            padding: 0.5rem 1rem;
        }
    }
</style>
""", unsafe_allow_html=True)

ETF_LIST = ["QDTE", "CHPY", "XDTE"]

# ETF underlying info
ETF_INFO = {
    "QDTE": {
        "name": "NASDAQ-100 0DTE Covered Call ETF",
        "underlying_index": "NASDAQ-100",
        "top_holdings": ["AAPL", "MSFT", "NVDA", "GOOGL", "AMZN"],
        "strategy": "0DTE covered calls on QQQ",
        "risk_level": "Medium-High"
    },
    "CHPY": {
        "name": "T-Rex 2X Long Nvidia Daily Target ETF",
        "underlying_index": "Technology Sector",
        "top_holdings": ["NVDA"],
        "strategy": "2x leveraged NVDA with covered calls",
        "risk_level": "High"
    },
    "XDTE": {
        "name": "S&P 500 0DTE Covered Call ETF",
        "underlying_index": "S&P 500",
        "top_holdings": ["AAPL", "MSFT", "NVDA", "AMZN", "GOOGL"],
        "strategy": "0DTE covered calls on SPY",
        "risk_level": "Medium"
    }
}

# =====================================================
# SESSION STATE - ENHANCED
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

# NEW: Dividend history tracking
if "dividend_history" not in st.session_state:
    st.session_state.dividend_history = defaultdict(list)
    # Initialize with some sample data
    for ticker in ETF_LIST:
        current_div = st.session_state.holdings[ticker]["div"]
        for i in range(12):  # Last 12 weeks
            variation = np.random.uniform(-0.02, 0.02)
            st.session_state.dividend_history[ticker].append({
                "date": datetime.now() - timedelta(weeks=12-i),
                "dividend": current_div + (current_div * variation),
                "verified": True
            })

# NEW: Price alerts
if "price_alerts" not in st.session_state:
    st.session_state.price_alerts = {
        "QDTE": {"stop_loss_pct": 20, "target_price": None, "enabled": False},
        "CHPY": {"stop_loss_pct": 20, "target_price": None, "enabled": False},
        "XDTE": {"stop_loss_pct": 20, "target_price": None, "enabled": False},
    }

# NEW: Alert settings
if "alert_settings" not in st.session_state:
    st.session_state.alert_settings = {
        "email": "",
        "sms": "",
        "enable_email": False,
        "enable_sms": False,
        "alert_on_dividend_drop": True,
        "alert_on_price_drop": True,
        "alert_on_news": True,
        "alert_frequency": "immediate"  # immediate, daily, weekly
    }

# NEW: AI Autopilot settings
if "autopilot" not in st.session_state:
    st.session_state.autopilot = {
        "enabled": False,
        "auto_rebalance": False,
        "risk_tolerance": "moderate",  # conservative, moderate, aggressive
        "max_action_size": 10.0,  # max % of portfolio to change at once
        "require_approval": True
    }

# NEW: News cache
if "news_cache" not in st.session_state:
    st.session_state.news_cache = {
        "last_update": None,
        "articles": [],
        "sentiment_score": 0
    }

# NEW: Recommendations queue
if "recommendations" not in st.session_state:
    st.session_state.recommendations = []

# =====================================================
# HELPER FUNCTIONS - ENHANCED
# =====================================================

@st.cache_data(ttl=600)
def get_price(ticker):
    try:
        stock = yf.Ticker(ticker)

        # Try intraday first
        hist = stock.history(period="1d", interval="1m")
        if not hist.empty:
            return round(hist["Close"].iloc[-1], 2)

        # Fallback to daily
        hist = stock.history(period="5d")
        if not hist.empty:
            return round(hist["Close"].iloc[-1], 2)

        # Fallback to fast_info
        if hasattr(stock, "fast_info"):
            price = stock.fast_info.get("last_price")
            if price:
                return round(price, 2)

        return None
    except:
        return None


@st.cache_data(ttl=3600)
def get_etf_info(ticker):
    """Get ETF information"""
    try:
        stock = yf.Ticker(ticker)
        info = stock.info
        return {
            "name": info.get("longName", ticker),
            "description": info.get("longBusinessSummary", "No description available"),
            "yield": info.get("yield", 0) * 100 if info.get("yield") else 0,
            "nav": info.get("navPrice", 0),
            "volume": info.get("volume", 0),
            "avg_volume": info.get("averageVolume", 0)
        }
    except:
        return {"name": ticker, "description": "Information unavailable", "yield": 0, "nav": 0}

@st.cache_data(ttl=3600)
def get_price_history(ticker, period="3mo"):
    """Get historical price data"""
    try:
        stock = yf.Ticker(ticker)
        hist = stock.history(period=period)
        return hist
    except:
        return pd.DataFrame()

def calculate_current_metrics():
    """Calculate current portfolio metrics"""
    prices = {t: get_price(t) for t in ETF_LIST}
    
    total_weekly = 0
    total_value = 0
    total_cost_basis = 0
    holdings_data = []
    
    for ticker in ETF_LIST:
        shares = st.session_state.holdings[ticker]["shares"]
        div = st.session_state.holdings[ticker]["div"]
        price = prices[ticker]
        cost_basis = st.session_state.holdings[ticker].get("cost_basis", price)
        
        weekly = shares * div
        monthly = weekly * 52 / 12
        annual = weekly * 52
        value = shares * price
        yield_pct = (annual / value * 100) if value > 0 else 0
        
        # Calculate gain/loss
        cost_total = shares * cost_basis
        gain_loss = value - cost_total
        gain_loss_pct = ((value / cost_total) - 1) * 100 if cost_total > 0 else 0
        
        total_weekly += weekly
        total_value += value
        total_cost_basis += cost_total
        
        holdings_data.append({
            "ticker": ticker,
            "shares": shares,
            "div": div,
            "price": price,
            "weekly": weekly,
            "monthly": monthly,
            "annual": annual,
            "value": value,
            "yield_pct": yield_pct,
            "cost_basis": cost_basis,
            "gain_loss": gain_loss,
            "gain_loss_pct": gain_loss_pct
        })
    
    total_value += st.session_state.cash
    monthly_income = total_weekly * 52 / 12
    annual_income = monthly_income * 12
    total_yield = (annual_income / total_value * 100) if total_value > 0 else 0
    total_gain_loss = total_value - total_cost_basis - st.session_state.cash
    total_gain_loss_pct = ((total_value / (total_cost_basis + st.session_state.cash)) - 1) * 100 if (total_cost_basis + st.session_state.cash) > 0 else 0
    
    return {
        "holdings": holdings_data,
        "prices": prices,
        "total_weekly": total_weekly,
        "monthly_income": monthly_income,
        "annual_income": annual_income,
        "total_value": total_value,
        "total_yield": total_yield,
        "total_gain_loss": total_gain_loss,
        "total_gain_loss_pct": total_gain_loss_pct
    }

def check_price_alerts():
    """Check if any price alerts should trigger"""
    alerts = []
    metrics = calculate_current_metrics()
    
    for holding in metrics["holdings"]:
        ticker = holding["ticker"]
        price = holding["price"]
        cost_basis = holding["cost_basis"]
        
        if st.session_state.price_alerts[ticker]["enabled"]:
            # Stop loss check
            stop_loss_pct = st.session_state.price_alerts[ticker]["stop_loss_pct"]
            loss_from_basis = ((price / cost_basis) - 1) * 100
            
            if loss_from_basis <= -stop_loss_pct:
                alerts.append({
                    "ticker": ticker,
                    "type": "stop_loss",
                    "severity": "critical",
                    "message": f"🚨 STOP LOSS TRIGGERED: {ticker} down {abs(loss_from_basis):.1f}% from cost basis",
                    "action": f"Consider selling {ticker} to limit losses",
                    "price": price,
                    "threshold": cost_basis * (1 - stop_loss_pct/100)
                })
            
            # Target price check
            target = st.session_state.price_alerts[ticker]["target_price"]
            if target and price >= target:
                alerts.append({
                    "ticker": ticker,
                    "type": "target_reached",
                    "severity": "success",
                    "message": f"🎯 TARGET REACHED: {ticker} hit ${price:.2f}",
                    "action": f"Consider taking profits on {ticker}",
                    "price": price,
                    "threshold": target
                })
    
    return alerts

def analyze_dividend_trends():
    """Analyze dividend payment trends"""
    alerts = []
    
    for ticker in ETF_LIST:
        history = st.session_state.dividend_history[ticker]
        if len(history) < 4:
            continue
        
        # Get last 4 weeks
        recent = history[-4:]
        recent_avg = np.mean([d["dividend"] for d in recent])
        
        # Get previous 4 weeks
        previous = history[-8:-4] if len(history) >= 8 else history[:-4]
        if not previous:
            continue
        previous_avg = np.mean([d["dividend"] for d in previous])
        
        # Calculate change
        change_pct = ((recent_avg / previous_avg) - 1) * 100 if previous_avg > 0 else 0
        
        if change_pct < -st.session_state.dividend_drop_threshold:
            alerts.append({
                "ticker": ticker,
                "type": "dividend_drop",
                "severity": "critical",
                "change_pct": change_pct,
                "current_avg": recent_avg,
                "previous_avg": previous_avg,
                "message": f"🚨 DIVIDEND DROP: {ticker} dividend decreased {abs(change_pct):.1f}% over last 4 weeks",
                "action": f"Review {ticker} position - consider reducing exposure"
            })
        elif change_pct < -5:
            alerts.append({
                "ticker": ticker,
                "type": "dividend_decline",
                "severity": "warning",
                "change_pct": change_pct,
                "current_avg": recent_avg,
                "previous_avg": previous_avg,
                "message": f"⚠️ DIVIDEND DECLINE: {ticker} dividend down {abs(change_pct):.1f}%",
                "action": f"Monitor {ticker} closely for further declines"
            })
        elif change_pct > 10:
            alerts.append({
                "ticker": ticker,
                "type": "dividend_increase",
                "severity": "success",
                "change_pct": change_pct,
                "current_avg": recent_avg,
                "previous_avg": previous_avg,
                "message": f"✅ DIVIDEND INCREASE: {ticker} dividend up {change_pct:.1f}%",
                "action": f"Consider increasing {ticker} position"
            })
    
    return alerts

def calculate_portfolio_risk_score():
    """Calculate comprehensive portfolio risk score (0-100)"""
    metrics = calculate_current_metrics()
    scores = {}
    
    # 1. Diversification score (0-20 points)
    values = [h["value"] for h in metrics["holdings"]]
    total = sum(values)
    if total > 0:
        concentrations = [v/total for v in values]
        max_concentration = max(concentrations)
        # Perfect = 33% each, worst = 100% in one
        diversification_score = 20 * (1 - (max_concentration - 0.33) / 0.67) if max_concentration > 0.33 else 20
    else:
        diversification_score = 0
    scores["diversification"] = max(0, min(20, diversification_score))
    
    # 2. Dividend stability score (0-25 points)
    div_alerts = analyze_dividend_trends()
    critical_div_alerts = [a for a in div_alerts if a["severity"] == "critical"]
    warning_div_alerts = [a for a in div_alerts if a["severity"] == "warning"]
    dividend_stability = 25 - (len(critical_div_alerts) * 10) - (len(warning_div_alerts) * 5)
    scores["dividend_stability"] = max(0, min(25, dividend_stability))
    
    # 3. Price performance score (0-20 points)
    # Check if holdings are in profit or loss
    avg_gain_loss_pct = np.mean([h["gain_loss_pct"] for h in metrics["holdings"]])
    if avg_gain_loss_pct >= 10:
        price_score = 20
    elif avg_gain_loss_pct >= 0:
        price_score = 15
    elif avg_gain_loss_pct >= -10:
        price_score = 10
    elif avg_gain_loss_pct >= -20:
        price_score = 5
    else:
        price_score = 0
    scores["price_performance"] = price_score
    
    # 4. Yield sustainability score (0-20 points)
    # Very high yields (>100%) are risky
    avg_yield = np.mean([h["yield_pct"] for h in metrics["holdings"]])
    if avg_yield > 150:
        yield_score = 5
    elif avg_yield > 100:
        yield_score = 10
    elif avg_yield > 50:
        yield_score = 15
    else:
        yield_score = 20
    scores["yield_sustainability"] = yield_score
    
    # 5. Risk exposure score (0-15 points)
    # Based on ETF risk levels
    risk_weights = {"Low": 1, "Medium": 2, "Medium-High": 3, "High": 4}
    weighted_risk = 0
    for holding in metrics["holdings"]:
        ticker = holding["ticker"]
        weight = holding["value"] / metrics["total_value"] if metrics["total_value"] > 0 else 0
        etf_risk = ETF_INFO[ticker]["risk_level"]
        risk_level = risk_weights.get(etf_risk, 2)
        weighted_risk += weight * risk_level
    
    # Lower weighted risk = higher score
    risk_score = 15 * (1 - (weighted_risk - 1) / 3)
    scores["risk_exposure"] = max(0, min(15, risk_score))
    
    # Total score
    total_score = sum(scores.values())
    
    # Determine risk level
    if total_score >= 80:
        risk_level = "LOW"
        risk_class = "risk-score-low"
        risk_color = "#22c55e"
    elif total_score >= 60:
        risk_level = "MODERATE"
        risk_class = "risk-score-medium"
        risk_color = "#f59e0b"
    else:
        risk_level = "HIGH"
        risk_class = "risk-score-high"
        risk_color = "#ef4444"
    
    return {
        "total_score": round(total_score, 1),
        "risk_level": risk_level,
        "risk_class": risk_class,
        "risk_color": risk_color,
        "scores": scores
    }

def generate_rebalance_recommendation(metrics, risk_score):
    """Generate intelligent rebalancing recommendation"""
    recommendations = []
    
    # Check concentration
    for holding in metrics["holdings"]:
        concentration = (holding["value"] / metrics["total_value"]) * 100 if metrics["total_value"] > 0 else 0
        
        if concentration > 50:
            # Find best alternative
            other_tickers = [t for t in ETF_LIST if t != holding["ticker"]]
            
            # Calculate how much to sell and buy
            target_concentration = 40  # Reduce to 40%
            shares_to_sell = int(holding["shares"] * (concentration - target_concentration) / concentration)
            proceeds = shares_to_sell * holding["price"]
            
            # Split between other ETFs
            for other_ticker in other_tickers:
                other_price = metrics["prices"][other_ticker]
                shares_to_buy = int((proceeds / len(other_tickers)) / other_price)
                other_div = st.session_state.holdings[other_ticker]["div"]
                
                income_lost = shares_to_sell * holding["div"] * 52
                income_gained = shares_to_buy * other_div * 52
                net_income_change = income_gained - (income_lost / len(other_tickers))
                
                recommendations.append({
                    "type": "rebalance",
                    "severity": "warning",
                    "reason": f"Reduce {holding['ticker']} concentration from {concentration:.1f}%",
                    "action": {
                        "sell": {"ticker": holding["ticker"], "shares": shares_to_sell, "proceeds": proceeds},
                        "buy": {"ticker": other_ticker, "shares": shares_to_buy, "cost": shares_to_buy * other_price},
                        "income_impact": net_income_change
                    },
                    "message": f"Sell {shares_to_sell} shares of {holding['ticker']} → Buy {shares_to_buy} shares of {other_ticker}"
                })
    
    return recommendations

def analyze_sentiment_from_title(title):
    """
    Enhanced sentiment analysis based on keywords and patterns
    """
    title_lower = title.lower()
    
    # Extended keyword lists with weights
    positive_words = {
        'surge': 2, 'soar': 2, 'rally': 2, 'jump': 2, 'boom': 2,
        'gain': 1.5, 'rise': 1.5, 'climb': 1.5, 'advance': 1.5,
        'beat': 1.5, 'exceed': 1.5, 'outperform': 1.5,
        'strong': 1, 'growth': 1, 'profit': 1, 'bullish': 1.5,
        'upgrade': 1.5, 'record': 1.5, 'high': 1, 'boost': 1,
        'positive': 1, 'win': 1, 'success': 1, 'breakthrough': 1.5,
        'optimistic': 1, 'confident': 1
    }
    
    negative_words = {
        'crash': 2, 'plunge': 2, 'collapse': 2, 'tumble': 2,
        'fall': 1.5, 'drop': 1.5, 'decline': 1.5, 'sink': 1.5,
        'loss': 1.5, 'miss': 1.5, 'weak': 1, 'bearish': 1.5,
        'downgrade': 1.5, 'concern': 1, 'worry': 1, 'risk': 1,
        'threat': 1.5, 'negative': 1, 'cut': 1.5, 'slash': 1.5,
        'warning': 1, 'crisis': 2, 'trouble': 1.5, 'struggle': 1.5,
        'disappointing': 1, 'uncertain': 1
    }
    
    positive_score = sum(weight for word, weight in positive_words.items() if word in title_lower)
    negative_score = sum(weight for word, weight in negative_words.items() if word in title_lower)
    
    # Normalize to [-1, 1]
    if positive_score + negative_score == 0:
        return 0
    
    net_score = (positive_score - negative_score) / (positive_score + negative_score)
    
    # Apply damping to avoid extreme values
    return net_score * 0.8

@st.cache_data(ttl=1800)  # Cache for 30 minutes
def fetch_real_news_sentiment(ticker=None):
    """
    Fetch real news and perform sentiment analysis
    Searches: ETFs, underlying stocks, and connected markets
    Uses yfinance news API which aggregates from multiple sources
    """
    articles = []
    sentiment_scores = {}
    
    try:
        tickers_to_search = [ticker] if ticker else ETF_LIST
        
        for t in tickers_to_search:
            ticker_articles = []
            ticker_sentiments = []
            
            # 1. ETF news via yfinance (aggregates from Yahoo Finance, which pulls from Reuters, Bloomberg, etc.)
            try:
                stock = yf.Ticker(t)
                if hasattr(stock, 'news') and stock.news:
                    for item in stock.news[:2]:  # Top 2 ETF articles
                        title = item.get('title', '')
                        if title:
                            sentiment = analyze_sentiment_from_title(title)
                            ticker_sentiments.append(sentiment)
                            
                            # Parse timestamp
                            pub_time = item.get('providerPublishTime', 0)
                            time_ago = "Recent"
                            if pub_time:
                                try:
                                    pub_date = datetime.fromtimestamp(pub_time)
                                    hours_ago = (datetime.now() - pub_date).total_seconds() / 3600
                                    if hours_ago < 1:
                                        time_ago = f"{int(hours_ago * 60)}m ago"
                                    elif hours_ago < 24:
                                        time_ago = f"{int(hours_ago)}h ago"
                                    else:
                                        time_ago = f"{int(hours_ago/24)}d ago"
                                except:
                                    time_ago = "Recent"
                            
                            ticker_articles.append({
                                "ticker": t,
                                "title": f"[{t} ETF] {title}",
                                "sentiment": "POSITIVE" if sentiment > 0.3 else "NEGATIVE" if sentiment < -0.3 else "NEUTRAL",
                                "sentiment_class": "sentiment-positive" if sentiment > 0.3 else "sentiment-negative" if sentiment < -0.3 else "sentiment-neutral",
                                "sentiment_score": sentiment,
                                "source": item.get('publisher', 'Financial News'),
                                "time": time_ago,
                                "summary": title[:200] + "..." if len(title) > 200 else title,
                                "link": item.get('link', '')
                            })
            except Exception:
                pass
            
            # 2. Underlying stocks news (weighted 0.7 since indirect)
            underlying_stocks = ETF_INFO[t]["top_holdings"]
            for stock_ticker in underlying_stocks[:2]:  # Top 2 holdings
                try:
                    stock = yf.Ticker(stock_ticker)
                    if hasattr(stock, 'news') and stock.news:
                        item = stock.news[0]
                        title = item.get('title', '')
                        if title:
                            sentiment = analyze_sentiment_from_title(title)
                            ticker_sentiments.append(sentiment * 0.7)  # Weighted lower
                            
                            pub_time = item.get('providerPublishTime', 0)
                            time_ago = "Recent"
                            if pub_time:
                                try:
                                    pub_date = datetime.fromtimestamp(pub_time)
                                    hours_ago = (datetime.now() - pub_date).total_seconds() / 3600
                                    time_ago = f"{int(hours_ago)}h ago" if hours_ago < 24 else f"{int(hours_ago/24)}d ago"
                                except:
                                    pass
                            
                            ticker_articles.append({
                                "ticker": f"{t} ({stock_ticker})",
                                "title": f"[{stock_ticker}] {title}",
                                "sentiment": "POSITIVE" if sentiment > 0.3 else "NEGATIVE" if sentiment < -0.3 else "NEUTRAL",
                                "sentiment_class": "sentiment-positive" if sentiment > 0.3 else "sentiment-negative" if sentiment < -0.3 else "sentiment-neutral",
                                "sentiment_score": sentiment,
                                "source": item.get('publisher', 'Financial News'),
                                "time": time_ago,
                                "summary": f"Holding in {t}: {title[:150]}" + ("..." if len(title) > 150 else ""),
                                "link": item.get('link', '')
                            })
                except Exception:
                    continue
            
            # 3. Market index news (weighted 0.5 since most indirect)
            underlying_index = ETF_INFO[t]["underlying_index"]
            index_ticker_map = {
                "NASDAQ-100": "QQQ",
                "S&P 500": "SPY",
                "Technology Sector": "XLK"
            }
            
            if underlying_index in index_ticker_map:
                index_ticker = index_ticker_map[underlying_index]
                try:
                    index = yf.Ticker(index_ticker)
                    if hasattr(index, 'news') and index.news:
                        item = index.news[0]
                        title = item.get('title', '')
                        if title:
                            sentiment = analyze_sentiment_from_title(title)
                            ticker_sentiments.append(sentiment * 0.5)  # Weighted even lower
                            
                            pub_time = item.get('providerPublishTime', 0)
                            time_ago = "Recent"
                            if pub_time:
                                try:
                                    pub_date = datetime.fromtimestamp(pub_time)
                                    hours_ago = (datetime.now() - pub_date).total_seconds() / 3600
                                    time_ago = f"{int(hours_ago)}h ago" if hours_ago < 24 else f"{int(hours_ago/24)}d ago"
                                except:
                                    pass
                            
                            ticker_articles.append({
                                "ticker": f"{t} (Market)",
                                "title": f"[{underlying_index}] {title}",
                                "sentiment": "POSITIVE" if sentiment > 0.3 else "NEGATIVE" if sentiment < -0.3 else "NEUTRAL",
                                "sentiment_class": "sentiment-positive" if sentiment > 0.3 else "sentiment-negative" if sentiment < -0.3 else "sentiment-neutral",
                                "sentiment_score": sentiment,
                                "source": item.get('publisher', 'Market News'),
                                "time": time_ago,
                                "summary": f"Market: {title[:150]}" + ("..." if len(title) > 150 else ""),
                                "link": item.get('link', '')
                            })
                except Exception:
                    pass
            
            # Calculate average sentiment for this ETF
            if ticker_sentiments:
                sentiment_scores[t] = np.mean(ticker_sentiments)
                articles.extend(ticker_articles)
            else:
                # No news found
                sentiment_scores[t] = 0
                articles.append({
                    "ticker": t,
                    "title": f"{t}: No Recent News Available",
                    "sentiment": "NEUTRAL",
                    "sentiment_class": "sentiment-neutral",
                    "sentiment_score": 0,
                    "source": "System",
                    "time": "N/A",
                    "summary": f"No news available for {t} or its holdings. Market data is still being tracked.",
                    "link": ""
                })
        
        # Calculate overall sentiment
        overall_sentiment = np.mean(list(sentiment_scores.values())) if sentiment_scores else 0
        
        return {
            "sentiment_scores": sentiment_scores,
            "overall_sentiment": overall_sentiment,
            "articles": articles[:15],  # Limit to 15 most recent
            "last_update": datetime.now()
        }
        
    except Exception as e:
        # If everything fails, return neutral sentiment
        return {
            "sentiment_scores": {t: 0 for t in ETF_LIST},
            "overall_sentiment": 0,
            "articles": [{
                "ticker": "SYSTEM",
                "title": "News service temporarily unavailable",
                "sentiment": "NEUTRAL",
                "sentiment_class": "sentiment-neutral",
                "sentiment_score": 0,
                "source": "System",
                "time": "Now",
                "summary": f"Unable to fetch news at this time. Please try again later.",
                "link": ""
            }],
            "last_update": datetime.now()
        }

def send_email_alert(subject, body, to_email):
    """
    Send email alert using SMTP
    Configure with your email provider
    """
    if not to_email or not st.session_state.alert_settings.get("enable_email"):
        return False
    
    try:
        # Email configuration
        # IMPORTANT: For production, use environment variables or Streamlit secrets
        # Don't hardcode credentials!
        
        # Check if email credentials are configured in Streamlit secrets
        if hasattr(st, 'secrets') and 'email' in st.secrets:
            smtp_server = st.secrets['email']['smtp_server']
            smtp_port = st.secrets['email']['smtp_port']
            sender_email = st.secrets['email']['sender_email']
            sender_password = st.secrets['email']['sender_password']
        else:
            # Fallback: Show configuration instructions
            st.warning("""
            📧 **Email alerts not configured**
            
            To enable email alerts:
            1. Create a `.streamlit/secrets.toml` file
            2. Add your email configuration:
            
            ```toml
            [email]
            smtp_server = "smtp.gmail.com"
            smtp_port = 587
            sender_email = "your-email@gmail.com"
            sender_password = "your-app-password"
            ```
            
            For Gmail, use an [App Password](https://support.google.com/accounts/answer/185833)
            """)
            return False
        
        # Create message
        message = MIMEMultipart()
        message["From"] = sender_email
        message["To"] = to_email
        message["Subject"] = subject
        
        # Add body
        message.attach(MIMEText(body, "html"))
        
        # Send email
        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.starttls()
            server.login(sender_email, sender_password)
            server.send_message(message)
        
        return True
        
    except Exception as e:
        st.error(f"Failed to send email: {str(e)}")
        return False

def send_sms_alert(message, to_phone):
    """
    Send SMS alert using Twilio or similar service
    """
    if not to_phone or not st.session_state.alert_settings.get("enable_sms"):
        return False
    
    try:
        # Check if SMS credentials are configured
        if hasattr(st, 'secrets') and 'sms' in st.secrets:
            # Twilio configuration
            from twilio.rest import Client
            
            account_sid = st.secrets['sms']['twilio_account_sid']
            auth_token = st.secrets['sms']['twilio_auth_token']
            from_phone = st.secrets['sms']['twilio_phone_number']
            
            client = Client(account_sid, auth_token)
            
            client.messages.create(
                body=message,
                from_=from_phone,
                to=to_phone
            )
            
            return True
        else:
            st.warning("""
            📱 **SMS alerts not configured**
            
            To enable SMS alerts:
            1. Sign up for [Twilio](https://www.twilio.com/)
            2. Add to `.streamlit/secrets.toml`:
            
            ```toml
            [sms]
            twilio_account_sid = "your_account_sid"
            twilio_auth_token = "your_auth_token"
            twilio_phone_number = "+1234567890"
            ```
            """)
            return False
            
    except ImportError:
        st.error("Twilio not installed. Run: pip install twilio")
        return False
    except Exception as e:
        st.error(f"Failed to send SMS: {str(e)}")
        return False

def trigger_alerts_if_needed():
    """
    Check all alert conditions and send notifications if needed
    """
    alerts_sent = []
    
    # Check dividend alerts
    div_alerts = analyze_dividend_trends()
    for alert in div_alerts:
        if alert["severity"] == "critical":
            subject = f"🚨 CRITICAL: {alert['ticker']} Alert"
            body = f"""
            <html>
            <body>
                <h2 style="color: #ef4444;">Critical Portfolio Alert</h2>
                <p><strong>{alert['message']}</strong></p>
                <p><strong>Recommendation:</strong> {alert['action']}</p>
                <p>Change: {alert.get('change_pct', 0):.1f}%</p>
                <hr>
                <p><em>Income Strategy Engine - AI Powered</em></p>
            </body>
            </html>
            """
            
            if st.session_state.alert_settings.get("enable_email"):
                email = st.session_state.alert_settings.get("email")
                if send_email_alert(subject, body, email):
                    alerts_sent.append(f"Email sent: {alert['ticker']}")
            
            if st.session_state.alert_settings.get("enable_sms"):
                phone = st.session_state.alert_settings.get("sms")
                sms_body = f"ALERT: {alert['message'][:100]}"
                if send_sms_alert(sms_body, phone):
                    alerts_sent.append(f"SMS sent: {alert['ticker']}")
    
    # Check price alerts
    price_alerts = check_price_alerts()
    for alert in price_alerts:
        if alert["type"] == "stop_loss":
            subject = f"🚨 STOP LOSS: {alert['ticker']}"
            body = f"""
            <html>
            <body>
                <h2 style="color: #ef4444;">Stop Loss Triggered</h2>
                <p><strong>{alert['message']}</strong></p>
                <p><strong>Action:</strong> {alert['action']}</p>
                <p>Current Price: ${alert['price']:.2f}</p>
                <hr>
                <p><em>Income Strategy Engine - AI Powered</em></p>
            </body>
            </html>
            """
            
            if st.session_state.alert_settings.get("enable_email"):
                email = st.session_state.alert_settings.get("email")
                if send_email_alert(subject, body, email):
                    alerts_sent.append(f"Email sent: Stop loss {alert['ticker']}")
    
    return alerts_sent

def generate_weekly_investment_recommendation():
    """
    Analyze all factors and recommend which ETF to invest in this week
    Returns detailed recommendation with reasoning
    """
    metrics = calculate_current_metrics()
    
    # Fetch real news sentiment
    try:
        news_data = fetch_real_news_sentiment()
    except Exception:
        # Fallback to neutral if news fails
        news_data = {
            "sentiment_scores": {t: 0 for t in ETF_LIST},
            "overall_sentiment": 0
        }
    
    # Get price history for trend analysis
    etf_scores = {}
    
    for ticker in ETF_LIST:
        score = 0
        factors = []
        warnings = []
        
        # Factor 1: News Sentiment (Weight: 30%)
        sentiment = news_data["sentiment_scores"].get(ticker, 0)
        sentiment_score = sentiment * 30
        score += sentiment_score
        
        if sentiment > 0.3:
            factors.append(f"✅ Positive news sentiment (+{sentiment_score:.1f} pts)")
        elif sentiment < -0.3:
            factors.append(f"❌ Negative news sentiment ({sentiment_score:.1f} pts)")
            warnings.append("Recent negative news coverage")
        else:
            factors.append(f"➖ Neutral news sentiment ({sentiment_score:.1f} pts)")
        
        # Factor 2: Price Trend (Weight: 25%)
        try:
            hist = get_price_history(ticker, period="1mo")
            if not hist.empty and len(hist) >= 5:
                recent_prices = hist['Close'].tail(5)
                price_change = ((recent_prices.iloc[-1] / recent_prices.iloc[0]) - 1) * 100
                
                # Contrarian approach: buying dips is good
                if price_change < -5:
                    trend_score = 25  # Great buying opportunity
                    factors.append(f"✅ Price dipped {abs(price_change):.1f}% - buying opportunity! (+25 pts)")
                elif price_change < -2:
                    trend_score = 20
                    factors.append(f"✅ Slight dip {abs(price_change):.1f}% - good entry (+20 pts)")
                elif price_change > 10:
                    trend_score = 5  # Expensive, maybe wait
                    factors.append(f"⚠️ Price up {price_change:.1f}% - expensive (+5 pts)")
                    warnings.append("Price near recent highs")
                else:
                    trend_score = 15  # Normal
                    factors.append(f"➖ Price stable {price_change:+.1f}% (+15 pts)")
                
                score += trend_score
            else:
                score += 15  # Default if no data
                factors.append("➖ Insufficient price data (+15 pts)")
        except:
            score += 15
            factors.append("➖ Could not analyze price trend (+15 pts)")
        
        # Factor 3: Dividend Stability (Weight: 20%)
        div_alerts = [a for a in analyze_dividend_trends() if a["ticker"] == ticker]
        
        if any(a["severity"] == "critical" for a in div_alerts):
            div_score = -10
            factors.append(f"🚨 Dividend dropping severely ({div_score} pts)")
            warnings.append("Critical dividend decline")
        elif any(a["severity"] == "warning" for a in div_alerts):
            div_score = 10
            factors.append(f"⚠️ Dividend declining moderately (+{div_score} pts)")
            warnings.append("Dividend showing weakness")
        elif any(a["type"] == "dividend_increase" for a in div_alerts):
            div_score = 25
            factors.append(f"✅ Dividend increasing! (+{div_score} pts)")
        else:
            div_score = 20
            factors.append(f"✅ Dividend stable (+{div_score} pts)")
        
        score += div_score
        
        # Factor 4: Current Yield (Weight: 15%)
        holding = next((h for h in metrics["holdings"] if h["ticker"] == ticker), None)
        if holding:
            yield_pct = holding["yield_pct"]
            
            if yield_pct > 80:
                yield_score = 15
                factors.append(f"✅ High annual yield {yield_pct:.1f}% (+{yield_score} pts)")
            elif yield_pct > 50:
                yield_score = 12
                factors.append(f"✅ Good annual yield {yield_pct:.1f}% (+{yield_score} pts)")
            elif yield_pct > 30:
                yield_score = 10
                factors.append(f"✅ Solid annual yield {yield_pct:.1f}% (+{yield_score} pts)")
            else:
                yield_score = 8
                factors.append(f"➖ Moderate annual yield {yield_pct:.1f}% (+{yield_score} pts)")
            
            score += yield_score
        
        # Factor 5: Portfolio Concentration (Weight: 10%)
        concentration = (holding["value"] / metrics["total_value"] * 100) if metrics["total_value"] > 0 else 0
        
        if concentration > 50:
            conc_score = -10
            factors.append(f"⚠️ Overweight {concentration:.1f}% ({conc_score} pts)")
            warnings.append(f"Already {concentration:.1f}% of portfolio - diversify")
        elif concentration > 40:
            conc_score = 0
            factors.append(f"⚠️ Near limit {concentration:.1f}% (0 pts)")
            warnings.append("Getting concentrated")
        elif concentration < 20:
            conc_score = 10
            factors.append(f"✅ Underweight {concentration:.1f}% - room to grow (+{conc_score} pts)")
        else:
            conc_score = 5
            factors.append(f"➖ Balanced {concentration:.1f}% (+{conc_score} pts)")
        
        score += conc_score
        
        # Factor 6: Risk Level (Weight: 10%)
        risk_level = ETF_INFO[ticker]["risk_level"]
        
        if risk_level == "High":
            risk_score = 5
            factors.append(f"⚠️ High risk level (+{risk_score} pts)")
        elif risk_level == "Medium-High":
            risk_score = 7
            factors.append(f"➖ Medium-high risk (+{risk_score} pts)")
        elif risk_level == "Medium":
            risk_score = 10
            factors.append(f"✅ Medium risk (+{risk_score} pts)")
        else:
            risk_score = 8
            factors.append(f"✅ Lower risk (+{risk_score} pts)")
        
        score += risk_score
        
        # Store results
        etf_scores[ticker] = {
            "total_score": round(score, 1),
            "factors": factors,
            "warnings": warnings,
            "sentiment": sentiment,
            "yield": holding["yield_pct"] if holding else 0,
            "concentration": concentration,
            "price": holding["price"] if holding else 0
        }
    
    # Find best option
    best_ticker = max(etf_scores.keys(), key=lambda t: etf_scores[t]["total_score"])
    best_score = etf_scores[best_ticker]
    
    # Generate recommendation confidence
    score_diff = best_score["total_score"] - sorted([s["total_score"] for s in etf_scores.values()])[-2]
    
    if score_diff > 20:
        confidence = "VERY HIGH"
        confidence_color = "#22c55e"
    elif score_diff > 10:
        confidence = "HIGH"
        confidence_color = "#10b981"
    elif score_diff > 5:
        confidence = "MODERATE"
        confidence_color = "#f59e0b"
    else:
        confidence = "LOW - Consider splitting investment"
        confidence_color = "#ef4444"
    
    return {
        "recommended_ticker": best_ticker,
        "confidence": confidence,
        "confidence_color": confidence_color,
        "all_scores": etf_scores,
        "reasoning": best_score["factors"],
        "warnings": best_score["warnings"],
        "alternative": sorted(etf_scores.keys(), key=lambda t: etf_scores[t]["total_score"])[-2]
    }

def generate_auto_rebalance_plan():
    """
    Generate automatic rebalancing plan based on current conditions
    """
    metrics = calculate_current_metrics()
    risk_score = calculate_portfolio_risk_score()
    
    rebalance_actions = []
    
    # Check if rebalancing is needed
    needs_rebalancing = False
    
    # Check 1: Concentration risk
    for holding in metrics["holdings"]:
        concentration = (holding["value"] / metrics["total_value"] * 100) if metrics["total_value"] > 0 else 0
        
        if concentration > 45:
            needs_rebalancing = True
            
            # Calculate how much to sell
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
    
    # Check 2: Weak performers with bad news
    weekly_rec = generate_weekly_investment_recommendation()
    
    for ticker, score_data in weekly_rec["all_scores"].items():
        if score_data["total_score"] < 40 and score_data["warnings"]:
            holding = next((h for h in metrics["holdings"] if h["ticker"] == ticker), None)
            
            if holding and holding["shares"] > 0:
                # Suggest reducing by 20%
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
        
        # Recommend buying the best performer
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
        else:  # BUY
            income_after += action["shares"] * div * 52 / 12
    
    income_change = income_after - income_before
    
    return {
        "needs_rebalancing": needs_rebalancing or len(rebalance_actions) > 0,
        "actions": rebalance_actions,
        "income_before": income_before,
        "income_after": income_after,
        "income_change": income_change,
        "risk_improvement": "Reduces concentration risk" if any(a["type"] == "SELL" for a in rebalance_actions) else "Maintains balance"
    }

def generate_ai_recommendations():
    """Generate AI-powered actionable recommendations"""
    recommendations = []
    metrics = calculate_current_metrics()
    risk_score = calculate_portfolio_risk_score()
    div_alerts = analyze_dividend_trends()
    price_alerts = check_price_alerts()
    
    # Fetch real news sentiment
    try:
        news_data = fetch_real_news_sentiment()
    except:
        news_data = {"sentiment_scores": {t: 0 for t in ETF_LIST}, "overall_sentiment": 0}
    
    # 1. Dividend-based recommendations
    for alert in div_alerts:
        if alert["severity"] == "critical":
            recommendations.append({
                "priority": "HIGH",
                "type": "dividend_action",
                "ticker": alert["ticker"],
                "title": f"🚨 Action Required: {alert['ticker']} Dividend Crisis",
                "description": alert["message"],
                "action": alert["action"],
                "impact": f"Potential income loss: ${abs(alert['change_pct']) * st.session_state.holdings[alert['ticker']]['shares'] * alert['current_avg'] * 52 / 100:.2f}/year",
                "confidence": 95
            })
    
    # 2. Price alert recommendations
    for alert in price_alerts:
        if alert["type"] == "stop_loss":
            recommendations.append({
                "priority": "CRITICAL",
                "type": "stop_loss",
                "ticker": alert["ticker"],
                "title": alert["message"],
                "description": alert["action"],
                "action": f"Sell {st.session_state.holdings[alert['ticker']]['shares']} shares at market price",
                "impact": f"Lock in loss of ${metrics['holdings'][[h['ticker'] for h in metrics['holdings']].index(alert['ticker'])]['gain_loss']:.2f}",
                "confidence": 100
            })
    
    # 3. News sentiment recommendations
    for ticker, sentiment in news_data["sentiment_scores"].items():
        if sentiment < -0.5:
            recommendations.append({
                "priority": "MEDIUM",
                "type": "news_sentiment",
                "ticker": ticker,
                "title": f"⚠️ Negative News Detected: {ticker}",
                "description": f"Recent news sentiment is strongly negative ({sentiment:.2f})",
                "action": f"Consider reducing {ticker} position by 20-30%",
                "impact": "Risk mitigation based on market sentiment",
                "confidence": 70
            })
        elif sentiment > 0.5:
            current_concentration = next((h["value"] / metrics["total_value"] * 100 for h in metrics["holdings"] if h["ticker"] == ticker), 0)
            if current_concentration < 40:
                recommendations.append({
                    "priority": "LOW",
                    "type": "news_sentiment",
                    "ticker": ticker,
                    "title": f"✅ Positive Outlook: {ticker}",
                    "description": f"Recent news sentiment is strongly positive ({sentiment:.2f})",
                    "action": f"Consider increasing {ticker} position",
                    "impact": "Potential for enhanced returns",
                    "confidence": 65
                })
    
    # 4. Risk-based recommendations
    if risk_score["total_score"] < 60:
        recommendations.append({
            "priority": "HIGH",
            "type": "risk_mitigation",
            "ticker": "PORTFOLIO",
            "title": "🛡️ Portfolio Risk Elevated",
            "description": f"Overall risk score is {risk_score['total_score']:.1f}/100 ({risk_score['risk_level']})",
            "action": "Review and rebalance portfolio to reduce risk exposure",
            "impact": "Improve portfolio stability and reduce downside risk",
            "confidence": 85
        })
    
    # 5. Income optimization
    if metrics["monthly_income"] < st.session_state.target_income:
        gap = st.session_state.target_income - metrics["monthly_income"]
        # Find best yielding ETF
        best_yield_holding = max(metrics["holdings"], key=lambda x: x["yield_pct"])
        shares_needed = int((gap * 12 / 52) / best_yield_holding["div"])
        cost = shares_needed * best_yield_holding["price"]
        
        if st.session_state.cash >= cost:
            recommendations.append({
                "priority": "MEDIUM",
                "type": "income_boost",
                "ticker": best_yield_holding["ticker"],
                "title": "💰 Income Opportunity Available",
                "description": f"You have ${st.session_state.cash:.2f} in cash and need ${gap:.2f}/month more income",
                "action": f"Buy {shares_needed} shares of {best_yield_holding['ticker']} (highest yield at {best_yield_holding['yield_pct']:.1f}%)",
                "impact": f"Close income gap by ${shares_needed * best_yield_holding['div'] * 52 / 12:.2f}/month",
                "confidence": 80
            })
    
    # Sort by priority
    priority_order = {"CRITICAL": 0, "HIGH": 1, "MEDIUM": 2, "LOW": 3}
    recommendations.sort(key=lambda x: priority_order[x["priority"]])
    
    return recommendations

# =====================================================
# SIDEBAR - AI AUTOPILOT & SETTINGS
# =====================================================
with st.sidebar:
    st.title("⚙️ AI Control Center")
    
    # Autopilot toggle
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
    
    # Alert settings
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
    
    # Price alert settings
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
                    st.caption(f"Current: ${current_price:.2f}")

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

# =====================================================
# TAB 1: AI COMMAND CENTER
# =====================================================
with tab1:
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

# =====================================================
# TAB 2: WEEKLY INVESTMENT ADVISOR
# =====================================================
with tab2:
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
        
        # Generate recommendation if not exists
        if "weekly_rec" not in st.session_state:
            with st.spinner("Analyzing markets..."):
                st.session_state.weekly_rec = generate_weekly_investment_recommendation()
        
        rec = st.session_state.weekly_rec
        
        # MAIN RECOMMENDATION
        st.markdown("---")
        
        # Create a nice container with border
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
        
        # Analysis breakdown - use Streamlit native
        st.markdown("**📊 Analysis Breakdown:**")
        for reason in rec['reasoning']:
            st.markdown(f"- {reason}")
        
        # Warnings
        if rec['warnings']:
            st.warning("**⚠️ Warnings:**")
            for warning in rec['warnings']:
                st.markdown(f"- {warning}")
        
        st.info(f"**Alternative option:** {rec['alternative']} (if diversifying this week)")
        
        # ALL SCORES COMPARISON
        st.divider()
        st.markdown("### 📊 All ETF Scores (This Week)")
        
        cols = st.columns(3)
        for idx, (ticker, score_data) in enumerate(sorted(rec["all_scores"].items(), key=lambda x: x[1]["total_score"], reverse=True)):
            with cols[idx]:
                # Determine rank
                rank_emoji = ["🥇", "🥈", "🥉"][idx]
                rank_color = ["#ffd700", "#c0c0c0", "#cd7f32"][idx]
                
                # Header
                st.markdown(f"""
                <div style="background: #1e293b; border-radius: 1rem; padding: 1.5rem; border: 2px solid {rank_color if idx == 0 else '#334155'}; text-align: center;">
                    <div style="font-size: 2rem;">{rank_emoji}</div>
                    <div style="font-size: 1.8rem; font-weight: 700; color: #3b82f6; margin: 0.5rem 0;">{ticker}</div>
                    <div style="font-size: 2.5rem; font-weight: 700; color: {rank_color if idx == 0 else '#94a3b8'};">
                        {score_data['total_score']}/100
                    </div>
                </div>
                """, unsafe_allow_html=True)
                
                # Factors - use native Streamlit
                st.markdown("**Factors:**")
                for factor in score_data['factors'][:4]:
                    st.caption(factor)
                
                st.caption("_Yield = annual dividend income / current market value_")
                
                # Warnings
                if score_data['warnings']:
                    st.warning(f"⚠️ {score_data['warnings'][0]}", icon="⚠️")
        
        # SUGGESTED INVESTMENT AMOUNTS
        st.divider()
        st.markdown("### 💰 Suggested Investment Amount")
        
        col1, col2 = st.columns(2)
        
        with col1:
            investment_amount = st.number_input(
                "How much are you investing this week?",
                min_value=0.0,
                value=st.session_state.monthly_deposit / 4.33,  # Monthly to weekly
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
        
        # AUTO-REBALANCER
        st.divider()
        st.markdown("### 🔄 Auto-Rebalancer Analysis")
        
        if st.button("🤖 Generate Rebalancing Plan", use_container_width=True):
            with st.spinner("Analyzing portfolio balance..."):
                st.session_state.rebalance_plan = generate_auto_rebalance_plan()
        
        if "rebalance_plan" in st.session_state:
            plan = st.session_state.rebalance_plan
            
            if plan["needs_rebalancing"]:
                st.warning(f"⚠️ Rebalancing recommended - Portfolio needs adjustment")
                
                # Show actions
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
                    else:  # BUY
                        st.markdown(f"""
                        <div style="background: rgba(34, 197, 94, 0.1); border-left: 4px solid #22c55e; padding: 1rem; border-radius: 0.5rem; margin-bottom: 0.5rem;">
                            <strong>📈 BUY {action['shares']} shares of {action['ticker']}</strong><br>
                            <em>Cost: ${action['cost']:.2f}</em><br>
                            <small>Reason: {action['reason']}</small>
                        </div>
                        """, unsafe_allow_html=True)
                
                # Show impact
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

# =====================================================
# TAB 3: DASHBOARD
# =====================================================
with tab3:
    if not st.session_state.PORTFOLIO_LOCKED:
        st.warning("⚠️ Fix validation errors to view dashboard")
    else:
        metrics = calculate_current_metrics()
        
        # KEY METRICS
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
            cash_pct = (st.session_state.cash / metrics['total_value'] * 100) if metrics['total_value'] > 0 else 0
            st.metric("Total Gain/Loss", f"${metrics['total_gain_loss']:,.0f}",
                     delta=f"{metrics['total_gain_loss_pct']:+.1f}%")
        
        st.divider()
        
        # GOAL PROGRESS
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
        
        # CHARTS
        st.subheader("Portfolio Analysis")
        col1, col2 = st.columns(2)
        
        with col1:
            # Income by holding
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
            # Portfolio allocation
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
        
        # HOLDINGS TABLE with P&L
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

# =====================================================
# TAB 4: SAFETY MONITOR
# =====================================================
with tab4:
    if not st.session_state.PORTFOLIO_LOCKED:
        st.warning("⚠️ Fix validation errors to view safety monitor")
    else:
        st.subheader("🛡️ Comprehensive Safety Analysis")
        
        col1, col2 = st.columns([1, 3])
        
        with col1:
            if st.button("🔍 Run Full Safety Check", type="primary", use_container_width=True):
                with st.spinner("Analyzing portfolio safety..."):
                    st.session_state.last_safety_check = datetime.now()
                    
                    # Trigger alerts if configured
                    if st.session_state.alert_settings.get("enable_email") or st.session_state.alert_settings.get("enable_sms"):
                        alerts_sent = trigger_alerts_if_needed()
                        if alerts_sent:
                            st.success(f"✅ Sent {len(alerts_sent)} alerts")
                            for alert in alerts_sent:
                                st.info(alert)
        
        with col2:
            if hasattr(st.session_state, 'last_safety_check'):
                st.info(f"Last check: {st.session_state.last_safety_check.strftime('%Y-%m-%d %H:%M:%S')}")
        
        # Get all alerts
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
            
            # Display alerts
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
        
        # Dividend History Charts
        st.subheader("📊 Dividend Trend Analysis")
        
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
            
            # Add average line
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
            
            # Stats
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

# =====================================================
# TAB 5: NEWS & INTELLIGENCE
# =====================================================
with tab5:
    if not st.session_state.PORTFOLIO_LOCKED:
        st.warning("⚠️ Fix validation errors to view news intelligence")
    else:
        st.subheader("📰 Real-Time News & Market Intelligence")
        
        st.info("ℹ️ **News Sources:** Searches news for (1) The ETF itself, (2) Underlying stocks (NVDA, AAPL, MSFT, etc.), and (3) Connected markets (NASDAQ-100, S&P 500, Tech Sector). This provides comprehensive market intelligence even for niche ETFs.")
        
        col1, col2 = st.columns([3, 1])
        
        with col1:
            selected_etf = st.selectbox("Select ETF for Deep Analysis", ["ALL"] + ETF_LIST)
        
        with col2:
            if st.button("🔄 Refresh News", type="primary", use_container_width=True):
                with st.spinner("Fetching latest news..."):
                    st.session_state.news_cache = fetch_real_news_sentiment()
                    st.success("News updated!")
        
        # Get news data
        if not st.session_state.news_cache.get("articles"):
            with st.spinner("Loading news..."):
                st.session_state.news_cache = fetch_real_news_sentiment()
        
        news_data = st.session_state.news_cache
        
        # Overall Sentiment Dashboard
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
            overall_pct = (overall + 1) / 2 * 100  # Convert from [-1,1] to [0,100]
            st.metric("Overall Score", f"{overall_pct:.0f}/100")
        
        st.divider()
        
        # News Articles
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
        
        # Underlying Holdings Monitor
        st.markdown("### Underlying Holdings Monitor")
        
        selected_for_underlying = st.selectbox(
            "Select ETF to view underlying stocks",
            ETF_LIST,
            key="underlying_select"
        )
        
        underlying_stocks = ETF_INFO[selected_for_underlying]["top_holdings"]
        
        st.info(f"**{selected_for_underlying}** tracks: {ETF_INFO[selected_for_underlying]['underlying_index']}")
        st.write(f"**Top Holdings:** {', '.join(underlying_stocks)}")

# =====================================================
# TAB 6: COMPOUND PROJECTIONS
# =====================================================
with tab6:
    st.subheader("🚀 Compound Growth Projections")
    
    if not st.session_state.PORTFOLIO_LOCKED:
        st.warning("⚠️ Fix validation errors to view projections")
    else:
        # Projection function
        def project_compound_growth():
            """Project portfolio growth with dividend reinvestment + monthly deposits"""
            current_metrics = calculate_current_metrics()
            target = st.session_state.target_income
            monthly_deposit = st.session_state.monthly_deposit
            
            # Starting values
            portfolio = {ticker: st.session_state.holdings[ticker]["shares"] for ticker in ETF_LIST}
            cash = st.session_state.cash
            
            # Track projection
            projection_data = []
            month = 0
            max_months = 360  # 30 years max
            
            while month < max_months:
                # Calculate current monthly income
                monthly_income = 0
                portfolio_value = cash
                
                for ticker in ETF_LIST:
                    shares = portfolio[ticker]
                    div = st.session_state.holdings[ticker]["div"]
                    price = current_metrics["prices"][ticker]
                    
                    weekly_income = shares * div
                    monthly_income += weekly_income * 52 / 12
                    portfolio_value += shares * price
                
                # Record projection point
                projection_data.append({
                    "month": month,
                    "portfolio_value": portfolio_value,
                    "monthly_income": monthly_income,
                    "portfolio": portfolio.copy()
                })
                
                # Check if target reached
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
                
                # Simulate one month of growth
                monthly_dividends = monthly_income
                available_cash = monthly_dividends + monthly_deposit
                
                # Reinvest proportionally
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
                    st.error(f"⚠️ Target of ${st.session_state.target_income:,.0f}/month not reachable within 30 years with current settings")
        
        # PROJECTION CHART
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
            
            # Final holdings breakdown
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

# =====================================================
# TAB 7: PORTFOLIO EDITOR
# =====================================================
with tab7:
    st.subheader("📁 Portfolio Editor")
    
    for ticker in ETF_LIST:
        price = get_price(ticker)
        
        st.markdown(f"""
        <div style="background: linear-gradient(135deg, #1e293b 0%, #0f172a 100%); border: 1px solid #334155; border-radius: 1rem; padding: 1.5rem; margin-bottom: 1rem;">
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 1rem; padding-bottom: 1rem; border-bottom: 1px solid #334155;">
                <div style="font-size: 1.8rem; font-weight: 700; color: #3b82f6;">{ticker}</div>
                <div style="font-size: 1.5rem; font-weight: 700; color: #22c55e;">${price:.2f}</div>
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
            st.session_state.holdings[ticker]["cost_basis"] = st.number_input(
                "Cost Basis per Share ($)",
                min_value=0.0,
                step=0.10,
                format="%.2f",
                value=st.session_state.holdings[ticker].get("cost_basis", price),
                key=f"cost_{ticker}_edit"
            )
        
        # Calculate and display metrics
        shares = st.session_state.holdings[ticker]["shares"]
        div = st.session_state.holdings[ticker]["div"]
        cost_basis = st.session_state.holdings[ticker].get("cost_basis", price)
        
        weekly = shares * div
        monthly = weekly * 52 / 12
        annual = weekly * 52
        value = shares * price
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
    
    # CASH
    st.subheader("💰 Cash Position")
    st.session_state.cash = st.number_input(
        "Cash Balance ($)",
        min_value=0.0,
        step=100.0,
        value=st.session_state.cash,
        key="cash_edit"
    )

# =====================================================
# TAB 8: PERFORMANCE TRACKING
# =====================================================
with tab8:
    st.subheader("📈 Performance Tracking")
    st.info("Track your portfolio performance over time with detailed metrics and charts.")
    
    if st.session_state.snapshots:
        st.success(f"You have {len(st.session_state.snapshots)} saved snapshots to analyze")
    else:
        st.warning("No snapshots yet. Save snapshots to track performance over time.")

# =====================================================
# TAB 9: SNAPSHOTS
# =====================================================
with tab9:
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

st.divider()
st.caption("Income Strategy Engine v4.0 - AI Powered Edition • " + datetime.now().strftime("%b %d, %Y %I:%M %p"))
