#!/usr/bin/env python3
"""
Direct Scraper Testing Suite

Tests the Crawlee scraper directly via Node.js to debug:
- CSS selector issues
- Anti-detection measures
- Different job sites and locations
- Raw scraper output without API layer
"""

import subprocess
import json
import time
from pathlib import Path
from typing import Dict, Any

class ScraperTester:
    def __init__(self, scraper_path: str = "src/crawlee-scraper.js"):
        self.scraper_path = Path(scraper_path)
        self.results = []
        
        # Verify scraper exists
        if not self.scraper_path.exists():
            print(f"❌ Scraper not found at: {self.scraper_path}")
            print("Looking for scraper files...")
            self._find_scraper_files()
    
    def _find_scraper_files(self):
        """Find all potential scraper files"""
        print("🔍 Searching for scraper files:")
        for pattern in ["**/crawlee*.js", "**/scraper*.js", "**/indeed*.js"]:
            files = list(Path(".").glob(pattern))
            for file in files:
                print(f"  Found: {file}")
        print()
    
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
    
    def test_node_availability(self):
        """Test if Node.js is available"""
        try:
            result = subprocess.run(
                ["node", "--version"],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if result.returncode == 0:
                version = result.stdout.strip()
                self.log_result("Node.js Availability", True, {
                    "version": version,
                    "summary": f"Node.js {version} available"
                })
            else:
                self.log_result("Node.js Availability", False, {
                    "error": f"Node.js not working: {result.stderr}"
                })
                
        except Exception as e:
            self.log_result("Node.js Availability", False, {
                "error": str(e)
            })
    
    def test_scraper_dependencies(self):
        """Test if scraper dependencies are installed"""
        try:
            # Check if package.json exists and npm install was run
            package_json = Path("package.json")
            node_modules = Path("node_modules")
            
            if not package_json.exists():
                self.log_result("Scraper Dependencies", False, {
                    "error": "package.json not found"
                })
                return
            
            if not node_modules.exists():
                print("📦 Installing Node.js dependencies...")
                result = subprocess.run(
                    ["npm", "install"],
                    capture_output=True,
                    text=True,
                    timeout=120
                )
                
                if result.returncode != 0:
                    self.log_result("Scraper Dependencies", False, {
                        "error": f"npm install failed: {result.stderr}"
                    })
                    return
            
            # Test if crawlee is available
            result = subprocess.run(
                ["node", "-e", "console.log(require('crawlee').VERSION || 'installed')"],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if result.returncode == 0:
                self.log_result("Scraper Dependencies", True, {
                    "crawlee_status": result.stdout.strip(),
                    "summary": "Dependencies installed successfully"
                })
            else:
                self.log_result("Scraper Dependencies", False, {
                    "error": f"Crawlee not available: {result.stderr}"
                })
                
        except Exception as e:
            self.log_result("Scraper Dependencies", False, {
                "error": str(e)
            })
    
    def test_scraper_direct(self, search_term: str, location: str, max_jobs: int = 5):
        """Test scraper directly with Node.js"""
        try:
            if not self.scraper_path.exists():
                self.log_result(f"Direct Scraping: {search_term}", False, {
                    "error": f"Scraper file not found: {self.scraper_path}"
                })
                return
            
            # Prepare scraper arguments
            args = [
                "node",
                str(self.scraper_path),
                "--search", search_term,
                "--location", location,
                "--max", str(max_jobs),
                "--site", "indeed",
                "--json"  # Enable JSON output for parsing
            ]
            
            print(f"🔍 Running: {' '.join(args)}")
            start_time = time.time()
            
            result = subprocess.run(
                args,
                capture_output=True,
                text=True,
                timeout=60,
                cwd=Path.cwd()
            )
            
            elapsed = time.time() - start_time
            
            if result.returncode == 0:
                # Try to parse JSON output
                try:
                    output_data = json.loads(result.stdout)
                    jobs_found = len(output_data.get("jobs", []))
                    
                    self.log_result(f"Direct Scraping: {search_term}", True, {
                        "jobs_found": jobs_found,
                        "execution_time": f"{elapsed:.2f}s",
                        "output_size": len(result.stdout),
                        "summary": f"Found {jobs_found} jobs in {elapsed:.2f}s"
                    })
                    
                    # Save raw output for debugging
                    debug_file = f"tests/results/scraper_debug_{int(time.time())}.json"
                    Path("tests/results").mkdir(parents=True, exist_ok=True)
                    with open(debug_file, 'w') as f:
                        json.dump(output_data, f, indent=2)
                    print(f"   Debug output saved: {debug_file}")
                    
                except json.JSONDecodeError:
                    # Raw text output
                    self.log_result(f"Direct Scraping: {search_term}", True, {
                        "raw_output": result.stdout[:200] + "..." if len(result.stdout) > 200 else result.stdout,
                        "execution_time": f"{elapsed:.2f}s",
                        "summary": f"Scraper executed but output not JSON"
                    })
            else:
                self.log_result(f"Direct Scraping: {search_term}", False, {
                    "error": result.stderr or "Script failed",
                    "stdout": result.stdout[:200] if result.stdout else "",
                    "return_code": result.returncode
                })
                
        except subprocess.TimeoutExpired:
            self.log_result(f"Direct Scraping: {search_term}", False, {
                "error": "Scraper timed out after 60 seconds"
            })
        except Exception as e:
            self.log_result(f"Direct Scraping: {search_term}", False, {
                "error": str(e)
            })
    
    def test_css_selectors(self):
        """Test if we can reach Indeed and inspect CSS selectors"""
        try:
            # Create a simple test script to check Indeed page structure
            test_script = '''
import { chromium } from 'playwright';

(async () => {
  const browser = await chromium.launch({ headless: true });
  const page = await browser.newPage();
  
  try {
    await page.goto('https://indeed.com/jobs?q=software+engineer&l=San+Francisco%2C+CA', {
      waitUntil: 'networkidle'
    });
    
    // Check for common job listing selectors
    const selectors = [
      '[data-testid="job-title"]',
      '.jobTitle',
      '.jobTitle a',
      '[data-testid="job-title"] a',
      '.slider_container .slider_item',
      '.job_seen_beacon'
    ];
    
    const results = {};
    for (const selector of selectors) {
      const elements = await page.$$(selector);
      results[selector] = elements.length;
    }
    
    console.log(JSON.stringify({
      success: true,
      url: page.url(),
      title: await page.title(),
      selectors: results
    }));
    
  } catch (error) {
    console.log(JSON.stringify({
      success: false,
      error: error.message
    }));
  } finally {
    await browser.close();
  }
})();
            '''
            
            # Write and execute test script
            test_file = Path("tests/temp_selector_test.js")
            with open(test_file, 'w') as f:
                f.write(test_script)
            
            result = subprocess.run(
                ["node", str(test_file)],
                capture_output=True,
                text=True,
                timeout=30
            )
            
            # Clean up
            test_file.unlink(missing_ok=True)
            
            if result.returncode == 0:
                try:
                    data = json.loads(result.stdout)
                    if data.get("success"):
                        selectors = data.get("selectors", {})
                        working_selectors = [sel for sel, count in selectors.items() if count > 0]
                        
                        self.log_result("CSS Selectors Test", True, {
                            "page_title": data.get("title"),
                            "working_selectors": working_selectors,
                            "selector_counts": selectors,
                            "summary": f"Found {len(working_selectors)} working selectors"
                        })
                    else:
                        self.log_result("CSS Selectors Test", False, {
                            "error": data.get("error", "Unknown error")
                        })
                except json.JSONDecodeError:
                    self.log_result("CSS Selectors Test", False, {
                        "error": f"Invalid JSON output: {result.stdout[:100]}"
                    })
            else:
                self.log_result("CSS Selectors Test", False, {
                    "error": result.stderr or "Script failed"
                })
                
        except Exception as e:
            self.log_result("CSS Selectors Test", False, {
                "error": str(e)
            })
    
    def test_multiple_locations(self):
        """Test scraper with multiple locations"""
        test_cases = [
            ("San Francisco, CA", "software engineer"),
            ("New York, NY", "python developer"), 
            ("Remote", "javascript developer"),
            ("Austin, TX", "react developer"),
            ("Grass Valley, CA", "software engineer"),  # Original failing case
        ]
        
        print("🌍 Testing Multiple Locations:")
        print("=" * 50)
        
        for location, search_term in test_cases:
            self.test_scraper_direct(search_term, location, max_jobs=3)
            time.sleep(5)  # Rate limiting
    
    def generate_report(self):
        """Generate comprehensive scraper test report"""
        print("\n" + "=" * 60)
        print("🤖 SCRAPER TESTING REPORT")
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
        report_file = f"tests/results/scraper_test_report_{timestamp}.json"
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
        return passed_tests == total_tests

def main():
    """Run all scraper tests"""
    print("🤖 JOBBOT SCRAPER TESTING SUITE")
    print("=" * 60)
    
    tester = ScraperTester()
    
    # Basic environment tests
    print("1️⃣ Environment Tests:")
    tester.test_node_availability()
    tester.test_scraper_dependencies()
    
    print("\n2️⃣ Scraper Functionality Tests:")
    tester.test_css_selectors()
    tester.test_multiple_locations()
    
    # Generate final report
    success = tester.generate_report()
    
    return 0 if success else 1

if __name__ == "__main__":
    exit(main())