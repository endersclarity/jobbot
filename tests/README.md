# JobBot Testing Suite 🧪

Comprehensive testing framework for debugging and validating the JobBot scraping system.

## 🎯 What This Solves

The JobBot dashboard was showing "Network Error" when clicking "Scrape Now". This testing suite helps:

1. **Isolate the problem** - Is it network, scraper, or dashboard?
2. **Debug systematically** - Test each component independently  
3. **Verify fixes** - Ensure changes actually work
4. **Monitor performance** - Track scraping success rates

## 🗂️ Test Suite Structure

```
tests/
├── test_api_endpoints.py      # Test FastAPI scraping endpoints
├── test_scraper_direct.py     # Test Crawlee scraper directly 
├── test_dashboard_e2e.py      # Test React dashboard UI
├── run_all_tests.py          # Master test runner
├── README.md                 # This file
└── results/                  # Test outputs and screenshots
    ├── screenshots/          # Dashboard screenshots
    ├── scraper_debug_*.json  # Raw scraper outputs
    └── *_report_*.json       # Detailed test reports
```

## 🚀 Quick Start

### Run All Tests
```bash
# Run comprehensive test suite
python tests/run_all_tests.py
```

### Run Individual Test Suites
```bash
# Test API endpoints only
python tests/test_api_endpoints.py

# Test scraper directly  
python tests/test_scraper_direct.py

# Test dashboard (requires display)
python tests/test_dashboard_e2e.py
```

## 📋 Test Categories

### 1. API Endpoint Tests (`test_api_endpoints.py`)
Tests the FastAPI backend endpoints:
- ✅ Health endpoint connectivity
- ✅ Scraping status endpoint
- ✅ Job scraping with different search terms
- ✅ CORS and timeout handling
- ✅ Response schema validation

**Use when**: Dashboard shows network errors, API seems down

### 2. Direct Scraper Tests (`test_scraper_direct.py`)  
Tests the Node.js Crawlee scraper directly:
- ✅ Node.js and dependency availability
- ✅ CSS selector validation on job sites
- ✅ Anti-detection measures working
- ✅ Raw scraper output debugging
- ✅ Multiple location/search combinations

**Use when**: API works but returns 0 jobs, scraper seems broken

### 3. Dashboard E2E Tests (`test_dashboard_e2e.py`)
Tests the React dashboard interface:
- ✅ Dashboard loads correctly
- ✅ Navigation between pages
- ✅ Form filling and interaction
- ✅ Button clicks trigger requests
- ✅ Results display properly
- ✅ Console errors and network monitoring

**Use when**: Backend works but dashboard doesn't interact correctly

## 🔧 Prerequisites

### Python Dependencies
```bash
pip install requests playwright
playwright install  # Install browser binaries
```

### Node.js Dependencies  
```bash
npm install  # Install Crawlee and dependencies
```

### Running Services
Make sure these are running before testing:
- FastAPI backend: `http://172.22.206.209:8001`
- React dashboard: `http://172.22.206.209:3002`

## 📊 Understanding Test Results

### Success Indicators
- ✅ **Green checkmarks** = Tests passed
- 📊 **Success rate >80%** = System healthy
- 🟢 **HEALTHY status** = All core functionality working

### Failure Analysis
- ❌ **Red X marks** = Tests failed  
- 📋 **Recommendations section** = Specific fixes needed
- 🔍 **Issues categorized** = Network, scraper, dashboard, environment

### Report Files
- `comprehensive_report_*.json` = Complete analysis with recommendations
- `api_test_report_*.json` = Detailed API test results
- `scraper_test_report_*.json` = Scraper-specific debugging info
- `dashboard_test_report_*.json` = UI interaction results

## 🐛 Common Issues & Solutions

### "Network Error" in Dashboard
1. Run API tests first: `python tests/test_api_endpoints.py`
2. Check CORS configuration in `app/main.py`
3. Verify dashboard API URL in `dashboard/src/services/api.js`

### Scraper Returns 0 Jobs
1. Run scraper tests: `python tests/test_scraper_direct.py`  
2. Check CSS selectors are working on target sites
3. Test with locations that definitely have jobs (San Francisco, NY)
4. Verify anti-detection measures are effective

### Dashboard UI Issues
1. Run E2E tests: `python tests/test_dashboard_e2e.py`
2. Check browser console for JavaScript errors
3. Verify React components render correctly
4. Screenshots saved in `tests/results/screenshots/`

## 📈 Debugging Workflow

1. **Start with Master Runner**
   ```bash
   python tests/run_all_tests.py
   ```

2. **Follow Recommendations**
   - Read the recommendations section
   - Address highest priority issues first
   - Re-run tests to verify fixes

3. **Dive Deeper on Failures**
   - Run individual test suites for failed components
   - Check detailed JSON reports
   - Review screenshots and debug outputs

4. **Iterate and Improve**
   - Fix issues one by one
   - Re-run tests after each fix
   - Achieve >80% success rate for healthy system

## 🎯 Success Criteria

A healthy JobBot system should show:
- ✅ API endpoints responding correctly
- ✅ Scraper finding jobs (>0 results for major cities)
- ✅ Dashboard successfully triggering scrapes
- ✅ End-to-end workflow completing without errors
- 📊 Overall success rate >80%

## 💡 Pro Tips

- **Run tests after code changes** to catch regressions
- **Use screenshots** to debug UI issues visually  
- **Check detailed JSON reports** for specific error messages
- **Test with known-good data** (major cities) before edge cases
- **Monitor both success rate and actual job counts**

---

*This testing suite was created to solve the "Network Error" issue and provide ongoing system validation. Use it regularly to maintain system health!* 🚀