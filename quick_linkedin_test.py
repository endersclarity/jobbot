#!/usr/bin/env python3
"""
Quick LinkedIn test using Browser MCP approach
"""

import requests
from bs4 import BeautifulSoup

def test_linkedin_access():
    """Test what we can access on LinkedIn without complex automation"""
    
    # Test direct HTTP access first
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    
    url = "https://www.linkedin.com/jobs/search/?keywords=software+engineer&location=Remote"
    
    try:
        print("🔍 Testing LinkedIn HTTP access...")
        response = requests.get(url, headers=headers, timeout=10)
        
        print(f"📊 Response: {response.status_code}")
        
        if response.status_code == 200:
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Look for job count
            job_count_text = soup.get_text()
            if "Software Engineer" in job_count_text and "jobs" in job_count_text:
                lines = job_count_text.split('\n')
                for line in lines:
                    if "Software Engineer" in line and "jobs" in line:
                        print(f"✅ Found job count: {line.strip()}")
                        break
            
            # Look for job titles
            job_titles = soup.find_all('h3') + soup.find_all('a', string=lambda text: text and 'engineer' in text.lower())
            
            print(f"📝 Found {len(job_titles)} potential job elements")
            
            if job_titles:
                print("📋 Sample job titles found:")
                for i, title in enumerate(job_titles[:5]):
                    print(f"  {i+1}. {title.get_text().strip()[:100]}")
            
            return True
            
        else:
            print(f"❌ LinkedIn returned status {response.status_code}")
            return False
            
    except Exception as e:
        print(f"💥 Error accessing LinkedIn: {e}")
        return False

if __name__ == "__main__":
    success = test_linkedin_access()
    
    if success:
        print("\n🎉 LinkedIn HTTP access successful!")
        print("💡 This suggests we can scrape LinkedIn with proper HTTP requests")
    else:
        print("\n⚠️ LinkedIn HTTP access failed - may need browser automation")