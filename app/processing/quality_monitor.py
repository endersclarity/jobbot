"""
Quality Monitoring and Validation for Phase 3B Processing Pipeline.

Validates data completeness, detects anomalies, and generates quality reports
to ensure high-quality job data imports.
"""

import json
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional, Tuple
from collections import Counter
import statistics
import logging

logger = logging.getLogger(__name__)


class QualityMonitor:
    """Monitor and validate data quality throughout processing pipeline."""

    def __init__(self):
        """Initialize quality monitor with validation rules."""
        self.quality_rules = {
            "required_fields": ["title", "company", "location"],
            "recommended_fields": ["description", "job_url", "salary_range"],
            "min_field_lengths": {"title": 3, "company": 2, "description": 20, "requirements": 10},
            "max_field_lengths": {"title": 200, "company": 100, "location": 100, "description": 10000},
            "valid_job_types": ["Full-time", "Part-time", "Contract", "Internship", "Temporary"],
            "valid_experience_levels": ["Entry level", "Mid level", "Senior level", "Not specified"],
        }

        self.anomaly_thresholds = {
            "salary_min_threshold": 15000,  # Minimum reasonable salary
            "salary_max_threshold": 500000,  # Maximum reasonable salary
            "title_word_count_min": 1,  # Minimum words in title
            "title_word_count_max": 15,  # Maximum words in title
            "posting_age_days_max": 180,  # Maximum posting age in days
        }

    def validate_data_completeness(self, processed_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Check percentage of required fields populated.

        Args:
            processed_data: List of processed job dictionaries

        Returns:
            Data completeness analysis
        """
        if not processed_data:
            return {
                "total_jobs": 0,
                "completeness_score": 0,
                "field_analysis": {},
                "recommendations": ["No data to analyze"],
            }

        total_jobs = len(processed_data)
        field_stats = {}

        # Analyze all fields present in the data
        all_fields = set()
        for job in processed_data:
            all_fields.update(job.keys())

        # Calculate completeness for each field
        for field in all_fields:
            populated_count = sum(1 for job in processed_data if job.get(field) and str(job[field]).strip())

            field_stats[field] = {
                "populated": populated_count,
                "percentage": round(populated_count / total_jobs * 100, 2),
                "is_required": field in self.quality_rules["required_fields"],
                "is_recommended": field in self.quality_rules["recommended_fields"],
            }

        # Calculate overall completeness score
        required_score = self._calculate_required_fields_score(field_stats)
        recommended_score = self._calculate_recommended_fields_score(field_stats)
        overall_score = (required_score * 0.7) + (recommended_score * 0.3)

        # Generate recommendations
        recommendations = self._generate_completeness_recommendations(field_stats)

        return {
            "total_jobs": total_jobs,
            "completeness_score": round(overall_score, 2),
            "required_fields_score": round(required_score, 2),
            "recommended_fields_score": round(recommended_score, 2),
            "field_analysis": field_stats,
            "recommendations": recommendations,
        }

    def detect_data_anomalies(self, job_batch: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Identify unusual patterns or outliers.

        Args:
            job_batch: List of job dictionaries to analyze

        Returns:
            Anomaly detection results
        """
        if not job_batch:
            return {"anomalies": [], "anomaly_count": 0}

        anomalies = []

        # Salary anomalies
        salary_anomalies = self._detect_salary_anomalies(job_batch)
        anomalies.extend(salary_anomalies)

        # Title anomalies
        title_anomalies = self._detect_title_anomalies(job_batch)
        anomalies.extend(title_anomalies)

        # Date anomalies
        date_anomalies = self._detect_date_anomalies(job_batch)
        anomalies.extend(date_anomalies)

        # Company anomalies
        company_anomalies = self._detect_company_anomalies(job_batch)
        anomalies.extend(company_anomalies)

        # Location anomalies
        location_anomalies = self._detect_location_anomalies(job_batch)
        anomalies.extend(location_anomalies)

        return {
            "total_jobs_analyzed": len(job_batch),
            "anomaly_count": len(anomalies),
            "anomaly_rate": round(len(anomalies) / len(job_batch) * 100, 2),
            "anomalies_by_type": self._categorize_anomalies(anomalies),
            "detailed_anomalies": anomalies[:50],  # Limit for readability
        }

    def generate_quality_report(self, processing_session: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create detailed quality metrics.

        Args:
            processing_session: Results from processing session

        Returns:
            Comprehensive quality report
        """
        report = {
            "report_metadata": {
                "generated_at": datetime.now().isoformat(),
                "session_id": processing_session.get("batch_name", "unknown"),
                "report_version": "3.1",
            },
            "data_quality_summary": {
                "total_jobs_processed": processing_session.get("total_jobs_output", 0),
                "overall_quality_score": 0,
                "data_completeness": {},
                "anomaly_analysis": {},
                "validation_results": {},
            },
            "quality_trends": {},
            "recommendations": [],
            "detailed_metrics": {},
        }

        # Get processed jobs for analysis
        if "output_file" in processing_session:
            try:
                with open(processing_session["output_file"], "r") as f:
                    data = json.load(f)
                jobs = data.get("jobs", [])

                # Perform quality analysis
                completeness_analysis = self.validate_data_completeness(jobs)
                anomaly_analysis = self.detect_data_anomalies(jobs)
                validation_results = self._validate_business_rules(jobs)

                # Calculate overall quality score
                quality_components = {
                    "completeness": completeness_analysis.get("completeness_score", 0),
                    "anomaly_score": max(0, 100 - anomaly_analysis.get("anomaly_rate", 0)),
                    "validation_score": validation_results.get("validation_score", 0),
                }

                overall_score = sum(quality_components.values()) / len(quality_components)

                # Update report
                report["data_quality_summary"].update(
                    {
                        "overall_quality_score": round(overall_score, 2),
                        "data_completeness": completeness_analysis,
                        "anomaly_analysis": anomaly_analysis,
                        "validation_results": validation_results,
                        "quality_components": quality_components,
                    }
                )

                # Generate recommendations
                report["recommendations"] = self.recommend_improvements(
                    {
                        "completeness": completeness_analysis,
                        "anomalies": anomaly_analysis,
                        "validation": validation_results,
                    }
                )

            except Exception as e:
                logger.error(f"Failed to analyze quality from output file: {e}")
                report["error"] = str(e)

        return report

    def recommend_improvements(self, quality_issues: Dict[str, Any]) -> List[str]:
        """
        Suggest processing pipeline improvements.

        Args:
            quality_issues: Dictionary of quality analysis results

        Returns:
            List of improvement recommendations
        """
        recommendations = []

        # Completeness recommendations
        completeness = quality_issues.get("completeness", {})
        if completeness.get("completeness_score", 0) < 80:
            recommendations.append("Data completeness is below 80%. Review scraping patterns for missing fields.")

        field_analysis = completeness.get("field_analysis", {})
        for field, stats in field_analysis.items():
            if stats.get("is_required") and stats.get("percentage", 0) < 95:
                recommendations.append(f"Required field '{field}' missing in {100 - stats['percentage']:.1f}% of jobs.")

        # Anomaly recommendations
        anomalies = quality_issues.get("anomalies", {})
        anomaly_rate = anomalies.get("anomaly_rate", 0)

        if anomaly_rate > 10:
            recommendations.append(
                f"High anomaly rate ({anomaly_rate:.1f}%). Review data sources and validation rules."
            )

        anomalies_by_type = anomalies.get("anomalies_by_type", {})
        if anomalies_by_type.get("salary_anomalies", 0) > 5:
            recommendations.append("Multiple salary anomalies detected. Check salary parsing patterns.")

        if anomalies_by_type.get("title_anomalies", 0) > 5:
            recommendations.append("Job title anomalies found. Review title extraction and cleaning.")

        # Validation recommendations
        validation = quality_issues.get("validation", {})
        if validation.get("validation_score", 0) < 85:
            recommendations.append("Business rule validation score is low. Review validation criteria.")

        # General recommendations
        if not recommendations:
            recommendations.append("Data quality is good. Continue monitoring for consistency.")

        return recommendations[:10]  # Limit to top 10 recommendations

    def _calculate_required_fields_score(self, field_stats: Dict[str, Any]) -> float:
        """Calculate score based on required field completeness."""
        required_fields = self.quality_rules["required_fields"]
        if not required_fields:
            return 100.0

        total_score = 0
        for field in required_fields:
            if field in field_stats:
                total_score += field_stats[field]["percentage"]

        return total_score / len(required_fields)

    def _calculate_recommended_fields_score(self, field_stats: Dict[str, Any]) -> float:
        """Calculate score based on recommended field completeness."""
        recommended_fields = self.quality_rules["recommended_fields"]
        if not recommended_fields:
            return 100.0

        total_score = 0
        for field in recommended_fields:
            if field in field_stats:
                total_score += field_stats[field]["percentage"]

        return total_score / len(recommended_fields)

    def _generate_completeness_recommendations(self, field_stats: Dict[str, Any]) -> List[str]:
        """Generate recommendations based on field completeness."""
        recommendations = []

        for field, stats in field_stats.items():
            if stats["is_required"] and stats["percentage"] < 95:
                recommendations.append(f"Improve {field} extraction - only {stats['percentage']:.1f}% complete")
            elif stats["is_recommended"] and stats["percentage"] < 70:
                recommendations.append(f"Consider improving {field} collection - {stats['percentage']:.1f}% complete")

        return recommendations

    def _detect_salary_anomalies(self, jobs: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Detect unusual salary values."""
        anomalies = []

        for i, job in enumerate(jobs):
            min_salary = job.get("min_salary")
            max_salary = job.get("max_salary")

            # Check minimum salary threshold
            if min_salary and min_salary < self.anomaly_thresholds["salary_min_threshold"]:
                anomalies.append(
                    {
                        "type": "salary_anomaly",
                        "subtype": "salary_too_low",
                        "job_index": i,
                        "job_title": job.get("title", "Unknown"),
                        "value": min_salary,
                        "threshold": self.anomaly_thresholds["salary_min_threshold"],
                    }
                )

            # Check maximum salary threshold
            if max_salary and max_salary > self.anomaly_thresholds["salary_max_threshold"]:
                anomalies.append(
                    {
                        "type": "salary_anomaly",
                        "subtype": "salary_too_high",
                        "job_index": i,
                        "job_title": job.get("title", "Unknown"),
                        "value": max_salary,
                        "threshold": self.anomaly_thresholds["salary_max_threshold"],
                    }
                )

            # Check salary range logic
            if min_salary and max_salary and min_salary > max_salary:
                anomalies.append(
                    {
                        "type": "salary_anomaly",
                        "subtype": "invalid_salary_range",
                        "job_index": i,
                        "job_title": job.get("title", "Unknown"),
                        "min_salary": min_salary,
                        "max_salary": max_salary,
                    }
                )

        return anomalies

    def _detect_title_anomalies(self, jobs: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Detect unusual job titles."""
        anomalies = []

        for i, job in enumerate(jobs):
            title = job.get("title", "")
            if not title:
                continue

            word_count = len(title.split())

            # Check title length
            if word_count < self.anomaly_thresholds["title_word_count_min"]:
                anomalies.append(
                    {
                        "type": "title_anomaly",
                        "subtype": "title_too_short",
                        "job_index": i,
                        "title": title,
                        "word_count": word_count,
                    }
                )

            if word_count > self.anomaly_thresholds["title_word_count_max"]:
                anomalies.append(
                    {
                        "type": "title_anomaly",
                        "subtype": "title_too_long",
                        "job_index": i,
                        "title": title,
                        "word_count": word_count,
                    }
                )

            # Check for suspicious patterns
            if title.isupper() and len(title) > 10:
                anomalies.append({"type": "title_anomaly", "subtype": "all_caps_title", "job_index": i, "title": title})

        return anomalies

    def _detect_date_anomalies(self, jobs: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Detect unusual posting dates."""
        anomalies = []
        current_date = datetime.now().date()

        for i, job in enumerate(jobs):
            posting_date_str = job.get("posting_date")
            if not posting_date_str:
                continue

            try:
                posting_date = datetime.fromisoformat(posting_date_str).date()
                days_old = (current_date - posting_date).days

                if days_old > self.anomaly_thresholds["posting_age_days_max"]:
                    anomalies.append(
                        {
                            "type": "date_anomaly",
                            "subtype": "posting_too_old",
                            "job_index": i,
                            "job_title": job.get("title", "Unknown"),
                            "posting_date": posting_date_str,
                            "days_old": days_old,
                        }
                    )

                if days_old < 0:  # Future date
                    anomalies.append(
                        {
                            "type": "date_anomaly",
                            "subtype": "future_posting_date",
                            "job_index": i,
                            "job_title": job.get("title", "Unknown"),
                            "posting_date": posting_date_str,
                        }
                    )

            except (ValueError, TypeError):
                anomalies.append(
                    {
                        "type": "date_anomaly",
                        "subtype": "invalid_date_format",
                        "job_index": i,
                        "job_title": job.get("title", "Unknown"),
                        "posting_date": posting_date_str,
                    }
                )

        return anomalies

    def _detect_company_anomalies(self, jobs: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Detect unusual company names."""
        anomalies = []
        company_counts = Counter(job.get("company", "").lower() for job in jobs)

        # Detect companies with unusually high job counts (possible spam)
        total_jobs = len(jobs)
        for company, count in company_counts.most_common(10):
            if count > total_jobs * 0.3:  # More than 30% of jobs
                anomalies.append(
                    {
                        "type": "company_anomaly",
                        "subtype": "excessive_job_postings",
                        "company": company,
                        "job_count": count,
                        "percentage": round(count / total_jobs * 100, 2),
                    }
                )

        return anomalies

    def _detect_location_anomalies(self, jobs: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Detect unusual location patterns."""
        anomalies = []
        location_counts = Counter(job.get("location", "").lower() for job in jobs)

        # Check for overly dominant locations
        total_jobs = len(jobs)
        for location, count in location_counts.most_common(5):
            if location and count > total_jobs * 0.5:  # More than 50% of jobs
                anomalies.append(
                    {
                        "type": "location_anomaly",
                        "subtype": "location_concentration",
                        "location": location,
                        "job_count": count,
                        "percentage": round(count / total_jobs * 100, 2),
                    }
                )

        return anomalies

    def _categorize_anomalies(self, anomalies: List[Dict[str, Any]]) -> Dict[str, int]:
        """Categorize anomalies by type."""
        categories = Counter(anomaly["type"] for anomaly in anomalies)
        return dict(categories)

    def _validate_business_rules(self, jobs: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Validate jobs against business rules."""
        total_jobs = len(jobs)
        if total_jobs == 0:
            return {"validation_score": 0, "violations": []}

        violations = []

        for i, job in enumerate(jobs):
            # Validate job type
            job_type = job.get("job_type")
            if job_type and job_type not in self.quality_rules["valid_job_types"]:
                violations.append(
                    {
                        "rule": "invalid_job_type",
                        "job_index": i,
                        "value": job_type,
                        "valid_values": self.quality_rules["valid_job_types"],
                    }
                )

            # Validate experience level
            exp_level = job.get("experience_level")
            if exp_level and exp_level not in self.quality_rules["valid_experience_levels"]:
                violations.append(
                    {
                        "rule": "invalid_experience_level",
                        "job_index": i,
                        "value": exp_level,
                        "valid_values": self.quality_rules["valid_experience_levels"],
                    }
                )

            # Validate field lengths
            for field, min_length in self.quality_rules["min_field_lengths"].items():
                value = job.get(field, "")
                if value and len(str(value)) < min_length:
                    violations.append(
                        {
                            "rule": "field_too_short",
                            "job_index": i,
                            "field": field,
                            "length": len(str(value)),
                            "min_length": min_length,
                        }
                    )

        validation_score = max(0, 100 - (len(violations) / total_jobs * 100))

        return {
            "validation_score": round(validation_score, 2),
            "total_violations": len(violations),
            "violation_rate": round(len(violations) / total_jobs * 100, 2),
            "violations_by_rule": Counter(v["rule"] for v in violations),
            "detailed_violations": violations[:20],  # Limit for readability
        }
