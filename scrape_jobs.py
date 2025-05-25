#!/usr/bin/env python3
"""
JobBot Scraper CLI - Phase 3A Raw Data Collection

Simple command-line interface for scraping job data.
Saves raw HTML/JSON files without LLM processing.
"""

import sys
import argparse
from pathlib import Path

# Add app directory to Python path
sys.path.append(str(Path(__file__).parent / "app"))

from scrapers.indeed import IndeedScraper
from scrapers.config import ScraperConfigManager


def main():
    parser = argparse.ArgumentParser(description='JobBot Raw Data Scraper')
    
    # Basic scraping options
    parser.add_argument('--query', '-q', type=str, help='Job search query')
    parser.add_argument('--location', '-l', type=str, default='', help='Job location')
    parser.add_argument('--pages', '-p', type=int, default=2, help='Number of pages to scrape')
    
    # Config options
    parser.add_argument('--config', '-c', action='store_true', help='Run with saved configuration')
    parser.add_argument('--setup-config', action='store_true', help='Create default configuration file')
    
    args = parser.parse_args()
    
    # Setup configuration if requested
    if args.setup_config:
        manager = ScraperConfigManager()
        config = manager.create_default_config()
        manager.save_config(config)
        print(f"Default configuration saved to: {manager.config_path}")
        return
    
    # Initialize scraper
    scraper = IndeedScraper()
    
    if args.config:
        # Run with saved configuration
        print("Running with saved configuration...")
        manager = ScraperConfigManager()
        config = manager.load_config()
        
        total_scraped = 0
        for query in config.queries:
            for location in config.locations:
                print(f"\nScraping: '{query}' in '{location}'")
                results = scraper.scrape_multiple_pages(
                    query, location, config.max_pages_per_search
                )
                total_scraped += len(results)
                
        print(f"\nTotal pages scraped: {total_scraped}")
        
    elif args.query:
        # Single query scraping
        print(f"Scraping: '{args.query}' in '{args.location}'")
        results = scraper.scrape_multiple_pages(args.query, args.location, args.pages)
        print(f"Scraped {len(results)} pages")
        
    else:
        # No arguments provided
        parser.print_help()
        print("\nExamples:")
        print("  python scrape_jobs.py --setup-config")
        print("  python scrape_jobs.py -q 'python developer' -l 'San Francisco' -p 3")
        print("  python scrape_jobs.py --config")


if __name__ == "__main__":
    main()