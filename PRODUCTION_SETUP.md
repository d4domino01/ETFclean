# 🚀 Production Setup Guide

This guide will help you set up all production features: real news, email alerts, and SMS notifications.

## 📋 Quick Start Checklist

- [ ] Install dependencies
- [ ] Configure email alerts (optional)
- [ ] Configure SMS alerts (optional)
- [ ] Test the setup
- [ ] Deploy to production

---

## 1️⃣ Install Dependencies

```bash
pip install -r requirements.txt
```

This installs:
- `streamlit` - Web framework
- `pandas` - Data manipulation
- `yfinance` - Real-time stock data & news
- `plotly` - Interactive charts
- `numpy` - Calculations
- `twilio` - SMS alerts (optional)

---

## 2️⃣ Configure Email Alerts (Optional)

### Using Gmail (Recommended)

1. **Enable 2-Factor Authentication**
   - Go to: https://myaccount.google.com/security
   - Turn on 2-Step Verification

2. **Create App Password**
   - Go to: https://myaccount.google.com/apppasswords
   - Select "Mail" and "Other (Custom name)"
   - Name it "Income Strategy Engine"
   - Copy the 16-character password

3. **Create Secrets File**
   ```bash
   mkdir -p .streamlit
   cp secrets.toml.template .streamlit/secrets.toml
   ```

4. **Edit `.streamlit/secrets.toml`**
   ```toml
   [email]
   smtp_server = "smtp.gmail.com"
   smtp_port = 587
   sender_email = "your-email@gmail.com"
   sender_password = "xxxx xxxx xxxx xxxx"  # Your app password
   ```

### Using Other Providers

**Outlook/Hotmail:**
```toml
[email]
smtp_server = "smtp.office365.com"
smtp_port = 587
sender_email = "your-email@outlook.com"
sender_password = "your-password"
```

**Yahoo:**
```toml
[email]
smtp_server = "smtp.mail.yahoo.com"
smtp_port = 587
sender_email = "your-email@yahoo.com"
sender_password = "your-password"
```

---

## 3️⃣ Configure SMS Alerts (Optional)

### Using Twilio

1. **Sign Up**
   - Go to: https://www.twilio.com/try-twilio
   - Free trial includes $15 credit

2. **Get Credentials**
   - Dashboard: https://console.twilio.com/
   - Copy your **Account SID**
   - Copy your **Auth Token**

3. **Get Phone Number**
   - Click "Get a Twilio phone number"
   - Copy the number (format: +1234567890)

4. **Update Secrets File**
   Add to `.streamlit/secrets.toml`:
   ```toml
   [sms]
   twilio_account_sid = "ACxxxxxxxxxxxxxxxxxxxx"
   twilio_auth_token = "your_auth_token"
   twilio_phone_number = "+1234567890"
   ```

5. **Verify Your Phone** (Free Trial Only)
   - Add your personal phone in Twilio console
   - Verify it before testing

---

## 4️⃣ Test the Setup

### Test Email Alerts

1. Run the app: `streamlit run app.py`
2. Go to sidebar → **Alert Settings**
3. Check ✅ "Enable Email Alerts"
4. Enter your email address
5. Go to **Safety Monitor** tab
6. Click "🔍 Run Full Safety Check"
7. Check your email inbox

### Test SMS Alerts

1. In sidebar → **Alert Settings**
2. Check ✅ "Enable SMS Alerts"
3. Enter your phone number (format: +1234567890)
4. Run safety check
5. Check your phone for SMS

---

## 5️⃣ Real News Integration

The app now fetches **real news** from yfinance:

✅ **Automatic Features:**
- Fetches latest news for each ETF
- Analyzes sentiment from headlines
- Shows news for underlying stocks (AAPL, MSFT, etc.)
- Updates when you click "Refresh News"

**Note:** yfinance provides free news data. For more comprehensive news, you can integrate:
- NewsAPI
- Alpha Vantage
- Financial Modeling Prep
- Bloomberg API

---

