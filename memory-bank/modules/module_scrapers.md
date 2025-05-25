# Module: Web Scrapers

## Module Identity
**Name**: Web Scrapers  
**Location**: `app/scrapers/` and root scripts  
**Status**: 🚧 Phase 3A Complete, Phase 3B In Progress  
**Version**: 3.1 (Strategic Pivot with BrowserMCP)  

## Purpose
Intelligent web scraping system for job boards with anti-detection measures, rate limiting, and token-efficient raw data collection. Evolved to support business intelligence gathering for the strategic pivot to market creation.

## Current Implementation

### Core Scraper Components
- **Indeed Scraper** (`app/scrapers/indeed.py`): Primary job board scraper
- **Browser Scraper** (`app/scrapers/browser_scraper.py`): BrowserMCP integration
- **Configuration** (`app/scrapers/config.py`): Scraper settings and parameters
- **CLI Scripts**: Multiple standalone scraping implementations

### Anti-Detection Features ✅
- **BrowserMCP Integration**: Real browser automation bypassing 403 errors
- **User Agent Rotation**: Randomized browser fingerprints
- **Request Delays**: Intelligent rate limiting (1-3 second delays)
- **Header Randomization**: Realistic request headers
- **Session Management**: Persistent cookies and session state

### Data Storage Strategy
```
scraped_data/
├── raw/                       # Unprocessed scraped data
│   ├── indeed_jobs_YYYYMMDD_HHMMSS.json
│   └── browser_test_plan.json
├── processed/                 # Cleaned data ready for database
└── logs/                     # Scraping operation logs
    └── indeed_scraper_YYYYMMDD.log
```

## File Structure
```
app/scrapers/
├── __init__.py
├── browser_scraper.py        # BrowserMCP integration
├── config.py                 # Scraper configuration
└── indeed.py                 # Indeed-specific scraper

# Root-level scraper scripts
├── scrape_jobs.py           # Basic Indeed scraper
├── grassvalley_scraper_working.py  # Location-specific scraper
├── puppeteer_grassvalley_scraper.py  # Puppeteer implementation
├── round5_advanced_headers.py      # Advanced anti-detection
├── round6_indeed_attack.py         # BrowserMCP implementation
└── test_browser_scraper.py         # Testing and validation
```

## Strategic Evolution Components

### Phase 3A: Raw Data Collection ✅
- **Token-Efficient Strategy**: Save raw HTML/JSON without LLM processing
- **Bulk Collection**: Scrape thousands of jobs without Claude Code limits
- **Data Rotation**: Daily/hourly batch organization
- **Quality Logging**: Comprehensive operation tracking

### Phase 3B: Business Intelligence (In Progress)
- **Company Research**: Local business data gathering
- **Market Analysis**: Industry trend identification  
- **Opportunity Detection**: Automation potential assessment
- **Value Proposition Data**: Problem/solution matching

## Current Capabilities

### Indeed Scraping ✅
```python
# Example usage
from app.scrapers.indeed import IndeedScraper

scraper = IndeedScraper()
jobs = scraper.scrape_jobs(
    search_term="python developer",
    location="grass valley ca", 
    max_jobs=50
)
```

### BrowserMCP Integration ✅
```python
# Anti-detection browser automation
from app.scrapers.browser_scraper import BrowserScraper

scraper = BrowserScraper()
success = scraper.scrape_indeed_with_browser(
    search_term="software engineer",
    location="remote",
    max_results=100
)
```

### Data Processing Pipeline 🚧
- **Duplicate Detection**: URL and title+company hash matching
- **Data Normalization**: Salary parsing, location standardization
- **Quality Validation**: Required field checking
- **Database Import**: Bulk import API integration

## Configuration
```python
# Scraper settings
SCRAPER_CONFIG = {
    "rate_limit_delay": (1, 3),        # Random delay range
    "max_retries": 3,                   # Retry failed requests
    "timeout": 30,                      # Request timeout
    "user_agents": [...],               # Rotation pool
    "headers": {...},                   # Request headers
    "proxy_rotation": False,            # Proxy support (planned)
}
```

## Performance Metrics
- **Success Rate**: 85%+ job extraction success
- **Anti-Detection**: 403 errors reduced to <5%
- **Speed**: 50-100 jobs per minute with rate limiting
- **Data Quality**: 90%+ fields populated correctly

## Implemented Scripts Analysis

### Production-Ready
- ✅ **`round6_indeed_attack.py`**: BrowserMCP implementation, best anti-detection
- ✅ **`grassvalley_scraper_working.py`**: Location-specific, proven results
- ✅ **`app/scrapers/browser_scraper.py`**: Modular BrowserMCP integration

### Development/Testing
- 🧪 **`round5_advanced_headers.py`**: Header rotation testing
- 🧪 **`test_browser_scraper.py`**: Validation and testing framework
- 🧪 **`simple_test.py`**: Basic functionality verification

### Legacy/Reference
- 📁 **`scrape_jobs.py`**: Original implementation (requests-based)
- 📁 **`puppeteer_grassvalley_scraper.py`**: Puppeteer attempt (dependency issues)

## Strategic Pivot Integration

### Business Intelligence Extensions
```python
# Planned business research capabilities
class BusinessResearcher:
    def research_local_companies(self, location, industry)
    def identify_automation_opportunities(self, company_data)
    def generate_value_propositions(self, opportunities)
    def create_outreach_targets(self, propositions)
```

### Data Model Evolution
- **Companies Table**: Local business intelligence
- **Opportunities Table**: Automation potential tracking
- **Value Propositions**: Problem/solution matching
- **Outreach Campaigns**: Business development tracking

## Dependencies
- **requests**: HTTP client for web requests
- **beautifulsoup4**: HTML parsing and data extraction
- **selenium**: Browser automation (fallback)
- **browsermcp**: Real browser automation (primary)
- **lxml**: Fast XML/HTML processing
- **fake-useragent**: User agent rotation

## Next Phase Requirements

### Phase 3B: Offline Processing
- [ ] HTML content extraction pipeline
- [ ] Duplicate detection and deduplication
- [ ] Data quality validation and filtering
- [ ] Bulk database import system

### Strategic Pivot: Business Intelligence
- [ ] Local company database scraping
- [ ] Industry analysis and trend detection
- [ ] Automation opportunity identification
- [ ] Value proposition generation system

## Error Handling
- **Network Errors**: Automatic retry with exponential backoff
- **Parsing Errors**: Graceful degradation with partial data
- **Rate Limiting**: Dynamic delay adjustment
- **Anti-Bot Measures**: BrowserMCP fallback strategies

## Testing Strategy
```bash
# Unit tests
pytest tests/test_scrapers.py

# Integration tests
python test_browser_scraper.py

# Manual validation
python round6_indeed_attack.py --test-mode
```

---

*This module provides the critical data collection infrastructure for both traditional job scraping and the strategic pivot to business intelligence gathering.*