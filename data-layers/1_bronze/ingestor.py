import json
import logging
from datetime import datetime, timezone
from scrapers import BronzeScraper
from database import save_to_bronze
from database import init_landing_table

if __name__ == "__main__":
    init_landing_table() # Safely checks if table exists before starting
    run_bronze_ingestion()
# Setup logging to track our progress/errors
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def run_bronze_ingestion():
    scraper = BronzeScraper()
    timestamp = datetime.now(timezone.utc)
    
    logging.info("--- Starting Bronze Ingestion Sweep ---")

    # --- 1. YouTube Ingestion (Static Categories) ---
    for category_name in scraper.yt_category_map.keys():
        logging.info(f"Fetching YouTube category: {category_name}")
        try:
            videos = scraper.fetch_youtube_by_category(category_name)
            for video in videos:
                # We wrap the raw API response with ingestion metadata
                record = {
                    "platform": "youtube",
                    "target_topic": category_name,
                    "payload": video, # The raw JSON from Google
                    "ingested_at": timestamp.isoformat()
                }
                save_to_bronze(record)
        except Exception as e:
            logging.error(f"Failed to ingest YouTube {category_name}: {e}")

    # --- 2. Bluesky Ingestion (Dynamic Trends) ---
    logging.info("Fetching current Bluesky trends...")
    trending_topics = scraper.fetch_bluesky_topics()
    
    for topic in trending_topics:
        logging.info(f"Fetching Bluesky posts for topic: {topic}")
        try:
            posts = scraper.fetch_bluesky_by_topic(topic, max_results=50)
            for post in posts:
                # atproto objects can be converted to dicts for JSON storage
                record = {
                    "platform": "bluesky",
                    "target_topic": topic,
                    "payload": post.model_dump(), # The raw JSON from Bluesky
                    "ingested_at": timestamp.isoformat()
                }
                save_to_bronze(record)
        except Exception as e:
            logging.error(f"Failed to ingest Bluesky topic {topic}: {e}")

    logging.info("--- Bronze Ingestion Complete ---")

if __name__ == "__main__":
    run_bronze_ingestion()
