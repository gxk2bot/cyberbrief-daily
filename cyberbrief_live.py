#!/usr/bin/env python3
"""
CyberBrief Daily - Live Data Version
Fetches real threat intelligence from current sources
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

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class CyberBriefLive:
    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        
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
            
            for item in root.findall('.//item')[:10]:
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
        exclude_terms = ['iot', 'smart home', 'consumer', 'gaming', 'personal', 'home router', 'wifi router']
        if any(term in text for term in exclude_terms):
            return False
            
        # Include enterprise/business relevant terms
        include_terms = [
            'ransomware', 'enterprise', 'corporate', 'business', 'zero-day', 'critical',
            'vulnerability', 'breach', 'attack', 'malware', 'supply chain', 'data',
            'microsoft', 'windows', 'linux', 'server', 'database', 'cloud', 'aws',
            'google', 'azure', 'healthcare', 'financial', 'banking', 'government'
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
            
            # Get vulnerabilities added in last 30 days
            cutoff_date = datetime.now() - timedelta(days=30)
            
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
            vulnerabilities = vulnerabilities[:10]
            
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
            {"name": "Dark Reading", "rss": "https://www.darkreading.com/rss/all.xml"},
            {"name": "Security Week", "rss": "https://www.securityweek.com/rss/"},
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
        if any(term in text for term in ['ransomware', 'zero-day', 'critical vulnerability', 'supply chain', 'breach']):
            if 'ransomware' in text:
                return "BUSINESS IMPACT: HIGH - Ransomware can cause complete operational shutdown, significant recovery costs, and regulatory compliance issues. Review backup systems and incident response procedures immediately."
            elif 'zero-day' in text:
                return "BUSINESS IMPACT: HIGH - Zero-day vulnerabilities require immediate attention as patches may not be available. Consider additional monitoring and containment measures."
            elif 'supply chain' in text:
                return "BUSINESS IMPACT: HIGH - Supply chain attacks can compromise entire business ecosystems. Review vendor security assessments and third-party risk management."
            elif 'breach' in text:
                return "BUSINESS IMPACT: HIGH - Data breaches carry regulatory, financial, and reputational risks. Legal and PR response may be required."
        
        # Medium impact patterns
        elif any(term in text for term in ['vulnerability', 'exploit', 'malware', 'attack']):
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
            for i, article in enumerate(articles[:3], 1):
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
                newsletter += f"  Risk: {vuln['short_description']}\n"
                if vuln.get('required_action'):
                    newsletter += f"  Action: {vuln['required_action']}\n"
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
        newsletter += "Generated by CyberBrief Daily (Live Data)\n"
        newsletter += f"Report generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC')}\n"
        newsletter += "Source: Real-time feeds from BleepingComputer, CISA KEV, and security blogs\n"
        newsletter += "═" * 67 + "\n"
        
        return newsletter
    
    def send_email(self, content: str, to_email: str):
        """Send newsletter via email using Gmail SMTP"""
        # This is a simplified version - you'd need real SMTP credentials
        logger.info(f"Would send newsletter to {to_email}")
        logger.info("Email sending requires SMTP configuration")
        
    def run(self, save_only: bool = True) -> str:
        """Generate newsletter and optionally send"""
        try:
            newsletter_content = self.generate_newsletter()
            
            # Save to file
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"cyberbrief_live_{timestamp}.txt"
            
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(newsletter_content)
            
            logger.info(f"Live newsletter saved to {filename}")
            
            if save_only:
                print("\n" + "="*60)
                print("CYBERBRIEF DAILY - LIVE DATA") 
                print("="*60)
                print(newsletter_content)
            
            return filename
            
        except Exception as e:
            logger.error(f"Error generating live newsletter: {e}")
            raise

def main():
    """Main entry point"""
    try:
        brief = CyberBriefLive()
        brief.run()
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        return 1

if __name__ == "__main__":
    main()