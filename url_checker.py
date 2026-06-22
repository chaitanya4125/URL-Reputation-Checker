#!/usr/bin/env python3
"""
URL Reputation Checker - Check URLs against known malicious patterns
Single file, zero dependencies
"""

import re
import ssl
import socket
from urllib.parse import urlparse
from datetime import datetime

class URLReputationChecker:
    def __init__(self):
        # Known malicious patterns
        self.suspicious_patterns = [
            r'\.tk$', r'\.ml$', r'\.ga$', r'\.cf$',  # Free domains often abused
            r'\.xyz$', r'\.top$', r'\.work$', r'\.date$',
            r'paypal.*\.(?!paypal\.com)',  # PayPal phishing
            r'bank.*\.(?!.*\.bank\.)',      # Bank phishing
            r'secure.*login',               # Fake login pages
            r'free.*gift',                  # Scam patterns
            r'win.*prize',                  # Fake prizes
            r'verify.*account',             # Phishing
            r'update.*payment',             # Payment scams
        ]
        
        # Known malicious TLDs
        self.risky_tlds = ['.tk', '.ml', '.ga', '.cf', '.xyz', '.top', '.work', '.date', '.gq']
        
        # Shortened URL services (often used to hide malicious URLs)
        self.shorteners = ['bit.ly', 'tinyurl.com', 't.co', 'goo.gl', 'ow.ly', 'is.gd', 'buff.ly']
    
    def check_url(self, url):
        """Check a URL and return risk assessment"""
        if not url.startswith(('http://', 'https://')):
            url = 'http://' + url
        
        result = {
            'url': url,
            'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            'risk_score': 0,
            'risk_level': 'SAFE',
            'warnings': [],
            'details': {}
        }
        
        try:
            parsed = urlparse(url)
            domain = parsed.netloc.lower()
            path = parsed.path.lower()
            full_url = url.lower()
            
            # Check 1: Suspicious TLDs
            for tld in self.risky_tlds:
                if domain.endswith(tld):
                    result['warnings'].append(f"⚠️  Risky TLD detected: {tld}")
                    result['risk_score'] += 30
            
            # Check 2: URL Shorteners
            for shortener in self.shorteners:
                if shortener in domain:
                    result['warnings'].append(f"⚠️  Shortened URL detected: {shortener}")
                    result['risk_score'] += 20
            
            # Check 3: IP Address instead of domain
            if re.match(r'^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}', domain):
                result['warnings'].append(f"⚠️  IP address used instead of domain")
                result['risk_score'] += 25
            
            # Check 4: Suspicious patterns
            for pattern in self.suspicious_patterns:
                if re.search(pattern, full_url, re.IGNORECASE):
                    result['warnings'].append(f"⚠️  Suspicious pattern detected: {pattern}")
                    result['risk_score'] += 20
            
            # Check 5: Excessive subdomains
            subdomains = domain.split('.')
            if len(subdomains) > 4:
                result['warnings'].append(f"⚠️  Excessive subdomains ({len(subdomains)} levels)")
                result['risk_score'] += 15
            
            # Check 6: Special characters in domain
            if re.search(r'[@!~`]', domain):
                result['warnings'].append(f"⚠️  Special characters in domain")
                result['risk_score'] += 25
            
            # Check 7: Long URL (potential obfuscation)
            if len(url) > 100:
                result['warnings'].append(f"⚠️  Unusually long URL ({len(url)} chars)")
                result['risk_score'] += 10
            
            # Check 8: HTTP vs HTTPS
            if not url.startswith('https://'):
                result['warnings'].append(f"⚠️  Not using HTTPS")
                result['risk_score'] += 10
            
            # Determine risk level
            if result['risk_score'] >= 60:
                result['risk_level'] = '🔴 HIGH RISK'
            elif result['risk_score'] >= 30:
                result['risk_level'] = '🟡 MEDIUM RISK'
            elif result['risk_score'] >= 10:
                result['risk_level'] = '🟢 LOW RISK'
            else:
                result['risk_level'] = '✅ SAFE'
            
            result['details'] = {
                'domain': domain,
                'path': path,
                'length': len(url),
                'uses_https': url.startswith('https://')
            }
            
        except Exception as e:
            result['warnings'].append(f"❌ Error parsing URL: {str(e)}")
            result['risk_level'] = '❓ UNKNOWN'
        
        return result
    
    def check_multiple(self, urls):
        """Check multiple URLs"""
        results = []
        for url in urls:
            results.append(self.check_url(url.strip()))
        return results

def main():
    print("="*60)
    print("  🔍 URL REPUTATION CHECKER - SOC Tool")
    print("="*60)
    print("\nChecks URLs for phishing, malware, and suspicious patterns\n")
    
    checker = URLReputationChecker()
    
    while True:
        print("-"*60)
        print("Options:")
        print("1. Check a single URL")
        print("2. Check multiple URLs (comma-separated)")
        print("3. Demo (test with sample URLs)")
        print("4. Exit")
        
        choice = input("\nChoice (1-4): ").strip()
        
        if choice == "1":
            url = input("Enter URL: ").strip()
            if url:
                result = checker.check_url(url)
                print_result(result)
        
        elif choice == "2":
            urls = input("Enter URLs (comma-separated): ").strip()
            if urls:
                url_list = [u.strip() for u in urls.split(',')]
                results = checker.check_multiple(url_list)
                for result in results:
                    print_result(result)
        
        elif choice == "3":
            print("\n🔬 Running demo with sample URLs...\n")
            sample_urls = [
                "https://google.com",
                "http://paypal-secure.tk/login",
                "https://bit.ly/3xK9mN2",
                "http://192.168.1.1/admin",
                "https://www.facebook.com",
                "http://free-prize-winner.xyz/claim",
                "https://github.com",
                "http://bank-verify-account.ml/update",
            ]
            
            for url in sample_urls:
                result = checker.check_url(url)
                print_result(result)
        
        elif choice == "4":
            print("\n👋 Goodbye!")
            break
        
        else:
            print("❌ Invalid choice!")

def print_result(result):
    """Print formatted result"""
    print(f"\n{'='*50}")
    print(f"  {result['risk_level']}")
    print(f"{'='*50}")
    print(f"  URL: {result['url']}")
    print(f"  Time: {result['timestamp']}")
    print(f"  Risk Score: {result['risk_score']}/100")
    
    if result['warnings']:
        print(f"\n  Warnings:")
        for warning in result['warnings']:
            print(f"    {warning}")
    else:
        print(f"\n  ✅ No warnings detected")
    
    print(f"{'='*50}\n")

if __name__ == "__main__":
    main()