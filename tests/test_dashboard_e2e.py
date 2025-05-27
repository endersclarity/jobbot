#!/usr/bin/env python3
"""
Dashboard End-to-End Testing Suite

Tests the React dashboard interface using Playwright to:
- Verify UI components render correctly
- Test button clicks and form submissions
- Validate scraping workflow end-to-end
- Generate screenshots for debugging
- Monitor console errors and network requests
"""

import asyncio
import json
import time
from pathlib import Path
from typing import Dict, List, Any
from playwright.async_api import async_playwright, Browser, Page

class DashboardTester:
    def __init__(self, dashboard_url: str = "http://172.22.206.209:3002"):
        self.dashboard_url = dashboard_url
        self.results = []
        self.browser = None
        self.page = None
        
    def log_result(self, test_name: str, success: bool, details: Dict[str, Any]):
        """Log test result"""
        result = {
            "test": test_name,
            "success": success,
            "timestamp": time.time(),
            "details": details
        }
        self.results.append(result)
        
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} {test_name}")
        if not success:
            print(f"   Error: {details.get('error', 'Unknown error')}")
        else:
            print(f"   {details.get('summary', 'Success')}")
        print()
    
    async def setup_browser(self):
        """Setup Playwright browser"""
        try:
            playwright = await async_playwright().start()
            self.browser = await playwright.chromium.launch(
                headless=False,  # Set to True for CI/CD
                args=['--no-sandbox', '--disable-setuid-sandbox']
            )
            
            context = await self.browser.new_context(
                viewport={'width': 1280, 'height': 720}
            )
            
            self.page = await context.new_page()
            
            # Setup console and network monitoring
            self.console_logs = []
            self.network_errors = []
            
            self.page.on('console', lambda msg: self.console_logs.append({
                'type': msg.type,
                'text': msg.text,
                'timestamp': time.time()
            }))
            
            self.page.on('requestfailed', lambda request: self.network_errors.append({
                'method': request.method,
                'url': request.url,
                'error': request.failure().error_text if request.failure() else 'Unknown error',
                'timestamp': time.time()
            }))
            
            self.log_result("Browser Setup", True, {
                "summary": "Playwright browser initialized"
            })
            
        except Exception as e:
            self.log_result("Browser Setup", False, {
                "error": str(e)
            })
    
    async def test_dashboard_load(self):
        """Test if dashboard loads correctly"""
        try:
            await self.page.goto(self.dashboard_url, wait_until='networkidle')
            
            # Check if main elements are present
            title = await self.page.title()
            url = self.page.url
            
            # Look for key dashboard elements
            dashboard_header = await self.page.query_selector('text=JobBot Dashboard')
            job_scraper_link = await self.page.query_selector('text=Job Scraper')
            system_status = await self.page.query_selector('text=System Status')
            
            if dashboard_header and job_scraper_link:
                # Take screenshot
                screenshot_path = await self.save_screenshot("dashboard_load")
                
                self.log_result("Dashboard Load", True, {
                    "title": title,
                    "url": url,
                    "screenshot": screenshot_path,
                    "summary": f"Dashboard loaded: {title}"
                })
            else:
                screenshot_path = await self.save_screenshot("dashboard_load_failed")
                self.log_result("Dashboard Load", False, {
                    "title": title,
                    "url": url,
                    "screenshot": screenshot_path,
                    "error": "Required dashboard elements not found"
                })
                
        except Exception as e:
            self.log_result("Dashboard Load", False, {
                "error": str(e)
            })
    
    async def test_navigation_to_scraper(self):
        """Test navigation to Job Scraper page"""
        try:
            # Click on Job Scraper link
            await self.page.click('text=Job Scraper')
            await self.page.wait_for_timeout(2000)
            
            # Check if we're on the scraper page
            scraper_heading = await self.page.query_selector('text=Job Scraper')
            scrape_button = await self.page.query_selector('text=Scrape Now')
            search_input = await self.page.query_selector('input[name="search_term"]')
            
            if scraper_heading and scrape_button and search_input:
                screenshot_path = await self.save_screenshot("scraper_page")
                
                self.log_result("Navigation to Scraper", True, {
                    "url": self.page.url,
                    "screenshot": screenshot_path,
                    "summary": "Successfully navigated to Job Scraper page"
                })
            else:
                screenshot_path = await self.save_screenshot("scraper_page_failed")
                self.log_result("Navigation to Scraper", False, {
                    "url": self.page.url,
                    "screenshot": screenshot_path,
                    "error": "Scraper page elements not found"
                })
                
        except Exception as e:
            self.log_result("Navigation to Scraper", False, {
                "error": str(e)
            })
    
    async def test_form_interaction(self):
        """Test form filling and interaction"""
        try:
            # Clear and fill search term
            search_input = await self.page.query_selector('input[name="search_term"]')
            if search_input:
                await search_input.clear()
                await search_input.fill('software engineer')
            
            # Clear and fill location
            location_input = await self.page.query_selector('input[name="location"]')
            if location_input:
                await location_input.clear()
                await location_input.fill('San Francisco, CA')
            
            # Select max jobs
            max_jobs_select = await self.page.query_selector('select[name="max_jobs"]')
            if max_jobs_select:
                await max_jobs_select.select_option('10')
            
            # Take screenshot of filled form
            screenshot_path = await self.save_screenshot("form_filled")
            
            # Verify values
            search_value = await search_input.input_value() if search_input else ""
            location_value = await location_input.input_value() if location_input else ""
            
            if search_value and location_value:
                self.log_result("Form Interaction", True, {
                    "search_term": search_value,
                    "location": location_value,
                    "screenshot": screenshot_path,
                    "summary": f"Form filled: '{search_value}' in '{location_value}'"
                })
            else:
                self.log_result("Form Interaction", False, {
                    "search_term": search_value,
                    "location": location_value,
                    "screenshot": screenshot_path,
                    "error": "Form values not set correctly"
                })
                
        except Exception as e:
            self.log_result("Form Interaction", False, {
                "error": str(e)
            })
    
    async def test_scrape_button_click(self):
        """Test clicking the Scrape Now button and monitoring results"""
        try:
            # Clear previous console logs and network errors
            self.console_logs.clear()
            self.network_errors.clear()
            
            # Click Scrape Now button
            scrape_button = await self.page.query_selector('text=Scrape Now')
            if not scrape_button:
                self.log_result("Scrape Button Click", False, {
                    "error": "Scrape Now button not found"
                })
                return
            
            await scrape_button.click()
            
            # Wait for request to complete (scraping can take time)
            await self.page.wait_for_timeout(10000)
            
            # Take screenshot after clicking
            screenshot_path = await self.save_screenshot("after_scrape_click")
            
            # Check for results section
            results_section = await self.page.query_selector('text=Scraping Results')
            
            # Look for success or error indicators
            success_message = await self.page.query_selector('text=Successfully scraped')
            network_error = await self.page.query_selector('text=Network Error')
            
            # Analyze console logs for errors
            console_errors = [log for log in self.console_logs if log['type'] == 'error']
            
            if results_section:
                if success_message:
                    # Try to extract job counts
                    jobs_found_element = await self.page.query_selector('text=/Jobs Found/')
                    jobs_found = await jobs_found_element.text_content() if jobs_found_element else "N/A"
                    
                    self.log_result("Scrape Button Click", True, {
                        "has_results": True,
                        "success_message": True,
                        "jobs_info": jobs_found,
                        "console_errors": len(console_errors),
                        "network_errors": len(self.network_errors),
                        "screenshot": screenshot_path,
                        "summary": f"Scraping executed successfully: {jobs_found}"
                    })
                elif network_error:
                    self.log_result("Scrape Button Click", False, {
                        "has_results": True,
                        "network_error": True,
                        "console_errors": console_errors[:3],  # First 3 errors
                        "network_errors": self.network_errors[:3],
                        "screenshot": screenshot_path,
                        "error": "Network error occurred"
                    })
                else:
                    self.log_result("Scrape Button Click", False, {
                        "has_results": True,
                        "unknown_result": True,
                        "console_errors": console_errors[:3],
                        "screenshot": screenshot_path,
                        "error": "Unknown result state"
                    })
            else:
                self.log_result("Scrape Button Click", False, {
                    "has_results": False,
                    "console_errors": console_errors[:3],
                    "network_errors": self.network_errors[:3],
                    "screenshot": screenshot_path,
                    "error": "No results section appeared"
                })
                
        except Exception as e:
            screenshot_path = await self.save_screenshot("scrape_click_error")
            self.log_result("Scrape Button Click", False, {
                "error": str(e),
                "screenshot": screenshot_path
            })
    
    async def test_different_search_terms(self):
        """Test multiple search terms"""
        test_cases = [
            ("python developer", "New York, NY"),
            ("data scientist", "San Francisco, CA"),
            ("web developer", "Remote"),
        ]
        
        for search_term, location in test_cases:
            try:
                # Fill form
                search_input = await self.page.query_selector('input[name="search_term"]')
                location_input = await self.page.query_selector('input[name="location"]')
                
                if search_input and location_input:
                    await search_input.clear()
                    await search_input.fill(search_term)
                    await location_input.clear()
                    await location_input.fill(location)
                    
                    # Click scrape button
                    await self.page.click('text=Scrape Now')
                    await self.page.wait_for_timeout(8000)
                    
                    # Check results
                    results_section = await self.page.query_selector('text=Scraping Results')
                    success = results_section is not None
                    
                    screenshot_path = await self.save_screenshot(f"search_{search_term.replace(' ', '_')}")
                    
                    self.log_result(f"Search: {search_term} in {location}", success, {
                        "search_term": search_term,
                        "location": location,
                        "has_results": success,
                        "screenshot": screenshot_path,
                        "summary": f"Tested search for {search_term}"
                    })
                    
                    # Wait between tests
                    await self.page.wait_for_timeout(2000)
                    
            except Exception as e:
                self.log_result(f"Search: {search_term} in {location}", False, {
                    "error": str(e)
                })
    
    async def save_screenshot(self, name: str) -> str:
        """Save screenshot with timestamp"""
        try:
            timestamp = int(time.time())
            screenshot_path = f"tests/results/screenshots/{name}_{timestamp}.png"
            Path("tests/results/screenshots").mkdir(parents=True, exist_ok=True)
            
            await self.page.screenshot(path=screenshot_path)
            return screenshot_path
        except Exception as e:
            print(f"Failed to save screenshot: {e}")
            return "screenshot_failed"
    
    async def cleanup(self):
        """Cleanup browser resources"""
        try:
            if self.browser:
                await self.browser.close()
            self.log_result("Browser Cleanup", True, {
                "summary": "Browser closed successfully"
            })
        except Exception as e:
            self.log_result("Browser Cleanup", False, {
                "error": str(e)
            })
    
    def generate_report(self):
        """Generate comprehensive dashboard test report"""
        print("\n" + "=" * 60)
        print("🖥️ DASHBOARD E2E TESTING REPORT")
        print("=" * 60)
        
        total_tests = len(self.results)
        passed_tests = len([r for r in self.results if r["success"]])
        failed_tests = total_tests - passed_tests
        
        print(f"Total Tests: {total_tests}")
        print(f"✅ Passed: {passed_tests}")
        print(f"❌ Failed: {failed_tests}")
        print(f"Success Rate: {(passed_tests/total_tests)*100:.1f}%")
        
        if failed_tests > 0:
            print(f"\n🔥 FAILED TESTS:")
            for result in self.results:
                if not result["success"]:
                    print(f"  • {result['test']}: {result['details'].get('error', 'Unknown error')}")
        
        # Save detailed results
        timestamp = int(time.time())
        report_file = f"tests/results/dashboard_test_report_{timestamp}.json"
        Path("tests/results").mkdir(exist_ok=True)
        
        with open(report_file, 'w') as f:
            json.dump({
                "summary": {
                    "total_tests": total_tests,
                    "passed_tests": passed_tests,
                    "failed_tests": failed_tests,
                    "success_rate": (passed_tests/total_tests)*100
                },
                "results": self.results
            }, f, indent=2)
        
        print(f"\n📄 Detailed report saved: {report_file}")
        print(f"📸 Screenshots saved in: tests/results/screenshots/")
        return passed_tests == total_tests

async def main():
    """Run all dashboard tests"""
    print("🖥️ JOBBOT DASHBOARD E2E TESTING SUITE")
    print("=" * 60)
    
    tester = DashboardTester()
    
    try:
        # Setup browser
        await tester.setup_browser()
        
        # Run tests
        print("1️⃣ Basic Dashboard Tests:")
        await tester.test_dashboard_load()
        await tester.test_navigation_to_scraper()
        
        print("\n2️⃣ Form Interaction Tests:")
        await tester.test_form_interaction()
        
        print("\n3️⃣ Scraping Functionality Tests:")
        await tester.test_scrape_button_click()
        await tester.test_different_search_terms()
        
    finally:
        # Cleanup
        await tester.cleanup()
    
    # Generate final report
    success = tester.generate_report()
    
    return 0 if success else 1

if __name__ == "__main__":
    exit(asyncio.run(main()))