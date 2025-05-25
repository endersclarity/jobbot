#!/usr/bin/env python3
"""
Round 6: BrowserMCP vs Manual Attack Comparison
Test both approaches against Indeed's defenses
"""

import requests
import time
import json
from datetime import datetime
from pathlib import Path

def test_manual_request():
    """Test basic manual request - should get 403"""
    print("🎯 ROUND 6A: Testing manual request (control test)...")
    
    url = "https://www.indeed.com/jobs?q=python+developer&l=Grass+Valley%2C+CA"
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
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
        'Sec-Ch-Ua-Platform': '"Windows"'
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=10)
        
        result = {
            'timestamp': datetime.now().isoformat(),
            'method': 'manual_request',
            'url': url,
            'status_code': response.status_code,
            'response_length': len(response.text),
            'headers': dict(response.headers),
            'success': response.status_code == 200,
            'blocked': response.status_code == 403
        }
        
        print(f"Status Code: {response.status_code}")
        print(f"Response Length: {len(response.text)} characters")
        print(f"Result: {'SUCCESS' if response.status_code == 200 else 'BLOCKED' if response.status_code == 403 else 'UNKNOWN'}")
        
        # Check if response contains actual job listings or blocking page
        if "jobs" in response.text.lower() and "indeed" in response.text.lower():
            result['contains_jobs'] = True
            print("✅ Response contains job-related content")
        else:
            result['contains_jobs'] = False
            print("❌ Response does not contain job listings")
            
        return result
        
    except Exception as e:
        result = {
            'timestamp': datetime.now().isoformat(),
            'method': 'manual_request',
            'url': url,
            'error': str(e),
            'success': False
        }
        print(f"❌ Request failed: {e}")
        return result

def save_attack_results(results):
    """Save attack results to war diary"""
    base_dir = Path(__file__).parent / "scraped_data" / "logs"
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"round6_attack_results_{timestamp}.json"
    filepath = base_dir / filename
    
    with open(filepath, 'w') as f:
        json.dump(results, f, indent=2)
        
    print(f"📊 Attack results saved: {filepath}")
    return filepath

if __name__ == "__main__":
    print("🔥 ROUND 6: BrowserMCP vs Manual Attack Test")
    print("=" * 50)
    
    # Test 1: Manual request baseline
    manual_result = test_manual_request()
    
    print("\n" + "=" * 50)
    print("📊 ATTACK SUMMARY:")
    print(f"Manual Request: {'SUCCESS' if manual_result.get('success') else 'FAILED'}")
    print("BrowserMCP Test: READY TO IMPLEMENT")
    
    # Save results
    attack_results = {
        'round': 6,
        'tests': {
            'manual_request': manual_result,
            'browsermcp_test': 'pending_implementation'
        },
        'next_steps': [
            'Implement BrowserMCP test',
            'Compare real browser vs manual request results',
            'Update INDEED_WAR.md with findings'
        ]
    }
    
    save_attack_results(attack_results)
    
    print("\n🎯 Next: Test BrowserMCP against same URL")
    print("Expected: BrowserMCP should bypass 403 blocks")