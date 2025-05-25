"""
Scraper Configuration System
Manages search terms, locations, rate limits, and scraping parameters
"""

import json
from pathlib import Path
from typing import List, Optional
from dataclasses import dataclass, asdict


@dataclass
class ScrapingConfig:
    """Configuration for scraping jobs"""

    # Search parameters
    queries: List[str]
    locations: List[str]
    max_pages_per_search: int = 5

    # Rate limiting
    min_delay: float = 1.5
    max_delay: float = 4.0
    request_timeout: int = 10

    # File management
    max_files_per_directory: int = 1000
    cleanup_old_files: bool = True
    days_to_keep: int = 30

    # User agent rotation
    rotate_user_agents: bool = True
    custom_user_agents: Optional[List[str]] = None


class ScraperConfigManager:
    """Manages scraper configuration files"""

    def __init__(self, config_path: str = None):
        if config_path:
            self.config_path = Path(config_path)
        else:
            self.config_path = Path(__file__).parent.parent.parent / "scraper_config.json"

    def create_default_config(self) -> ScrapingConfig:
        """Create default scraping configuration"""
        return ScrapingConfig(
            queries=[
                "python developer",
                "software engineer python",
                "backend developer",
                "full stack developer python",
                "data engineer python",
            ],
            locations=["San Francisco, CA", "New York, NY", "Seattle, WA", "Austin, TX", "Remote"],
            max_pages_per_search=3,
        )

    def save_config(self, config: ScrapingConfig):
        """Save configuration to JSON file"""
        with open(self.config_path, "w") as f:
            json.dump(asdict(config), f, indent=2)

    def load_config(self) -> ScrapingConfig:
        """Load configuration from JSON file"""
        if not self.config_path.exists():
            config = self.create_default_config()
            self.save_config(config)
            return config

        with open(self.config_path, "r") as f:
            data = json.load(f)
            return ScrapingConfig(**data)


def get_default_config() -> ScrapingConfig:
    """Quick function to get default configuration"""
    manager = ScraperConfigManager()
    return manager.load_config()
