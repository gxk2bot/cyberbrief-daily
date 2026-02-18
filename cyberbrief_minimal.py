#!/usr/bin/env python3
"""
CyberBrief Daily - Minimal version for testing
Basic structure without heavy dependencies
"""

import json
import logging
import smtplib
import sys
import urllib.request
import urllib.parse
from datetime import datetime, timedelta
from email.mime.text import MIMEText
from pathlib import Path
from typing import List, Dict, Any

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class CyberBriefMinimal:
    def __init__(self, config_path: str = "config.json"):
        self.config_path = Path(config_path)
        self.config = self.load_config() if self.config_path.exists() else self.get_default_config()
        
    def get_default_config(self) -> Dict[str, Any]:
        """Default configuration for testing"""
        return {
            "email": {
                "smtp_server": "smtp.gmail.com",
                "smtp_port": 587,
                "username": "test@example.com",
                "password": "test-password",
                "from_addr": "test@example.com",
                "to_addrs": ["recipient@example.com"]
            },
            "openai": {
                "api_key": "test-key",
                "model": "gpt-4"
            },
            "sources": {
                "bleepingcomputer": {"enabled": True},
                "cisa_kev": {"enabled": True}
            },
            "content": {
                "max_articles": 3,
                "max_blogs": 5,
                "exclude_topics": ["IoT vulnerabilities"],
                "focus_areas": ["business impact", "trending threats"]
            }
        }
        
    def load_config(self) -> Dict[str, Any]:
        """Load configuration from JSON file"""
        try:
            with open(self.config_path, 'r') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Error loading config: {e}")
            return self.get_default_config()
    
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
    
    def fetch_sample_articles(self) -> List[Dict]:
        """Generate sample articles for testing"""
        return [
            {
                'title': 'Major Ransomware Group Targets Healthcare Sector',
                'link': 'https://example.com/article1',
                'published': datetime.now() - timedelta(hours=2),
                'summary': 'New ransomware variant specifically targeting hospital systems',
                'source': 'BleepingComputer',
                'relevance_score': 3
            },
            {
                'title': 'Critical Zero-Day Exploited in Enterprise Software',
                'link': 'https://example.com/article2', 
                'published': datetime.now() - timedelta(hours=4),
                'summary': 'Widespread exploitation of unpatched vulnerability in corporate environments',
                'source': 'Security Week',
                'relevance_score': 3
            },
            {
                'title': 'Supply Chain Attack Affects Fortune 500 Companies',
                'link': 'https://example.com/article3',
                'published': datetime.now() - timedelta(hours=6),
                'summary': 'Compromised software update mechanism leads to widespread breaches',
                'source': 'Dark Reading',
                'relevance_score': 2
            }
        ]
    
    def fetch_sample_vulnerabilities(self) -> List[Dict]:
        """Generate sample vulnerabilities for testing"""
        return [
            {
                'cve_id': 'CVE-2024-1234',
                'vendor_project': 'Microsoft',
                'product': 'Windows',
                'vulnerability_name': 'Remote Code Execution',
                'date_added': datetime.now() - timedelta(days=1),
                'short_description': 'Authentication bypass leading to RCE'
            },
            {
                'cve_id': 'CVE-2024-5678', 
                'vendor_project': 'Apache',
                'product': 'HTTP Server',
                'vulnerability_name': 'Information Disclosure',
                'date_added': datetime.now() - timedelta(days=2),
                'short_description': 'Directory traversal vulnerability'
            }
        ]
    
    def fetch_sample_blogs(self) -> List[Dict]:
        """Generate sample active blogs for testing"""
        return [
            {
                'name': 'Krebs on Security',
                'recent_posts': [
                    {
                        'title': 'New Banking Trojan Campaign Discovered',
                        'link': 'https://krebsonsecurity.com/2024/02/banking-trojan/',
                        'published': datetime.now() - timedelta(hours=3)
                    }
                ]
            },
            {
                'name': 'Schneier on Security',
                'recent_posts': [
                    {
                        'title': 'AI Security Implications for Enterprise',
                        'link': 'https://schneier.com/blog/ai-security/',
                        'published': datetime.now() - timedelta(hours=5)
                    }
                ]
            },
            {
                'name': 'SANS ISC',
                'recent_posts': [
                    {
                        'title': 'Network Anomaly Detection Techniques',
                        'link': 'https://isc.sans.edu/diary/detection/',
                        'published': datetime.now() - timedelta(hours=8)
                    }
                ]
            }
        ]
    
    def analyze_business_impact_simple(self, article: Dict) -> str:
        """Simple business impact analysis without AI"""
        # Basic impact analysis based on keywords
        title = article['title'].lower()
        summary = article.get('summary', '').lower()
        
        high_impact_keywords = ['ransomware', 'zero-day', 'critical', 'breach', 'supply chain']
        medium_impact_keywords = ['vulnerability', 'exploit', 'attack', 'malware']
        
        impact_level = "LOW"
        if any(keyword in title or keyword in summary for keyword in high_impact_keywords):
            impact_level = "HIGH"
        elif any(keyword in title or keyword in summary for keyword in medium_impact_keywords):
            impact_level = "MEDIUM"
        
        # Generate simple business-focused summary
        if 'ransomware' in title or 'ransomware' in summary:
            return f"BUSINESS IMPACT: {impact_level} - Ransomware threats can cause operational shutdown, data loss, and significant recovery costs. Immediate review of backup systems and incident response procedures recommended."
        elif 'zero-day' in title or 'zero-day' in summary:
            return f"BUSINESS IMPACT: {impact_level} - Unpatched vulnerabilities pose immediate risk. Emergency patching may be required, potentially disrupting operations."
        elif 'supply chain' in title or 'supply chain' in summary:
            return f"BUSINESS IMPACT: {impact_level} - Third-party risks affect entire business ecosystem. Vendor security assessments should be reviewed."
        else:
            return f"BUSINESS IMPACT: {impact_level} - {article.get('summary', 'Cybersecurity incident requiring executive awareness and potential action.')}"
    
    def generate_newsletter(self) -> str:
        """Generate the complete newsletter content"""
        logger.info("Generating CyberBrief Daily newsletter...")
        
        # Fetch sample content
        top_articles = self.fetch_sample_articles()
        vulnerabilities = self.fetch_sample_vulnerabilities()
        active_blogs = self.fetch_sample_blogs()
        
        # Start building newsletter
        newsletter = self.generate_ascii_header()
        
        # Top 3 Articles Section
        newsletter += "═" * 67 + "\n"
        newsletter += "🔥 TOP CYBER THREATS TODAY\n"
        newsletter += "═" * 67 + "\n\n"
        
        for i, article in enumerate(top_articles[:3], 1):
            business_impact = self.analyze_business_impact_simple(article)
            newsletter += f"{i}. {article['title']}\n"
            newsletter += f"   Source: {article['source']}\n"
            newsletter += f"   {business_impact}\n"
            newsletter += f"   Read more: {article['link']}\n\n"
        
        # Vulnerabilities Section  
        newsletter += "═" * 67 + "\n"
        newsletter += "🚨 KNOWN EXPLOITABLE VULNERABILITIES\n"
        newsletter += "═" * 67 + "\n\n"
        
        for vuln in vulnerabilities:
            newsletter += f"• CVE: {vuln['cve_id']}\n"
            newsletter += f"  Vendor: {vuln['vendor_project']}\n"
            newsletter += f"  Product: {vuln['product']}\n"
            newsletter += f"  Added: {vuln['date_added'].strftime('%Y-%m-%d')}\n"
            newsletter += f"  Risk: {vuln['short_description']}\n\n"
        
        # Active Blogs Section
        newsletter += "═" * 67 + "\n"
        newsletter += "📖 ACTIVE SECURITY BLOGS TODAY\n"
        newsletter += "═" * 67 + "\n\n"
        
        for i, blog in enumerate(active_blogs, 1):
            newsletter += f"{i}. {blog['name']}\n"
            if blog['recent_posts']:
                latest_post = blog['recent_posts'][0]
                newsletter += f"   Latest: {latest_post['title']}\n"
                newsletter += f"   Link: {latest_post['link']}\n\n"
        
        # Footer
        newsletter += "═" * 67 + "\n"
        newsletter += "Generated by CyberBrief Daily (Test Mode)\n"
        newsletter += f"Report generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S MST')}\n"
        newsletter += "═" * 67 + "\n"
        
        return newsletter
    
    def save_newsletter(self, content: str) -> str:
        """Save newsletter to file"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"test_newsletter_{timestamp}.txt"
        
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(content)
        
        return filename
    
    def run(self):
        """Main execution function"""
        try:
            logger.info("Starting CyberBrief Daily generation (Test Mode)")
            
            # Generate newsletter content
            newsletter_content = self.generate_newsletter()
            
            # Save to file
            filename = self.save_newsletter(newsletter_content)
            logger.info(f"Test newsletter saved to {filename}")
            
            # Print preview
            print("\n" + "="*60)
            print("CYBERBRIEF DAILY - TEST PREVIEW")
            print("="*60)
            print(newsletter_content)
            
            logger.info("CyberBrief Daily test completed successfully")
            return filename
            
        except Exception as e:
            logger.error(f"Error in CyberBrief execution: {e}")
            raise

def main():
    """Main entry point"""
    try:
        brief = CyberBriefMinimal()
        brief.run()
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()