# 💡 Weekly Investment Advisor - Feature Guide

## 🎯 What It Does

The **Weekly Investment Advisor** analyzes your portfolio and market conditions to tell you **exactly which ETF to invest in this week**.

### Key Features:

1. **Smart Recommendations** - Tells you "This week, invest in QDTE" with confidence level
2. **Multi-Factor Analysis** - Considers 6 different factors
3. **Score Comparison** - Shows all 3 ETFs ranked with scores out of 100
4. **Investment Calculator** - Calculates exactly how many shares to buy
5. **Auto-Rebalancer** - Suggests when to sell/buy to maintain balance

---

## 📊 How It Works

### The 6-Factor Scoring System:

**1. News Sentiment (30% weight)**
- Fetches real news for each ETF
- Analyzes headlines for positive/negative keywords
- Recent good news = higher score

**2. Price Trend (25% weight)**
- Looks at last 5 days of prices
- **Buying dips is GOOD** (contrarian approach)
- Price down 5%+ = Great buying opportunity!
- Price up 10%+ = Maybe wait (expensive)

**3. Dividend Stability (20% weight)**
- Checks last 12 weeks of dividend history
- Declining dividends = lower score
- Stable/increasing dividends = higher score

**4. Current Yield (15% weight)**
- Higher yield = higher score
- Rewards ETFs with better income generation

**5. Portfolio Concentration (10% weight)**
- Already own 50%+ of one ETF? Score penalized
- Under 20%? Bonus points (room to grow)
- Prevents over-concentration

**6. Risk Level (10% weight)**
- Medium risk ETFs score highest
- High risk gets lower score
- Balances safety with returns

---

## 🥇 Example Output

```
💡 THIS WEEK, INVEST IN:

      QDTE
   
Confidence: VERY HIGH

📊 Analysis Breakdown:
✅ Positive news sentiment (+21.0 pts)
✅ Price dipped 3.2% - good entry (+20 pts)
✅ Dividend stable (+20 pts)
✅ High yield 82.3% (+15 pts)
✅ Underweight 28.4% - room to grow (+10 pts)
✅ Medium risk (+10 pts)

TOTAL SCORE: 96/100

Alternative option: XDTE (if diversifying this week)
```

---

## 💰 Investment Calculator

Enter how much you're investing (e.g., $50/week from your $200/month):

```
💵 Investment Breakdown:
Buy: 2 shares of QDTE
Cost: $39.68
Leftover: $10.32

Weekly income added: $0.35
Monthly income added: $1.53
Annual income added: $18.40
```

---

## 🔄 Auto-Rebalancer

Analyzes if your portfolio is too concentrated and suggests trades:

### Example Rebalancing:

```
⚠️ Rebalancing recommended

📉 SELL 20 shares of CHPY
   Proceeds: $523.00
   Reason: Reduce concentration from 65.2% to ~35%

📈 BUY 15 shares of QDTE
   Cost: $297.60
   Reason: Highest score (96/100)

📈 BUY 11 shares of XDTE
   Cost: $208.12
   Reason: Diversification

Income Before: $2,615.00
Income After: $2,598.50
Income Change: -$16.50 (-0.6%)

ℹ️ Reduces concentration risk
```

---

## 🎯 When To Use

### Weekly Investing
- **Every Monday**: Check the recommendation
- **Before buying**: See which ETF scores highest
- **Split decision?**: Check the scores - if close, split your investment

### Monthly Rebalancing
- **First of month**: Run the Auto-Rebalancer
- **High concentration?**: Follow rebalancing suggestions
- **Quarterly**: Major rebalance check

---

## 📈 Real-World Example

**Week 1:**
- Recommendation: QDTE (Score: 92/100)
- Reason: Price dipped, positive news, stable dividends
- Action: Invested $50 → Bought 2 shares

**Week 2:**
- Recommendation: XDTE (Score: 88/100)
- Reason: QDTE now 45% of portfolio (too concentrated), XDTE has good news
- Action: Invested $50 → Bought 2 shares XDTE

**Week 3:**
- Recommendation: CHPY (Score: 85/100)
- Reason: Strong positive news, high yield, underweight in portfolio
- Action: Invested $50 → Bought 1 share

**Result**: Balanced portfolio, buying the best option each week!

---

## 🧠 Smart Strategies

### 1. Follow The Recommendation
- **90+ score**: Strong buy signal
- **70-89 score**: Good buy
- **Below 70**: Consider alternatives or split investment

### 2. Contrarian Buying
- The system **rewards buying dips**
- Price down = opportunity (if fundamentals strong)
- Don't chase rallies

### 3. Concentration Management
- Keep each ETF under 45% of portfolio
- Auto-rebalancer will alert you
- Diversification reduces risk

### 4. News-Driven
- Negative news week? System steers you away
- Positive news? Get the recommendation
- Real-time adaptation

---

## ⚙️ Configuration

### In Sidebar:
- **Enable AI Autopilot** - Auto-generates weekly recommendations
- **Auto-rebalance** - Automatically suggests rebalancing
- **Require approval** - You confirm before any changes

### In Weekly Advisor Tab:
- **🔄 Get Recommendation** - Refresh the analysis
- **Investment amount** - How much you're investing
- **🤖 Generate Rebalancing Plan** - Check if rebalancing needed

---

## 💡 Pro Tips

1. **Check every Monday** - Markets change weekly
2. **Don't ignore warnings** - Red flags are important
3. **Use with compound calculator** - Plan long-term
4. **Track in Snapshots** - See if following recommendations helped
5. **Split if scores are close** - 85 vs 83? Buy both!

---

## 🎓 Advanced: Understanding Scores

**96-100**: Perfect conditions - strong buy
**85-95**: Excellent opportunity
**70-84**: Good buy
**60-69**: Okay, but watch for warnings
**Below 60**: Caution - check warnings carefully

**Confidence Levels**:
- **VERY HIGH**: Winner is clear (20+ points ahead)
- **HIGH**: Strong favorite (10-20 points ahead)
- **MODERATE**: Good choice (5-10 points ahead)
- **LOW**: Split investment recommended (<5 points difference)

---

## 🔮 What Makes It Smart

Unlike static strategies ("buy QDTE every week"), this system:

✅ **Adapts to market conditions**
✅ **Considers YOUR portfolio** (concentration)
✅ **Uses real news** (not simulated)
✅ **Rewards buying dips** (contrarian)
✅ **Maintains balance** (auto-rebalancer)
✅ **Protects income** (dividend stability focus)

---

## 📊 Track Your Results

Use the **Snapshots** feature to track:
- Did following recommendations beat static strategy?
- Portfolio value growth
- Income growth
- Risk reduction

**Example tracking**:
```
Month 1: Followed recommendations
- QDTE: 3 weeks
- XDTE: 1 week  
- Rebalanced once
- Result: +2.3% better than "always QDTE"

Month 2: Followed recommendations
- CHPY: 2 weeks (negative QDTE news)
- QDTE: 2 weeks
- Result: Avoided 5% drawdown
```

---

## 🚀 Getting Started

1. Go to **💡 Weekly Advisor** tab
2. Click **🔄 Get Recommendation**
3. Review the scores and reasoning
4. Enter your investment amount
5. See exactly what to buy
6. Optional: Check **Auto-Rebalancer**

**It's that simple!**

---

This feature turns your app from a passive tracker into an **active investment guide** that tells you exactly what to do each week! 📈💰
