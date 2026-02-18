# CyberBrief Daily

🚀 **PRODUCTION READY** - Automated daily cybersecurity newsletter focused on executive-level threat intelligence.

## ✅ Live Features

- **Daily email delivery** at 7 AM MST (2 PM UTC) 
- **Live threat intelligence** from current feeds
- **Executive-focused** business impact analysis
- **CISA KEV integration** for exploitable vulnerabilities  
- **Security blog aggregation** from major sources
- **Gmail SMTP delivery** with app password authentication
- **Automated scheduling** via OpenClaw cron system
- **Backup system** - all newsletters saved to files

## 📊 Current Data Sources

- **BleepingComputer RSS** - Real-time security articles
- **Krebs on Security** - Financial crime and cybersecurity investigations  
- **Schneier on Security** - AI security and cryptography insights
- **SANS ISC Diary** - Incident analysis and threat research
- **Threatpost** - Enterprise security threats
- **CISA KEV Catalog** - Known Exploitable Vulnerabilities

**Smart Filtering**: Prioritizes financial services and broad industry impact, excludes consumer/IoT topics

## 🚀 Quick Start

### 1. Clone and Setup
```bash
git clone https://github.com/gxk2bot/cyberbrief-daily.git
cd cyberbrief-daily
mkdir -p logs newsletters
```

### 2. Configure Email
```bash
# Copy template and fill in your credentials
cp .env.example .env
cp config.production.json config.json

# Edit .env with your Gmail details:
GMAIL_USER=your-gmail@gmail.com
GMAIL_APP_PASSWORD=your-16-char-app-password
```

### 3. Test System
```bash
# Test email delivery
python3 test_email.py

# Test full system
python3 test_full_system.py

# Run production version
python3 cyberbrief_production.py
```

### 4. Schedule Daily Delivery
The system uses OpenClaw's cron system for automated scheduling:
- **Schedule**: Daily at 7:00 AM MST (14:00 UTC)
- **Delivery**: Automatic email + file backup
- **Monitoring**: Complete logs in `logs/cyberbrief.log`

## 📧 Gmail App Password Setup

1. **Enable 2FA** on your Gmail account
2. **Generate App Password**:
   - Go to https://myaccount.google.com/apppasswords  
   - Select "Mail" 
   - Copy the 16-character password
3. **Add to .env file** (not your regular Gmail password!)

## 📋 Production Status

- ✅ **Email Delivery**: Fully operational with Gmail SMTP
- ✅ **Live Data**: Real-time threat intelligence feeds
- ✅ **Automation**: Scheduled daily at 7 AM MST  
- ✅ **Error Handling**: Graceful fallbacks and logging
- ✅ **Security**: Credentials stored in .env (excluded from git)
- ✅ **Backup**: All newsletters archived automatically

## 🔧 Testing & Validation

- `test_email.py` - Test Gmail SMTP connection
- `test_full_system.py` - End-to-end system validation
- `cyberbrief_production.py` - Production newsletter generator

## 📁 File Structure

```
cyberbrief-daily/
├── cyberbrief_production.py    # Main production system
├── config.production.json      # Configuration template  
├── .env.example               # Environment template
├── test_email.py              # Email testing utility
├── test_full_system.py        # System validation
├── logs/                      # Application logs
└── newsletters/               # Generated newsletters
```

## 🎯 Newsletter Format

**Mobile-optimized, executive-focused content:**

### 📱 Four Clear Sections:
- **Cybersecurity News** - Current threats and incidents (5 articles)
- **Cybersecurity Regulation News** - Compliance and legal developments (4 articles)  
- **AI News** - AI security threats and developments (4 articles)
- **Notable Vulnerabilities** - CISA KEV with actionable details (4 vulnerabilities)

### 💼 Business Priority Features:
- 🏦 Financial services priority indicators
- Source attribution for all articles
- Executive-focused summaries (no technical jargon)
- Links to full articles for detailed reading
- Published within 36 hours for currency

Perfect for cybersecurity executives who need comprehensive threat awareness across all relevant categories.