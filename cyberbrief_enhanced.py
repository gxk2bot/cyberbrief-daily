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
        
        # AI News - broader detection for AI security topics
        ai_keywords = [
            'artificial intelligence', 'machine learning', 'ai ', ' ai', 'llm', 'chatgpt', 'openai', 
            'neural network', 'deepfake', 'ai model', 'generative ai', 'large language model',
            'ai security', 'ai vulnerability', 'ai attack', 'prompt injection', 'ai bias',
            'grok', 'claude', 'gemini', 'copilot', 'bard', 'ai-powered', 'ai tool',
            'algorithmic', 'automated decision', 'ai system'
        ]
        if any(keyword in text for keyword in ai_keywords):
            return 'ai'
        
        # Regulation News - expanded detection
        regulation_keywords = [
            'regulatory', 'compliance fine', 'gdpr violation', 'gdpr', 'ccpa', 'sec filing', 'sec charges',
            'ftc action', 'ftc', 'cisa directive', 'cisa advisory', 'nist framework', 'government mandate',
            'new law', 'policy change', 'court ruling', 'lawsuit', 'regulatory fine',
            'compliance requirement', 'data protection law', 'privacy regulation', 'privacy law',
            'investigation', 'enforcement action', 'penalty', 'sanctions', 'court order',
            'legal settlement', 'doj', 'department of justice', 'attorney general'
        ]
        if any(keyword in text for keyword in regulation_keywords):
            return 'regulation'
        
        # Check for specific regulatory action phrases
        regulation_phrases = [
            'ordered to pay', 'fined for', 'fined ', 'regulatory action', 'compliance violation',
            'government investigation', 'legal action', 'court orders', 'settlement agreement',
            'consent decree', 'agrees to pay', 'must pay', 'penalty of', 'violating'
        ]
        if any(phrase in text for phrase in regulation_phrases):
            return 'regulation'
        
        # Check for government/agency sources
        agency_keywords = [
            'cisa ', 'fbi ', 'nsa ', 'sec ', 'ftc ', 'doj ', 'treasury', 'homeland security',
            'cyber command', 'federal', 'government', 'congress', 'senate', 'house of representatives'
        ]
        if any(keyword in text for keyword in agency_keywords):
            return 'regulation'
        
        # General Cybersecurity (default)
        return 'cybersecurity'
    
    def parse_date(self, date_str: str) -> datetime:
        """Parse various RSS date formats"""
        import email.utils
        try:
            # Try RFC 2822 format (most common in RSS)
            parsed = email.utils.parsedate_tz(date_str)
            if parsed:
                timestamp = email.utils.mktime_tz(parsed)
                return datetime.fromtimestamp(timestamp)
        except:
            pass
        
        # Fallback to current time if parsing fails
        return datetime.now()
    
    def is_recent(self, pub_date: str) -> bool:
        """Check if article was published in last 36 hours (more lenient)"""
        try:
            article_date = self.parse_date(pub_date)
            cutoff = datetime.now() - timedelta(hours=36)
            return article_date > cutoff
        except:
            # If we can't parse date, assume it's recent
            return True
    
    def get_priority_score(self, title: str, description: str) -> int:
        """Calculate priority score - higher for financial services and broad impact"""
        text = f"{title} {description}".lower()
        score = 0
        
        # Financial services keywords (highest priority)
        financial_keywords = [
            'bank', 'banking', 'financial', 'credit union', 'payment', 'fintech',
            'wall street', 'trading', 'investment', 'mortgage', 'loan', 'credit card',
            'financial services', 'financial institution', 'swift', 'fedwire', 'ach'
        ]
        for keyword in financial_keywords:
            if keyword in text:
                score += 3
                break
        
        # Broad industry impact keywords (high priority)
        broad_keywords = [
            'fortune 500', 'enterprise', 'all industries', 'widespread', 'global',
            'supply chain', 'critical infrastructure', 'healthcare', 'government',
            'microsoft', 'google', 'amazon', 'cloud', 'saas', 'zero-day', 'ransomware'
        ]
        for keyword in broad_keywords:
            if keyword in text:
                score += 2
                break
        
        # General business relevance
        business_keywords = ['corporate', 'business', 'company', 'organization']
        for keyword in business_keywords:
            if keyword in text:
                score += 1
                break
        
        return score
    
    def fetch_all_articles(self) -> List[Dict]:
        """Fetch articles from all sources and prioritize by financial/broad impact"""
        all_articles = []
        
        # Source configurations
        sources = [
            {
                'name': 'BleepingComputer',
                'url': 'https://www.bleepingcomputer.com/feed/',
                'type': 'rss'
            },
            {
                'name': 'Krebs on Security',
                'url': 'https://krebsonsecurity.com/feed/',
                'type': 'rss'
            },
            {
                'name': 'Schneier on Security', 
                'url': 'https://www.schneier.com/blog/atom.xml',
                'type': 'atom'
            },
            {
                'name': 'SANS ISC Diary',
                'url': 'https://isc.sans.edu/rssfeed.xml',
                'type': 'rss'
            },
            {
                'name': 'Threatpost',
                'url': 'https://threatpost.com/feed/',
                'type': 'rss'
            }
        ]
        
        for source in sources:
            try:
                logger.info(f"Fetching articles from {source['name']}...")
                content = self.fetch_url(source['url'])
                
                if not content:
                    continue
                
                # Parse RSS/Atom
                root = ET.fromstring(content)
                
                # Handle both RSS and Atom formats
                items = root.findall('.//item') or root.findall('.//{http://www.w3.org/2005/Atom}entry')
                
                for item in items[:20]:  # Get up to 20 articles per source
                    try:
                        # Extract title
                        title_elem = item.find('title')
                        if title_elem is None:
                            title_elem = item.find('.//{http://www.w3.org/2005/Atom}title')
                        if title_elem is None:
                            continue
                        title = title_elem.text.strip() if title_elem.text else ""
                        
                        # Extract link
                        link_elem = item.find('link')
                        if link_elem is None:
                            link_elem = item.find('.//{http://www.w3.org/2005/Atom}link')
                        if link_elem is None:
                            continue
                            
                        if hasattr(link_elem, 'get') and link_elem.get('href'):
                            link = link_elem.get('href')
                        else:
                            link = link_elem.text.strip() if link_elem.text else ""
                        
                        # Extract description
                        desc_elem = item.find('description')
                        if desc_elem is None:
                            desc_elem = item.find('summary')
                        if desc_elem is None:
                            desc_elem = item.find('.//{http://www.w3.org/2005/Atom}summary')
                        if desc_elem is None:
                            desc_elem = item.find('.//{http://www.w3.org/2005/Atom}content')
                        desc = desc_elem.text.strip() if desc_elem is not None and desc_elem.text else ""
                        
                        # Extract publication date
                        pub_elem = item.find('pubDate')
                        if pub_elem is None:
                            pub_elem = item.find('.//{http://www.w3.org/2005/Atom}published')
                        if pub_elem is None:
                            pub_elem = item.find('.//{http://www.w3.org/2005/Atom}updated')
                        pub_date = pub_elem.text.strip() if pub_elem is not None and pub_elem.text else ""
                        
                        # Skip if no title or link
                        if not title or not link:
                            continue
                        
                        # Check if recent (last 24 hours) and relevant
                        if not self.is_recent(pub_date):
                            continue
                            
                        if not self.is_relevant(title, desc):
                            continue
                        
                        # Calculate priority score
                        priority = self.get_priority_score(title, desc)
                        category = self.categorize_article({'title': title, 'description': desc})
                        
                        all_articles.append({
                            'title': title,
                            'link': link,
                            'description': desc,
                            'published': pub_date,
                            'source': source['name'],
                            'category': category,
                            'priority': priority
                        })
                        
                    except Exception as e:
                        logger.error(f"Error parsing item from {source['name']}: {e}")
                        continue
                        
                logger.info(f"Found {len([a for a in all_articles if a['source'] == source['name']])} relevant articles from {source['name']}")
                        
            except Exception as e:
                logger.error(f"Error fetching {source['name']}: {e}")
                continue
        
        # Sort all articles by priority score (highest first), then by source diversity
        all_articles.sort(key=lambda x: x['priority'], reverse=True)
        
        logger.info(f"Total articles fetched from all sources: {len(all_articles)}")
        return all_articles
    
    def is_relevant(self, title: str, description: str) -> bool:
        """Check if article is relevant to executive cybersecurity interests"""
        text = f"{title} {description}".lower()
        
        # Exclude consumer/gaming/personal/unrelated topics
        exclude_terms = [
            'gaming', 'game console', 'consumer router', 'home wifi', 'personal device', 
            'smartphone app', 'mobile game', 'personal computer', 'home security system',
            'smart tv', 'fitness tracker', 'personal data', 'individual user',
            'squid blogging', 'squid fishing', 'ebook sale', 'book sale', 'friday squid',
            'fishing tips', 'on sale', 'discount', 'recipe', 'cooking', 'travel',
            'movie review', 'book review', 'personal blog', 'personal story'
        ]
        if any(term in text for term in exclude_terms):
            return False
            
        # Exclude specific irrelevant patterns
        if 'squid' in text and 'blogging' in text:
            return False
        if 'ebook' in text and ('sale' in text or 'discount' in text):
            return False
        if len(title) > 0 and title.startswith('friday squid'):
            return False
            
        # Include business and security relevant terms
        include_terms = [
            'cyber', 'security', 'hack', 'breach', 'vulnerability', 'malware', 'ransomware',
            'attack', 'threat', 'exploit', 'zero-day', 'data breach', 'enterprise', 'corporate',
            'microsoft', 'google', 'amazon', 'cloud', 'server', 'network', 'ai security',
            'regulation', 'compliance', 'gdpr', 'government', 'critical infrastructure', 
            'supply chain', 'financial', 'banking', 'healthcare', 'manufacturing',
            'phishing', 'social engineering', 'insider threat', 'nation state',
            'criminal group', 'apt', 'advanced persistent threat', 'artificial intelligence',
            'machine learning', 'privacy', 'encryption', 'authentication', 'authorization'
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
        import html
        
        title = article['title']
        desc = article.get('description', '')
        
        # Clean HTML tags and decode HTML entities
        clean_desc = re.sub(r'<[^>]+>', '', desc)
        clean_desc = html.unescape(clean_desc)
        clean_desc = clean_desc.replace('\n', ' ').replace('\r', ' ')
        clean_desc = ' '.join(clean_desc.split())  # Normalize whitespace
        
        # Create executive-focused summary
        if len(clean_desc) > 250:
            # Find a good breaking point near 200 characters
            break_point = clean_desc.rfind('. ', 0, 200)
            if break_point > 100:
                summary = clean_desc[:break_point + 1]
            else:
                summary = clean_desc[:200].rsplit(' ', 1)[0] + "..."
        else:
            summary = clean_desc
            
        # If no good description, create executive-focused summary from title
        if not summary or len(summary) < 40:
            title_lower = title.lower()
            if any(word in title_lower for word in ['ransomware', 'ransom']):
                summary = "Ransomware attack or campaign identified with potential business impact on targeted organizations."
            elif any(word in title_lower for word in ['vulnerability', 'flaw', 'bug']):
                summary = "Security vulnerability discovered that could allow unauthorized access or system compromise."
            elif any(word in title_lower for word in ['breach', 'hack', 'compromise']):
                summary = "Cybersecurity incident reported with potential data exposure or system compromise."
            elif any(word in title_lower for word in ['ai', 'artificial intelligence', 'machine learning']):
                summary = "AI-related security development affecting enterprise systems or security practices."
            elif any(word in title_lower for word in ['regulation', 'compliance', 'legal', 'court']):
                summary = "Regulatory or legal development affecting cybersecurity compliance requirements."
            elif any(word in title_lower for word in ['malware', 'trojan', 'virus']):
                summary = "Malicious software discovered targeting business or enterprise environments."
            else:
                summary = "Cybersecurity development with potential implications for business operations."
        
        return summary.strip()
    
    def generate_newsletter(self) -> str:
        """Generate newsletter with enhanced format"""
        logger.info("Generating CyberBrief Daily with enhanced format...")
        
        # Fetch real data from all sources
        articles = self.fetch_all_articles()
        vulnerabilities = self.fetch_cisa_kev()
        
        # Categorize articles (already sorted by priority)
        cybersecurity_articles = [a for a in articles if a['category'] == 'cybersecurity']
        regulation_articles = [a for a in articles if a['category'] == 'regulation']
        ai_articles = [a for a in articles if a['category'] == 'ai']
        
        logger.info(f"Article breakdown: {len(cybersecurity_articles)} cybersecurity, {len(regulation_articles)} regulation, {len(ai_articles)} AI")
        
        # Start building newsletter
        newsletter = self.generate_header()
        
        # Cybersecurity News Section
        newsletter += "CYBERSECURITY NEWS\n"
        newsletter += "=" * 20 + "\n\n"
        
        if cybersecurity_articles:
            for article in cybersecurity_articles[:5]:  # Top 5
                summary = self.generate_article_summary(article)
                priority_indicator = " 🏦" if article['priority'] >= 3 else ""
                newsletter += f"• {article['title']}{priority_indicator}\n"
                newsletter += f"  {summary}\n"
                newsletter += f"  Source: {article['source']} | {article['link']}\n\n"
        else:
            newsletter += "No major cybersecurity news found in current feeds.\n\n"
        
        # Cybersecurity Regulation News Section
        newsletter += "CYBERSECURITY REGULATION NEWS\n"
        newsletter += "=" * 30 + "\n\n"
        
        if regulation_articles:
            for article in regulation_articles[:4]:  # Top 4
                summary = self.generate_article_summary(article)
                priority_indicator = " 🏦" if article['priority'] >= 3 else ""
                newsletter += f"• {article['title']}{priority_indicator}\n"
                newsletter += f"  {summary}\n"
                newsletter += f"  Source: {article['source']} | {article['link']}\n\n"
        else:
            newsletter += "No cybersecurity regulation news found in current feeds.\n\n"
        
        # AI News Section
        newsletter += "AI NEWS\n"
        newsletter += "=" * 8 + "\n\n"
        
        if ai_articles:
            for article in ai_articles[:4]:  # Top 4
                summary = self.generate_article_summary(article)
                priority_indicator = " 🏦" if article['priority'] >= 3 else ""
                newsletter += f"• {article['title']}{priority_indicator}\n"
                newsletter += f"  {summary}\n"
                newsletter += f"  Source: {article['source']} | {article['link']}\n\n"
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
        newsletter += "Sources: BleepingComputer, Krebs on Security, Schneier on Security,\n"
        newsletter += "         SANS ISC, Threatpost, CISA KEV\n"
        newsletter += "🏦 = Financial services priority\n"
        
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