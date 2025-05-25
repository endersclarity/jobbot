"""
Command-line interface for Phase 3B data processing operations.

Provides CLI tools for processing raw scraped data, quality monitoring,
and database import operations.
"""

import click
import json
import sys
from datetime import datetime
from pathlib import Path
import logging

# Import processing components
from app.processing.batch_processor import BatchProcessor
from app.processing.db_importer import DatabaseImporter
from app.processing.quality_monitor import QualityMonitor

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@click.group()
@click.option('--verbose', '-v', is_flag=True, help='Enable verbose logging')
def cli(verbose):
    """JobBot Data Processing CLI - Phase 3B Offline Processing Pipeline."""
    if verbose:
        logging.getLogger().setLevel(logging.DEBUG)


@cli.command()
@click.option('--date', '-d', help='Process files for specific date (YYYY-MM-DD)')
@click.option('--data-dir', default='scraped_data', help='Base data directory')
def process_date(date, data_dir):
    """Process all raw files for a specific date."""
    if not date:
        click.echo("Error: Date is required. Use format YYYY-MM-DD", err=True)
        sys.exit(1)
    
    try:
        # Validate date format
        datetime.strptime(date, '%Y-%m-%d')
    except ValueError:
        click.echo("Error: Invalid date format. Use YYYY-MM-DD", err=True)
        sys.exit(1)
    
    click.echo(f"Processing data for date: {date}")
    
    processor = BatchProcessor(data_dir)
    results = processor.process_daily_batch(date)
    
    if results['status'] == 'no_files':
        click.echo(f"No raw files found for date {date}")
        return
    
    # Display results
    click.echo("\n" + "="*50)
    click.echo("PROCESSING RESULTS")
    click.echo("="*50)
    click.echo(f"Files processed: {results['files_processed']}")
    click.echo(f"Files failed: {results['files_failed']}")
    click.echo(f"Jobs input: {results['total_jobs_input']}")
    click.echo(f"Jobs output: {results['total_jobs_output']}")
    click.echo(f"Duplicates removed: {results['total_jobs_input'] - results['total_jobs_output']}")
    
    if results.get('output_file'):
        click.echo(f"Output file: {results['output_file']}")
    
    if results.get('errors'):
        click.echo(f"\nErrors encountered: {len(results['errors'])}")
        for error in results['errors'][:5]:  # Show first 5 errors
            click.echo(f"  - {error}")


@cli.command()
@click.option('--data-dir', default='scraped_data', help='Base data directory')
@click.option('--batch-name', help='Custom batch name')
def process_all(data_dir, batch_name):
    """Process all pending raw files."""
    click.echo("Processing all pending raw files...")
    
    processor = BatchProcessor(data_dir)
    results = processor.process_all_pending()
    
    if results['status'] in ['no_files', 'all_processed']:
        click.echo(results['message'])
        return
    
    # Display results
    click.echo("\n" + "="*50)
    click.echo("BATCH PROCESSING RESULTS")
    click.echo("="*50)
    click.echo(f"Batch: {results['batch_name']}")
    click.echo(f"Files processed: {results['files_processed']}")
    click.echo(f"Files failed: {results['files_failed']}")
    click.echo(f"Jobs input: {results['total_jobs_input']}")
    click.echo(f"Jobs output: {results['total_jobs_output']}")
    
    dedup_stats = results.get('deduplication_stats', {})
    if dedup_stats:
        click.echo(f"Duplicate rate: {dedup_stats.get('duplicate_rate', 0)}%")
    
    if results.get('output_file'):
        click.echo(f"Output file: {results['output_file']}")


@cli.command()
@click.argument('file_path')
@click.option('--batch-id', help='Custom import batch ID')
def import_data(file_path, batch_id):
    """Import processed job data to database."""
    if not Path(file_path).exists():
        click.echo(f"Error: File {file_path} not found", err=True)
        sys.exit(1)
    
    click.echo(f"Importing data from: {file_path}")
    
    importer = DatabaseImporter()
    results = importer.bulk_import_jobs(file_path)
    
    if results['status'] == 'error':
        click.echo(f"Import failed: {results['message']}", err=True)
        sys.exit(1)
    
    # Display import results
    click.echo("\n" + "="*50)
    click.echo("IMPORT RESULTS")
    click.echo("="*50)
    click.echo(f"Total jobs: {results['total_jobs']}")
    click.echo(f"Jobs imported: {results['jobs_imported']}")
    click.echo(f"Jobs updated: {results['jobs_updated']}")
    click.echo(f"Jobs skipped: {results['jobs_skipped']}")
    click.echo(f"Success rate: {results['success_rate']}%")
    
    if results.get('errors'):
        click.echo(f"\nErrors: {len(results['errors'])}")
        for error in results['errors'][:3]:  # Show first 3 errors
            click.echo(f"  - {error}")


