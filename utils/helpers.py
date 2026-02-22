"""
Helper functions for the Income Strategy Engine
This module contains all utility and calculation functions
"""

import streamlit as st
import pandas as pd
import yfinance as yf
import numpy as np
from datetime import datetime, timedelta
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart


# =====================================================
# CONSTANTS - Data used across modules
# =====================================================
ETF_LIST = ["QDTE", "CHPY", "XDTE"]

ETF_INFO = {
    "QDTE": {
        "name": "Invesco NASDAQ-100 Ex-Tech Equal Weight ETF",
        "risk_level": "Medium",
        "underlying_index": "NASDAQ-100",
        "top_holdings": ["AMAT", "COST", "AMZN"],
        "yield": 4.5
    },
    "CHPY": {
        "name": "Invesco S&P 500 Aristocrats 25 Equally Weighted ETF",
        "risk_level": "Medium",
        "underlying_index": "S&P 500",
        "top_holdings": ["JNJ", "PG", "KO"],
        "yield": 2.8
    },
    "XDTE": {
        "name": "Invesco S&P 500 Quality ETF",
        "risk_level": "Low",
        "underlying_index": "Technology Sector",
        "top_holdings": ["AAPL", "MSFT", "NVDA"],
        "yield": 1.5
    }
}


# =====================================================
# DATA FETCHING FUNCTIONS
# =====================================================

@st.cache_data(ttl=600)
def get_price(ticker):
    """Fetch current price for a ticker"""
    try:
        stock = yf.Ticker(ticker)
        hist = stock.history(period="1d", interval="1m")
        if not hist.empty:
            return round(hist["Close"].iloc[-1], 2)
        hist = stock.history(period="5d")
        if not hist.empty:
            return round(hist["Close"].iloc[-1], 2)
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


# =====================================================
# CALCULATION FUNCTIONS
# =====================================================

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
        cost_basis = st.session_state.holdings[ticker].get("cost_basis", 0.0)
        
        # Use fetched price, fallback to cost_basis if fetch failed, default to 0
        price = prices[ticker]
        if price is None:
            price = cost_basis if cost_basis > 0 else 0.0
        
        weekly = shares * div
        monthly = weekly * 52 / 12
        annual = weekly * 52
        value = shares * price
        yield_pct = (annual / value * 100) if value > 0 else 0
        
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
            # Skip if we don't have valid data
            if not price or not cost_basis or cost_basis <= 0:
                continue
                
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
        
        recent = history[-4:]
        recent_avg = np.mean([d["dividend"] for d in recent])
        
        previous = history[-8:-4] if len(history) >= 8 else history[:-4]
        if not previous:
            continue
        previous_avg = np.mean([d["dividend"] for d in previous])
        
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
    
    values = [h["value"] for h in metrics["holdings"]]
    total = sum(values)
    if total > 0:
        concentrations = [v/total for v in values]
        max_concentration = max(concentrations)
        diversification_score = 20 * (1 - (max_concentration - 0.33) / 0.67) if max_concentration > 0.33 else 20
    else:
        diversification_score = 0
    scores["diversification"] = max(0, min(20, diversification_score))
    
    div_alerts = analyze_dividend_trends()
    critical_div_alerts = [a for a in div_alerts if a["severity"] == "critical"]
    warning_div_alerts = [a for a in div_alerts if a["severity"] == "warning"]
    dividend_stability = 25 - (len(critical_div_alerts) * 10) - (len(warning_div_alerts) * 5)
    scores["dividend_stability"] = max(0, min(25, dividend_stability))
    
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
    
    risk_weights = {"Low": 1, "Medium": 2, "Medium-High": 3, "High": 4}
    weighted_risk = 0
    for holding in metrics["holdings"]:
        ticker = holding["ticker"]
        weight = holding["value"] / metrics["total_value"] if metrics["total_value"] > 0 else 0
        etf_risk = ETF_INFO[ticker]["risk_level"]
        risk_level = risk_weights.get(etf_risk, 2)
        weighted_risk += weight * risk_level
    
    risk_score = 15 * (1 - (weighted_risk - 1) / 3)
    scores["risk_exposure"] = max(0, min(15, risk_score))
    
    total_score = sum(scores.values())
    
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


# =====================================================
# NEWS & SENTIMENT FUNCTIONS
# =====================================================

def analyze_sentiment_from_title(title):
    """Enhanced sentiment analysis based on keywords and patterns"""
    title_lower = title.lower()
    
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
    
    if positive_score + negative_score == 0:
        return 0
    
    net_score = (positive_score - negative_score) / (positive_score + negative_score)
    return net_score * 0.8


@st.cache_data(ttl=1800)
def fetch_real_news_sentiment(ticker=None):
    """Fetch real news and perform sentiment analysis"""
    articles = []
    sentiment_scores = {}
    
    try:
        tickers_to_search = [ticker] if ticker else ETF_LIST
        
        for t in tickers_to_search:
            ticker_articles = []
            ticker_sentiments = []
            
            try:
                stock = yf.Ticker(t)
                if hasattr(stock, 'news') and stock.news:
                    for item in stock.news[:2]:
                        title = item.get('title', '')
                        if title:
                            sentiment = analyze_sentiment_from_title(title)
                            ticker_sentiments.append(sentiment)
                            
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
            
            if ticker_sentiments:
                sentiment_scores[t] = np.mean(ticker_sentiments)
                articles.extend(ticker_articles)
            else:
                sentiment_scores[t] = 0
                articles.append({
                    "ticker": t,
                    "title": f"{t}: No Recent News Available",
                    "sentiment": "NEUTRAL",
                    "sentiment_class": "sentiment-neutral",
                    "sentiment_score": 0,
                    "source": "System",
                    "time": "N/A",
                    "summary": f"No news available for {t} or its holdings.",
                    "link": ""
                })
        
        overall_sentiment = np.mean(list(sentiment_scores.values())) if sentiment_scores else 0
        
        return {
            "sentiment_scores": sentiment_scores,
            "overall_sentiment": overall_sentiment,
            "articles": articles[:15],
            "last_update": datetime.now()
        }
        
    except Exception as e:
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
                "summary": "Unable to fetch news at this time. Please try again later.",
                "link": ""
            }],
            "last_update": datetime.now()
        }


