#!/usr/bin/env python3
"""
ROUND 5: Advanced Header Warfare
Advanced session simulation and header rotation to defeat Indeed
"""

import requests
import json
import time
import random
from datetime import datetime
from pathlib import Path
from urllib.parse import quote_plus


class IndeedWarrior:
    """Advanced Indeed scraper with session simulation"""
    
    def __init__(self):
        self.session = requests.Session()
        self.base_dir = Path(__file__).parent / "scraped_data" / "raw"
        
    def get_rotating_headers(self):
        """Rotate between different browser profiles"""
        profiles = [
            {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
                'Accept-Language': 'en-US,en;q=0.9',
                'Accept-Encoding': 'gzip, deflate, br',
                'Sec-Ch-Ua': '"Not_A Brand";v="8", "Chromium";v="120", "Google Chrome";v="120"',
                'Sec-Ch-Ua-Platform': '"Windows"'
            },
            {
                'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.9',
                'Accept-Encoding': 'gzip, deflate, br',
                'Sec-Ch-Ua': '"Not_A Brand";v="8", "Chromium";v="120", "Google Chrome";v="120"',
                'Sec-Ch-Ua-Platform': '"macOS"'
            }
        ]
        
        profile = random.choice(profiles)
        profile.update({
            'DNT': '1',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'none',
            'Cache-Control': 'max-age=0'
        })
        
        return profile
    
    def simulate_human_session(self):
        """Simulate human browsing behavior"""
        print("🎭 Starting human behavior simulation...")
        
        # Step 1: Visit Indeed homepage
        print("1. Visiting Indeed homepage...")
        self.session.headers.update(self.get_rotating_headers())
        
        homepage_response = self.session.get('https://www.indeed.com', timeout=15)
        print(f"   Homepage: {homepage_response.status_code}")
        
        # Human-like delay
        time.sleep(random.uniform(3, 7))
        
        # Step 2: Accept cookies/terms (if needed)
        if 'cookie' in homepage_response.text.lower():
            print("2. Handling cookies...")
            time.sleep(random.uniform(1, 3))
        
        return homepage_response.status_code == 200
    
    def advanced_grassvalley_attack(self):
        """Advanced attack on Grass Valley, CA jobs"""
        print("⚔️ ROUND 5: Advanced Header Warfare")
        print("🎯 Target: Grass Valley, CA jobs (15 mile radius)")
        
        # Simulate human session first
        if not self.simulate_human_session():
            print("❌ Failed to establish human session")
            return None
        
        # Build search URL
        query = "python developer"
        location = "Grass Valley, CA"
        search_url = f"https://www.indeed.com/jobs?q={quote_plus(query)}&l={quote_plus(location)}&radius=15"
        
        print(f"3. Performing search: {search_url}")
        
        # Update headers for search request
        search_headers = self.get_rotating_headers()
        search_headers['Referer'] = 'https://www.indeed.com'
        self.session.headers.update(search_headers)
        
        # Human delay before search
        time.sleep(random.uniform(2, 5))
        
        try:
            response = self.session.get(search_url, timeout=15)
            
            result = {
                'timestamp': datetime.now().isoformat(),
                'round': 5,
                'method': 'advanced_header_warfare',
                'location': f"{location} (15 mile radius)",
                'query': query,
                'url': search_url,
                'status_code': response.status_code,
                'response_size': len(response.text) if response.text else 0,
                'session_cookies': len(self.session.cookies),
                'success': response.status_code == 200
            }
            
            if response.status_code == 200:
                print(f"🎉 SUCCESS! Status: {response.status_code}")
                print(f"📊 Response size: {len(response.text)} characters")
                result['html_content'] = response.text
                result['note'] = "VICTORY: Successfully bypassed Indeed's defenses!"
            elif response.status_code == 403:
                print(f"🔒 Still blocked: {response.status_code}")
                result['html_content'] = response.text if response.text else ""
                result['note'] = "Blocked but got response - analyzing defense patterns"
            else:
                print(f"❓ Unexpected: {response.status_code}")
                result['note'] = f"Unexpected response: {response.status_code}"
            
            # Save battle results
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"round5_advanced_{timestamp}.json"
            filepath = self.base_dir / filename
            
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(result, f, indent=2, ensure_ascii=False)
                
            print(f"💾 Battle data saved: {filepath}")
            return result
            
        except Exception as e:
            print(f"💥 Attack failed: {str(e)}")
            return {'error': str(e), 'round': 5}


if __name__ == "__main__":
    warrior = IndeedWarrior()
    result = warrior.advanced_grassvalley_attack()
    
    if result and result.get('success'):
        print("\n🏆 ROUND 5 VICTORY!")
        print("✅ Indeed defenses breached!")
    else:
        print("\n⚔️ Round 5 complete - analyzing results for Round 6...")
        print("🔍 Gathering intelligence for next attack...")