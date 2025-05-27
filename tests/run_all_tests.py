#!/usr/bin/env python3
"""
Master Test Runner

Runs all testing suites and generates a comprehensive report:
- API endpoint tests
- Direct scraper tests  
- Dashboard E2E tests
- Integration tests
- Generates combined report with actionable recommendations
"""

import subprocess
import sys
import time
import json
from pathlib import Path
from typing import Dict, List, Any

class MasterTestRunner:
    def __init__(self):
        self.test_results = {}
        self.start_time = time.time()
        
        # Ensure results directory exists
        Path("tests/results").mkdir(parents=True, exist_ok=True)
    
    def run_test_suite(self, test_name: str, test_script: str) -> Dict[str, Any]:
        """Run a test suite and capture results"""
        print(f"\n{'='*60}")
        print(f"🚀 RUNNING: {test_name}")
        print(f"{'='*60}")
        
        try:
            start_time = time.time()
            
            # Run the test script
            result = subprocess.run(
                [sys.executable, test_script],
                capture_output=True,
                text=True,
                timeout=300  # 5 minutes max per test suite
            )
            
            elapsed = time.time() - start_time
            
            # Parse output for results
            success = result.returncode == 0
            
            return {
                "test_name": test_name,
                "success": success,
                "execution_time": elapsed,
                "return_code": result.returncode,
                "stdout": result.stdout,
                "stderr": result.stderr,
                "summary": f"{'PASSED' if success else 'FAILED'} in {elapsed:.1f}s"
            }
            
        except subprocess.TimeoutExpired:
            return {
                "test_name": test_name,
                "success": False,
                "execution_time": 300,
                "return_code": -1,
                "stdout": "",
                "stderr": "Test suite timed out after 5 minutes",
                "summary": "TIMEOUT after 300s"
            }
        except Exception as e:
            return {
                "test_name": test_name,
                "success": False,
                "execution_time": 0,
                "return_code": -1,
                "stdout": "",
                "stderr": str(e),
                "summary": f"ERROR: {str(e)}"
            }
    
    def analyze_results(self) -> Dict[str, Any]:
        """Analyze all test results and generate recommendations"""
        total_suites = len(self.test_results)
        passed_suites = len([r for r in self.test_results.values() if r["success"]])
        failed_suites = total_suites - passed_suites
        
        # Categorize issues
        issues = {
            "network_connectivity": [],
            "scraper_functionality": [],
            "dashboard_ui": [],
            "environment_setup": []
        }
        
        recommendations = []
        
        # Check API tests
        api_result = self.test_results.get("API Endpoints")
        if api_result and not api_result["success"]:
            if "connection" in api_result["stderr"].lower() or "network" in api_result["stderr"].lower():
                issues["network_connectivity"].append("API endpoints unreachable")
                recommendations.append("🔧 Check if FastAPI server is running on correct port")
                recommendations.append("🔧 Verify CORS configuration")
            
        # Check scraper tests
        scraper_result = self.test_results.get("Direct Scraper")
        if scraper_result and not scraper_result["success"]:
            if "node" in scraper_result["stderr"].lower():
                issues["environment_setup"].append("Node.js environment issues")
                recommendations.append("🔧 Install Node.js and npm dependencies")
            elif "selector" in scraper_result["stderr"].lower():
                issues["scraper_functionality"].append("CSS selector problems")
                recommendations.append("🔧 Update CSS selectors for job sites")
            elif "crawlee" in scraper_result["stderr"].lower():
                issues["scraper_functionality"].append("Crawlee framework issues")
                recommendations.append("🔧 Check Crawlee installation and configuration")
        
        # Check dashboard tests
        dashboard_result = self.test_results.get("Dashboard E2E")
        if dashboard_result and not dashboard_result["success"]:
            if "browser" in dashboard_result["stderr"].lower():
                issues["environment_setup"].append("Browser automation issues")
                recommendations.append("🔧 Install Playwright browsers: playwright install")
            elif "network error" in dashboard_result["stdout"].lower():
                issues["network_connectivity"].append("Dashboard can't reach API")
                recommendations.append("🔧 Check API URL configuration in dashboard")
        
        # Generate system health assessment
        health_score = (passed_suites / total_suites) * 100 if total_suites > 0 else 0
        
        if health_score >= 80:
            health_status = "🟢 HEALTHY"
        elif health_score >= 50:
            health_status = "🟡 DEGRADED"
        else:
            health_status = "🔴 CRITICAL"
        
        return {
            "overview": {
                "total_test_suites": total_suites,
                "passed_suites": passed_suites,
                "failed_suites": failed_suites,
                "success_rate": health_score,
                "health_status": health_status,
                "total_execution_time": time.time() - self.start_time
            },
            "issues": issues,
            "recommendations": recommendations,
            "detailed_results": self.test_results
        }
    
    def generate_comprehensive_report(self, analysis: Dict[str, Any]):
        """Generate comprehensive test report"""
        print(f"\n{'='*80}")
        print("🎯 JOBBOT COMPREHENSIVE TEST REPORT")
        print(f"{'='*80}")
        
        overview = analysis["overview"]
        print(f"System Health: {overview['health_status']}")
        print(f"Success Rate: {overview['success_rate']:.1f}%")
        print(f"Test Suites: {overview['passed_suites']}/{overview['total_test_suites']} passed")
        print(f"Total Time: {overview['total_execution_time']:.1f}s")
        
        # Show individual test results
        print(f"\n📊 TEST SUITE RESULTS:")
        for test_name, result in self.test_results.items():
            status = "✅" if result["success"] else "❌"
            print(f"  {status} {test_name}: {result['summary']}")
        
        # Show issues
        issues = analysis["issues"]
        if any(issues.values()):
            print(f"\n🔍 IDENTIFIED ISSUES:")
            for category, issue_list in issues.items():
                if issue_list:
                    print(f"  🔸 {category.replace('_', ' ').title()}:")
                    for issue in issue_list:
                        print(f"    • {issue}")
        
        # Show recommendations
        recommendations = analysis["recommendations"]
        if recommendations:
            print(f"\n💡 RECOMMENDATIONS:")
            for i, rec in enumerate(recommendations, 1):
                print(f"  {i}. {rec}")
        
        # Show next steps
        print(f"\n🎯 NEXT STEPS:")
        if overview["success_rate"] >= 80:
            print("  ✅ System is healthy! Focus on optimizing scraper performance.")
        elif overview["success_rate"] >= 50:
            print("  🔧 Address failed test suites to improve system reliability.")
        else:
            print("  🚨 Critical issues detected. Focus on basic connectivity and setup.")
            print("  📋 Start with environment setup and API connectivity.")
        
        # Save detailed report
        timestamp = int(time.time())
        report_file = f"tests/results/comprehensive_report_{timestamp}.json"
        
        with open(report_file, 'w') as f:
            json.dump(analysis, f, indent=2, default=str)
        
        print(f"\n📄 Detailed report saved: {report_file}")
        
        return overview["success_rate"] >= 50  # 50% success threshold

def main():
    """Run all test suites"""
    print("🚀 JOBBOT MASTER TEST RUNNER")
    print(f"Started at: {time.strftime('%Y-%m-%d %H:%M:%S')}")
    
    runner = MasterTestRunner()
    
    # Define test suites to run
    test_suites = [
        ("API Endpoints", "tests/test_api_endpoints.py"),
        ("Direct Scraper", "tests/test_scraper_direct.py"),
        ("Dashboard E2E", "tests/test_dashboard_e2e.py"),
    ]
    
    # Run each test suite
    for test_name, test_script in test_suites:
        if Path(test_script).exists():
            result = runner.run_test_suite(test_name, test_script)
            runner.test_results[test_name] = result
        else:
            print(f"⚠️  Test script not found: {test_script}")
            runner.test_results[test_name] = {
                "test_name": test_name,
                "success": False,
                "summary": f"Test script not found: {test_script}"
            }
    
    # Analyze results and generate report
    analysis = runner.analyze_results()
    success = runner.generate_comprehensive_report(analysis)
    
    return 0 if success else 1

if __name__ == "__main__":
    exit(main())