## 6️⃣ Security Best Practices

### ⚠️ CRITICAL: Protect Your Secrets

1. **Never commit secrets.toml**
   ```bash
   echo ".streamlit/secrets.toml" >> .gitignore
   ```

2. **Use Environment Variables (Production)**
   For deployment (Heroku, AWS, etc.):
   ```python
   import os
   smtp_server = os.environ.get('SMTP_SERVER')
   ```

3. **Use Streamlit Cloud Secrets**
   If deploying to Streamlit Cloud:
   - Go to App Settings → Secrets
   - Paste your secrets.toml content

---

## 7️⃣ Deployment Options

### Streamlit Cloud (Easiest)

1. Push code to GitHub
2. Go to: https://share.streamlit.io
3. Connect your repo
4. Add secrets in app settings
5. Deploy!

### Heroku

```bash
heroku create your-app-name
heroku config:set SMTP_SERVER="smtp.gmail.com"
heroku config:set SMTP_PORT="587"
# ... set other config vars
git push heroku main
```

### AWS / Azure / Google Cloud

Follow their Python app deployment guides and set environment variables.

---

## 8️⃣ Alert Frequency

By default, alerts trigger when you:
- Click "Run Full Safety Check"
- Open the app (if autopilot enabled)

### Automated Alerts (Advanced)

To get alerts automatically every hour/day:

**Option A: Use a cron job**
```bash
# Run safety check every hour
0 * * * * cd /path/to/app && python run_checks.py
```

**Option B: Use a task scheduler**
- APScheduler (Python)
- Celery (Python)
- Cloud Functions (AWS Lambda, Google Cloud Functions)

---

## 9️⃣ Troubleshooting

### Email Not Sending

**"Authentication failed"**
- Gmail: Use App Password, not regular password
- Outlook: Enable "Less secure apps" or use OAuth

**"Connection refused"**
- Check SMTP server and port
- Try port 465 (SSL) instead of 587 (TLS)

### SMS Not Sending

**"Unable to create record"**
- Verify phone number in Twilio console (free trial)
- Check phone number format: +1234567890

**"Insufficient funds"**
- Free trial has $15 credit
- Add payment method for continued use

### News Not Loading

**"Could not fetch live news"**
- yfinance sometimes rate limits
- Wait a few minutes and try again
- App falls back to simulated data automatically

---

## 🎯 What You Get

### ✅ Real Features (Working Now)

1. **Real News Sentiment**
   - Fetches actual news from yfinance
   - Analyzes sentiment from headlines
   - Shows news for ETFs and underlying stocks

2. **Email Alerts**
   - Critical dividend drops
   - Stop-loss triggers
   - Portfolio warnings
   - HTML formatted emails

3. **SMS Alerts**
   - Text messages for critical events
   - 160-character summaries
   - Instant notifications

4. **All Previous Features**
   - Compound projections
   - Risk scoring
   - AI recommendations
   - Mobile-friendly UI

---

## 💡 Pro Tips

1. **Start with email only** - Easier to set up than SMS
2. **Test with small values** - Don't set stop-losses too tight at first
3. **Check spam folder** - First email might go to spam
4. **Use test mode** - Twilio free trial is perfect for testing
5. **Monitor costs** - SMS costs $0.0075 per message after free trial

---

## 📚 Additional Resources

- [Gmail App Passwords](https://support.google.com/accounts/answer/185833)
- [Twilio Documentation](https://www.twilio.com/docs)
- [Streamlit Secrets](https://docs.streamlit.io/streamlit-community-cloud/get-started/deploy-an-app/connect-to-data-sources/secrets-management)
- [yfinance Documentation](https://pypi.org/project/yfinance/)

---

## ✅ You're Production Ready!

Your app now has:
- ✅ Real-time news analysis
- ✅ Email notifications
- ✅ SMS alerts
- ✅ Professional UI
- ✅ Mobile support
- ✅ AI recommendations
- ✅ Safety monitoring

**Time to invest smarter!** 🚀📈
