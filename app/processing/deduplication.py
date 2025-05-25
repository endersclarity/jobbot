"""
Duplicate Detection and Deduplication System for Phase 3B Processing Pipeline.

Identifies and merges duplicate job postings using multiple detection strategies:
- Exact URL matching
- Content hash matching (company + title + location)
- Fuzzy string matching for similar titles
"""

import hashlib
import json
from datetime import datetime
from typing import Dict, Any, List, Tuple, Set
from difflib import SequenceMatcher
import logging

logger = logging.getLogger(__name__)


class DuplicateDetector:
    """Detect and handle duplicate job postings in scraped data."""
    
    def __init__(self, similarity_threshold: float = 0.85):
        """
        Initialize the duplicate detector.
        
        Args:
            similarity_threshold: Minimum similarity score for fuzzy matching (0.0-1.0)
        """
        self.similarity_threshold = similarity_threshold
        self.processed_urls: Set[str] = set()
        self.processed_hashes: Set[str] = set()
        
    def generate_job_hash(self, job_data: Dict[str, Any]) -> str:
        """
        Create unique hash from company + title + location.
        
        Args:
            job_data: Job data dictionary
            
        Returns:
            SHA-256 hash string
        """
        # Extract and normalize key fields
        company = str(job_data.get('company', '')).strip().lower()
        title = str(job_data.get('title', '')).strip().lower()
        location = str(job_data.get('location', '')).strip().lower()
        
        # Remove common variations that shouldn't affect uniqueness
        title = self._normalize_title_for_hashing(title)
        location = self._normalize_location_for_hashing(location)
        
        # Create composite key
        composite_key = f"{company}|{title}|{location}"
        
        # Generate hash
        return hashlib.sha256(composite_key.encode('utf-8')).hexdigest()
    
    def detect_url_duplicates(self, job_list: List[Dict[str, Any]]) -> Dict[str, List[Dict[str, Any]]]:
        """
        Find exact URL matches (highest priority duplicates).
        
        Args:
            job_list: List of job dictionaries
            
        Returns:
            Dictionary mapping URLs to lists of duplicate jobs
        """
        url_groups = {}
        
        for job in job_list:
            url = job.get('job_url', '').strip()
            if not url:
                continue
                
            # Normalize URL for comparison
            normalized_url = self._normalize_url(url)
            
            if normalized_url not in url_groups:
                url_groups[normalized_url] = []
            url_groups[normalized_url].append(job)
        
        # Return only groups with duplicates
        duplicates = {url: jobs for url, jobs in url_groups.items() if len(jobs) > 1}
        
        if duplicates:
            logger.info(f"Found {len(duplicates)} URL duplicate groups")
        
        return duplicates
    
    def detect_content_duplicates(self, job_list: List[Dict[str, Any]]) -> Dict[str, List[Dict[str, Any]]]:
        """
        Find similar content with hash and fuzzy matching.
        
        Args:
            job_list: List of job dictionaries
            
        Returns:
            Dictionary mapping hashes to lists of duplicate jobs
        """
        hash_groups = {}
        fuzzy_groups = []
        
        # First pass: exact hash matching
        for job in job_list:
            job_hash = self.generate_job_hash(job)
            
            if job_hash not in hash_groups:
                hash_groups[job_hash] = []
            hash_groups[job_hash].append(job)
        
        # Second pass: fuzzy matching for remaining singles
        singles = []
        hash_duplicates = {}
        
        for job_hash, jobs in hash_groups.items():
            if len(jobs) > 1:
                hash_duplicates[job_hash] = jobs
            else:
                singles.extend(jobs)
        
        # Fuzzy match remaining singles
        fuzzy_duplicates = self._find_fuzzy_duplicates(singles)
        
        # Combine results
        all_duplicates = hash_duplicates.copy()
        for i, group in enumerate(fuzzy_duplicates):
            all_duplicates[f"fuzzy_group_{i}"] = group
        
        if all_duplicates:
            total_duplicate_jobs = sum(len(jobs) for jobs in all_duplicates.values())
            logger.info(f"Found {len(all_duplicates)} content duplicate groups with {total_duplicate_jobs} jobs")
        
        return all_duplicates
    
    def merge_duplicate_records(self, duplicate_group: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Combine information from duplicate jobs into single record.
        
        Args:
            duplicate_group: List of duplicate job dictionaries
            
        Returns:
            Merged job dictionary with best available data
        """
        if not duplicate_group:
            return {}
        
        if len(duplicate_group) == 1:
            return duplicate_group[0]
        
        # Start with the most recent job as base
        merged = self._select_best_base_job(duplicate_group)
        
        # Merge additional information from other jobs
        for job in duplicate_group:
            if job is merged:
                continue
                
            merged = self._merge_job_data(merged, job)
        
        # Add deduplication metadata
        merged['is_merged'] = True
        merged['merged_count'] = len(duplicate_group)
        merged['merged_sources'] = [job.get('job_url', 'unknown') for job in duplicate_group]
        merged['deduplication_date'] = datetime.now().isoformat()
        
        logger.debug(f"Merged {len(duplicate_group)} duplicate jobs for: {merged.get('title', 'Unknown')}")
        
        return merged
    
    def remove_duplicates_from_batch(self, job_list: List[Dict[str, Any]]) -> Tuple[List[Dict[str, Any]], Dict[str, Any]]:
        """
        Remove duplicates from a batch of jobs and return clean list with stats.
        
        Args:
            job_list: List of job dictionaries to deduplicate
            
        Returns:
            Tuple of (clean_job_list, deduplication_stats)
        """
        if not job_list:
            return [], {'total_input': 0, 'total_output': 0, 'duplicates_removed': 0}
        
        original_count = len(job_list)
        logger.info(f"Starting deduplication of {original_count} jobs")
        
        # Step 1: Remove URL duplicates
        url_duplicates = self.detect_url_duplicates(job_list)
        
        # Step 2: Remove content duplicates from remaining jobs
        remaining_jobs = []
        url_merged_jobs = []
        
        # Merge URL duplicates and collect remaining jobs
        processed_urls = set()
        for job in job_list:
            url = self._normalize_url(job.get('job_url', ''))
            
            if url in url_duplicates and url not in processed_urls:
                merged_job = self.merge_duplicate_records(url_duplicates[url])
                url_merged_jobs.append(merged_job)
                processed_urls.add(url)
            elif url not in url_duplicates:
                remaining_jobs.append(job)
        
        # Find content duplicates in remaining jobs
        content_duplicates = self.detect_content_duplicates(remaining_jobs)
        
        # Merge content duplicates
        content_merged_jobs = []
        processed_in_content = set()
        
        for group_id, duplicate_group in content_duplicates.items():
            merged_job = self.merge_duplicate_records(duplicate_group)
            content_merged_jobs.append(merged_job)
            
            # Track processed jobs
            for job in duplicate_group:
                job_id = id(job)  # Use object ID for tracking
                processed_in_content.add(job_id)
        
        # Collect remaining singles
        single_jobs = []
        for job in remaining_jobs:
            if id(job) not in processed_in_content:
                single_jobs.append(job)
        
        # Combine all results
        clean_jobs = url_merged_jobs + content_merged_jobs + single_jobs
        final_count = len(clean_jobs)
        
        # Generate statistics
        stats = {
            'total_input': original_count,
            'total_output': final_count,
            'duplicates_removed': original_count - final_count,
            'url_duplicate_groups': len(url_duplicates),
            'content_duplicate_groups': len(content_duplicates),
            'duplicate_rate': round((original_count - final_count) / original_count * 100, 2) if original_count > 0 else 0,
        }
        
        logger.info(f"Deduplication complete: {original_count} → {final_count} jobs ({stats['duplicate_rate']}% duplicates)")
        
        return clean_jobs, stats
    
    def _normalize_title_for_hashing(self, title: str) -> str:
        """Normalize job title for consistent hashing."""
        if not title:
            return ""
        
        title = title.lower().strip()
        
        # Remove common variations
        variations_to_remove = [
            r'\s*-\s*\d+\s*(?:month|year)s?\s*contract',
            r'\s*\(.*?\)',  # Remove parenthetical information
            r'\s*-\s*remote',
            r'\s*-\s*urgent',
            r'\s*-\s*immediate\s*start',
        ]
        
        import re
        for pattern in variations_to_remove:
            title = re.sub(pattern, '', title, flags=re.IGNORECASE)
        
        # Normalize whitespace
        title = re.sub(r'\s+', ' ', title).strip()
        
        return title
    
    def _normalize_location_for_hashing(self, location: str) -> str:
        """Normalize location for consistent hashing."""
        if not location:
            return ""
        
        location = location.lower().strip()
        
        # Handle remote variations
        if 'remote' in location:
            return "remote"
        
        # Remove ZIP codes and extra formatting
        import re
        location = re.sub(r'\s*\d{5}(?:-\d{4})?\s*', '', location)
        location = re.sub(r'\s+', ' ', location).strip()
        
        return location
    
    def _normalize_url(self, url: str) -> str:
        """Normalize URL for comparison."""
        if not url:
            return ""
        
        # Remove common URL variations that don't affect job identity
        import re
        
        # Remove tracking parameters
        url = re.sub(r'[?&](?:utm_|ref|source|campaign).*?(?=&|$)', '', url)
        
        # Remove fragment identifiers
        url = url.split('#')[0]
        
        # Normalize protocol
        url = url.replace('http://', 'https://')
        
        # Remove trailing slash
        url = url.rstrip('/')
        
        return url.lower()
    
    def _find_fuzzy_duplicates(self, job_list: List[Dict[str, Any]]) -> List[List[Dict[str, Any]]]:
        """Find fuzzy duplicate groups using string similarity."""
        if len(job_list) < 2:
            return []
        
        groups = []
        processed = set()
        
        for i, job1 in enumerate(job_list):
            if i in processed:
                continue
            
            group = [job1]
            processed.add(i)
            
            for j, job2 in enumerate(job_list[i+1:], i+1):
                if j in processed:
                    continue
                
                if self._are_jobs_similar(job1, job2):
                    group.append(job2)
                    processed.add(j)
            
            if len(group) > 1:
                groups.append(group)
        
        return groups
    
    def _are_jobs_similar(self, job1: Dict[str, Any], job2: Dict[str, Any]) -> bool:
        """Check if two jobs are similar enough to be duplicates."""
        # Company must match exactly
        company1 = str(job1.get('company', '')).strip().lower()
        company2 = str(job2.get('company', '')).strip().lower()
        
        if company1 != company2:
            return False
        
        # Title similarity check
        title1 = str(job1.get('title', '')).strip().lower()
        title2 = str(job2.get('title', '')).strip().lower()
        
        title_similarity = SequenceMatcher(None, title1, title2).ratio()
        
        if title_similarity < self.similarity_threshold:
            return False
        
        # Location similarity check (more lenient)
        location1 = str(job1.get('location', '')).strip().lower()
        location2 = str(job2.get('location', '')).strip().lower()
        
        location_similarity = SequenceMatcher(None, location1, location2).ratio()
        
        # Accept if locations are very similar or if one is remote
        if location_similarity > 0.7 or 'remote' in (location1 + location2):
            return True
        
        return False
    
    def _select_best_base_job(self, job_group: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Select the best job from a group to use as merge base."""
        if not job_group:
            return {}
        
        # Scoring criteria (higher is better)
        def score_job(job):
            score = 0
            
            # Prefer jobs with more complete data
            score += len([v for v in job.values() if v and str(v).strip()])
            
            # Prefer jobs with salary information
            if job.get('salary_range'):
                score += 10
            
            # Prefer jobs with descriptions
            if job.get('description') and len(str(job['description'])) > 50:
                score += 5
            
            # Prefer jobs with requirements
            if job.get('requirements'):
                score += 3
            
            # Prefer more recent postings
            if job.get('posting_date'):
                score += 2
            
            return score
        
        # Return highest scoring job
        return max(job_group, key=score_job)
    
    def _merge_job_data(self, base_job: Dict[str, Any], additional_job: Dict[str, Any]) -> Dict[str, Any]:
        """Merge additional job data into base job."""
        merged = base_job.copy()
        
        # Merge fields, preferring longer/more complete values
        mergeable_fields = [
            'description', 'requirements', 'benefits', 'salary_range',
            'job_type', 'experience_level', 'industry', 'keywords'
        ]
        
        for field in mergeable_fields:
            base_value = merged.get(field, '')
            additional_value = additional_job.get(field, '')
            
            # Use longer value if base is empty or additional is significantly longer
            if not base_value and additional_value:
                merged[field] = additional_value
            elif additional_value and len(str(additional_value)) > len(str(base_value)) * 1.5:
                merged[field] = additional_value
        
        return merged