# Implementation Plan: Phase 3B - Offline Processing Pipeline

## Implementation Identity
**Name**: Phase 3B - Offline Processing Pipeline  
**Priority**: High  
**Status**: 🚧 Ready to Begin  
**Target Completion**: 2 weeks  
**Dependencies**: Phase 3A Raw Data Collection ✅ Complete  

## Overview
Transform raw scraped data into clean, structured, database-ready format without burning Claude Code tokens. Build robust data processing pipeline for thousands of job records.

## Problem Statement
Phase 3A successfully collects raw job data but produces unstructured HTML/JSON files. Need efficient offline processing to:
- Extract clean job data from raw HTML
- Deduplicate job postings across sources
- Normalize salary, location, and other fields
- Validate data quality before database import
- Handle processing errors gracefully

## Implementation Approach

### Week 1: Core Processing Infrastructure

#### Day 1-2: HTML Parser and Data Extractor
```python
# New module: app/processing/html_parser.py
class JobDataExtractor:
    def extract_from_indeed_html(self, raw_html):
        """Extract structured data from Indeed job HTML"""
        
    def extract_from_json_dump(self, raw_json):
        """Process JSON data from scrapers"""
        
    def normalize_job_fields(self, raw_job_data):
        """Standardize field formats and values"""
        
    def validate_required_fields(self, job_data):
        """Ensure minimum data quality standards"""
```

**Technical Details:**
- **BeautifulSoup** for robust HTML parsing
- **Regex patterns** for salary/location extraction
- **Field mapping** from raw data to database schema
- **Error logging** for parsing failures

**Input:** `scraped_data/raw/indeed_jobs_*.json`  
**Output:** `scraped_data/processed/cleaned_jobs_*.json`

#### Day 3-4: Duplicate Detection System
```python
# New module: app/processing/deduplication.py
class DuplicateDetector:
    def generate_job_hash(self, job_data):
        """Create unique hash: company + title + location"""
        
    def detect_url_duplicates(self, job_list):
        """Find exact URL matches"""
        
    def detect_content_duplicates(self, job_list):
        """Find similar content with fuzzy matching"""
        
    def merge_duplicate_records(self, duplicate_group):
        """Combine information from duplicate jobs"""
```

**Deduplication Strategy:**
1. **Exact URL Match**: Highest priority, perfect duplicates
2. **Hash Match**: Company + normalized title + location
3. **Fuzzy Matching**: Similar titles with edit distance < 3
4. **Date Preference**: Keep most recent posting

#### Day 5-7: Data Normalization Pipeline
```python
# New module: app/processing/normalizer.py
class DataNormalizer:
    def normalize_salary_ranges(self, salary_text):
        """Parse salary strings into min/max integers"""
        
    def standardize_locations(self, location_text):
        """Normalize city, state, remote options"""
        
    def extract_job_types(self, description_text):
        """Identify full-time, part-time, contract, etc."""
        
    def categorize_experience_levels(self, requirements_text):
        """Extract entry, mid, senior level requirements"""
```

**Normalization Rules:**
- **Salary**: Extract numeric ranges, handle "$50K - $75K" → (50000, 75000)
- **Location**: "San Francisco, CA" → city="San Francisco", state="CA"
- **Remote**: Detect "remote", "work from home", "WFH" keywords
- **Experience**: "2-5 years" → experience_level="mid"

### Week 2: Processing Pipeline and Database Integration

#### Day 8-10: Batch Processing System
```python
# New module: app/processing/batch_processor.py
class BatchProcessor:
    def process_daily_batch(self, date_str):
        """Process all files for a specific date"""
        
    def process_file_queue(self, file_list):
        """Process multiple files in sequence"""
        
    def generate_processing_report(self, batch_results):
        """Create summary of processing results"""
        
    def handle_processing_errors(self, error_list):
        """Log and categorize processing failures"""
```

**Processing Workflow:**
1. **File Discovery**: Scan `scraped_data/raw/` for unprocessed files
2. **Data Extraction**: Parse HTML/JSON to structured data
3. **Deduplication**: Remove duplicate jobs within batch
4. **Normalization**: Standardize all field formats
5. **Validation**: Check data quality requirements
6. **Export**: Save cleaned data to `scraped_data/processed/`

#### Day 11-12: Database Import System
```python
# New module: app/processing/db_importer.py
class DatabaseImporter:
    def bulk_import_jobs(self, processed_job_file):
        """Import cleaned jobs to database efficiently"""
        
    def update_existing_jobs(self, job_updates):
        """Update job records with new information"""
        
    def handle_import_conflicts(self, conflict_list):
        """Resolve database constraint violations"""
        
    def generate_import_statistics(self, import_results):
        """Report import success/failure metrics"""
```

**Import Strategy:**
- **Bulk INSERT**: Use SQLAlchemy bulk operations for performance
- **Conflict Resolution**: Handle unique constraint violations gracefully
- **Progress Tracking**: Log import progress for large batches
- **Rollback Support**: Transaction management for failed imports

