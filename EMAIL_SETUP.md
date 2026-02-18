# Email Setup for CyberBrief Daily

## Quick Setup for Gmail

1. **Enable 2-Factor Authentication** on your Gmail account
2. **Generate an App Password**:
   - Go to https://myaccount.google.com/security
   - Click "2-Step Verification" 
   - Click "App passwords"
   - Generate password for "Mail"
3. **Set Environment Variables**:
   ```bash
   export GMAIL_USER="your-gmail@gmail.com"
   export GMAIL_APP_PASSWORD="your-16-character-app-password"
   ```
4. **Or edit config.json directly**:
   ```json
   {
     "email": {
       "smtp_server": "smtp.gmail.com",
       "smtp_port": 587,
       "username": "your-gmail@gmail.com",
       "password": "your-app-password",
       "from_addr": "your-gmail@gmail.com",
       "to_addrs": ["casey.l.beaumont@gmail.com"]
     }
   }
   ```

## Current Status

✅ **CyberBrief Daily is SCHEDULED**: Runs daily at 7:00 AM MST (2:00 PM UTC)
✅ **Live Data Sources**: BleepingComputer RSS, CISA KEV, security blogs
✅ **Backup System**: All newsletters saved to `newsletters/` directory
✅ **Logging**: Full logs in `logs/cyberbrief.log`

## Without Email Setup

If email isn't configured, the system will:
- Generate the newsletter with live threat data
- Save it to `newsletters/cyberbrief_YYYYMMDD_HHMMSS.txt`
- Log the event
- Still run on schedule daily

## Test Email Setup

```bash
cd /root/.openclaw/workspace/cyberbrief-daily
python3 cyberbrief_production.py
```

Check the log output - if email is configured correctly, you'll see "Newsletter sent successfully".

## Cron Job Details

- **Schedule**: 0 14 * * * (2:00 PM UTC = 7:00 AM MST daily)
- **Command**: `python3 cyberbrief_production.py`
- **Working Directory**: `/root/.openclaw/workspace/cyberbrief-daily`
- **Managed by**: OpenClaw cron system
- **Job ID**: a947593c-489a-407f-aef8-4f9415f3a652

## Next Steps

1. Configure email settings (above)
2. Wait for tomorrow's 7 AM delivery, or...
3. Test manually: `cd cyberbrief-daily && python3 cyberbrief_production.py`

Your CyberBrief Daily is ready! 📧