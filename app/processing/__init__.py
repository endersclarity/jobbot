"""
Processing package for JobBot Phase 3B offline data pipeline.

This package handles token-efficient processing of raw scraped data:
- HTML parsing and data extraction
- Duplicate detection and deduplication  
- Data normalization and standardization
- Quality validation and filtering
- Database import utilities
"""

from .html_parser import JobDataExtractor
from .deduplication import DuplicateDetector
from .normalizer import DataNormalizer
from .batch_processor import BatchProcessor
from .db_importer import DatabaseImporter
from .quality_monitor import QualityMonitor

__all__ = [
    "JobDataExtractor",
    "DuplicateDetector",
    "DataNormalizer",
    "BatchProcessor",
    "DatabaseImporter",
    "QualityMonitor",
]