#### Day 13-14: Quality Assurance and Monitoring
```python
# New module: app/processing/quality_monitor.py
class QualityMonitor:
    def validate_data_completeness(self, processed_data):
        """Check percentage of required fields populated"""
        
    def detect_data_anomalies(self, job_batch):
        """Identify unusual patterns or outliers"""
        
    def generate_quality_report(self, processing_session):
        """Create detailed quality metrics"""
        
    def recommend_improvements(self, quality_issues):
        """Suggest processing pipeline improvements"""
```

## File Structure Changes

### New Processing Modules
```
app/
├── processing/                   # New processing package
│   ├── __init__.py
│   ├── html_parser.py           # HTML/JSON data extraction
│   ├── deduplication.py         # Duplicate detection and merging
│   ├── normalizer.py            # Data field normalization
│   ├── batch_processor.py       # Batch processing orchestration
│   ├── db_importer.py           # Database import utilities
│   └── quality_monitor.py       # Data quality validation
└── cli/                         # New CLI package
    ├── __init__.py
    └── process_data.py           # Command-line processing interface
```

### Enhanced Data Storage
```
scraped_data/
├── raw/                         # Unprocessed scraper output
│   ├── indeed_jobs_20250524.json
│   └── grassvalley_enhanced_20250524.json
├── processed/                   # Cleaned, normalized data
│   ├── cleaned_jobs_20250524.json
│   └── processing_report_20250524.json
├── imported/                    # Successfully imported to database
│   └── import_log_20250524.json
└── errors/                      # Processing failures for review
    ├── parsing_errors_20250524.json
    └── validation_failures_20250524.json
```

## CLI Interface
```bash
# Process specific date
python -m app.cli.process_data --date 2025-05-24

# Process all pending files
python -m app.cli.process_data --process-all

# Import to database
python -m app.cli.process_data --import --file processed/cleaned_jobs_20250524.json

# Generate quality report
python -m app.cli.process_data --quality-report --date 2025-05-24
```

## Data Quality Standards

### Required Fields (Must be present)
- **title**: Job title (non-empty string)
- **company**: Company name (non-empty string)
- **location**: Location information (city/state or "Remote")

### Validated Fields (Quality checked)
- **salary_min/max**: Numeric values, min <= max
- **posting_date**: Valid date format, not future
- **job_url**: Valid URL format, unique in batch
- **description**: Minimum 50 characters
- **requirements**: Minimum 20 characters

### Quality Metrics
- **Completeness**: % of jobs with all required fields
- **Accuracy**: % of validated fields passing checks
- **Uniqueness**: % of jobs without duplicates
- **Freshness**: Average age of job postings

## Performance Targets

### Processing Speed
- **Parsing Rate**: 100+ jobs per minute
- **Deduplication**: Handle 10,000+ jobs in memory
- **Normalization**: Process full batch in < 5 minutes
- **Database Import**: 1,000+ jobs per minute bulk insert

### Data Quality Goals
- **Required Field Completeness**: > 95%
- **Salary Parsing Success**: > 80%
- **Location Normalization**: > 90%
- **Duplicate Detection**: > 99% accuracy

## Error Handling Strategy

### Parsing Errors
- **Log Details**: Raw HTML snippet, error message, job URL
- **Graceful Degradation**: Save partial data when possible
- **Manual Review Queue**: Flag complex cases for human review

### Validation Failures
- **Field-Level Validation**: Check each field independently
- **Soft Failures**: Allow import with warnings for minor issues
- **Hard Failures**: Reject jobs missing critical data

### Database Errors
- **Constraint Violations**: Handle unique constraint conflicts
- **Connection Issues**: Retry with exponential backoff
- **Transaction Rollback**: Maintain data consistency

## Testing Strategy

### Unit Tests
```python
def test_salary_parsing():
    """Test various salary format parsing"""
    
def test_duplicate_detection():
    """Validate duplicate identification accuracy"""
    
def test_data_normalization():
    """Check field standardization results"""
```

### Integration Tests
```python
def test_end_to_end_processing():
    """Test complete raw → processed → imported workflow"""
    
def test_batch_processing_performance():
    """Validate processing speed with large datasets"""
```

### Quality Assurance
- **Sample Data Validation**: Manual review of processed results
- **Performance Benchmarking**: Processing speed measurement
- **Data Accuracy Verification**: Spot-check against original sources

## Success Criteria

### Technical Milestones
- [ ] Process 1,000+ jobs without errors
- [ ] Achieve < 5% duplicate rate in processed data
- [ ] Import 10,000+ jobs to database successfully
- [ ] Maintain processing speed > 50 jobs/minute

### Quality Milestones
- [ ] 95%+ required field completeness
- [ ] 85%+ salary parsing success rate
- [ ] 90%+ location normalization accuracy
- [ ] < 2% false positive duplicate detection

### Operational Milestones
- [ ] Automated daily processing pipeline
- [ ] Quality monitoring dashboard
- [ ] Error handling and recovery procedures
- [ ] Documentation for maintenance and scaling

---

*This implementation completes the token-efficient scraping strategy by providing robust offline data processing without burning Claude Code tokens on content analysis.*