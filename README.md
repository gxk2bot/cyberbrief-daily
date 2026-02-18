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

## 📊 Comprehensive Data Sources (13+ Premium Feeds)

### 🎯 Primary Security Sources
- **BleepingComputer** - Breaking cybersecurity news and incidents
- **The Hacker News** - Global cybersecurity developments  
- **Krebs on Security** - Financial crime and cybersecurity investigations
- **Schneier on Security** - AI security, cryptography, and policy insights

### 🔬 Threat Research & Intelligence  
- **Securelist (Kaspersky)** - Advanced threat research and APT analysis
- **SANS Internet Storm Center** - Incident analysis and threat hunting
- **Sophos Security Operations** - Enterprise security operations
- **Sophos Threat Research** - Advanced persistent threats and malware

### 🎙️ Industry Expertise & Analysis
- **Darknet Diaries** - Deep-dive cybercrime investigations
- **Graham Cluley** - Security expertise and industry commentary
- **Troy Hunt** - Data breach analysis and security awareness  
- **Risky Business** - Security industry news and analysis
- **Threatpost** - Enterprise-focused security threats

### 🏛️ Government & Standards
- **CISA Known Exploitable Vulnerabilities** - Government threat advisories

**🎯 Smart Prioritization**: Financial services (🏦), broad industry impact, nation-state threats, zero-days

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

## 📋 Production Status - Enterprise Grade

- ✅ **13+ RSS Sources**: Comprehensive threat intelligence coverage
- ✅ **26+ Daily Articles**: Curated from premium security sources
- ✅ **Financial Priority**: 🏦 Banking/fintech threats highlighted  
- ✅ **Email Delivery**: Fully operational Gmail SMTP with failover
- ✅ **Daily Automation**: 7 AM MST via OpenClaw cron system
- ✅ **Smart Filtering**: 36-hour currency window, business relevance
- ✅ **Error Handling**: Graceful timeouts, source diversity protection
- ✅ **Mobile Optimized**: Clean formatting for executive consumption
- ✅ **Source Attribution**: Full transparency and traceability
- ✅ **Archive System**: Complete newsletter history and backup

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

### 📱 Five Executive-Focused Sections:
- **Cybersecurity News** - Current threats and incidents (up to 5 articles)
- **Notable Breaches Reported** - Company breach disclosures and incidents (up to 5 articles)
- **Cybersecurity Regulation News** - Compliance and legal developments (up to 4 articles)  
- **AI News** - AI security threats and developments (up to 4 articles)
- **Notable Vulnerabilities** - CISA KEV with actionable details (up to 4 vulnerabilities)

### 💼 Business Priority Features:
- 🏦 Financial services priority indicators
- Source attribution for all articles
- Executive-focused summaries (no technical jargon)
- Links to full articles for detailed reading
- Published within 36 hours for currency

Perfect for cybersecurity executives who need comprehensive threat awareness across all relevant categories.