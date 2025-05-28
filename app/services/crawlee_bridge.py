"""
🔥 Crawlee Bridge Service - Python ↔ Node.js Integration

This service bridges our enterprise-grade Crawlee scraper (Node.js) 
with the FastAPI backend (Python) for seamless job scraping integration.

What Apify charges $500+/month for, we do for FREE! 💀
"""

import json
import subprocess
import asyncio
from pathlib import Path
from typing import Dict, List, Optional, Any
from datetime import datetime
import logging

from ..models.jobs import Job
from ..core.database import get_db
from sqlalchemy.orm import Session

logger = logging.getLogger(__name__)


class CrawleeIntegrationError(Exception):
    """Custom exception for Crawlee integration errors"""
    pass


class CrawleeBridge:
    """
    Bridge service for integrating Crawlee Node.js scraper with Python FastAPI backend
    
    Handles:
    - Subprocess management for Node.js scraper
    - JSON data parsing and validation
    - Database integration for scraped jobs
    - Error handling and logging
    """
    
    def __init__(self):
        self.project_root = Path(__file__).parent.parent.parent
        self.scraper_script = self.project_root / "src" / "crawlee-scraper.js"
        self.orchestrator_script = self.project_root / "src" / "multi_site_orchestrator.js"
        self.node_timeout = 600  # 10 minutes timeout for multi-site scraping
        
    async def scrape_jobs(
        self,
        search_term: str,
        location: str = "San Francisco, CA",
        max_jobs: int = 50,
        job_site: str = "indeed"
    ) -> Dict[str, Any]:
        """
        Execute Crawlee scraper and return structured results
        
        Args:
            search_term: Job search keywords (e.g., "software engineer")
            location: Geographic location for job search
            max_jobs: Maximum number of jobs to scrape
            job_site: Target job site (currently "indeed")
            
        Returns:
            Dict containing scraping results and metadata
            
        Raises:
            CrawleeIntegrationError: If scraping fails or returns invalid data
        """
        try:
            logger.info(f"🔥 Starting Crawlee scraping: {search_term} in {location}")
            
            # Build command for Node.js scraper
            cmd = [
                "node", 
                str(self.scraper_script),
                "--search", search_term,
                "--location", location,
                "--max", str(max_jobs),
                "--site", job_site,
                "--json"
            ]
            
            logger.debug(f"Executing command: {' '.join(cmd)}")
            
            # Execute scraper with timeout
            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                cwd=self.project_root
            )
            
            try:
                stdout, stderr = await asyncio.wait_for(
                    process.communicate(), 
                    timeout=self.node_timeout
                )
            except asyncio.TimeoutError:
                process.kill()
                raise CrawleeIntegrationError(f"Scraping timeout after {self.node_timeout} seconds")
            
            # Check process exit code
            if process.returncode != 0:
                error_msg = stderr.decode('utf-8') if stderr else "Unknown error"
                logger.error(f"Crawlee scraper failed: {error_msg}")
                raise CrawleeIntegrationError(f"Scraper process failed: {error_msg}")
            
            # Parse JSON output (extract JSON from mixed output)
            try:
                stdout_text = stdout.decode('utf-8')
                
                # Method 1: Find the JSON object by looking for complete JSON block
                import re
                json_pattern = r'\{(?:[^{}]|{(?:[^{}]|{[^{}]*})*})*\}'
                json_matches = re.findall(json_pattern, stdout_text, re.DOTALL)
                
                # Look for the largest JSON object (likely our result)
                json_text = None
                for match in reversed(json_matches):  # Start from the end
                    try:
                        test_parse = json.loads(match)
                        if 'success' in test_parse:  # This looks like our result
                            json_text = match
                            break
                    except:
                        continue
                
                if not json_text:
                    # Fallback: use the last complete JSON found
                    if json_matches:
                        json_text = json_matches[-1]
                    else:
                        raise json.JSONDecodeError("No valid JSON found in output", stdout_text, 0)
                
                result_data = json.loads(json_text)
                
            except json.JSONDecodeError as e:
                logger.error(f"Invalid JSON from scraper: {stdout.decode('utf-8')[:500]}")
                logger.error(f"JSON extraction failed: {e}")
                raise CrawleeIntegrationError(f"Invalid JSON response from scraper: {e}")
            
            # Validate result structure
            if not result_data.get('success'):
                error_msg = result_data.get('error', 'Unknown scraping error')
                raise CrawleeIntegrationError(f"Scraping failed: {error_msg}")
            
            logger.info(f"✅ Crawlee scraping completed: {result_data['jobsScraped']} jobs")
            return result_data
            
        except Exception as e:
            if isinstance(e, CrawleeIntegrationError):
                raise
            logger.error(f"Unexpected error in Crawlee bridge: {e}")
            raise CrawleeIntegrationError(f"Bridge service error: {str(e)}")
    
    async def save_jobs_to_database(
        self, 
        scrape_result: Dict[str, Any], 
        db: Session
    ) -> Dict[str, Any]:
        """
        Save scraped jobs to database with duplicate detection
        
        Args:
            scrape_result: Result from scrape_jobs()
            db: Database session
            
        Returns:
            Dict with save statistics and job IDs
        """
        try:
            jobs_data = scrape_result.get('jobs', [])
            if not jobs_data:
                return {
                    'saved_count': 0,
                    'duplicate_count': 0,
                    'error_count': 0,
                    'job_ids': []
                }
            
            saved_count = 0
            duplicate_count = 0
            error_count = 0
            job_ids = []
            
            for job_data in jobs_data:
                try:
                    # Check for existing job by URL
                    existing_job = db.query(Job).filter(
                        Job.job_url == job_data.get('url')
                    ).first()
                    
                    if existing_job:
                        duplicate_count += 1
                        continue
                    
                    # Create job record (simplified to match existing Job model)
                    job = Job(
                        title=job_data.get('title', ''),
                        company=job_data.get('company', ''),
                        location=job_data.get('location', ''),
                        description=job_data.get('summary', ''),
                        job_url=job_data.get('url'),
                        source_site=job_data.get('source', 'crawlee'),
                        scraped_date=datetime.fromisoformat(
                            job_data.get('scrapedAt', datetime.now().isoformat()).replace('Z', '+00:00')
                        )
                    )
                    
                    db.add(job)
                    db.flush()  # Get job ID
                    job_ids.append(job.id)
                    saved_count += 1
                    
                except Exception as e:
                    logger.error(f"Error saving job {job_data.get('title', 'Unknown')}: {e}")
                    error_count += 1
            
            # Commit all changes
            db.commit()
            
            logger.info(f"💾 Database save complete: {saved_count} saved, {duplicate_count} duplicates, {error_count} errors")
            
            return {
                'saved_count': saved_count,
                'duplicate_count': duplicate_count,
                'error_count': error_count,
                'job_ids': job_ids
            }
            
        except Exception as e:
            db.rollback()
            logger.error(f"Database save failed: {e}")
            raise CrawleeIntegrationError(f"Failed to save jobs to database: {str(e)}")
    
    async def scrape_multi_site(
        self,
        search_term: str,
        location: str = "San Francisco, CA",
        sites: List[str] = None,
        max_jobs_per_site: int = 50,
        max_concurrency: int = 3
    ) -> Dict[str, Any]:
        """
        Execute multi-site scraping using the orchestrator
        
        Args:
            search_term: Job search keywords
            location: Geographic location
            sites: List of sites to scrape (defaults to ['indeed', 'linkedin', 'glassdoor'])
            max_jobs_per_site: Maximum jobs per site
            max_concurrency: Maximum concurrent scrapers
            
        Returns:
            Combined results from all sites
        """
        if sites is None:
            sites = ['indeed', 'linkedin', 'glassdoor']
            
        try:
            logger.info(f"🎼 Starting multi-site scraping: {search_term} across {len(sites)} sites")
            
            # Build command for multi-site orchestrator
            cmd = [
                "node", 
                str(self.orchestrator_script),
                f"--search={search_term}",
                f"--location={location}",
                f"--sites={','.join(sites)}",
                f"--max={max_jobs_per_site}",
                f"--concurrency={max_concurrency}",
                "--json"
            ]
            
            logger.debug(f"Executing orchestrator command: {' '.join(cmd)}")
            
            # Execute orchestrator with extended timeout
            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                cwd=self.project_root
            )
            
            try:
                stdout, stderr = await asyncio.wait_for(
                    process.communicate(), 
                    timeout=self.node_timeout
                )
            except asyncio.TimeoutError:
                process.kill()
                raise CrawleeIntegrationError(f"Multi-site scraping timeout after {self.node_timeout} seconds")
            
            # Check process exit code
            if process.returncode != 0:
                error_msg = stderr.decode('utf-8') if stderr else "Unknown error"
                logger.error(f"Multi-site orchestrator failed: {error_msg}")
                raise CrawleeIntegrationError(f"Orchestrator process failed: {error_msg}")
            
            # Parse JSON output
            try:
                stdout_text = stdout.decode('utf-8')
                
                # Find the JSON portion (starts with { and ends with })
                json_start = stdout_text.rfind('{')
                json_end = stdout_text.rfind('}') + 1
                
                if json_start == -1 or json_end == 0:
                    raise json.JSONDecodeError("No JSON found in output", stdout_text, 0)
                
                json_text = stdout_text[json_start:json_end]
                result_data = json.loads(json_text)
                
            except json.JSONDecodeError as e:
                logger.error(f"Invalid JSON from orchestrator: {stdout.decode('utf-8')[:500]}")
                raise CrawleeIntegrationError(f"Invalid JSON response from orchestrator: {e}")
            
            # Validate result structure
            if not result_data.get('success'):
                error_msg = result_data.get('error', 'Unknown orchestration error')
                raise CrawleeIntegrationError(f"Multi-site scraping failed: {error_msg}")
            
            logger.info(f"✅ Multi-site scraping completed: {result_data['totalJobs']} jobs from {result_data['sitesSuccessful']} sites")
            return result_data
            
        except Exception as e:
            if isinstance(e, CrawleeIntegrationError):
                raise
            logger.error(f"Unexpected error in multi-site bridge: {e}")
            raise CrawleeIntegrationError(f"Multi-site bridge error: {str(e)}")

    async def scrape_and_save(
        self,
        search_term: str,
        location: str = "San Francisco, CA",
        max_jobs: int = 50,
        job_site: str = "indeed",
        db: Optional[Session] = None
    ) -> Dict[str, Any]:
        """
        Complete workflow: scrape jobs and save to database
        
        Args:
            search_term: Job search keywords
            location: Geographic location
            max_jobs: Maximum jobs to scrape
            job_site: Target job site
            db: Database session (optional, will create if not provided)
            
        Returns:
            Combined results from scraping and database operations
        """
        # Get database session if not provided
        if db is None:
            db = next(get_db())
        
        try:
            # Execute scraping
            scrape_result = await self.scrape_jobs(
                search_term=search_term,
                location=location,
                max_jobs=max_jobs,
                job_site=job_site
            )
            
            # Save to database
            save_result = await self.save_jobs_to_database(scrape_result, db)
            
            # Combine results
            return {
                'success': True,
                'scraping': {
                    'search_term': search_term,
                    'location': location,
                    'max_jobs': max_jobs,
                    'jobs_scraped': scrape_result['jobsScraped'],
                    'scraped_at': scrape_result['scrapedAt']
                },
                'database': save_result,
                'summary': {
                    'jobs_found': scrape_result['jobsScraped'],
                    'jobs_saved': save_result['saved_count'],
                    'duplicates_skipped': save_result['duplicate_count'],
                    'save_errors': save_result['error_count']
                }
            }
            
        except Exception as e:
            logger.error(f"Complete scrape and save workflow failed: {e}")
            return {
                'success': False,
                'error': str(e),
                'scraping': None,
                'database': None,
                'summary': {
                    'jobs_found': 0,
                    'jobs_saved': 0,
                    'duplicates_skipped': 0,
                    'save_errors': 1
                }
            }

    async def scrape_multi_site_and_save(
        self,
        search_term: str,
        location: str = "San Francisco, CA",
        sites: List[str] = None,
        max_jobs_per_site: int = 50,
        max_concurrency: int = 3,
        db: Optional[Session] = None
    ) -> Dict[str, Any]:
        """
        Complete multi-site workflow: scrape jobs from multiple sites and save to database
        
        Args:
            search_term: Job search keywords
            location: Geographic location
            sites: List of sites to scrape
            max_jobs_per_site: Maximum jobs per site
            max_concurrency: Maximum concurrent scrapers
            db: Database session (optional)
            
        Returns:
            Combined results from multi-site scraping and database operations
        """
        # Get database session if not provided
        if db is None:
            db = next(get_db())
        
        try:
            # Execute multi-site scraping
            scrape_result = await self.scrape_multi_site(
                search_term=search_term,
                location=location,
                sites=sites,
                max_jobs_per_site=max_jobs_per_site,
                max_concurrency=max_concurrency
            )
            
            # Save all jobs to database
            save_result = await self.save_jobs_to_database(scrape_result, db)
            
            # Combine results with multi-site statistics
            return {
                'success': True,
                'scraping': {
                    'search_term': search_term,
                    'location': location,
                    'sites_queried': scrape_result['sitesQueried'],
                    'sites_successful': scrape_result['sitesSuccessful'],
                    'total_jobs': scrape_result['totalJobs'],
                    'duration': scrape_result['duration'],
                    'scraped_at': scrape_result['scrapedAt'],
                    'site_stats': scrape_result['siteStats']
                },
                'database': save_result,
                'summary': {
                    'jobs_found': scrape_result['totalJobs'],
                    'jobs_saved': save_result['saved_count'],
                    'duplicates_skipped': save_result['duplicate_count'],
                    'save_errors': save_result['error_count']
                },
                'orchestrator_stats': scrape_result.get('orchestratorStats', {})
            }
            
        except Exception as e:
            logger.error(f"Complete multi-site scrape and save workflow failed: {e}")
            return {
                'success': False,
                'error': str(e),
                'scraping': None,
                'database': None,
                'summary': {
                    'jobs_found': 0,
                    'jobs_saved': 0,
                    'duplicates_skipped': 0,
                    'save_errors': 1
                }
            }


# Global bridge instance
crawlee_bridge = CrawleeBridge()