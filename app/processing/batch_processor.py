"""
Batch Processing System for Phase 3B Offline Data Pipeline.

Orchestrates the complete processing workflow from raw scraped data
to clean, normalized, database-ready job records.
"""

import os
import json
import glob
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple
import logging

from .html_parser import JobDataExtractor
from .deduplication import DuplicateDetector
from .normalizer import DataNormalizer

logger = logging.getLogger(__name__)


class BatchProcessor:
    """Orchestrate batch processing of scraped job data."""

    def __init__(self, base_data_dir: str = "scraped_data"):
        """
        Initialize the batch processor.

        Args:
            base_data_dir: Base directory containing scraped data structure
        """
        self.base_data_dir = Path(base_data_dir)
        self.raw_dir = self.base_data_dir / "raw"
        self.processed_dir = self.base_data_dir / "processed"
        self.imported_dir = self.base_data_dir / "imported"
        self.errors_dir = self.base_data_dir / "errors"

        # Initialize processing components
        self.extractor = JobDataExtractor()
        self.deduplicator = DuplicateDetector()
        self.normalizer = DataNormalizer()

        # Ensure directories exist
        self._ensure_directories()

    def process_daily_batch(self, date_str: str) -> Dict[str, Any]:
        """
        Process all files for a specific date.

        Args:
            date_str: Date string in YYYY-MM-DD format

        Returns:
            Processing results and statistics
        """
        logger.info(f"Starting daily batch processing for {date_str}")

        # Find all raw files for the date
        date_pattern = date_str.replace("-", "")  # Convert to YYYYMMDD
        raw_files = self._find_raw_files_for_date(date_pattern)

        if not raw_files:
            logger.warning(f"No raw files found for date {date_str}")
            return {"date": date_str, "status": "no_files", "files_processed": 0, "jobs_processed": 0, "errors": []}

        return self.process_file_queue(raw_files, batch_name=f"daily_{date_str}")

    def process_file_queue(self, file_list: List[str], batch_name: str = None) -> Dict[str, Any]:
        """
        Process multiple files in sequence.

        Args:
            file_list: List of file paths to process
            batch_name: Optional name for the batch

        Returns:
            Comprehensive processing results
        """
        if not batch_name:
            batch_name = f"batch_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

        logger.info(f"Processing {len(file_list)} files in batch: {batch_name}")

        batch_results = {
            "batch_name": batch_name,
            "start_time": datetime.now().isoformat(),
            "files_processed": 0,
            "files_failed": 0,
            "total_jobs_input": 0,
            "total_jobs_output": 0,
            "deduplication_stats": {},
            "normalization_stats": {},
            "errors": [],
            "processed_files": [],
        }

        all_jobs = []

        # Process each file
        for file_path in file_list:
            try:
                file_results = self._process_single_file(file_path)

                if file_results["status"] == "success":
                    all_jobs.extend(file_results["jobs"])
                    batch_results["files_processed"] += 1
                    batch_results["total_jobs_input"] += len(file_results["jobs"])
                    batch_results["processed_files"].append(
                        {
                            "file": file_path,
                            "jobs_extracted": len(file_results["jobs"]),
                            "processing_time": file_results.get("processing_time", 0),
                        }
                    )
                else:
                    batch_results["files_failed"] += 1
                    batch_results["errors"].extend(file_results.get("errors", []))

            except Exception as e:
                batch_results["files_failed"] += 1
                batch_results["errors"].append({"file": file_path, "error": str(e), "type": "file_processing_error"})
                logger.error(f"Failed to process file {file_path}: {e}")

        # Deduplicate across all jobs in batch
        if all_jobs:
            clean_jobs, dedup_stats = self.deduplicator.remove_duplicates_from_batch(all_jobs)
            batch_results["deduplication_stats"] = dedup_stats
            batch_results["total_jobs_output"] = len(clean_jobs)

            # Normalize all clean jobs
            normalized_jobs = []
            normalization_errors = 0

            for job in clean_jobs:
                try:
                    normalized_job = self.normalizer.normalize_all_fields(job)
                    normalized_jobs.append(normalized_job)
                except Exception as e:
                    normalization_errors += 1
                    logger.warning(f"Normalization failed for job: {e}")

            batch_results["normalization_stats"] = {
                "jobs_normalized": len(normalized_jobs),
                "normalization_errors": normalization_errors,
                "normalization_success_rate": round(len(normalized_jobs) / len(clean_jobs) * 100, 2)
                if clean_jobs
                else 0,
            }

            # Save processed batch
            output_file = self._save_processed_batch(normalized_jobs, batch_name)
            batch_results["output_file"] = str(output_file)

        batch_results["end_time"] = datetime.now().isoformat()
        batch_results["total_processing_time"] = self._calculate_processing_time(
            batch_results["start_time"], batch_results["end_time"]
        )

        # Generate and save processing report
        report_file = self._save_processing_report(batch_results)
        batch_results["report_file"] = str(report_file)

        logger.info(
            f"Batch processing complete: {batch_results['total_jobs_input']} → "
            f"{batch_results['total_jobs_output']} jobs"
        )

        return batch_results

    def process_all_pending(self) -> Dict[str, Any]:
        """
        Process all unprocessed files in the raw directory.

        Returns:
            Processing results for all pending files
        """
        logger.info("Processing all pending raw files")

        # Find all raw files
        all_raw_files = list(self.raw_dir.glob("*.json"))

        if not all_raw_files:
            return {"status": "no_files", "message": "No raw files found to process"}

        # Filter out already processed files
        pending_files = self._filter_unprocessed_files(all_raw_files)

        if not pending_files:
            return {"status": "all_processed", "message": "All raw files have already been processed"}

        return self.process_file_queue(
            [str(f) for f in pending_files], batch_name=f"pending_all_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        )

    def generate_processing_report(self, batch_results: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create summary of processing results.

        Args:
            batch_results: Results from batch processing

        Returns:
            Formatted processing report
        """
        report = {
            "summary": {
                "batch_name": batch_results.get("batch_name", "Unknown"),
                "processing_date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "total_files": batch_results.get("files_processed", 0) + batch_results.get("files_failed", 0),
                "successful_files": batch_results.get("files_processed", 0),
                "failed_files": batch_results.get("files_failed", 0),
                "success_rate": self._calculate_success_rate(batch_results),
            },
            "job_statistics": {
                "jobs_input": batch_results.get("total_jobs_input", 0),
                "jobs_output": batch_results.get("total_jobs_output", 0),
                "duplicates_removed": batch_results.get("total_jobs_input", 0)
                - batch_results.get("total_jobs_output", 0),
                "duplicate_rate": batch_results.get("deduplication_stats", {}).get("duplicate_rate", 0),
            },
            "processing_performance": {
                "total_time": batch_results.get("total_processing_time", 0),
                "jobs_per_minute": self._calculate_jobs_per_minute(batch_results),
                "average_file_size": self._calculate_average_file_jobs(batch_results),
            },
            "quality_metrics": batch_results.get("normalization_stats", {}),
            "errors": batch_results.get("errors", []),
            "deduplication_details": batch_results.get("deduplication_stats", {}),
        }

        return report

    def handle_processing_errors(self, error_list: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Log and categorize processing failures.

        Args:
            error_list: List of error dictionaries

        Returns:
            Error analysis and recommendations
        """
        if not error_list:
            return {"status": "no_errors"}

        # Categorize errors
        error_categories = {
            "file_parsing_errors": [],
            "data_extraction_errors": [],
            "normalization_errors": [],
            "validation_errors": [],
            "unknown_errors": [],
        }

        for error in error_list:
            error_type = error.get("type", "unknown")

            if "parsing" in error_type:
                error_categories["file_parsing_errors"].append(error)
            elif "extraction" in error_type:
                error_categories["data_extraction_errors"].append(error)
            elif "normalization" in error_type:
                error_categories["normalization_errors"].append(error)
            elif "validation" in error_type:
                error_categories["validation_errors"].append(error)
            else:
                error_categories["unknown_errors"].append(error)

        # Generate recommendations
        recommendations = self._generate_error_recommendations(error_categories)

        # Save error analysis
        error_analysis = {
            "analysis_date": datetime.now().isoformat(),
            "total_errors": len(error_list),
            "error_categories": {k: len(v) for k, v in error_categories.items()},
            "detailed_errors": error_categories,
            "recommendations": recommendations,
        }

        error_file = self.errors_dir / f"error_analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"

        with open(error_file, "w") as f:
            json.dump(error_analysis, f, indent=2)

        logger.info(f"Error analysis saved to {error_file}")

        return error_analysis

    def _ensure_directories(self):
        """Create necessary directories if they don't exist."""
        for directory in [self.raw_dir, self.processed_dir, self.imported_dir, self.errors_dir]:
            directory.mkdir(parents=True, exist_ok=True)

    def _find_raw_files_for_date(self, date_pattern: str) -> List[str]:
        """Find all raw files matching a date pattern."""
        pattern = f"*{date_pattern}*.json"
        files = list(self.raw_dir.glob(pattern))
        return [str(f) for f in files]

    def _process_single_file(self, file_path: str) -> Dict[str, Any]:
        """Process a single raw data file."""
        start_time = datetime.now()

        try:
            with open(file_path, "r", encoding="utf-8") as f:
                raw_content = f.read()

            # Determine if file contains HTML or JSON
            if file_path.endswith(".html") or "<html" in raw_content.lower():
                jobs = self.extractor.extract_from_indeed_html(raw_content)
            else:
                jobs = self.extractor.extract_from_json_dump(raw_content)

            processing_time = (datetime.now() - start_time).total_seconds()

            return {"status": "success", "file": file_path, "jobs": jobs, "processing_time": processing_time}

        except Exception as e:
            return {
                "status": "error",
                "file": file_path,
                "errors": [{"type": "file_processing_error", "message": str(e), "file": file_path}],
            }

    def _save_processed_batch(self, jobs: List[Dict[str, Any]], batch_name: str) -> Path:
        """Save processed jobs to output file."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_file = self.processed_dir / f"{batch_name}_{timestamp}.json"

        output_data = {
            "batch_name": batch_name,
            "processing_date": datetime.now().isoformat(),
            "total_jobs": len(jobs),
            "jobs": jobs,
        }

        with open(output_file, "w") as f:
            json.dump(output_data, f, indent=2)

        logger.info(f"Saved {len(jobs)} processed jobs to {output_file}")
        return output_file

    def _save_processing_report(self, batch_results: Dict[str, Any]) -> Path:
        """Save processing report to file."""
        report = self.generate_processing_report(batch_results)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_file = self.processed_dir / f"processing_report_{timestamp}.json"

        with open(report_file, "w") as f:
            json.dump(report, f, indent=2)

        return report_file

    def _filter_unprocessed_files(self, raw_files: List[Path]) -> List[Path]:
        """Filter out files that have already been processed."""
        processed_files = set()

        # Check what files have already been processed
        for processed_file in self.processed_dir.glob("*.json"):
            if not processed_file.name.startswith("processing_report_"):
                processed_files.add(processed_file.stem)

        # Return files not yet processed
        return [f for f in raw_files if f.stem not in processed_files]

    def _calculate_processing_time(self, start_time: str, end_time: str) -> float:
        """Calculate processing time in seconds."""
        start = datetime.fromisoformat(start_time)
        end = datetime.fromisoformat(end_time)
        return (end - start).total_seconds()

    def _calculate_success_rate(self, batch_results: Dict[str, Any]) -> float:
        """Calculate file processing success rate."""
        total = batch_results.get("files_processed", 0) + batch_results.get("files_failed", 0)
        if total == 0:
            return 0.0
        return round(batch_results.get("files_processed", 0) / total * 100, 2)

    def _calculate_jobs_per_minute(self, batch_results: Dict[str, Any]) -> float:
        """Calculate job processing rate."""
        total_time = batch_results.get("total_processing_time", 0)
        total_jobs = batch_results.get("total_jobs_input", 0)

        if total_time == 0:
            return 0.0

        return round(total_jobs / (total_time / 60), 2)

    def _calculate_average_file_jobs(self, batch_results: Dict[str, Any]) -> float:
        """Calculate average number of jobs per file."""
        files = batch_results.get("files_processed", 0)
        jobs = batch_results.get("total_jobs_input", 0)

        if files == 0:
            return 0.0

        return round(jobs / files, 2)

    def _generate_error_recommendations(self, error_categories: Dict[str, List]) -> List[str]:
        """Generate recommendations based on error patterns."""
        recommendations = []

        if error_categories["file_parsing_errors"]:
            recommendations.append(
                "Check raw file formats and encoding. Consider adding more robust file type detection."
            )

        if error_categories["data_extraction_errors"]:
            recommendations.append("Review HTML parsing patterns. Job board structure may have changed.")

        if error_categories["normalization_errors"]:
            recommendations.append("Check normalization patterns for salary, location, and date formats.")

        if error_categories["validation_errors"]:
            recommendations.append("Review data quality requirements. Consider relaxing validation rules.")

        if not any(error_categories.values()):
            recommendations.append("No significant error patterns detected. Processing pipeline is stable.")

        return recommendations
