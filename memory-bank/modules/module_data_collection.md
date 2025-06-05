# Module: LLM-Guided Data Collection

## Purpose & Responsibility
The LLM-Guided Data Collection module revolutionizes job data extraction by combining Claude Code's intelligent interpretation with Browser MCP automation and human guidance. This approach replaces brittle automated scrapers with an adaptive, reliable system that can handle authentication, site changes, and anti-bot measures naturally while maintaining high data quality and extraction efficiency.

## ARCHITECTURAL PIVOT: From Automation to LLM-Guided Extraction

### The Transformation
**Previous Approach**: Fully automated scrapers with complex anti-detection
**New Approach**: LLM interpretation + Browser MCP + Human guidance
**Core Insight**: Human+AI collaboration is more reliable than complex automation

## New LLM-Guided Interfaces
* `LLMGuidedScraper`: Intelligent extraction interface
  * `guided_site_navigation()`: LLM interprets and navigates job sites
  * `adaptive_data_extraction()`: Extract structured data with LLM interpretation
  * `handle_authentication()`: Human-guided login and verification flows
  * `session_management()`: Maintain browsing sessions across interactions
* `BrowserMCPIntegration`: Browser automation with human guidance
  * `launch_guided_session()`: Start Browser MCP with LLM oversight
  * `navigate_with_adaptation()`: Navigate sites with real-time LLM guidance
  * `extract_with_intelligence()`: Use LLM to interpret page content and structure
* `JSONExportPipeline`: Data export and transfer
  * `structure_extracted_data()`: Format scraped data into standardized JSON
  * `export_session_results()`: Export job data for dashboard import
  * `validate_extraction_quality()`: LLM-assisted quality validation
* Input: Site URLs, search parameters, human authentication assistance
* Output: Structured JSON files ready for dashboard import

## Implementation Details (LLM-Guided Architecture)
* Environment: 
  - **Claude Code**: Primary scraping environment with Browser MCP integration
  - **Browser MCP**: Headless browser automation with LLM oversight
  - **Human Interface**: Authentication, captcha solving, guidance provision
* Core Workflow:
  - **Session Initiation**: Start Browser MCP within Claude Code session
  - **Site Navigation**: LLM interprets site structure and guides navigation
  - **Data Extraction**: LLM identifies and extracts relevant job information
  - **Quality Validation**: Real-time validation of extracted data accuracy
  - **JSON Export**: Format and export structured data for dashboard import
* Key Advantages:
  - **Immediate Adaptation**: LLM adjusts to site changes without code updates
  - **Natural Authentication**: Human handles complex login flows seamlessly
  - **Intelligent Extraction**: LLM interprets page content contextually
  - **Session Continuity**: Maintain browsing state across interactions
* Data Models
  - `LLMGuidedSession`: Session state with LLM interaction history
  - `ExtractedJobData`: Structured job information with LLM validation
  - `ExportedDataset`: JSON-formatted data ready for dashboard import

## Current Implementation Status (Post-Pivot)
* Architecture Status: 
  - ✅ **Pivot Decision**: Completed transition from automated to LLM-guided approach
  - ✅ **Lessons Learned**: Documented failures and insights from automated scraping attempts
  - ✅ **Browser MCP Integration**: Basic Browser MCP functionality verified
  - ✅ **Site Analysis**: Identified which sites require LLM-guided vs simple approaches
* Ready for Implementation: 
  - **LLM-Guided Scraping Patterns**: Design proven workflow for guided extraction
  - **Browser MCP Sessions**: Establish reliable session management with Browser MCP
  - **JSON Export Pipeline**: Create standardized data export for dashboard import
  - **Authentication Handling**: Develop human-in-the-loop authentication flows
* Next Priority Implementation: 
  - **Indeed LLM-Guided Scraper**: Implement first LLM-guided extraction workflow
  - **LinkedIn Authentication Flow**: Human-guided login and data extraction
  - **Dashboard Import System**: JSON data import and processing capabilities

## Implementation Plans & Tasks (LLM-Guided)
* `implementation_llm_guided_scraping.md` (NEW)
  - [Browser MCP Integration]: Establish reliable LLM + Browser MCP workflow
  - [Guided Navigation Patterns]: Design repeatable site interaction patterns
  - [JSON Export Pipeline]: Create standardized data export for dashboard
  - [Authentication Workflows]: Human-in-the-loop login and verification flows
* `implementation_strategic_pivot.md` (UPDATED)
  - [Multi-Site LLM Guidance]: Extend guided scraping to multiple job platforms
  - [Company Research Integration]: LLM-guided company website analysis
  - [Contact Discovery]: Intelligent identification of decision makers
  - [Tech Stack Detection]: LLM-powered technology stack identification

## Competitive Advantages of LLM-Guided Approach
1. **Zero Infrastructure Costs**: No scraping service subscriptions ($0 vs $500-10,000/month)
2. **Immediate Adaptation**: LLM adjusts to site changes without development time
3. **Perfect Authentication**: Human naturally handles all auth complexity
4. **Undetectable**: Real human browsing patterns cannot be blocked
5. **Higher Accuracy**: LLM interpretation more accurate than brittle selectors
6. **Lower Maintenance**: No code updates needed for site changes

## Mini Dependency Tracker (Updated)
---mini_tracker_start---
Dependencies:
- Claude Code environment with Browser MCP access
- Human operator for authentication and guidance
- JSON export/import capabilities for data transfer
- Browser MCP server and WebDriver infrastructure

Dependents:
- Dashboard Interface module (receives exported JSON data)
- Database Infrastructure module (imports processed data)
- Intelligence Analysis module (analyzes extracted data)
- All downstream business intelligence and opportunity detection systems
---mini_tracker_end---