"""
Database Import System for Phase 3B Processing Pipeline.

Handles bulk import of processed job data into the JobBot database
with conflict resolution and import statistics.
"""

import json
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from sqlalchemy import text
import logging

# Import application database components
from app.core.database import get_db
from app.models.jobs import Job

logger = logging.getLogger(__name__)


class DatabaseImporter:
    """Import processed job data into the JobBot database."""
    
    def __init__(self, db_session: Optional[Session] = None):
        """
        Initialize the database importer.
        
        Args:
            db_session: Optional database session, will create if not provided
        """
        self.db_session = db_session
        self.import_stats = {
            'jobs_imported': 0,
            'jobs_updated': 0,
            'jobs_skipped': 0,
            'conflicts_resolved': 0,
            'errors': []
        }
    
    def bulk_import_jobs(self, processed_job_file: str) -> Dict[str, Any]:
        """
        Import cleaned jobs to database efficiently.
        
        Args:
            processed_job_file: Path to processed job JSON file
            
        Returns:
            Import results and statistics
        """
        logger.info(f"Starting bulk import from {processed_job_file}")
        
        # Load processed jobs
        try:
            with open(processed_job_file, 'r') as f:
                data = json.load(f)
            
            jobs = data.get('jobs', [])
            if not jobs:
                return {
                    'status': 'no_data',
                    'message': 'No jobs found in processed file'
                }
        
        except (FileNotFoundError, json.JSONDecodeError) as e:
            logger.error(f"Failed to load processed file: {e}")
            return {
                'status': 'error',
                'message': f'Failed to load file: {e}'
            }
        
        # Get database session
        if not self.db_session:
            self.db_session = next(get_db())
        
        import_results = {
            'start_time': datetime.now().isoformat(),
            'source_file': processed_job_file,
            'total_jobs': len(jobs),
            'jobs_imported': 0,
            'jobs_updated': 0,
            'jobs_skipped': 0,
            'conflicts_resolved': 0,
            'errors': [],
            'import_batch_id': f"import_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        }
        
        try:
            # Process jobs in batches for better performance
            batch_size = 100
            for i in range(0, len(jobs), batch_size):
                batch = jobs[i:i + batch_size]
                batch_results = self._import_job_batch(batch, import_results['import_batch_id'])
                
                # Update overall statistics
                import_results['jobs_imported'] += batch_results['imported']
                import_results['jobs_updated'] += batch_results['updated']
                import_results['jobs_skipped'] += batch_results['skipped']
                import_results['conflicts_resolved'] += batch_results['conflicts']
                import_results['errors'].extend(batch_results['errors'])
                
                logger.info(f"Batch {i//batch_size + 1}: {batch_results['imported']} imported, {batch_results['updated']} updated")
            
            # Commit all changes
            self.db_session.commit()
            
            import_results['end_time'] = datetime.now().isoformat()
            import_results['status'] = 'success'
            import_results['success_rate'] = round(
                (import_results['jobs_imported'] + import_results['jobs_updated']) / import_results['total_jobs'] * 100, 2
            ) if import_results['total_jobs'] > 0 else 0
            
            logger.info(f"Import complete: {import_results['jobs_imported']} imported, {import_results['jobs_updated']} updated")
            
        except Exception as e:
            self.db_session.rollback()
            logger.error(f"Import failed: {e}")
            import_results['status'] = 'error'
            import_results['message'] = str(e)
        
        finally:
            if not self.db_session:
                self.db_session.close()
        
        return import_results
    
    def update_existing_jobs(self, job_updates: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Update job records with new information.
        
        Args:
            job_updates: List of job update dictionaries
            
        Returns:
            Update results and statistics
        """
        logger.info(f"Updating {len(job_updates)} existing jobs")
        
        if not self.db_session:
            self.db_session = next(get_db())
        
        update_results = {
            'total_updates': len(job_updates),
            'successful_updates': 0,
            'failed_updates': 0,
            'errors': []
        }
        
        try:
            for update_data in job_updates:
                try:
                    job_id = update_data.get('id')
                    if not job_id:
                        continue
                    
                    # Find existing job
                    existing_job = self.db_session.query(Job).filter(Job.id == job_id).first()
                    if not existing_job:
                        update_results['failed_updates'] += 1
                        continue
                    
                    # Update fields
                    updated_fields = self._update_job_fields(existing_job, update_data)
                    
                    if updated_fields:
                        existing_job.updated_at = datetime.now()
                        update_results['successful_updates'] += 1
                
                except Exception as e:
                    update_results['failed_updates'] += 1
                    update_results['errors'].append({
                        'job_id': update_data.get('id'),
                        'error': str(e)
                    })
            
            self.db_session.commit()
            
        except Exception as e:
            self.db_session.rollback()
            logger.error(f"Update operation failed: {e}")
            update_results['errors'].append({'general_error': str(e)})
        
        return update_results
    
    def handle_import_conflicts(self, conflict_list: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Resolve database constraint violations.
        
        Args:
            conflict_list: List of conflict details
            
        Returns:
            Conflict resolution results
        """
        resolution_strategies = {
            'duplicate_url': self._resolve_duplicate_url,
            'missing_required_field': self._resolve_missing_field,
            'invalid_data_format': self._resolve_invalid_format,
        }
        
        resolution_results = {
            'total_conflicts': len(conflict_list),
            'resolved': 0,
            'unresolved': 0,
            'resolution_details': []
        }
        
        for conflict in conflict_list:
            conflict_type = conflict.get('type', 'unknown')
            resolver = resolution_strategies.get(conflict_type)
            
            if resolver:
                try:
                    resolution = resolver(conflict)
                    if resolution['resolved']:
                        resolution_results['resolved'] += 1
                    else:
                        resolution_results['unresolved'] += 1
                    
                    resolution_results['resolution_details'].append(resolution)
                
                except Exception as e:
                    resolution_results['unresolved'] += 1
                    resolution_results['resolution_details'].append({
                        'conflict': conflict,
                        'resolved': False,
                        'error': str(e)
                    })
            else:
                resolution_results['unresolved'] += 1
        
        return resolution_results
    
    def generate_import_statistics(self, import_results: Dict[str, Any]) -> Dict[str, Any]:
        """
        Report import success/failure metrics.
        
        Args:
            import_results: Results from import operation
            
        Returns:
            Formatted import statistics
        """
        stats = {
            'import_summary': {
                'batch_id': import_results.get('import_batch_id', 'unknown'),
                'import_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'source_file': import_results.get('source_file', 'unknown'),
                'status': import_results.get('status', 'unknown')
            },
            'job_statistics': {
                'total_jobs': import_results.get('total_jobs', 0),
                'jobs_imported': import_results.get('jobs_imported', 0),
                'jobs_updated': import_results.get('jobs_updated', 0),
                'jobs_skipped': import_results.get('jobs_skipped', 0),
                'success_rate': import_results.get('success_rate', 0)
            },
            'conflict_resolution': {
                'conflicts_resolved': import_results.get('conflicts_resolved', 0),
                'total_errors': len(import_results.get('errors', []))
            },
            'performance_metrics': {
                'processing_time': self._calculate_import_time(import_results),
                'jobs_per_minute': self._calculate_import_rate(import_results)
            }
        }
        
        return stats
    
    def _import_job_batch(self, job_batch: List[Dict[str, Any]], batch_id: str) -> Dict[str, Any]:
        """Import a batch of jobs with conflict handling."""
        batch_results = {
            'imported': 0,
            'updated': 0,
            'skipped': 0,
            'conflicts': 0,
            'errors': []
        }
        
        for job_data in job_batch:
            try:
                result = self._import_single_job(job_data, batch_id)
                
                if result['action'] == 'imported':
                    batch_results['imported'] += 1
                elif result['action'] == 'updated':
                    batch_results['updated'] += 1
                elif result['action'] == 'skipped':
                    batch_results['skipped'] += 1
                
                if result.get('conflict_resolved'):
                    batch_results['conflicts'] += 1
            
            except Exception as e:
                batch_results['errors'].append({
                    'job_title': job_data.get('title', 'Unknown'),
                    'error': str(e)
                })
                batch_results['skipped'] += 1
        
        return batch_results
    
    def _import_single_job(self, job_data: Dict[str, Any], batch_id: str) -> Dict[str, Any]:
        """Import a single job with duplicate checking."""
        # Check for existing job by URL
        existing_job = None
        job_url = job_data.get('job_url')
        
        if job_url:
            existing_job = self.db_session.query(Job).filter(Job.job_url == job_url).first()
        
        if existing_job:
            # Update existing job if new data is more complete
            if self._should_update_job(existing_job, job_data):
                self._update_job_fields(existing_job, job_data)
                existing_job.updated_at = datetime.now()
                return {'action': 'updated', 'job_id': existing_job.id}
            else:
                return {'action': 'skipped', 'reason': 'existing_more_complete'}
        
        # Create new job
        try:
            new_job = self._create_job_from_data(job_data, batch_id)
            self.db_session.add(new_job)
            self.db_session.flush()  # Get ID without committing
            
            return {'action': 'imported', 'job_id': new_job.id}
        
        except IntegrityError as e:
            self.db_session.rollback()
            
            # Handle constraint violations
            if 'UNIQUE constraint failed' in str(e) or 'duplicate key' in str(e):
                return {'action': 'skipped', 'reason': 'duplicate_constraint', 'conflict_resolved': True}
            else:
                raise e
    
    def _create_job_from_data(self, job_data: Dict[str, Any], batch_id: str) -> Job:
        """Create a Job model instance from processed data."""
        # Map processed data to Job model fields
        job_fields = {
            'title': job_data.get('title', ''),
            'company': job_data.get('company', ''),
            'location': job_data.get('location', ''),
            'description': job_data.get('description', ''),
            'requirements': job_data.get('requirements', ''),
            'benefits': job_data.get('benefits', ''),
            'salary_range': self._format_salary_range(job_data),
            'job_url': job_data.get('job_url', ''),
            'source_site': job_data.get('source_site', 'indeed'),
            'remote_option': job_data.get('is_remote', False),
            'job_type': job_data.get('job_type', 'Full-time'),
            'experience_level': job_data.get('experience_level', 'Not specified'),
            'industry': job_data.get('industry', 'Not specified'),
            'posting_date': self._parse_posting_date(job_data.get('posting_date')),
            'scraped_date': datetime.now(),
            'status': 'active',
            'import_batch_id': batch_id
        }
        
        # Remove None values
        job_fields = {k: v for k, v in job_fields.items() if v is not None}
        
        return Job(**job_fields)
    
    def _should_update_job(self, existing_job: Job, new_data: Dict[str, Any]) -> bool:
        """Determine if existing job should be updated with new data."""
        # Count non-empty fields in new data
        new_data_completeness = sum(1 for v in new_data.values() if v and str(v).strip())
        
        # Count non-empty fields in existing job
        existing_data_completeness = sum(1 for field in existing_job.__dict__.values() 
                                       if field and str(field).strip() and field != 'id')
        
        # Update if new data is significantly more complete
        return new_data_completeness > existing_data_completeness * 1.2
    
    def _update_job_fields(self, job: Job, update_data: Dict[str, Any]) -> List[str]:
        """Update job fields with new data and return list of updated fields."""
        updated_fields = []
        
        # Field mapping for updates
        updateable_fields = {
            'description': 'description',
            'requirements': 'requirements', 
            'benefits': 'benefits',
            'salary_range': 'salary_range',
            'job_type': 'job_type',
            'experience_level': 'experience_level',
            'industry': 'industry',
            'remote_option': 'is_remote'
        }
        
        for db_field, data_field in updateable_fields.items():
            if data_field in update_data and update_data[data_field]:
                new_value = update_data[data_field]
                
                if db_field == 'salary_range':
                    new_value = self._format_salary_range(update_data)
                
                if getattr(job, db_field) != new_value:
                    setattr(job, db_field, new_value)
                    updated_fields.append(db_field)
        
        return updated_fields
    
    def _format_salary_range(self, job_data: Dict[str, Any]) -> Optional[str]:
        """Format salary range from normalized data."""
        min_sal = job_data.get('min_salary')
        max_sal = job_data.get('max_salary')
        
        if min_sal and max_sal:
            return f"${min_sal:,} - ${max_sal:,}"
        elif min_sal:
            return f"${min_sal:,}+"
        elif max_sal:
            return f"Up to ${max_sal:,}"
        else:
            return job_data.get('salary_range')
    
    def _parse_posting_date(self, date_str: Optional[str]) -> Optional[datetime]:
        """Parse posting date string to datetime."""
        if not date_str:
            return None
        
        try:
            if 'T' in date_str:  # ISO format
                return datetime.fromisoformat(date_str.replace('Z', '+00:00'))
            else:  # Date only
                return datetime.strptime(date_str, '%Y-%m-%d')
        except (ValueError, TypeError):
            return None
    
    def _resolve_duplicate_url(self, conflict: Dict[str, Any]) -> Dict[str, Any]:
        """Resolve duplicate URL conflicts."""
        # For now, skip duplicates - could implement merge logic
        return {
            'conflict': conflict,
            'resolved': True,
            'action': 'skipped_duplicate',
            'message': 'Duplicate URL detected and skipped'
        }
    
    def _resolve_missing_field(self, conflict: Dict[str, Any]) -> Dict[str, Any]:
        """Resolve missing required field conflicts."""
        return {
            'conflict': conflict,
            'resolved': False,
            'action': 'manual_review_required',
            'message': 'Missing required field needs manual attention'
        }
    
    def _resolve_invalid_format(self, conflict: Dict[str, Any]) -> Dict[str, Any]:
        """Resolve invalid data format conflicts."""
        return {
            'conflict': conflict,
            'resolved': False,
            'action': 'data_cleaning_required', 
            'message': 'Invalid format requires data cleaning'
        }
    
    def _calculate_import_time(self, import_results: Dict[str, Any]) -> float:
        """Calculate total import time in seconds."""
        start_time = import_results.get('start_time')
        end_time = import_results.get('end_time')
        
        if start_time and end_time:
            start = datetime.fromisoformat(start_time)
            end = datetime.fromisoformat(end_time)
            return (end - start).total_seconds()
        
        return 0.0
    
    def _calculate_import_rate(self, import_results: Dict[str, Any]) -> float:
        """Calculate import rate in jobs per minute."""
        import_time = self._calculate_import_time(import_results)
        total_jobs = import_results.get('total_jobs', 0)
        
        if import_time > 0:
            return round(total_jobs / (import_time / 60), 2)
        
        return 0.0