# =====================================================
# ALERT FUNCTIONS
# =====================================================

def send_email_alert(subject, body, to_email):
    """Send email alert using SMTP"""
    if not to_email or not st.session_state.alert_settings.get("enable_email"):
        return False
    
    try:
        if hasattr(st, 'secrets') and 'email' in st.secrets:
            smtp_server = st.secrets['email']['smtp_server']
            smtp_port = st.secrets['email']['smtp_port']
            sender_email = st.secrets['email']['sender_email']
            sender_password = st.secrets['email']['sender_password']
        else:
            st.warning("📧 Email alerts not configured. See secrets.toml.template for setup.")
            return False
        
        message = MIMEMultipart()
        message["From"] = sender_email
        message["To"] = to_email
        message["Subject"] = subject
        message.attach(MIMEText(body, "html"))
        
        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.starttls()
            server.login(sender_email, sender_password)
            server.send_message(message)
        
        return True
        
    except Exception as e:
        st.error(f"Failed to send email: {str(e)}")
        return False


def trigger_alerts_if_needed():
    """Check all alert conditions and send notifications"""
    alerts_sent = []
    
    div_alerts = analyze_dividend_trends()
    for alert in div_alerts:
        if alert["severity"] == "critical":
            if st.session_state.alert_settings.get("enable_email"):
                email = st.session_state.alert_settings.get("email")
                subject = f"🚨 CRITICAL: {alert['ticker']} Alert"
                body = f"<h2>{alert['message']}</h2><p>{alert['action']}</p>"
                if send_email_alert(subject, body, email):
                    alerts_sent.append(f"Email sent: {alert['ticker']}")
    
    price_alerts = check_price_alerts()
    for alert in price_alerts:
        if alert["type"] == "stop_loss":
            if st.session_state.alert_settings.get("enable_email"):
                email = st.session_state.alert_settings.get("email")
                subject = f"🚨 STOP LOSS: {alert['ticker']}"
                body = f"<h2>{alert['message']}</h2><p>{alert['action']}</p>"
                if send_email_alert(subject, body, email):
                    alerts_sent.append(f"Email sent: Stop loss {alert['ticker']}")
    
    return alerts_sent


# =====================================================
# AI RECOMMENDATION FUNCTIONS
# =====================================================

def generate_weekly_investment_recommendation():
    """Analyze all factors and recommend which ETF to invest in"""
    metrics = calculate_current_metrics()
    
    try:
        news_data = fetch_real_news_sentiment()
    except Exception:
        news_data = {
            "sentiment_scores": {t: 0 for t in ETF_LIST},
            "overall_sentiment": 0
        }
    
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
                
                if price_change < -5:
                    trend_score = 25
                    factors.append(f"✅ Price dipped {abs(price_change):.1f}% - buying opportunity! (+25 pts)")
                elif price_change < -2:
                    trend_score = 20
                    factors.append(f"✅ Slight dip {abs(price_change):.1f}% - good entry (+20 pts)")
                elif price_change > 10:
                    trend_score = 5
                    factors.append(f"⚠️ Price up {price_change:.1f}% - expensive (+5 pts)")
                    warnings.append("Price near recent highs")
                else:
                    trend_score = 15
                    factors.append(f"➖ Price stable {price_change:+.1f}% (+15 pts)")
                
                score += trend_score
            else:
                score += 15
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
        
        etf_scores[ticker] = {
            "total_score": round(score, 1),
            "factors": factors,
            "warnings": warnings,
            "sentiment": sentiment,
            "yield": holding["yield_pct"] if holding else 0,
            "concentration": concentration,
            "price": holding["price"] if holding else 0
        }
    
    best_ticker = max(etf_scores.keys(), key=lambda t: etf_scores[t]["total_score"])
    best_score = etf_scores[best_ticker]
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


def generate_ai_recommendations():
    """Generate AI-powered actionable recommendations"""
    recommendations = []
    metrics = calculate_current_metrics()
    risk_score = calculate_portfolio_risk_score()
    div_alerts = analyze_dividend_trends()
    price_alerts = check_price_alerts()
    
    try:
        news_data = fetch_real_news_sentiment()
    except:
        news_data = {"sentiment_scores": {t: 0 for t in ETF_LIST}, "overall_sentiment": 0}
    
    # Dividend-based recommendations
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
    
    # Price alert recommendations
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
    
    # News sentiment recommendations
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
    
    # Risk-based recommendations
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
    
    # Sort by priority
    priority_order = {"CRITICAL": 0, "HIGH": 1, "MEDIUM": 2, "LOW": 3}
    recommendations.sort(key=lambda x: priority_order.get(x.get("priority", "LOW"), 3))
    
    return recommendations
