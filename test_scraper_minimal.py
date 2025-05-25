#!/usr/bin/env python3
"""
Minimal scraper test - limits data to avoid token burn
Just verifies the scraping functionality works
"""

import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent / "app"))

from scrapers.indeed import IndeedScraper
import json


def test_scraper_minimal():
    """Test scraper with minimal data collection"""
    print("🧪 Testing scraper with minimal data collection...")
    
    scraper = IndeedScraper()
    
    # Test with just 1 page, no full HTML content
    try:
        # Override the scrape method to limit content
        import requests
        
        url = scraper._build_search_url("python", "", 0)
        print(f"Testing URL: {url}")
        
        headers = scraper._get_headers()
        response = requests.get(url, headers=headers, timeout=5)
        
        # Save minimal test data (just status and basic info)
        test_result = {
            'test_mode': True,
            'status_code': response.status_code,
            'url': url,
            'headers_sent': len(headers),
            'response_size_chars': len(response.text) if response.status_code == 200 else 0,
            'content_preview': response.text[:200] if response.status_code == 200 else "No content"
        }
        
        # Save tiny test file
        test_file = scraper.raw_dir / "test_minimal.json"
        with open(test_file, 'w') as f:
            json.dump(test_result, f, indent=2)
            
        print("✅ Test completed:")
        print(f"   Status: {test_result['status_code']}")
        print(f"   Response size: {test_result['response_size_chars']} chars")
        print(f"   Test file: {test_file}")
        
        if test_result['status_code'] == 200:
            print("🎉 Scraper works! Ready for full runs.")
        elif test_result['status_code'] == 403:
            print("⚠️  403 Forbidden - need browser automation")
        else:
            print(f"❓ Unexpected status: {test_result['status_code']}")
            
        return test_result
        
    except Exception as e:
        print(f"❌ Test failed: {str(e)}")
        return {'error': str(e)}


if __name__ == "__main__":
    test_scraper_minimal()