#!/usr/bin/env python3
"""
Working Grass Valley Indeed Scraper
Uses requests with enhanced headers - ready for Puppeteer when browser is setup
"""

import requests
import json
import time
import random
from datetime import datetime
from pathlib import Path
from urllib.parse import quote_plus


def scrape_grassvalley_jobs_enhanced():
    """
    Enhanced scraper for Grass Valley, CA with better headers
    Falls back to requests until Puppeteer browser is configured
    """
    print("🎯 Scraping jobs in Grass Valley, CA (15 mile radius)...")
    
    query = "python developer"
    location = "Grass Valley, CA"
    
    # Enhanced headers to mimic real browser
    headers = {
        'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.9',
        'Accept-Encoding': 'gzip, deflate, br',
        'DNT': '1',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1',
        'Sec-Fetch-Dest': 'document',
        'Sec-Fetch-Mode': 'navigate',
        'Sec-Fetch-Site': 'none',
        'Sec-Ch-Ua': '"Not_A Brand";v="8", "Chromium";v="120", "Google Chrome";v="120"',
        'Sec-Ch-Ua-Mobile': '?0',
        'Sec-Ch-Ua-Platform': '"Linux"',
        'Cache-Control': 'max-age=0'
    }
    
    # Build URL for Grass Valley, CA search
    base_url = "https://www.indeed.com/jobs"
    params = {
        'q': query,
        'l': location,
        'radius': '15'  # 15 mile radius
    }
    
    # Manual URL construction for better control
    url = f"{base_url}?q={quote_plus(query)}&l={quote_plus(location)}&radius=15"
    
    print(f"Target URL: {url}")
    
    try:
        # Create session with persistent cookies
        session = requests.Session()
        session.headers.update(headers)
        
        # Add small delay
        time.sleep(random.uniform(2, 4))
        
        print("Making request to Indeed...")
        response = session.get(url, timeout=15)
        
        # Create result data
        result = {
            'timestamp': datetime.now().isoformat(),
            'method': 'enhanced_requests',
            'location': f"{location} (15 mile radius)",
            'query': query,
            'url': url,
            'status_code': response.status_code,
            'response_size': len(response.text) if response.text else 0,
            'headers_sent': dict(headers),
            'success': response.status_code == 200
        }
        
        if response.status_code == 200:
            print(f"✅ SUCCESS! Retrieved {len(response.text)} characters")
            result['html_content'] = response.text
            result['note'] = "Successfully retrieved job listings"
        elif response.status_code == 403:
            print("⚠️  403 Forbidden - Indeed blocked the request")
            result['note'] = "Blocked by Indeed - Puppeteer browser automation needed"
        else:
            print(f"❓ Unexpected status: {response.status_code}")
            result['note'] = f"Unexpected response: {response.status_code}"
        
        # Save result
        base_dir = Path(__file__).parent / "scraped_data" / "raw"
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"grassvalley_enhanced_{timestamp}.json"
        filepath = base_dir / filename
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(result, f, indent=2, ensure_ascii=False)
            
        print(f"📁 Data saved to: {filepath}")
        
        # Print summary
        print(f"\n📊 Scraping Summary:")
        print(f"   Location: {location} (15 mile radius)")
        print(f"   Query: {query}")
        print(f"   Status: {response.status_code}")
        print(f"   Data size: {result['response_size']} characters")
        print(f"   Success: {result['success']}")
        
        return result
        
    except Exception as e:
        error_result = {
            'timestamp': datetime.now().isoformat(),
            'error': str(e),
            'location': location,
            'query': query,
            'url': url
        }
        print(f"❌ Error: {str(e)}")
        return error_result


if __name__ == "__main__":
    scrape_grassvalley_jobs_enhanced()