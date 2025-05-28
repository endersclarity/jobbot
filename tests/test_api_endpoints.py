#!/usr/bin/env python3
"""
API Endpoints Testing Suite

Tests all scraping API endpoints with various parameters to verify:
- Network connectivity
- Response schemas
- Error handling
- Performance timing
- Different search combinations
"""

import requests
import json
import time
from typing import Dict, Any
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

class APITester:
    def __init__(self, base_url: str = "http://172.22.206.209:8001"):
        self.base_url = base_url
        self.results = []
        
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
    
    def test_health_endpoint(self):
        """Test basic health endpoint"""
        try:
            start_time = time.time()
            response = requests.get(f"{self.base_url}/health", timeout=10)
            elapsed = time.time() - start_time
            
            if response.status_code == 200:
                data = response.json()
                self.log_result("Health Endpoint", True, {
                    "status_code": response.status_code,
                    "response_time": f"{elapsed:.2f}s",
                    "database_status": data.get("database"),
                    "summary": f"Health check passed in {elapsed:.2f}s"
                })
            else:
                self.log_result("Health Endpoint", False, {
                    "status_code": response.status_code,
                    "error": f"HTTP {response.status_code}"
                })
                
        except Exception as e:
            self.log_result("Health Endpoint", False, {
                "error": str(e)
            })
    
    def test_scraping_status(self):
        """Test scraping status endpoint"""
        try:
            start_time = time.time()
            response = requests.get(f"{self.base_url}/api/v1/scraping/status", timeout=10)
            elapsed = time.time() - start_time
            
            if response.status_code == 200:
                data = response.json()
                self.log_result("Scraping Status", True, {
                    "status_code": response.status_code,
                    "response_time": f"{elapsed:.2f}s",
                    "crawlee_available": data.get("crawlee_available"),
                    "node_version": data.get("node_version"),
                    "summary": f"Crawlee status: {data.get('status', 'unknown')}"
                })
            else:
                self.log_result("Scraping Status", False, {
                    "status_code": response.status_code,
                    "error": f"HTTP {response.status_code}"
                })
                
        except Exception as e:
            self.log_result("Scraping Status", False, {
                "error": str(e)
            })
    
    def test_scraping_job_endpoint(self, search_term: str, location: str, max_jobs: int = 5):
        """Test job scraping endpoint with specific parameters"""
        try:
            payload = {
                "search_term": search_term,
                "location": location,
                "max_jobs": max_jobs,
                "job_site": "indeed"
            }
            
            print(f"Testing scraping: '{search_term}' in '{location}' (max {max_jobs} jobs)")
            start_time = time.time()
            
            response = requests.post(
                f"{self.base_url}/api/v1/scraping/jobs",
                json=payload,
                timeout=60  # Scraping can take time
            )
            
            elapsed = time.time() - start_time
            
            if response.status_code == 200:
                data = response.json()
                scraping_data = data.get("scraping", {})
                summary_data = data.get("summary", {})
                
                self.log_result(f"Scraping: {search_term} in {location}", True, {
                    "status_code": response.status_code,
                    "response_time": f"{elapsed:.2f}s",
                    "jobs_found": scraping_data.get("jobs_scraped", 0),
                    "jobs_saved": summary_data.get("jobs_saved", 0),
                    "duplicates_skipped": summary_data.get("duplicates_skipped", 0),
                    "success": data.get("success", False),
                    "summary": f"Found {scraping_data.get('jobs_scraped', 0)} jobs, saved {summary_data.get('jobs_saved', 0)}"
                })
            else:
                try:
                    error_data = response.json()
                    error_detail = error_data.get("detail", f"HTTP {response.status_code}")
                except:
                    error_detail = f"HTTP {response.status_code}"
                    
                self.log_result(f"Scraping: {search_term} in {location}", False, {
                    "status_code": response.status_code,
                    "error": error_detail
                })
                
        except Exception as e:
            self.log_result(f"Scraping: {search_term} in {location}", False, {
                "error": str(e)
            })
    
    def test_multiple_searches(self):
        """Test multiple search combinations"""
        test_cases = [
            # Location, Search term - chosen to likely have jobs
            ("San Francisco, CA", "software engineer"),
            ("New York, NY", "data scientist"),
            ("Remote", "python developer"),
            ("Grass Valley, CA", "software engineer"),  # Original failing case
            ("Austin, TX", "web developer"),
        ]
        
        print("🔥 Testing Multiple Search Combinations:")
        print("=" * 50)
        
        for location, search_term in test_cases:
            self.test_scraping_job_endpoint(search_term, location, max_jobs=3)
            time.sleep(2)  # Rate limiting
    
    def test_supported_sites(self):
        """Test supported sites endpoint"""
        try:
            response = requests.get(f"{self.base_url}/api/v1/scraping/sites", timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                supported_sites = data.get("supported_sites", [])
                
                self.log_result("Supported Sites", True, {
                    "status_code": response.status_code,
                    "supported_sites": len(supported_sites),
                    "sites": [site.get("id") for site in supported_sites],
                    "summary": f"Found {len(supported_sites)} supported sites"
                })
            else:
                self.log_result("Supported Sites", False, {
                    "status_code": response.status_code,
                    "error": f"HTTP {response.status_code}"
                })
                
        except Exception as e:
            self.log_result("Supported Sites", False, {
                "error": str(e)
            })
    
    def test_economics_endpoint(self):
        """Test cost savings economics endpoint"""
        try:
            response = requests.get(f"{self.base_url}/api/v1/scraping/economics", timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                self.log_result("Economics Endpoint", True, {
                    "status_code": response.status_code,
                    "lunch_status": data.get("lunch_status"),
                    "our_cost": data.get("our_solution", {}).get("cost_per_1000_jobs"),
                    "summary": f"Economics: {data.get('lunch_status', 'Unknown status')}"
                })
            else:
                self.log_result("Economics Endpoint", False, {
                    "status_code": response.status_code,
                    "error": f"HTTP {response.status_code}"
                })
                
        except Exception as e:
            self.log_result("Economics Endpoint", False, {
                "error": str(e)
            })
    
    def generate_report(self):
        """Generate comprehensive test report"""
        print("\n" + "=" * 60)
        print("📊 API TESTING REPORT")
        print("=" * 60)
        
        total_tests = len(self.results)
        passed_tests = len([r for r in self.results if r["success"]])
        failed_tests = total_tests - passed_tests
        
        print(f"Total Tests: {total_tests}")
        print(f"✅ Passed: {passed_tests}")
        print(f"❌ Failed: {failed_tests}")
        print(f"Success Rate: {(passed_tests/total_tests)*100:.1f}%")
        
        if failed_tests > 0:
            print("\n🔥 FAILED TESTS:")
            for result in self.results:
                if not result["success"]:
                    print(f"  • {result['test']}: {result['details'].get('error', 'Unknown error')}")
        
        # Save detailed results
        timestamp = int(time.time())
        report_file = f"tests/results/api_test_report_{timestamp}.json"
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
    """Run all API tests"""
    print("🚀 JOBBOT API TESTING SUITE")
    print("=" * 60)
    
    tester = APITester()
    
    # Basic connectivity tests
    print("1️⃣ Basic Connectivity Tests:")
    tester.test_health_endpoint()
    tester.test_scraping_status()
    tester.test_supported_sites()
    tester.test_economics_endpoint()
    
    print("\n2️⃣ Scraping Functionality Tests:")
    tester.test_multiple_searches()
    
    # Generate final report
    success = tester.generate_report()
    
    return 0 if success else 1

if __name__ == "__main__":
    exit(main())