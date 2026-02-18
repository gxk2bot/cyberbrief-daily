#!/usr/bin/env python3
"""
CyberBrief Daily - Enhanced Version
Mobile-optimized newsletter with improved content categorization
"""

import json
import logging
import smtplib
import urllib.request
import urllib.parse
import xml.etree.ElementTree as ET
from datetime import datetime, timedelta
from email.mime.text import MIMEText
from pathlib import Path
from typing import List, Dict, Any
import re
import csv
from io import StringIO
import os
import sys

# Add current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/cyberbrief.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class CyberBriefEnhanced:
    def __init__(self, config_path: str = "config.json"):
        # Ensure directories exist
        Path("logs").mkdir(exist_ok=True)
        Path("newsletters").mkdir(exist_ok=True)
        
        self.config_path = Path(config_path)
        self.config = self.load_config()
        
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        
    def load_config(self) -> Dict[str, Any]:
        """Load configuration from JSON file"""
        
        # Load environment variables from .env file if it exists
        env_file = Path(".env")
        if env_file.exists():
            try:
                with open(env_file, 'r') as f:
                    for line in f:
                        line = line.strip()
                        if line and not line.startswith('#') and '=' in line:
                            key, value = line.split('=', 1)
                            os.environ[key] = value
            except Exception as e:
                logger.error(f"Error loading .env file: {e}")
        
        if not self.config_path.exists():
            logger.error(f"Config file {self.config_path} not found")
            return {
                "email": {"to_addrs": ["casey.l.beaumont@gmail.com"]},
                "content": {"max_articles": 3, "max_blogs": 5}
            }
            
        try:
            with open(self.config_path, 'r') as f:
                config = json.load(f)
                
            # Replace environment variable placeholders
            if 'email' in config:
                if config['email']['username'] == 'GMAIL_USER':
                    config['email']['username'] = os.getenv('GMAIL_USER', '')
                if config['email']['password'] == 'GMAIL_APP_PASSWORD':
                    config['email']['password'] = os.getenv('GMAIL_APP_PASSWORD', '')
                if config['email']['from_addr'] == 'GMAIL_USER':
                    config['email']['from_addr'] = os.getenv('GMAIL_USER', '')
                    
            if 'openai' in config:
                if config['openai']['api_key'] == 'OPENAI_API_KEY':
                    config['openai']['api_key'] = os.getenv('OPENAI_API_KEY', '')
                    
            return config
            
        except Exception as e:
            logger.error(f"Error loading config: {e}")
            return {"email": {"to_addrs": ["casey.l.beaumont@gmail.com"]}}
    
    def fetch_url(self, url: str) -> str:
        """Fetch URL content with error handling"""
        try:
            req = urllib.request.Request(url, headers=self.headers)
            with urllib.request.urlopen(req, timeout=15) as response:
                return response.read().decode('utf-8')
        except Exception as e:
            logger.error(f"Error fetching {url}: {e}")
            return ""
    
    def generate_header(self) -> str:
        """Generate simple text header"""
        date_str = datetime.now().strftime("%B %d, %Y")
        
        return f"""CYBERBRIEF DAILY
Executive Cyber Threat Intelligence
{date_str}

"""
    
    def categorize_article(self, article: Dict) -> str:
        """Categorize article into one of the four sections"""
        title = article['title'].lower()
        desc = article.get('description', '').lower()
        text = f"{title} {desc}"
        
        # AI News - more specific keywords
        ai_keywords = [
            'artificial intelligence', 'machine learning', 'llm', 'chatgpt', 'openai', 
            'neural network', 'deepfake', 'ai model', 'generative ai', 'large language model',
            'ai security', 'ai vulnerability', 'ai attack', 'prompt injection', 'ai bias'
        ]
        if any(keyword in text for keyword in ai_keywords):
            return 'ai'
        
        # Regulation News - more specific
        regulation_keywords = [
            'regulatory', 'compliance fine', 'gdpr violation', 'ccpa', 'sec filing', 'sec charges',
            'ftc action', 'cisa directive', 'cisa advisory', 'nist framework', 'government mandate',
            'new law', 'policy change', 'court ruling', 'lawsuit settlement', 'regulatory fine',
            'compliance requirement', 'data protection law', 'privacy regulation'
        ]
        if any(keyword in text for keyword in regulation_keywords):
            return 'regulation'
        
        # Also check for specific regulatory phrases
        regulation_phrases = [
            'ordered to pay', 'fined for', 'regulatory action', 'compliance violation',
            'government investigation', 'legal action', 'court orders', 'settlement agreement'
        ]
        if any(phrase in text for phrase in regulation_phrases):
            return 'regulation'
        
        # General Cybersecurity (default)
        return 'cybersecurity'
    
    def fetch_bleepingcomputer_articles(self) -> List[Dict]:
        """Fetch real articles from BleepingComputer RSS"""
        articles = []
        try:
            logger.info("Fetching BleepingComputer RSS...")
            rss_content = self.fetch_url("https://www.bleepingcomputer.com/feed/")
            
            if not rss_content:
                return articles
                
            # Parse RSS XML
            root = ET.fromstring(rss_content)
            
            for item in root.findall('.//item')[:15]:
                try:
                    title_elem = item.find('title')
                    link_elem = item.find('link') 
                    desc_elem = item.find('description')
                    pub_elem = item.find('pubDate')
                    
                    if title_elem is not None and link_elem is not None:
                        title = title_elem.text.strip()
                        link = link_elem.text.strip()
                        desc = desc_elem.text.strip() if desc_elem is not None else ""
                        pub_date = pub_elem.text.strip() if pub_elem is not None else ""
                        
                        # Simple business relevance filtering
                        if self.is_relevant(title, desc):
                            category = self.categorize_article({'title': title, 'description': desc})
                            articles.append({
                                'title': title,
                                'link': link,
                                'description': desc,
                                'published': pub_date,
                                'source': 'BleepingComputer',
                                'category': category
                            })
                            
                except Exception as e:
                    logger.error(f"Error parsing RSS item: {e}")
                    continue
                    
            logger.info(f"Found {len(articles)} relevant articles from BleepingComputer")
                    
        except Exception as e:
            logger.error(f"Error fetching BleepingComputer RSS: {e}")
            
        return articles
    
    def is_relevant(self, title: str, description: str) -> bool:
        """Check if article is relevant"""
        text = f"{title} {description}".lower()
        
        # Exclude consumer/gaming topics
        exclude_terms = ['gaming', 'game', 'consumer router', 'home wifi', 'personal device', 'smartphone app']
        if any(term in text for term in exclude_terms):
            return False
            
        # Include relevant terms
        include_terms = [
            'cyber', 'security', 'hack', 'breach', 'vulnerability', 'malware', 'ransomware',
            'attack', 'threat', 'exploit', 'zero-day', 'data', 'enterprise', 'corporate',
            'microsoft', 'google', 'amazon', 'cloud', 'server', 'network', 'ai', 'regulation',
            'compliance', 'government', 'critical infrastructure', 'supply chain'
        ]
        
        return any(term in text for term in include_terms)
    
    def fetch_cisa_kev(self) -> List[Dict]:
        """Fetch real Known Exploitable Vulnerabilities from CISA"""
        vulnerabilities = []
        try:
            logger.info("Fetching CISA KEV data...")
            csv_content = self.fetch_url("https://www.cisa.gov/sites/default/files/csv/known_exploited_vulnerabilities.csv")
            
            if not csv_content:
                return vulnerabilities
                
            # Parse CSV
            csv_reader = csv.DictReader(StringIO(csv_content))
            
            # Get vulnerabilities added in last 14 days
            cutoff_date = datetime.now() - timedelta(days=14)
            
            for row in csv_reader:
                try:
                    date_added_str = row.get('dateAdded', '')
                    if date_added_str:
                        date_added = datetime.strptime(date_added_str, '%Y-%m-%d')
                        
                        if date_added > cutoff_date:
                            vulnerabilities.append({
                                'cve_id': row.get('cveID', ''),
                                'vendor_project': row.get('vendorProject', ''),
                                'product': row.get('product', ''),
                                'vulnerability_name': row.get('vulnerabilityName', ''),
                                'date_added': date_added,
                                'short_description': row.get('shortDescription', ''),
                                'required_action': row.get('requiredAction', ''),
                                'due_date': row.get('dueDate', '')
                            })
                            
                except Exception as e:
                    logger.error(f"Error parsing KEV row: {e}")
                    continue
            
            # Sort by date added (newest first) and limit
            vulnerabilities.sort(key=lambda x: x['date_added'], reverse=True)
            vulnerabilities = vulnerabilities[:6]
            
            logger.info(f"Found {len(vulnerabilities)} recent vulnerabilities from CISA KEV")
            
        except Exception as e:
            logger.error(f"Error fetching CISA KEV data: {e}")
            
        return vulnerabilities
    
    def generate_article_summary(self, article: Dict) -> str:
        """Generate a few sentence summary of the article"""
        title = article['title']
        desc = article.get('description', '')
        
        # Extract meaningful content from description (remove HTML tags)
        clean_desc = re.sub(r'<[^>]+>', '', desc)
        
        # Create summary based on title and description
        if len(clean_desc) > 200:
            summary = clean_desc[:200] + "..."
        else:
            summary = clean_desc
            
        # If no good description, create summary from title
        if not summary or len(summary) < 50:
            if 'ransomware' in title.lower():
                summary = f"A ransomware attack or campaign has been discovered. {summary}"
            elif 'vulnerability' in title.lower() or 'flaw' in title.lower():
                summary = f"Security researchers have identified a vulnerability that could be exploited by attackers. {summary}"
            elif 'breach' in title.lower() or 'hack' in title.lower():
                summary = f"A cybersecurity incident has been reported affecting systems or data. {summary}"
            elif 'malware' in title.lower():
                summary = f"New malware has been discovered with capabilities that pose risks to organizations. {summary}"
            else:
                summary = f"Cybersecurity development requiring executive attention. {summary}"
        
        return summary.strip()
    
    def generate_newsletter(self) -> str:
        """Generate newsletter with enhanced format"""
        logger.info("Generating CyberBrief Daily with enhanced format...")
        
        # Fetch real data
        articles = self.fetch_bleepingcomputer_articles()
        vulnerabilities = self.fetch_cisa_kev()
        
        # Categorize articles
        cybersecurity_articles = [a for a in articles if a['category'] == 'cybersecurity']
        regulation_articles = [a for a in articles if a['category'] == 'regulation']
        ai_articles = [a for a in articles if a['category'] == 'ai']
        
        # Start building newsletter
        newsletter = self.generate_header()
        
        # Cybersecurity News Section
        newsletter += "CYBERSECURITY NEWS\n"
        newsletter += "=" * 20 + "\n\n"
        
        if cybersecurity_articles:
            for article in cybersecurity_articles[:4]:  # Top 4
                summary = self.generate_article_summary(article)
                newsletter += f"• {article['title']}\n"
                newsletter += f"  {summary}\n"
                newsletter += f"  Read more: {article['link']}\n\n"
        else:
            newsletter += "No major cybersecurity news found in current feeds.\n\n"
        
        # Cybersecurity Regulation News Section
        newsletter += "CYBERSECURITY REGULATION NEWS\n"
        newsletter += "=" * 30 + "\n\n"
        
        if regulation_articles:
            for article in regulation_articles[:3]:  # Top 3
                summary = self.generate_article_summary(article)
                newsletter += f"• {article['title']}\n"
                newsletter += f"  {summary}\n"
                newsletter += f"  Read more: {article['link']}\n\n"
        else:
            newsletter += "No cybersecurity regulation news found in current feeds.\n\n"
        
        # AI News Section
        newsletter += "AI NEWS\n"
        newsletter += "=" * 8 + "\n\n"
        
        if ai_articles:
            for article in ai_articles[:3]:  # Top 3
                summary = self.generate_article_summary(article)
                newsletter += f"• {article['title']}\n"
                newsletter += f"  {summary}\n"
                newsletter += f"  Read more: {article['link']}\n\n"
        else:
            newsletter += "No AI-related cybersecurity news found in current feeds.\n\n"
        
        # Notable Vulnerabilities Section
        newsletter += "NOTABLE VULNERABILITIES\n"
        newsletter += "=" * 22 + "\n\n"
        
        if vulnerabilities:
            for vuln in vulnerabilities[:4]:  # Top 4
                newsletter += f"• {vuln['cve_id']} - {vuln['vendor_project']} {vuln['product']}\n"
                newsletter += f"  Added: {vuln['date_added'].strftime('%Y-%m-%d')}\n"
                newsletter += f"  Risk: {vuln['short_description'][:120]}{'...' if len(vuln['short_description']) > 120 else ''}\n"
                if vuln.get('required_action'):
                    action = vuln['required_action'][:100]
                    newsletter += f"  Action: {action}{'...' if len(vuln['required_action']) > 100 else ''}\n"
                newsletter += "\n"
        else:
            newsletter += "No new notable vulnerabilities in recent weeks.\n\n"
        
        # Footer
        newsletter += "=" * 40 + "\n"
        newsletter += "CyberBrief Daily\n"
        mst_time = datetime.now() - timedelta(hours=7)  # Convert to MST
        newsletter += f"Generated: {mst_time.strftime('%Y-%m-%d %H:%M:%S MST')}\n"
        newsletter += "Sources: BleepingComputer, CISA KEV\n"
        
        return newsletter
    
    def send_email(self, content: str) -> bool:
        """Send newsletter via email"""
        try:
            email_config = self.config.get('email', {})
            
            if not email_config.get('username') or not email_config.get('password'):
                logger.info("Email not configured - saving newsletter to file only")
                return False
            
            # Create message
            msg = MIMEText(content)
            msg['Subject'] = f"CyberBrief Daily - {datetime.now().strftime('%B %d, %Y')}"
            msg['From'] = email_config['from_addr']
            msg['To'] = ", ".join(email_config['to_addrs'])
            
            # Connect to SMTP server
            logger.info("Connecting to email server...")
            with smtplib.SMTP(email_config['smtp_server'], email_config['smtp_port']) as server:
                server.starttls()
                server.login(email_config['username'], email_config['password'])
                
                for to_addr in email_config['to_addrs']:
                    server.send_message(msg, to_addrs=[to_addr])
            
            logger.info(f"Newsletter sent successfully to {len(email_config['to_addrs'])} recipients")
            return True
            
        except Exception as e:
            logger.error(f"Error sending email: {e}")
            return False
    
    def run(self) -> bool:
        """Main execution function"""
        try:
            logger.info("Starting CyberBrief Daily Enhanced generation")
            
            # Generate newsletter content
            newsletter_content = self.generate_newsletter()
            
            # Save backup
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            backup_file = f"newsletters/cyberbrief_enhanced_{timestamp}.txt"
            
            with open(backup_file, 'w', encoding='utf-8') as f:
                f.write(newsletter_content)
            logger.info(f"Newsletter saved to {backup_file}")
            
            # Try to send email
            email_sent = self.send_email(newsletter_content)
            
            if email_sent:
                logger.info("CyberBrief Daily Enhanced completed successfully - email sent")
            else:
                logger.info("CyberBrief Daily Enhanced completed - newsletter saved to file")
                # Print preview
                print("\n" + "="*60)
                print("CYBERBRIEF DAILY - ENHANCED FORMAT")
                print("="*60)
                print(newsletter_content)
            
            return True
            
        except Exception as e:
            logger.error(f"Error in CyberBrief Enhanced execution: {e}")
            return False

def main():
    """Main entry point"""
    try:
        brief = CyberBriefEnhanced()
        success = brief.run()
        sys.exit(0 if success else 1)
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()