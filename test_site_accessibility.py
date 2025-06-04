#!/usr/bin/env python3
"""
Quick test to see which job sites are actually scrapable
"""
import subprocess
import json
import time
from pathlib import Path

def test_site_scraping():
    """Test scraping across different job sites"""
    
    # Test the specific scrapers we have
    test_sites = [
        {
            "name": "Indeed (Main Scraper)",
            "command": ["node", "src/crawlee-scraper.js", "--search", "software engineer", "--location", "remote", "--max", "3", "--json"]
        },
        {
            "name": "Indeed (Dedicated)",
            "command": ["node", "src/scrapers/indeed_scraper.js", "software engineer", "remote", "3"]
        },
        {
            "name": "Glassdoor (Dedicated)", 
            "command": ["node", "src/scrapers/glassdoor_scraper.js", "python developer", "san francisco", "3"]
        },
        {
            "name": "LinkedIn (Dedicated)",
            "command": ["node", "src/scrapers/linkedin_scraper.js", "startup engineer", "remote", "3"]
        }
    ]
    
    # Also test direct URL access to see what sites block us
    direct_url_tests = [
        {"name": "Indeed", "url": "https://www.indeed.com/jobs?q=software+engineer&l=remote"},
        {"name": "Glassdoor", "url": "https://www.glassdoor.com/Job/jobs.htm?sc.keyword=python+developer"},
        {"name": "LinkedIn", "url": "https://www.linkedin.com/jobs/search/?keywords=software+engineer"},
        {"name": "AngelList", "url": "https://angel.co/jobs"},
        {"name": "SimplyHired", "url": "https://www.simplyhired.com/search?q=software+engineer"},
        {"name": "FlexJobs", "url": "https://www.flexjobs.com/search?q=remote+developer"}
    ]
    
    results = {}
    
    for site_test in test_sites:
        print(f"\n🧪 Testing {site_test['name']}...")
        
        try:
            # Run the scraper
            result = subprocess.run(
                site_test["command"],
                capture_output=True,
                text=True,
                timeout=45,
                cwd="/home/ender/.claude/projects/job-search-automation"
            )
            
            print(f"Return code: {result.returncode}")
            print(f"STDOUT: {result.stdout[:500]}...")
            print(f"STDERR: {result.stderr[:200]}...")
            
            # Try to extract JSON from output
            try:
                # Look for JSON in stdout
                import re
                json_pattern = r'\{(?:[^{}]|{(?:[^{}]|{[^{}]*})*})*\}'
                matches = re.findall(json_pattern, result.stdout)
                
                jobs_found = 0
                is_demo = False
                
                for match in matches:
                    try:
                        data = json.loads(match)
                        if 'jobs' in data:
                            jobs_found = len(data['jobs'])
                            # Check if it's demo data (contains "Demo" in title)
                            if jobs_found > 0:
                                is_demo = any("Demo" in job.get('title', '') for job in data['jobs'])
                            break
                    except:
                        continue
                
                results[site_test['name']] = {
                    "success": result.returncode == 0,
                    "jobs_found": jobs_found,
                    "is_demo_data": is_demo,
                    "output_preview": result.stdout[:200],
                    "error_preview": result.stderr[:200]
                }
                
                if is_demo:
                    print(f"❌ {site_test['name']}: Demo data only (blocked)")
                elif jobs_found > 0:
                    print(f"✅ {site_test['name']}: {jobs_found} real jobs found!")
                else:
                    print(f"⚠️ {site_test['name']}: No jobs returned")
                    
            except Exception as e:
                results[site_test['name']] = {
                    "success": False,
                    "error": str(e),
                    "output_preview": result.stdout[:200]
                }
                print(f"❌ {site_test['name']}: Parse error - {e}")
                
        except subprocess.TimeoutExpired:
            results[site_test['name']] = {
                "success": False,
                "error": "Timeout after 45 seconds"
            }
            print(f"⏰ {site_test['name']}: Timeout")
            
        except Exception as e:
            results[site_test['name']] = {
                "success": False,
                "error": str(e)
            }
            print(f"💥 {site_test['name']}: Exception - {e}")
        
        # Brief pause between tests
        time.sleep(2)
    
    # Test direct URL access
    print("\n" + "="*30)
    print("🌐 TESTING DIRECT URL ACCESS")
    print("="*30)
    
    for url_test in direct_url_tests:
        print(f"\n🔗 Testing {url_test['name']} direct access...")
        try:
            import urllib.request
            import urllib.error
            
            # Create request with realistic headers
            req = urllib.request.Request(
                url_test['url'],
                headers={
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
                }
            )
            
            response = urllib.request.urlopen(req, timeout=10)
            status_code = response.getcode()
            
            if status_code == 200:
                print(f"✅ {url_test['name']}: HTTP {status_code} - Accessible")
            else:
                print(f"⚠️ {url_test['name']}: HTTP {status_code}")
                
        except urllib.error.HTTPError as e:
            if e.code == 403:
                print(f"🚫 {url_test['name']}: HTTP 403 Forbidden - Anti-bot protection")
            elif e.code == 404:
                print(f"❌ {url_test['name']}: HTTP 404 Not Found")
            else:
                print(f"⚠️ {url_test['name']}: HTTP {e.code}")
        except Exception as e:
            print(f"💥 {url_test['name']}: {str(e)[:50]}...")
        
        time.sleep(1)  # Brief pause between tests

    # Summary report
    print("\n" + "="*50)
    print("🎯 SCRAPING CAPABILITY SUMMARY")
    print("="*50)
    
    working_sites = []
    demo_only_sites = []
    broken_sites = []
    
    for site, result in results.items():
        if result.get('success') and result.get('jobs_found', 0) > 0:
            if result.get('is_demo_data'):
                demo_only_sites.append(site)
                print(f"🟡 {site}: Demo data only (anti-bot blocked)")
            else:
                working_sites.append(site)
                print(f"🟢 {site}: REAL JOBS AVAILABLE ({result['jobs_found']} found)")
        else:
            broken_sites.append(site)
            error = result.get('error', 'Unknown error')
            print(f"🔴 {site}: Failed - {error}")
    
    print(f"\n📊 Results: {len(working_sites)} working, {len(demo_only_sites)} demo-only, {len(broken_sites)} broken")
    
    # Save detailed results
    with open('site_scraping_results.json', 'w') as f:
        json.dump(results, f, indent=2)
    
    print(f"\n💾 Detailed results saved to site_scraping_results.json")
    
    return working_sites, demo_only_sites, broken_sites

if __name__ == "__main__":
    working, demo, broken = test_site_scraping()
    
    if working:
        print(f"\n🎉 SUCCESS: We can scrape real jobs from: {', '.join(working)}")
    else:
        print(f"\n😞 No sites provide real job data - all are blocked or demo-only")