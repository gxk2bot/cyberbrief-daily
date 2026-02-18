#!/usr/bin/env python3
"""
CyberBrief Daily - Automated cybersecurity newsletter
Generates daily executive-focused cyber threat intelligence emails
"""

import json
import logging
import smtplib
import sys
from datetime import datetime, timedelta
from email.mime.text import MIMEText
from pathlib import Path
from typing import List, Dict, Any

from dotenv import load_dotenv
import requests
from bs4 import BeautifulSoup
import feedparser
import openai
from newspaper import Article

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('cyberbrief.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class CyberBrief:
    def __init__(self, config_path: str = "config.json"):
        self.config_path = Path(config_path)
        self.config = self.load_config()
        
        # Initialize OpenAI
        openai.api_key = self.config["openai"]["api_key"]
        self.model = self.config["openai"]["model"]
        
    def load_config(self) -> Dict[str, Any]:
        """Load configuration from JSON file"""
        if not self.config_path.exists():
            logger.error(f"Config file {self.config_path} not found")
            sys.exit(1)
            
        with open(self.config_path, 'r') as f:
            return json.load(f)
    
    def generate_ascii_header(self) -> str:
        """Generate ASCII art header for the newsletter"""
        return """
╔═══════════════════════════════════════════════════════════════════╗
║                          CYBERBRIEF DAILY                        ║
║               Executive Cyber Threat Intelligence                 ║
║                     """ + datetime.now().strftime("%B %d, %Y") + """                      ║
╚═══════════════════════════════════════════════════════════════════╝

"""
    
    def fetch_bleepingcomputer_articles(self) -> List[Dict]:
        """Fetch recent articles from BleepingComputer RSS"""
        articles = []
        try:
            feed_url = self.config["sources"]["bleepingcomputer"]["rss_url"]
            feed = feedparser.parse(feed_url)
            
            for entry in feed.entries[:10]:  # Get recent 10 articles
                # Parse publish date
                pub_date = datetime(*entry.published_parsed[:6])
                
                # Only include articles from last 24 hours
                if pub_date > datetime.now() - timedelta(days=1):
                    articles.append({
                        'title': entry.title,
                        'link': entry.link,
                        'published': pub_date,
                        'summary': entry.summary,
                        'source': 'BleepingComputer'
                    })
                    
        except Exception as e:
            logger.error(f"Error fetching BleepingComputer articles: {e}")
            
        return articles
    
    def fetch_major_outlet_articles(self) -> List[Dict]:
        """Fetch cybersecurity articles from major news outlets"""
        articles = []
        
        # WSJ cybersecurity search
        if self.config["sources"]["major_outlets"]["check_wsj"]:
            try:
                # Note: This would require WSJ API access or web scraping
                # For demo purposes, showing structure
                logger.info("Fetching WSJ cybersecurity articles...")
            except Exception as e:
                logger.error(f"Error fetching WSJ articles: {e}")
        
        # Washington Post cybersecurity search  
        if self.config["sources"]["major_outlets"]["check_wapo"]:
            try:
                logger.info("Fetching Washington Post cybersecurity articles...")
            except Exception as e:
                logger.error(f"Error fetching Washington Post articles: {e}")
        
        return articles
    
    def fetch_cisa_kev(self) -> List[Dict]:
        """Fetch latest Known Exploitable Vulnerabilities from CISA"""
        vulnerabilities = []
        try:
            url = self.config["sources"]["cisa_kev"]["url"]
            response = requests.get(url, timeout=30)
            response.raise_for_status()
            
            lines = response.text.strip().split('\n')
            headers = lines[0].split(',')
            
            # Get vulnerabilities added in last 7 days
            recent_date = datetime.now() - timedelta(days=7)
            
            for line in lines[1:20]:  # Check recent 20 entries
                values = line.split(',')
                if len(values) >= 6:
                    try:
                        date_added = datetime.strptime(values[5], '%Y-%m-%d')
                        if date_added > recent_date:
                            vulnerabilities.append({
                                'cve_id': values[0],
                                'vendor_project': values[1],
                                'product': values[2],
                                'vulnerability_name': values[3],
                                'date_added': date_added,
                                'short_description': values[4]
                            })
                    except (ValueError, IndexError):
                        continue
                        
        except Exception as e:
            logger.error(f"Error fetching CISA KEV data: {e}")
            
        return vulnerabilities
    
    def discover_active_security_blogs(self) -> List[Dict]:
        """Discover top 5 security blogs with recent activity"""
        blogs = []
        
        # Known security blog RSS feeds
        security_blogs = [
            {"name": "Krebs on Security", "rss": "https://krebsonsecurity.com/feed/"},
            {"name": "Schneier on Security", "rss": "https://www.schneier.com/blog/atom.xml"},
            {"name": "Dark Reading", "rss": "https://www.darkreading.com/rss.xml"},
            {"name": "Threat Post", "rss": "https://threatpost.com/feed/"},
            {"name": "SecurityWeek", "rss": "https://www.securityweek.com/rss/"},
            {"name": "SANS ISC", "rss": "https://isc.sans.edu/rssfeed.xml"},
            {"name": "FireEye Threat Research", "rss": "https://www.mandiant.com/resources/blog/rss.xml"}
        ]
        
        for blog in security_blogs:
            try:
                feed = feedparser.parse(blog["rss"])
                recent_posts = []
                
                for entry in feed.entries[:5]:
                    try:
                        pub_date = datetime(*entry.published_parsed[:6])
                        if pub_date > datetime.now() - timedelta(days=1):
                            recent_posts.append({
                                'title': entry.title,
                                'link': entry.link,
                                'published': pub_date
                            })
                    except:
                        continue
                
                if recent_posts:
                    blogs.append({
                        'name': blog["name"],
                        'rss': blog["rss"],
                        'recent_posts': recent_posts
                    })
                    
            except Exception as e:
                logger.error(f"Error checking {blog['name']}: {e}")
                continue
        
        # Sort by number of recent posts and return top 5
        blogs.sort(key=lambda x: len(x['recent_posts']), reverse=True)
        return blogs[:5]
    
    def analyze_business_impact(self, article: Dict) -> str:
        """Use AI to analyze business impact of a cybersecurity article"""
        try:
            prompt = f"""
            Analyze this cybersecurity article for business impact relevant to executives:
            
            Title: {article['title']}
            Summary: {article.get('summary', article.get('content', ''))}
            
            Provide a concise one-paragraph summary focusing on:
            - Business risk and potential impact
            - What executives need to know
            - Any action items or implications
            
            Keep it executive-level, avoid technical jargon, focus on business consequences.
            """
            
            response = openai.ChatCompletion.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=200,
                temperature=0.3
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            logger.error(f"Error analyzing article impact: {e}")
            return article.get('summary', 'Unable to analyze impact')
    
    def filter_and_rank_articles(self, articles: List[Dict]) -> List[Dict]:
        """Filter and rank articles by relevance to executives"""
        # Filter out excluded topics
        exclude_terms = [term.lower() for term in self.config["content"]["exclude_topics"]]
        
        filtered_articles = []
        for article in articles:
            text_to_check = f"{article['title']} {article.get('summary', '')}".lower()
            
            # Skip if contains excluded terms
            if any(term in text_to_check for term in exclude_terms):
                continue
                
            # Basic relevance scoring (can be enhanced)
            score = 0
            focus_areas = [area.lower() for area in self.config["content"]["focus_areas"]]
            for area in focus_areas:
                if area in text_to_check:
                    score += 1
            
            article['relevance_score'] = score
            filtered_articles.append(article)
        
        # Sort by relevance score and recency
        filtered_articles.sort(key=lambda x: (x['relevance_score'], x['published']), reverse=True)
        
        return filtered_articles[:self.config["content"]["max_articles"]]
    
    def generate_newsletter(self) -> str:
        """Generate the complete newsletter content"""
        logger.info("Generating CyberBrief Daily newsletter...")
        
        # Fetch content
        bleeping_articles = self.fetch_bleepingcomputer_articles()
        major_articles = self.fetch_major_outlet_articles()
        vulnerabilities = self.fetch_cisa_kev()
        active_blogs = self.discover_active_security_blogs()
        
        # Combine and filter articles
        all_articles = bleeping_articles + major_articles
        top_articles = self.filter_and_rank_articles(all_articles)
        
        # Start building newsletter
        newsletter = self.generate_ascii_header()
        
        # Top 3 Articles Section
        newsletter += "═" * 67 + "\n"
        newsletter += "🔥 TOP CYBER THREATS TODAY\n"
        newsletter += "═" * 67 + "\n\n"
        
        if top_articles:
            for i, article in enumerate(top_articles, 1):
                business_impact = self.analyze_business_impact(article)
                newsletter += f"{i}. {article['title']}\n"
                newsletter += f"   Source: {article['source']}\n"
                newsletter += f"   Impact: {business_impact}\n"
                newsletter += f"   Read more: {article['link']}\n\n"
        else:
            newsletter += "No significant threat articles found in the last 24 hours.\n\n"
        
        # Vulnerabilities Section
        newsletter += "═" * 67 + "\n"
        newsletter += "🚨 KNOWN EXPLOITABLE VULNERABILITIES\n"
        newsletter += "═" * 67 + "\n\n"
        
        if vulnerabilities:
            for vuln in vulnerabilities[:5]:
                newsletter += f"• CVE: {vuln['cve_id']}\n"
                newsletter += f"  Vendor: {vuln['vendor_project']}\n"
                newsletter += f"  Product: {vuln['product']}\n"
                newsletter += f"  Added: {vuln['date_added'].strftime('%Y-%m-%d')}\n"
                newsletter += f"  Risk: {vuln['short_description']}\n\n"
        else:
            newsletter += "No new known exploitable vulnerabilities in the past week.\n\n"
        
        # Active Blogs Section
        newsletter += "═" * 67 + "\n"
        newsletter += "📖 ACTIVE SECURITY BLOGS TODAY\n"
        newsletter += "═" * 67 + "\n\n"
        
        if active_blogs:
            for i, blog in enumerate(active_blogs, 1):
                newsletter += f"{i}. {blog['name']}\n"
                if blog['recent_posts']:
                    latest_post = blog['recent_posts'][0]
                    newsletter += f"   Latest: {latest_post['title']}\n"
                    newsletter += f"   Link: {latest_post['link']}\n\n"
                else:
                    newsletter += f"   RSS: {blog['rss']}\n\n"
        else:
            newsletter += "No active security blogs found with recent content.\n\n"
        
        # Footer
        newsletter += "═" * 67 + "\n"
        newsletter += "Generated by CyberBrief Daily\n"
        newsletter += f"Report generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S MST')}\n"
        newsletter += "═" * 67 + "\n"
        
        return newsletter
    
    def send_email(self, content: str):
        """Send the newsletter via email"""
        try:
            msg = MIMEText(content)
            msg['Subject'] = f"CyberBrief Daily - {datetime.now().strftime('%B %d, %Y')}"
            msg['From'] = self.config["email"]["from_addr"]
            msg['To'] = ", ".join(self.config["email"]["to_addrs"])
            
            # Connect to SMTP server
            with smtplib.SMTP(self.config["email"]["smtp_server"], self.config["email"]["smtp_port"]) as server:
                server.starttls()
                server.login(self.config["email"]["username"], self.config["email"]["password"])
                
                # Send to all recipients
                for to_addr in self.config["email"]["to_addrs"]:
                    server.send_message(msg, to_addrs=[to_addr])
            
            logger.info(f"Newsletter sent successfully to {len(self.config['email']['to_addrs'])} recipients")
            
        except Exception as e:
            logger.error(f"Error sending email: {e}")
            raise
    
    def run(self):
        """Main execution function"""
        try:
            logger.info("Starting CyberBrief Daily generation")
            
            # Generate newsletter content
            newsletter_content = self.generate_newsletter()
            
            # Save to file for backup
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            backup_file = f"newsletters/cyberbrief_{timestamp}.txt"
            Path("newsletters").mkdir(exist_ok=True)
            
            with open(backup_file, 'w', encoding='utf-8') as f:
                f.write(newsletter_content)
            logger.info(f"Newsletter saved to {backup_file}")
            
            # Send email
            self.send_email(newsletter_content)
            
            logger.info("CyberBrief Daily completed successfully")
            
        except Exception as e:
            logger.error(f"Error in CyberBrief execution: {e}")
            raise

def main():
    """Main entry point"""
    try:
        brief = CyberBrief()
        brief.run()
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()