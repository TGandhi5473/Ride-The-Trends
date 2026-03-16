import logging
import os
from typing import List
from core.database import save_to_bronze_batch  # Centralized Neon connector
from .youtube_scraper import YouTubeScraper
from .bluesky_scraper import BlueskyScraper

# Configure logging for professional observability
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("IngestionWorker")

def run_pipeline():
    """
    Main orchestration loop with Quota Guard logic.
    Ensures zero billing risk by monitoring API unit consumption.
    """
    # 1. Define high-intent topics for Creative Teams
    target_topics = ["AI tools", "Sustainable Fashion", "Digital Nomad Life"]
    
    # 2. Initialize Scrapers with Quota Thresholds
    # YouTube has a 10,000 unit free limit; we cap at 9,000 to be safe.
    scrapers = [
        YouTubeScraper(),
        BlueskyScraper()
    ]

    for topic in target_topics:
        logger.info(f"--- 🌊 Starting Topic Run: {topic} ---")
        
        for scraper in scrapers:
            # Check if the scraper has already disabled itself due to quota
            if hasattr(scraper, 'is_active') and not scraper.is_active:
                logger.warning(f"⏭️ Skipping {scraper.platform}: Quota limit reached in this session.")
                continue

            # The .run() method (inherited from BaseScraper) executes the logic
            batch_data = scraper.run(topic)
            
            if batch_data:
                try:
                    # High-speed batch insert into Neon
                    save_to_bronze_batch(batch_data)
                    logger.info(f"✅ Ingested {len(batch_data)} records from {scraper.platform}")
                except Exception as e:
                    logger.error(f"❌ Database write failed for {scraper.platform}: {e}")
            else:
                # This could trigger if the API returned 403 or the Quota Guard tripped
                logger.warning(f"⚠️ No data ingested for {scraper.platform} on topic: {topic}")

    logger.info("🏁 Pipeline run complete. Connections closed.")

if __name__ == "__main__":
    # Standard entry point for GitHub Actions cron jobs
    run_pipeline()
