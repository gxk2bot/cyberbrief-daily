#!/bin/bash

# CyberBrief Daily Setup Script

echo "Setting up CyberBrief Daily..."

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Create directories
mkdir -p newsletters
mkdir -p logs

# Copy config template
if [ ! -f config.json ]; then
    cp config.example.json config.json
    echo "Created config.json - please edit with your settings"
else
    echo "config.json already exists"
fi

# Make main script executable
chmod +x cyberbrief.py

echo ""
echo "Setup complete!"
echo ""
echo "Next steps:"
echo "1. Edit config.json with your email and API settings"
echo "2. Test with: python cyberbrief.py"
echo "3. Schedule with cron:"
echo "   crontab -e"
echo "   Add: 0 14 * * * /usr/bin/python3 $(pwd)/cyberbrief.py"
echo "   (This runs at 7 AM MST / 2 PM UTC daily)"
echo ""