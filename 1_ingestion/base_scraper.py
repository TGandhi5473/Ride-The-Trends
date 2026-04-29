from abc import ABC, abstractmethod
from typing import List, Dict, Any
import logging
from datetime import datetime

class BaseScraper(ABC):
    """
    Interface for all Social Media Scrapers.
    Enforces a standardized 'Fetch -> Format' lifecycle.
    """
    
    def __init__(self, platform: str):
        self.platform = platform
        self.is_active = True
        self.logger = logging.getLogger(f"{platform.capitalize()}Scraper")

    @abstractmethod
    def fetch_trending(self, topic: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Fetch raw data from the platform."""
        pass

    @abstractmethod
    def format_payload(self, raw_data: Any) -> Dict[str, Any]:
        """Standardize the raw JSON into a 'Bronze' compatible format."""
        pass

    def run(self, topic: str) -> List[Dict[str, Any]]:
        """
        The main execution loop. 
        Returns a list of standardized dictionaries ready for Bronze ingestion.
        """
        try:
            if not self.is_active:
                self.logger.warning(f"⚠️ Scraper for {self.platform} is currently inactive.")
                return []

            self.logger.info(f"🚀 Starting ingestion for {topic}")
            raw_results = self.fetch_trending(topic)
            
            if not raw_results:
                return []

            # We build the full DB record here to ensure architectural consistency
            formatted_records = [
                {
                    "platform": self.platform,
                    "target_topic": topic,
                    "payload": self.format_payload(item),
                    "ingested_at": datetime.utcnow().isoformat() # Traceability
                }
                for item in raw_results
            ]
            return formatted_records

        except Exception as e:
            self.logger.error(f"❌ Failed to execute {self.platform} run: {e}")
            return []
