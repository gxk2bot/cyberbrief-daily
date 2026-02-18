#!/usr/bin/env python3
"""
CyberBrief Daily - Production Version
Automated cybersecurity newsletter with email delivery
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

class CyberBriefProduction:
    def __init__(self, config_path: str = "config.json"):
        # Ensure logs directory exists
        Path("logs").mkdir(exist_ok=True)
        Path("newsletters").mkdir(exist_ok=True)
        
        self.config_path = Path(config_path)
        self.config = self.load_config()
        
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        
    def load_config(self) -> Dict[str, Any]:
        """Load configuration from JSON file"""
        if not self.config_path.exists():
            logger.error(f"Config file {self.config_path} not found")
            # Create minimal config for fallback
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
    
    def generate_ascii_header(self) -> str:
        """Generate ASCII art header for the newsletter"""
        date_str = datetime.now().strftime("%B %d, %Y")
        padding = (67 - len(date_str)) // 2
        
        return f"""
╔═══════════════════════════════════════════════════════════════════╗
║                          CYBERBRIEF DAILY                        ║
║               Executive Cyber Threat Intelligence                 ║
║{' ' * padding}{date_str}{' ' * (67 - len(date_str) - padding)}║
╚═══════════════════════════════════════════════════════════════════╝

"""
    
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
                        if self.is_business_relevant(title, desc):
                            articles.append({
                                'title': title,
                                'link': link,
                                'description': desc,
                                'published': pub_date,
                                'source': 'BleepingComputer'
                            })
                            
                except Exception as e:
                    logger.error(f"Error parsing RSS item: {e}")
                    continue
                    
            logger.info(f"Found {len(articles)} relevant articles from BleepingComputer")
                    
        except Exception as e:
            logger.error(f"Error fetching BleepingComputer RSS: {e}")
            
        return articles
    
    def is_business_relevant(self, title: str, description: str) -> bool:
        """Check if article is relevant to business executives"""
        text = f"{title} {description}".lower()
        
        # Exclude consumer/IoT topics
        exclude_terms = self.config.get('content', {}).get('exclude_topics', [])
        exclude_terms = [term.lower() for term in exclude_terms]
        if any(term in text for term in exclude_terms):
            return False
            
        # Include enterprise/business relevant terms
        include_terms = [
            'ransomware', 'enterprise', 'corporate', 'business', 'zero-day', 'critical',
            'vulnerability', 'breach', 'attack', 'malware', 'supply chain', 'data',
            'microsoft', 'windows', 'linux', 'server', 'database', 'cloud', 'aws',
            'google', 'azure', 'healthcare', 'financial', 'banking', 'government',
            'phishing', 'social engineering', 'insider threat', 'compliance'
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
            
            # Sort by date added (newest first) and limit to recent additions
            vulnerabilities.sort(key=lambda x: x['date_added'], reverse=True)
            vulnerabilities = vulnerabilities[:8]
            
            logger.info(f"Found {len(vulnerabilities)} recent vulnerabilities from CISA KEV")
            
        except Exception as e:
            logger.error(f"Error fetching CISA KEV data: {e}")
            
        return vulnerabilities
    
    def fetch_security_blogs(self) -> List[Dict]:
        """Fetch from known security blogs"""
        blogs = []
        
        # Try major security blogs
        blog_sources = [
            {"name": "Krebs on Security", "rss": "https://krebsonsecurity.com/feed/"},
            {"name": "Schneier on Security", "rss": "https://www.schneier.com/blog/atom.xml"},
            {"name": "SANS ISC Diary", "rss": "https://isc.sans.edu/rssfeed.xml"},
            {"name": "Threatpost", "rss": "https://threatpost.com/feed/"},
        ]
        
        for blog in blog_sources:
            try:
                logger.info(f"Checking {blog['name']}...")
                rss_content = self.fetch_url(blog["rss"])
                
                if not rss_content:
                    continue
                    
                # Parse RSS/Atom
                root = ET.fromstring(rss_content)
                recent_posts = []
                
                # Handle both RSS and Atom formats
                items = root.findall('.//item') or root.findall('.//{http://www.w3.org/2005/Atom}entry')
                
                for item in items[:3]:  # Get recent 3 posts
                    try:
                        # Try RSS format first
                        title_elem = item.find('title')
                        link_elem = item.find('link')
                        
                        # Try Atom format if RSS fails
                        if title_elem is None:
                            title_elem = item.find('.//{http://www.w3.org/2005/Atom}title')
                        if link_elem is None:
                            link_elem = item.find('.//{http://www.w3.org/2005/Atom}link')
                            
                        if title_elem is not None and link_elem is not None:
                            title = title_elem.text.strip() if title_elem.text else ""
                            
                            # Extract link (handle both RSS and Atom)
                            if hasattr(link_elem, 'get') and link_elem.get('href'):
                                link = link_elem.get('href')
                            else:
                                link = link_elem.text.strip() if link_elem.text else ""
                            
                            if title and link:
                                recent_posts.append({
                                    'title': title,
                                    'link': link
                                })
                                
                    except Exception as e:
                        logger.error(f"Error parsing blog post from {blog['name']}: {e}")
                        continue
                
                if recent_posts:
                    blogs.append({
                        'name': blog['name'],
                        'recent_posts': recent_posts
                    })
                    logger.info(f"Found {len(recent_posts)} posts from {blog['name']}")
                    
            except Exception as e:
                logger.error(f"Error fetching {blog['name']}: {e}")
                continue
        
        return blogs[:5]  # Return top 5
    
    def analyze_business_impact(self, article: Dict) -> str:
        """Analyze business impact without AI - pattern matching"""
        title = article['title'].lower()
        desc = article.get('description', '').lower()
        text = f"{title} {desc}"
        
        # High impact patterns
        if any(term in text for term in ['ransomware', 'zero-day', 'critical vulnerability', 'supply chain', 'data breach', 'major breach']):
            if 'ransomware' in text:
                return "BUSINESS IMPACT: HIGH - Ransomware can cause complete operational shutdown, significant recovery costs, and regulatory compliance issues. Review backup systems and incident response procedures immediately."
            elif 'zero-day' in text or 'zero day' in text:
                return "BUSINESS IMPACT: HIGH - Zero-day vulnerabilities require immediate attention as patches may not be available. Consider additional monitoring and containment measures."
            elif 'supply chain' in text:
                return "BUSINESS IMPACT: HIGH - Supply chain attacks can compromise entire business ecosystems. Review vendor security assessments and third-party risk management."
            elif 'breach' in text and any(x in text for x in ['data', 'customer', 'personal', 'credit']):
                return "BUSINESS IMPACT: HIGH - Data breaches carry regulatory, financial, and reputational risks. Legal and PR response may be required."
        
        # Medium-high impact patterns
        elif any(term in text for term in ['critical', 'exploit', 'rce', 'remote code execution']):
            return "BUSINESS IMPACT: MEDIUM-HIGH - Critical vulnerability requiring prompt attention. Assess exposure and prioritize patching efforts."
        
        # Medium impact patterns
        elif any(term in text for term in ['vulnerability', 'attack', 'malware', 'phishing']):
            return "BUSINESS IMPACT: MEDIUM - Cybersecurity threat requiring attention. Review current security posture and ensure appropriate defenses are in place."
        
        # Default
        return "BUSINESS IMPACT: MEDIUM - Emerging cybersecurity concern. Monitor for developments and assess potential impact on business operations."
    
    def generate_newsletter(self) -> str:
        """Generate newsletter with real data"""
        logger.info("Generating CyberBrief Daily with live data...")
        
        # Fetch real data
        articles = self.fetch_bleepingcomputer_articles()
        vulnerabilities = self.fetch_cisa_kev()
        blogs = self.fetch_security_blogs()
        
        # Start building newsletter
        newsletter = self.generate_ascii_header()
        
        # Top Articles Section
        newsletter += "═" * 67 + "\n"
        newsletter += "🔥 TOP CYBER THREATS TODAY\n"
        newsletter += "═" * 67 + "\n\n"
        
        if articles:
            max_articles = self.config.get('content', {}).get('max_articles', 3)
            for i, article in enumerate(articles[:max_articles], 1):
                impact = self.analyze_business_impact(article)
                newsletter += f"{i}. {article['title']}\n"
                newsletter += f"   Source: {article['source']}\n"
                newsletter += f"   {impact}\n"
                newsletter += f"   Read more: {article['link']}\n\n"
        else:
            newsletter += "No major cybersecurity threats detected in current feeds.\n\n"
        
        # Vulnerabilities Section
        newsletter += "═" * 67 + "\n"
        newsletter += "🚨 RECENT KNOWN EXPLOITABLE VULNERABILITIES\n"
        newsletter += "═" * 67 + "\n\n"
        
        if vulnerabilities:
            for vuln in vulnerabilities[:5]:
                newsletter += f"• CVE: {vuln['cve_id']}\n"
                newsletter += f"  Vendor: {vuln['vendor_project']}\n"
                newsletter += f"  Product: {vuln['product']}\n"
                newsletter += f"  Added: {vuln['date_added'].strftime('%Y-%m-%d')}\n"
                newsletter += f"  Risk: {vuln['short_description'][:100]}{'...' if len(vuln['short_description']) > 100 else ''}\n"
                if vuln.get('required_action'):
                    action = vuln['required_action'][:80]
                    newsletter += f"  Action: {action}{'...' if len(vuln['required_action']) > 80 else ''}\n"
                newsletter += "\n"
        else:
            newsletter += "No new known exploitable vulnerabilities in recent weeks.\n\n"
        
        # Active Blogs Section
        newsletter += "═" * 67 + "\n"
        newsletter += "📖 ACTIVE SECURITY BLOGS TODAY\n"  
        newsletter += "═" * 67 + "\n\n"
        
        if blogs:
            for i, blog in enumerate(blogs, 1):
                newsletter += f"{i}. {blog['name']}\n"
                if blog.get('recent_posts'):
                    for post in blog['recent_posts'][:2]:  # Show top 2 posts
                        newsletter += f"   • {post['title']}\n"
                        newsletter += f"     {post['link']}\n"
                newsletter += "\n"
        else:
            newsletter += "Unable to retrieve active security blog content at this time.\n\n"
        
        # Footer
        newsletter += "═" * 67 + "\n"
        newsletter += "Generated by CyberBrief Daily\n"
        mst_time = datetime.now() - timedelta(hours=7)  # Convert to MST
        newsletter += f"Report generated: {mst_time.strftime('%Y-%m-%d %H:%M:%S MST')}\n"
        newsletter += "Source: Real-time feeds from BleepingComputer, CISA KEV, security blogs\n"
        newsletter += "═" * 67 + "\n"
        
        return newsletter
    
    def send_email(self, content: str) -> bool:
        """Send newsletter via email"""
        try:
            email_config = self.config.get('email', {})
            
            # Check if email is configured
            if not email_config.get('username') or not email_config.get('password'):
                logger.info("Email not configured - saving newsletter to file only")
                return False
            
            # Create message
            msg = MIMEText(content)
            msg['Subject'] = f"CyberBrief Daily - Executive Threat Intelligence - {datetime.now().strftime('%B %d, %Y')}"
            msg['From'] = email_config['from_addr']
            msg['To'] = ", ".join(email_config['to_addrs'])
            
            # Connect to SMTP server
            logger.info("Connecting to email server...")
            with smtplib.SMTP(email_config['smtp_server'], email_config['smtp_port']) as server:
                server.starttls()
                server.login(email_config['username'], email_config['password'])
                
                # Send to all recipients
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
            logger.info("Starting CyberBrief Daily generation")
            
            # Generate newsletter content
            newsletter_content = self.generate_newsletter()
            
            # Save backup
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            backup_file = f"newsletters/cyberbrief_{timestamp}.txt"
            
            with open(backup_file, 'w', encoding='utf-8') as f:
                f.write(newsletter_content)
            logger.info(f"Newsletter saved to {backup_file}")
            
            # Try to send email
            email_sent = self.send_email(newsletter_content)
            
            if email_sent:
                logger.info("CyberBrief Daily completed successfully - email sent")
            else:
                logger.info("CyberBrief Daily completed - newsletter saved to file (email not configured)")
                # Still print to console for manual review
                print("\n" + "="*60)
                print("CYBERBRIEF DAILY - SAVED TO FILE")
                print("="*60)
                print(newsletter_content[:1000] + "..." if len(newsletter_content) > 1000 else newsletter_content)
            
            return True
            
        except Exception as e:
            logger.error(f"Error in CyberBrief execution: {e}")
            return False

def main():
    """Main entry point"""
    try:
        brief = CyberBriefProduction()
        success = brief.run()
        sys.exit(0 if success else 1)
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()