@cli.command()
@click.argument('file_path')
@click.option('--output', '-o', help='Output file for quality report')
def quality_report(file_path, output):
    """Generate quality report for processed data."""
    if not Path(file_path).exists():
        click.echo(f"Error: File {file_path} not found", err=True)
        sys.exit(1)
    
    click.echo(f"Generating quality report for: {file_path}")
    
    # Load processed data
    try:
        with open(file_path, 'r') as f:
            data = json.load(f)
        jobs = data.get('jobs', [])
    except (json.JSONDecodeError, KeyError) as e:
        click.echo(f"Error loading data: {e}", err=True)
        sys.exit(1)
    
    monitor = QualityMonitor()
    
    # Generate analyses
    completeness = monitor.validate_data_completeness(jobs)
    anomalies = monitor.detect_data_anomalies(jobs)
    
    # Display summary
    click.echo("\n" + "="*50)
    click.echo("QUALITY REPORT SUMMARY")
    click.echo("="*50)
    click.echo(f"Total jobs analyzed: {len(jobs)}")
    click.echo(f"Completeness score: {completeness['completeness_score']}%")
    click.echo(f"Anomaly rate: {anomalies['anomaly_rate']}%")
    
    # Field completeness
    click.echo("\nField Completeness:")
    for field, stats in completeness['field_analysis'].items():
        status = "✓" if stats['percentage'] > 80 else "⚠"
        required = "(Required)" if stats['is_required'] else ""
        click.echo(f"  {status} {field}: {stats['percentage']}% {required}")
    
    # Anomalies
    if anomalies['anomaly_count'] > 0:
        click.echo(f"\nAnomalies by type:")
        for anomaly_type, count in anomalies['anomalies_by_type'].items():
            click.echo(f"  - {anomaly_type}: {count}")
    
    # Recommendations
    recommendations = monitor.recommend_improvements({
        'completeness': completeness,
        'anomalies': anomalies
    })
    
    if recommendations:
        click.echo("\nRecommendations:")
        for rec in recommendations[:5]:  # Show top 5
            click.echo(f"  • {rec}")
    
    # Save detailed report if output specified
    if output:
        full_report = {
            'generated_at': datetime.now().isoformat(),
            'source_file': file_path,
            'completeness_analysis': completeness,
            'anomaly_analysis': anomalies,
            'recommendations': recommendations
        }
        
        with open(output, 'w') as f:
            json.dump(full_report, f, indent=2)
        
        click.echo(f"\nDetailed report saved to: {output}")


@cli.command()
@click.option('--data-dir', default='scraped_data', help='Base data directory')
def status(data_dir):
    """Show processing pipeline status."""
    base_dir = Path(data_dir)
    
    if not base_dir.exists():
        click.echo(f"Data directory {data_dir} does not exist", err=True)
        return
    
    # Count files in each directory
    raw_files = list((base_dir / 'raw').glob('*.json')) if (base_dir / 'raw').exists() else []
    processed_files = list((base_dir / 'processed').glob('*.json')) if (base_dir / 'processed').exists() else []
    imported_files = list((base_dir / 'imported').glob('*.json')) if (base_dir / 'imported').exists() else []
    error_files = list((base_dir / 'errors').glob('*.json')) if (base_dir / 'errors').exists() else []
    
    click.echo("="*50)
    click.echo("PROCESSING PIPELINE STATUS")
    click.echo("="*50)
    click.echo(f"Data directory: {base_dir.absolute()}")
    click.echo(f"Raw files: {len(raw_files)}")
    click.echo(f"Processed files: {len(processed_files)}")
    click.echo(f"Imported files: {len(imported_files)}")
    click.echo(f"Error files: {len(error_files)}")
    
    # Show recent files
    if raw_files:
        recent_raw = sorted(raw_files, key=lambda x: x.stat().st_mtime, reverse=True)[:3]
        click.echo("\nRecent raw files:")
        for f in recent_raw:
            mtime = datetime.fromtimestamp(f.stat().st_mtime)
            click.echo(f"  - {f.name} ({mtime.strftime('%Y-%m-%d %H:%M')})")
    
    if processed_files:
        recent_processed = sorted(processed_files, key=lambda x: x.stat().st_mtime, reverse=True)[:3]
        click.echo("\nRecent processed files:")
        for f in recent_processed:
            mtime = datetime.fromtimestamp(f.stat().st_mtime)
            click.echo(f"  - {f.name} ({mtime.strftime('%Y-%m-%d %H:%M')})")


@cli.command()
@click.argument('files', nargs=-1)
@click.option('--batch-name', help='Custom batch name')
def process_files(files, batch_name):
    """Process specific raw data files."""
    if not files:
        click.echo("Error: No files specified", err=True)
        sys.exit(1)
    
    # Validate files exist
    file_paths = []
    for file_path in files:
        path = Path(file_path)
        if not path.exists():
            click.echo(f"Error: File {file_path} not found", err=True)
            sys.exit(1)
        file_paths.append(str(path))
    
    click.echo(f"Processing {len(file_paths)} files...")
    
    processor = BatchProcessor()
    results = processor.process_file_queue(file_paths, batch_name)
    
    # Display results
    click.echo("\n" + "="*50)
    click.echo("FILE PROCESSING RESULTS")
    click.echo("="*50)
    click.echo(f"Files processed: {results['files_processed']}")
    click.echo(f"Files failed: {results['files_failed']}")
    click.echo(f"Jobs input: {results['total_jobs_input']}")
    click.echo(f"Jobs output: {results['total_jobs_output']}")
    
    if results.get('output_file'):
        click.echo(f"Output file: {results['output_file']}")


if __name__ == '__main__':
    cli()