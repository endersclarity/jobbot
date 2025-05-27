"""
Indeed Job Scraper - Phase 3A Raw Data Collection

Token-efficient scraping that saves raw HTML/JSON without LLM processing.
Designed to avoid Claude Code token burn during large-scale scraping.
"""

import requests
import time
import json
import random
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any
from urllib.parse import urlencode
import logging


class IndeedScraper:
    """Raw data scraper for Indeed job listings"""

    def __init__(self, base_dir: Optional[str] = None):
        self.base_dir = Path(base_dir) if base_dir else Path(__file__).parent.parent.parent / "scraped_data"
        self.raw_dir = self.base_dir / "raw"
        self.logs_dir = self.base_dir / "logs"

        # User agents for rotation
        self.user_agents = [
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
            "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
        ]

        # Setup logging
        self._setup_logging()

    def _setup_logging(self):
        """Setup logging to file"""
        log_file = self.logs_dir / f"indeed_scraper_{datetime.now().strftime('%Y%m%d')}.log"
        logging.basicConfig(
            level=logging.INFO,
            format="%(asctime)s - %(levelname)s - %(message)s",
            handlers=[logging.FileHandler(log_file), logging.StreamHandler()],
        )
        self.logger = logging.getLogger(__name__)

    def _get_headers(self) -> Dict[str, str]:
        """Get randomized headers for requests"""
        return {
            "User-Agent": random.choice(self.user_agents),
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.5",
            "Accept-Encoding": "gzip, deflate, br",
            "Connection": "keep-alive",
            "Upgrade-Insecure-Requests": "1",
            "Sec-Fetch-Dest": "document",
            "Sec-Fetch-Mode": "navigate",
            "Sec-Fetch-Site": "none",
            "Cache-Control": "max-age=0",
        }

    def _build_search_url(self, query: str, location: str = "", start: int = 0) -> str:
        """Build Indeed search URL"""
        base_url = "https://www.indeed.com/jobs"
        params = {"q": query, "l": location, "start": start}
        return f"{base_url}?{urlencode(params)}"

    def _rate_limit(self):
        """Random delay to avoid detection"""
        delay = random.uniform(1.5, 4.0)  # 1.5-4 second delay
        time.sleep(delay)

    def scrape_search_page(self, query: str, location: str = "", page: int = 0) -> Dict:
        """
        Scrape a single Indeed search results page
        Returns raw data without processing
        """
        start = page * 10  # Indeed shows 10 results per page
        url = self._build_search_url(query, location, start)

        self.logger.info(f"Scraping: {url}")

        try:
            # Create session for better handling
            session = requests.Session()
            session.headers.update(self._get_headers())

            response = session.get(url, timeout=10)

            if response.status_code == 403:
                self.logger.warning(f"403 Forbidden - may need to use browser automation for: {url}")

            response.raise_for_status()

            # Create raw data structure
            raw_data = {
                "timestamp": datetime.now().isoformat(),
                "url": url,
                "query": query,
                "location": location,
                "page": page,
                "status_code": response.status_code,
                "html_content": response.text,
                "headers": dict(response.headers),
            }

            # Save raw data immediately
            filename = self._save_raw_data(raw_data, query, location, page)

            self.logger.info(f"Saved raw data: {filename}")
            return raw_data

        except Exception as e:
            self.logger.error(f"Error scraping {url}: {str(e)}")
            return {"error": str(e), "url": url}

    def _save_raw_data(self, data: Dict, query: str, location: str, page: int) -> str:
        """Save raw scraped data to JSON file"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        safe_query = "".join(c for c in query if c.isalnum() or c in (" ", "-", "_")).rstrip()
        safe_location = "".join(c for c in location if c.isalnum() or c in (" ", "-", "_")).rstrip()

        filename = f"indeed_{safe_query.replace(' ', '_')}_{safe_location.replace(' ', '_')}_{page}_{timestamp}.json"
        filepath = self.raw_dir / filename

        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

        return filename

    def scrape_multiple_pages(self, query: str, location: str = "", max_pages: int = 5) -> List[Dict]:
        """
        Scrape multiple pages of Indeed results

        Args:
            query: Job search query (e.g., "python developer")
            location: Location (e.g., "San Francisco, CA")
            max_pages: Maximum number of pages to scrape

        Returns:
            List of raw data dictionaries
        """
        results = []

        self.logger.info(f"Starting scrape: '{query}' in '{location}' - {max_pages} pages")

        for page in range(max_pages):
            self.logger.info(f"Scraping page {page + 1}/{max_pages}")

            raw_data = self.scrape_search_page(query, location, page)
            results.append(raw_data)

            # Rate limiting between pages
            if page < max_pages - 1:  # Don't delay after last page
                self._rate_limit()

        self.logger.info(f"Completed scraping {len(results)} pages")
        return results


def main():
    """Simple CLI interface for testing"""
    import sys

    if len(sys.argv) < 2:
        print("Usage: python indeed.py 'search query' [location] [max_pages]")
        print("Example: python indeed.py 'python developer' 'San Francisco' 3")
        return

    query = sys.argv[1]
    location = sys.argv[2] if len(sys.argv) > 2 else ""
    max_pages = int(sys.argv[3]) if len(sys.argv) > 3 else 2

    scraper = IndeedScraper()
    results = scraper.scrape_multiple_pages(query, location, max_pages)

    print("\nScraping completed!")
    print(f"- Query: '{query}'")
    print(f"- Location: '{location}'")
    print(f"- Pages scraped: {len(results)}")
    print(f"- Raw data saved to: {scraper.raw_dir}")


if __name__ == "__main__":
    main()
