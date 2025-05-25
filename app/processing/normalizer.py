"""
Data Normalization Pipeline for Phase 3B Processing.

Standardizes salary ranges, locations, job types, and experience levels
for consistent database storage and analysis.
"""

import re
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, Tuple
import logging

logger = logging.getLogger(__name__)


class DataNormalizer:
    """Normalize job data fields for consistent storage."""
    
    def __init__(self):
        """Initialize the data normalizer with pattern definitions."""
        # Salary extraction patterns
        self.salary_patterns = [
            # $50,000 - $75,000 format
            r'\$(\d{1,3}(?:,\d{3})*(?:\.\d{2})?)\s*[-–—to]\s*\$(\d{1,3}(?:,\d{3})*(?:\.\d{2})?)',
            # $50K - $75K format
            r'\$(\d{1,3}(?:,\d{3})*)(?:k|K)\s*[-–—to]\s*\$(\d{1,3}(?:,\d{3})*)(?:k|K)',
            # 50000 - 75000 (no dollar signs)
            r'(\d{1,3}(?:,\d{3})*)\s*[-–—to]\s*(\d{1,3}(?:,\d{3})*)\s*(?:per\s+year|annually|yearly)',
            # Up to $X format
            r'up\s+to\s+\$(\d{1,3}(?:,\d{3})*(?:\.\d{2})?)',
            # Starting at $X format
            r'starting\s+(?:at\s+)?\$(\d{1,3}(?:,\d{3})*(?:\.\d{2})?)',
            # Single salary figure
            r'\$(\d{1,3}(?:,\d{3})*(?:\.\d{2})?)\s*(?:per\s+year|annually|yearly)?',
        ]
        
        # Location standardization patterns
        self.state_abbreviations = {
            'alabama': 'AL', 'alaska': 'AK', 'arizona': 'AZ', 'arkansas': 'AR',
            'california': 'CA', 'colorado': 'CO', 'connecticut': 'CT', 'delaware': 'DE',
            'florida': 'FL', 'georgia': 'GA', 'hawaii': 'HI', 'idaho': 'ID',
            'illinois': 'IL', 'indiana': 'IN', 'iowa': 'IA', 'kansas': 'KS',
            'kentucky': 'KY', 'louisiana': 'LA', 'maine': 'ME', 'maryland': 'MD',
            'massachusetts': 'MA', 'michigan': 'MI', 'minnesota': 'MN', 'mississippi': 'MS',
            'missouri': 'MO', 'montana': 'MT', 'nebraska': 'NE', 'nevada': 'NV',
            'new hampshire': 'NH', 'new jersey': 'NJ', 'new mexico': 'NM', 'new york': 'NY',
            'north carolina': 'NC', 'north dakota': 'ND', 'ohio': 'OH', 'oklahoma': 'OK',
            'oregon': 'OR', 'pennsylvania': 'PA', 'rhode island': 'RI', 'south carolina': 'SC',
            'south dakota': 'SD', 'tennessee': 'TN', 'texas': 'TX', 'utah': 'UT',
            'vermont': 'VT', 'virginia': 'VA', 'washington': 'WA', 'west virginia': 'WV',
            'wisconsin': 'WI', 'wyoming': 'WY'
        }
        
        # Remote work keywords
        self.remote_keywords = [
            'remote', 'work from home', 'wfh', 'telecommute', 'virtual',
            'distributed', 'anywhere', 'home-based', 'telework'
        ]
        
        # Job type keywords
        self.job_type_keywords = {
            'full-time': ['full time', 'full-time', 'fulltime', 'ft', 'permanent'],
            'part-time': ['part time', 'part-time', 'parttime', 'pt'],
            'contract': ['contract', 'contractor', 'consulting', 'freelance', 'temp', 'temporary'],
            'internship': ['intern', 'internship', 'co-op', 'co op', 'student'],
        }
        
        # Experience level keywords
        self.experience_keywords = {
            'entry': ['entry', 'junior', 'new grad', 'graduate', '0-2', '0-1', 'beginner', 'associate'],
            'mid': ['mid', 'intermediate', 'experienced', '3-5', '2-5', '3-7', '4-6'],
            'senior': ['senior', 'lead', 'principal', 'staff', '5+', '7+', '8+', '10+', 'expert'],
        }
    
    def normalize_salary_ranges(self, salary_text: str) -> Dict[str, Optional[int]]:
        """
        Parse salary strings into min/max integers.
        
        Args:
            salary_text: Raw salary text from job posting
            
        Returns:
            Dictionary with 'min_salary' and 'max_salary' keys
        """
        if not salary_text or not isinstance(salary_text, str):
            return {'min_salary': None, 'max_salary': None}
        
        salary_text = salary_text.strip().lower()
        
        # Try each pattern
        for pattern in self.salary_patterns:
            match = re.search(pattern, salary_text, re.IGNORECASE)
            if match:
                try:
                    if len(match.groups()) == 2:  # Range pattern
                        min_sal = self._parse_salary_value(match.group(1), salary_text)
                        max_sal = self._parse_salary_value(match.group(2), salary_text)
                        
                        if min_sal and max_sal and min_sal <= max_sal:
                            return {'min_salary': min_sal, 'max_salary': max_sal}
                    
                    elif len(match.groups()) == 1:  # Single value pattern
                        sal = self._parse_salary_value(match.group(1), salary_text)
                        if sal:
                            if 'up to' in salary_text:
                                return {'min_salary': None, 'max_salary': sal}
                            elif 'starting' in salary_text:
                                return {'min_salary': sal, 'max_salary': None}
                            else:
                                # Single salary - use as both min and max
                                return {'min_salary': sal, 'max_salary': sal}
                
                except (ValueError, TypeError):
                    continue
        
        logger.debug(f"Could not parse salary: {salary_text}")
        return {'min_salary': None, 'max_salary': None}
    
    def standardize_locations(self, location_text: str) -> Dict[str, str]:
        """
        Normalize city, state, remote options.
        
        Args:
            location_text: Raw location text from job posting
            
        Returns:
            Dictionary with 'city', 'state', 'is_remote' keys
        """
        if not location_text or not isinstance(location_text, str):
            return {'city': '', 'state': '', 'is_remote': False}
        
        location_text = location_text.strip()
        
        # Check for remote work
        is_remote = any(keyword in location_text.lower() for keyword in self.remote_keywords)
        
        if is_remote:
            return {
                'city': 'Remote',
                'state': '',
                'is_remote': True
            }
        
        # Parse standard location formats
        # Format: "City, State" or "City, State ZIP"
        location_match = re.match(r'^([^,]+),\s*([A-Za-z\s]+?)(?:\s+\d{5}(?:-\d{4})?)?$', location_text)
        
        if location_match:
            city = location_match.group(1).strip().title()
            state_part = location_match.group(2).strip().lower()
            
            # Convert state name to abbreviation if needed
            if len(state_part) == 2:
                state = state_part.upper()
            else:
                state = self.state_abbreviations.get(state_part, state_part.title())
            
            return {
                'city': city,
                'state': state,
                'is_remote': False
            }
        
        # Fallback: treat as city if no comma found
        return {
            'city': location_text.title(),
            'state': '',
            'is_remote': False
        }
    
    def extract_job_types(self, description_text: str) -> str:
        """
        Identify full-time, part-time, contract, etc.
        
        Args:
            description_text: Job description or requirements text
            
        Returns:
            Standardized job type string
        """
        if not description_text or not isinstance(description_text, str):
            return 'Full-time'  # Default assumption
        
        text_lower = description_text.lower()
        
        # Check each job type category
        for job_type, keywords in self.job_type_keywords.items():
            if any(keyword in text_lower for keyword in keywords):
                return job_type.title()
        
        return 'Full-time'  # Default if no keywords found
    
    def categorize_experience_levels(self, requirements_text: str) -> str:
        """
        Extract entry, mid, senior level requirements.
        
        Args:
            requirements_text: Job requirements or description text
            
        Returns:
            Standardized experience level string
        """
        if not requirements_text or not isinstance(requirements_text, str):
            return 'Not specified'
        
        text_lower = requirements_text.lower()
        
        # Check for numeric experience requirements first
        numeric_matches = re.findall(r'(\d+)[-+]?\s*(?:years?|yrs?)\s*(?:of\s+)?experience', text_lower)
        if numeric_matches:
            years = int(numeric_matches[0])
            if years <= 2:
                return 'Entry level'
            elif years <= 6:
                return 'Mid level'
            else:
                return 'Senior level'
        
        # Check keyword-based experience levels
        for level, keywords in self.experience_keywords.items():
            if any(keyword in text_lower for keyword in keywords):
                if level == 'entry':
                    return 'Entry level'
                elif level == 'mid':
                    return 'Mid level'
                elif level == 'senior':
                    return 'Senior level'
        
        return 'Not specified'
    
    def extract_industry_from_description(self, description_text: str, company_name: str = '') -> str:
        """
        Attempt to identify industry from job description.
        
        Args:
            description_text: Job description text
            company_name: Company name for additional context
            
        Returns:
            Industry classification string
        """
        if not description_text:
            return 'Not specified'
        
        text_lower = (description_text + ' ' + company_name).lower()
        
        # Industry keyword mapping
        industry_keywords = {
            'Technology': [
                'software', 'tech', 'programming', 'development', 'engineer', 'developer',
                'cloud', 'data', 'ai', 'machine learning', 'cybersecurity', 'devops'
            ],
            'Healthcare': [
                'healthcare', 'medical', 'hospital', 'nurse', 'doctor', 'patient',
                'clinical', 'pharmaceutical', 'biotech', 'health'
            ],
            'Finance': [
                'finance', 'financial', 'banking', 'investment', 'accounting',
                'insurance', 'fintech', 'analyst', 'advisor'
            ],
            'Education': [
                'education', 'school', 'university', 'teacher', 'instructor',
                'academic', 'student', 'curriculum'
            ],
            'Retail': [
                'retail', 'sales', 'customer service', 'store', 'merchandise',
                'e-commerce', 'shopping'
            ],
            'Manufacturing': [
                'manufacturing', 'production', 'factory', 'assembly', 'quality',
                'industrial', 'operations'
            ],
            'Marketing': [
                'marketing', 'advertising', 'brand', 'campaign', 'social media',
                'content', 'seo', 'digital marketing'
            ],
        }
        
        # Score each industry
        industry_scores = {}
        for industry, keywords in industry_keywords.items():
            score = sum(1 for keyword in keywords if keyword in text_lower)
            if score > 0:
                industry_scores[industry] = score
        
        # Return highest scoring industry
        if industry_scores:
            return max(industry_scores.keys(), key=lambda k: industry_scores[k])
        
        return 'Not specified'
    
    def normalize_posting_date(self, date_text: str) -> Optional[str]:
        """
        Normalize posting date to ISO format.
        
        Args:
            date_text: Raw date text from job posting
            
        Returns:
            ISO formatted date string or None
        """
        if not date_text or not isinstance(date_text, str):
            return None
        
        date_text = date_text.strip().lower()
        
        # Handle relative dates
        today = datetime.now().date()
        
        if 'today' in date_text or 'just posted' in date_text:
            return today.isoformat()
        
        if 'yesterday' in date_text:
            return (today - timedelta(days=1)).isoformat()
        
        # Handle "X days ago" format
        days_ago_match = re.search(r'(\d+)\s*days?\s*ago', date_text)
        if days_ago_match:
            days = int(days_ago_match.group(1))
            return (today - timedelta(days=days)).isoformat()
        
        # Handle "X weeks ago" format
        weeks_ago_match = re.search(r'(\d+)\s*weeks?\s*ago', date_text)
        if weeks_ago_match:
            weeks = int(weeks_ago_match.group(1))
            return (today - timedelta(weeks=weeks)).isoformat()
        
        # Try to parse actual dates
        date_patterns = [
            r'(\d{1,2})/(\d{1,2})/(\d{4})',  # MM/DD/YYYY
            r'(\d{4})-(\d{1,2})-(\d{1,2})',  # YYYY-MM-DD
            r'(\d{1,2})-(\d{1,2})-(\d{4})',  # MM-DD-YYYY
        ]
        
        for pattern in date_patterns:
            match = re.search(pattern, date_text)
            if match:
                try:
                    if 'yyyy-mm-dd' in pattern:
                        year, month, day = match.groups()
                    else:
                        month, day, year = match.groups()
                    
                    parsed_date = datetime(int(year), int(month), int(day)).date()
                    
                    # Sanity check: don't accept future dates or very old dates
                    if today >= parsed_date >= (today - timedelta(days=365)):
                        return parsed_date.isoformat()
                
                except (ValueError, TypeError):
                    continue
        
        logger.debug(f"Could not parse date: {date_text}")
        return None
    
    def _parse_salary_value(self, value_str: str, original_text: str) -> Optional[int]:
        """Parse a single salary value, handling K notation and formatting."""
        if not value_str:
            return None
        
        try:
            # Remove commas and whitespace
            value_str = value_str.replace(',', '').replace(' ', '')
            
            # Handle K notation
            if 'k' in original_text.lower():
                return int(float(value_str) * 1000)
            else:
                return int(float(value_str))
        
        except (ValueError, TypeError):
            return None
    
    def normalize_all_fields(self, job_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Apply all normalization functions to a job record.
        
        Args:
            job_data: Raw job data dictionary
            
        Returns:
            Normalized job data dictionary
        """
        normalized = job_data.copy()
        
        # Normalize salary
        salary_info = self.normalize_salary_ranges(job_data.get('salary_range', ''))
        normalized.update(salary_info)
        
        # Normalize location
        location_info = self.standardize_locations(job_data.get('location', ''))
        normalized.update(location_info)
        
        # Normalize job type
        description = job_data.get('description', '') + ' ' + job_data.get('requirements', '')
        normalized['job_type'] = self.extract_job_types(description)
        
        # Normalize experience level
        normalized['experience_level'] = self.categorize_experience_levels(description)
        
        # Extract industry
        normalized['industry'] = self.extract_industry_from_description(
            description, job_data.get('company', '')
        )
        
        # Normalize posting date
        normalized['posting_date'] = self.normalize_posting_date(job_data.get('posting_date', ''))
        
        # Add normalization metadata
        normalized['normalization_date'] = datetime.now().isoformat()
        normalized['normalization_version'] = '3.1'
        
        return normalized