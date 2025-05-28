#!/usr/bin/env python3
"""
LinkedIn Job Scraper Test - Phase 3 Implementation
Test what we can scrape from LinkedIn with different approaches
"""

import time
import json
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options

def test_linkedin_scraping():
    """Test LinkedIn job scraping capabilities"""
    
    print("🔍 Testing LinkedIn Job Scraping Capabilities")
    
    # Setup Chrome with realistic options
    chrome_options = Options()
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")
    chrome_options.add_argument("--disable-web-security")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
    chrome_options.add_experimental_option('useAutomationExtension', False)
    
    try:
        driver = webdriver.Chrome(options=chrome_options)
        driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        
        # Test LinkedIn Jobs page
        print("\n📱 Navigating to LinkedIn Jobs...")
        driver.get("https://www.linkedin.com/jobs/search/?keywords=software+engineer&location=Remote")
        
        time.sleep(3)  # Wait for page load
        
        # Check if login is required
        login_modal = driver.find_elements(By.CSS_SELECTOR, '[data-testid="sign-in-modal"]')
        if login_modal:
            print("🔐 Login modal detected - dismissing...")
            dismiss_btn = driver.find_elements(By.CSS_SELECTOR, 'button[aria-label="Dismiss"]')
            if dismiss_btn:
                dismiss_btn[0].click()
                time.sleep(2)
        
        # Extract job count
        job_count_elements = driver.find_elements(By.CSS_SELECTOR, 'span:contains("jobs")')
        job_count = "Unknown"
        for element in job_count_elements:
            if "Software Engineer" in element.text:
                job_count = element.text
                break
        
        print(f"📊 Job Count Found: {job_count}")
        
        # Try to find job listings
        job_selectors = [
            '[data-entity-urn*="job"]',
            '.job-card-container',
            '.jobs-search-results__list-item',
            '.job-result-card',
            '[data-control-name="job_search_job_title"]'
        ]
        
        jobs_found = []
        for selector in job_selectors:
            elements = driver.find_elements(By.CSS_SELECTOR, selector)
            if elements:
                print(f"✅ Found {len(elements)} elements with selector: {selector}")
                jobs_found.extend(elements)
                break
        
        # Extract job details from visible listings
        extracted_jobs = []
        for i, job_element in enumerate(jobs_found[:5]):  # Limit to first 5
            try:
                # Try different ways to extract job info
                title_element = job_element.find_element(By.CSS_SELECTOR, 'h3 a') if job_element.find_elements(By.CSS_SELECTOR, 'h3 a') else None
                company_element = job_element.find_element(By.CSS_SELECTOR, 'h4 a') if job_element.find_elements(By.CSS_SELECTOR, 'h4 a') else None
                
                job_data = {
                    "title": title_element.text if title_element else "No title found",
                    "company": company_element.text if company_element else "No company found",
                    "url": title_element.get_attribute('href') if title_element else "No URL",
                    "raw_text": job_element.text[:200] + "..." if len(job_element.text) > 200 else job_element.text
                }
                
                extracted_jobs.append(job_data)
                
            except Exception as e:
                print(f"⚠️ Error extracting job {i}: {e}")
        
        # Results summary
        print("\n📋 LINKEDIN SCRAPING RESULTS:")
        print("✅ Page loaded successfully")
        print(f"📊 Total job count: {job_count}")
        print(f"🎯 Job elements found: {len(jobs_found)}")
        print(f"📝 Successfully extracted: {len(extracted_jobs)} jobs")
        
        if extracted_jobs:
            print(f"\n📋 Sample Jobs:")
            for i, job in enumerate(extracted_jobs[:3]):
                print(f"\n{i+1}. {job['title']}")
                print(f"   Company: {job['company']}")
                print(f"   URL: {job['url'][:50]}...")
        
        # Test scrolling for more jobs
        print(f"\n📜 Testing infinite scroll...")
        initial_height = driver.execute_script("return document.body.scrollHeight")
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(3)
        
        new_height = driver.execute_script("return document.body.scrollHeight")
        if new_height > initial_height:
            print(f"✅ Page grew from {initial_height}px to {new_height}px - infinite scroll works!")
        else:
            print(f"⚠️ No height change detected - may need authentication for more results")
        
        # Save results
        results = {
            "success": True,
            "job_count": job_count,
            "jobs_found": len(jobs_found),
            "extracted_jobs": extracted_jobs,
            "infinite_scroll_works": new_height > initial_height,
            "requires_auth": bool(login_modal)
        }
        
        with open("linkedin_scraping_results.json", "w") as f:
            json.dump(results, f, indent=2)
        
        print(f"\n💾 Results saved to linkedin_scraping_results.json")
        
        return results
        
    except Exception as e:
        print(f"❌ LinkedIn scraping failed: {e}")
        return {"success": False, "error": str(e)}
        
    finally:
        if 'driver' in locals():
            driver.quit()

if __name__ == "__main__":
    results = test_linkedin_scraping()
    
    if results.get("success"):
        print(f"\n🎉 LinkedIn scraping test completed!")
        print(f"📊 Found {results.get('jobs_found', 0)} job elements")
        print(f"📝 Extracted {len(results.get('extracted_jobs', []))} job details")
    else:
        print(f"\n💥 LinkedIn scraping test failed: {results.get('error', 'Unknown error')}")