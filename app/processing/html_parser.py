"""
HTML Parser and Data Extractor for Phase 3B Processing Pipeline.

Extracts structured job data from raw HTML and JSON scraped files
without burning Claude Code tokens on content analysis.
"""

import json
import re
from datetime import datetime
from typing import Dict, Any, List, Optional
from bs4 import BeautifulSoup
import logging

logger = logging.getLogger(__name__)


class JobDataExtractor:
    """Extract structured job data from raw scraped HTML and JSON."""

    def __init__(self):
        """Initialize the job data extractor."""
        self.salary_patterns = [
            r"\$(\d{1,3}(?:,\d{3})*(?:\.\d{2})?)\s*-\s*\$(\d{1,3}(?:,\d{3})*(?:\.\d{2})?)",
            r"\$(\d{1,3}(?:,\d{3})*(?:\.\d{2})?)\s*to\s*\$(\d{1,3}(?:,\d{3})*(?:\.\d{2})?)",
            r"(\d{1,3}(?:,\d{3})*)\s*-\s*(\d{1,3}(?:,\d{3})*)\s*(?:per\s+year|annually)",
            r"\$(\d{1,3}(?:,\d{3})*)(?:k|K)\s*-\s*\$(\d{1,3}(?:,\d{3})*)(?:k|K)",
        ]

        self.location_patterns = [
            r"^([^,]+),\s*([A-Z]{2})(?:\s+\d{5})?$",  # City, State format
            r"^([^,]+),\s*([^,]+),\s*([A-Z]{2})$",  # City, County, State
            r"^Remote\s*(?:in\s*(.+))?$",  # Remote locations
        ]

    def extract_from_indeed_html(self, raw_html: str) -> List[Dict[str, Any]]:
        """
        Extract structured data from Indeed job HTML.

        Args:
            raw_html: Raw HTML content from Indeed scraping

        Returns:
            List of extracted job dictionaries
        """
        try:
            soup = BeautifulSoup(raw_html, "html.parser")
            jobs = []

            # Find job containers (Indeed uses various selectors)
            job_containers = soup.find_all(
                ["div"], attrs={"class": re.compile(r"job_seen_beacon|slider_container|jobsearch-SerpJobCard")}
            )

            if not job_containers:
                # Fallback: look for any div with job-related data attributes
                job_containers = soup.find_all(["div"], attrs={"data-jk": True})  # Indeed job key attribute

            for container in job_containers:
                try:
                    job_data = self._extract_job_from_container(container)
                    if job_data and self._is_valid_job(job_data):
                        jobs.append(job_data)
                except Exception as e:
                    logger.warning(f"Failed to extract job from container: {e}")
                    continue

            logger.info(f"Extracted {len(jobs)} jobs from HTML")
            return jobs

        except Exception as e:
            logger.error(f"Failed to parse HTML: {e}")
            return []

    def extract_from_json_dump(self, raw_json: str) -> List[Dict[str, Any]]:
        """
        Process JSON data from scrapers.

        Args:
            raw_json: JSON string from scraper output

        Returns:
            List of processed job dictionaries
        """
        try:
            data = json.loads(raw_json)

            # Handle different JSON structures
            if isinstance(data, list):
                jobs = data
            elif isinstance(data, dict) and "jobs" in data:
                jobs = data["jobs"]
            elif isinstance(data, dict) and "results" in data:
                jobs = data["results"]
            else:
                jobs = [data]  # Single job object

            processed_jobs = []
            for job in jobs:
                try:
                    normalized_job = self.normalize_job_fields(job)
                    if self._is_valid_job(normalized_job):
                        processed_jobs.append(normalized_job)
                except Exception as e:
                    logger.warning(f"Failed to normalize job: {e}")
                    continue

            logger.info(f"Processed {len(processed_jobs)} jobs from JSON")
            return processed_jobs

        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON format: {e}")
            return []
        except Exception as e:
            logger.error(f"Failed to process JSON: {e}")
            return []

    def normalize_job_fields(self, raw_job_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Standardize field formats and values.

        Args:
            raw_job_data: Raw job data dictionary

        Returns:
            Normalized job data dictionary
        """
        normalized = {}

        # Standard field mappings
        field_mappings = {
            "title": ["title", "job_title", "position", "jobTitle"],
            "company": ["company", "company_name", "employer", "companyName"],
            "location": ["location", "job_location", "city", "jobLocation"],
            "description": ["description", "job_description", "summary", "jobDescription"],
            "requirements": ["requirements", "qualifications", "skills"],
            "benefits": ["benefits", "perks", "compensation"],
            "job_url": ["url", "job_url", "link", "apply_url"],
            "salary_range": ["salary", "salary_range", "compensation", "pay"],
            "posting_date": ["date", "posting_date", "posted_date", "datePosted"],
            "job_type": ["type", "job_type", "employment_type", "employmentType"],
            "experience_level": ["experience", "experience_level", "level"],
            "remote_option": ["remote", "remote_option", "work_from_home"],
        }

        # Extract and normalize each field
        for standard_field, possible_keys in field_mappings.items():
            value = self._extract_field_value(raw_job_data, possible_keys)
            if value:
                normalized[standard_field] = self._normalize_field_value(standard_field, value)

        # Add processing metadata
        normalized["scraped_date"] = datetime.now().isoformat()
        normalized["source_site"] = "indeed"  # Default, should be parameterized
        normalized["processing_version"] = "3.1"

        return normalized

    def validate_required_fields(self, job_data: Dict[str, Any]) -> bool:
        """
        Ensure minimum data quality standards.

        Args:
            job_data: Job data dictionary to validate

        Returns:
            True if job meets minimum requirements
        """
        required_fields = ["title", "company", "location"]

        for field in required_fields:
            if not job_data.get(field) or not str(job_data[field]).strip():
                logger.debug(f"Job missing required field: {field}")
                return False

        # Additional quality checks
        if len(str(job_data.get("title", ""))) < 3:
            logger.debug("Job title too short")
            return False

        if len(str(job_data.get("company", ""))) < 2:
            logger.debug("Company name too short")
            return False

        return True

    def _extract_job_from_container(self, container) -> Optional[Dict[str, Any]]:
        """Extract job data from a single HTML container."""
        job_data = {}

        # Extract title
        title_elem = container.find(["h2", "a"], attrs={"data-jk": True}) or container.find(
            ["span"], attrs={"class": re.compile(r"jobTitle|job-title")}
        )
        if title_elem:
            job_data["title"] = title_elem.get_text(strip=True)

        # Extract company
        company_elem = container.find(["span", "a"], attrs={"class": re.compile(r"companyName|company")})
        if company_elem:
            job_data["company"] = company_elem.get_text(strip=True)

        # Extract location
        location_elem = container.find(["div", "span"], attrs={"class": re.compile(r"companyLocation|location")})
        if location_elem:
            job_data["location"] = location_elem.get_text(strip=True)

        # Extract salary if present
        salary_elem = container.find(["span", "div"], attrs={"class": re.compile(r"salary|estimated-salary")})
        if salary_elem:
            job_data["salary_range"] = salary_elem.get_text(strip=True)

        # Extract job URL
        link_elem = container.find("a", href=True)
        if link_elem:
            job_data["job_url"] = link_elem["href"]

        # Extract summary/description if available
        summary_elem = container.find(["div"], attrs={"class": re.compile(r"summary|job-snippet")})
        if summary_elem:
            job_data["description"] = summary_elem.get_text(strip=True)

        return job_data if job_data else None

    def _extract_field_value(self, data: Dict[str, Any], possible_keys: List[str]) -> Any:
        """Extract value from data using possible key names."""
        for key in possible_keys:
            if key in data and data[key] is not None:
                return data[key]
        return None

    def _normalize_field_value(self, field_name: str, value: Any) -> Any:
        """Normalize a specific field value based on field type."""
        if value is None:
            return None

        str_value = str(value).strip()

        if field_name == "salary_range":
            return self._normalize_salary(str_value)
        elif field_name == "location":
            return self._normalize_location(str_value)
        elif field_name == "remote_option":
            return self._normalize_remote_option(str_value)
        elif field_name == "job_type":
            return self._normalize_job_type(str_value)
        elif field_name == "experience_level":
            return self._normalize_experience_level(str_value)
        else:
            return str_value

    def _normalize_salary(self, salary_text: str) -> Optional[str]:
        """Normalize salary range text."""
        if not salary_text:
            return None

        # Try to extract salary range
        for pattern in self.salary_patterns:
            match = re.search(pattern, salary_text, re.IGNORECASE)
            if match:
                min_sal = match.group(1).replace(",", "")
                max_sal = match.group(2).replace(",", "")

                # Handle K notation
                if "k" in salary_text.lower():
                    min_sal = str(int(float(min_sal)) * 1000)
                    max_sal = str(int(float(max_sal)) * 1000)

                return f"${min_sal} - ${max_sal}"

        return salary_text  # Return original if no pattern matches

    def _normalize_location(self, location_text: str) -> str:
        """Normalize location information."""
        if not location_text:
            return ""

        # Handle remote locations
        if re.search(r"\bremote\b", location_text, re.IGNORECASE):
            return "Remote"

        # Try to parse standard location formats
        for pattern in self.location_patterns:
            match = re.match(pattern, location_text, re.IGNORECASE)
            if match:
                if len(match.groups()) == 2:  # City, State
                    return f"{match.group(1).title()}, {match.group(2).upper()}"
                elif len(match.groups()) == 3:  # City, County, State
                    return f"{match.group(1).title()}, {match.group(3).upper()}"

        return location_text.title()

    def _normalize_remote_option(self, value: str) -> bool:
        """Normalize remote work option."""
        if not value:
            return False

        remote_keywords = ["remote", "work from home", "wfh", "telecommute", "virtual"]
        return any(keyword in value.lower() for keyword in remote_keywords)

    def _normalize_job_type(self, job_type: str) -> str:
        """Normalize job type."""
        if not job_type:
            return "Full-time"  # Default

        job_type_lower = job_type.lower()

        if "part" in job_type_lower:
            return "Part-time"
        elif "contract" in job_type_lower or "freelance" in job_type_lower:
            return "Contract"
        elif "intern" in job_type_lower:
            return "Internship"
        elif "temporary" in job_type_lower or "temp" in job_type_lower:
            return "Temporary"
        else:
            return "Full-time"

    def _normalize_experience_level(self, experience: str) -> str:
        """Normalize experience level requirements."""
        if not experience:
            return "Not specified"

        experience_lower = experience.lower()

        if any(word in experience_lower for word in ["entry", "junior", "0-2", "new grad"]):
            return "Entry level"
        elif any(word in experience_lower for word in ["senior", "lead", "7+", "8+", "10+"]):
            return "Senior level"
        elif any(word in experience_lower for word in ["mid", "intermediate", "3-7", "4-6"]):
            return "Mid level"
        else:
            return "Not specified"

    def _is_valid_job(self, job_data: Dict[str, Any]) -> bool:
        """Check if job data meets basic quality requirements."""
        return self.validate_required_fields(job_data)
