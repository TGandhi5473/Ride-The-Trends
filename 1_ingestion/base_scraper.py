from abc import ABC, abstractmethod
from typing import List, Dict, Any
import logging

class BaseScraper(ABC):
    """
    Interface for all Social Media Scrapers.
    Enforces a standardized 'Fetch -> Save' lifecycle.
    """
    
    def __init__(self, platform: str):
        self.platform = platform
        self.logger = logging.getLogger(f"{platform.capitalize()}Scraper")

    @abstractmethod
    def fetch_trending(self, topic: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Fetch raw data from the platform."""
        pass

    @abstractmethod
    def format_payload(self, raw_data: Any) -> Dict[str, Any]:
        """Standardize the raw JSON into a 'Bronze' compatible format."""
        pass

    def run(self, topic: str):
        """The main execution loop for the worker to call."""
        try:
            self.logger.info(f"🚀 Starting ingestion for {topic}")
            raw_results = self.fetch_trending(topic)
            
            # Prepare for database.save_to_bronze_batch (from our previous file)
            formatted_records = [
                {
                    "platform": self.platform,
                    "target_topic": topic,
                    "payload": self.format_payload(item)
                }
                for item in raw_results
            ]
            return formatted_records
        except Exception as e:
            self.logger.error(f"❌ Failed to ingest {self.platform}: {e}")
            return []
