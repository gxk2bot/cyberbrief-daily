# CyberBrief Daily

Automated daily cybersecurity newsletter focused on executive-level threat intelligence.

## Features

- Daily email at 7 AM MST
- Top 3 cybersecurity news articles with business impact summaries
- Known exploitable vulnerabilities (CISA KEV + vendor advisories)
- Top 5 active security blogs with new content
- ASCII art header, plain text format
- Executive-focused content filtering

## Sources

- BleepingComputer
- Wall Street Journal (cyber sections)
- Washington Post (cyber sections)
- Major security news outlets
- CISA Known Exploitable Vulnerabilities Catalog
- Dynamic discovery of active security blogs

## Installation

```bash
pip install -r requirements.txt
cp config.example.json config.json
# Edit config.json with your email settings
```

## Usage

```bash
# Manual run (testing)
python cyberbrief.py

# Schedule via cron (7 AM MST daily)
crontab -e
# Add: 0 14 * * * /path/to/cyberbrief.py
```

## Configuration

Edit `config.json`:
- Email SMTP settings
- Recipient list
- Content preferences
- Source priorities