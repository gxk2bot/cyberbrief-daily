# CyberBrief Daily - Deployment Guide

## Quick Start

1. **Clone the repository**
   ```bash
   git clone https://github.com/gxk2bot/cyberbrief-daily.git
   cd cyberbrief-daily
   ```

2. **Run setup**
   ```bash
   chmod +x setup.sh
   ./setup.sh
   ```

3. **Configure settings**
   ```bash
   cp config.example.json config.json
   # Edit config.json with your email and API settings
   ```

4. **Test the system**
   ```bash
   python3 test.py
   # or test with minimal version:
   python3 cyberbrief_minimal.py
   ```

5. **Schedule daily execution (7 AM MST)**
   ```bash
   crontab -e
   # Add this line:
   0 14 * * * cd /path/to/cyberbrief-daily && python3 cyberbrief.py
   ```

## Configuration

### Email Settings
- **Gmail**: Use app passwords, enable 2FA
- **SMTP Server**: Configure your email provider's SMTP settings
- **Recipients**: List all email addresses that should receive the newsletter

### OpenAI API
- Get API key from https://platform.openai.com/
- Model recommendation: gpt-4 for best business impact analysis

### Content Filtering
- Exclude topics not relevant to executives (IoT, consumer devices)
- Focus areas: business impact, trending threats, enterprise security

## Scheduling

The newsletter runs daily at 7 AM Arizona Time (MST):
- **Cron time**: 14:00 UTC (MST = UTC-7)
- **Command**: `0 14 * * * /path/to/cyberbrief.py`

## File Structure

```
cyberbrief-daily/
├── cyberbrief.py          # Main application (full version)
├── cyberbrief_minimal.py  # Test version (no external APIs)
├── test.py               # Test suite
├── config.example.json   # Configuration template
├── requirements.txt      # Python dependencies
├── setup.sh             # Installation script
├── newsletters/         # Generated newsletters (auto-created)
└── logs/               # Log files (auto-created)
```

## Monitoring

- Check logs in `cyberbrief.log`
- Monitor cron execution: `grep CRON /var/log/syslog`
- Newsletter backups saved in `newsletters/` directory

## Troubleshooting

1. **Missing dependencies**: Run `pip install -r requirements.txt`
2. **Email auth errors**: Check app passwords and SMTP settings
3. **API limits**: Monitor OpenAI usage, consider rate limiting
4. **Cron not running**: Check cron service and user permissions

## Security Notes

- Store config.json securely (contains API keys and passwords)
- Use environment variables for sensitive data in production
- Regular security updates for dependencies
- Monitor for API key exposure in logs