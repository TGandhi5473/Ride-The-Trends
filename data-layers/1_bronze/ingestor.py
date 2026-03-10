import json
import logging
from datetime import datetime, timezone
from scrapers import BronzeScraper
from database import save_to_bronze_batch # Updated to reflect batching
from database import init_landing_table

def run_bronze_ingestion():
    scraper = BronzeScraper()
    timestamp = datetime.now(timezone.utc)
    
    logging.info("--- Starting Bronze Ingestion Sweep ---")

    # --- 1. YouTube Ingestion (Batching by Platform) ---
    all_youtube_records = []
    for category_name in scraper.yt_category_map.keys():
        logging.info(f"Fetching YouTube category: {category_name}")
        try:
            videos = scraper.fetch_youtube_by_category(category_name)
            for video in videos:
                all_youtube_records.append({
                    "platform": "youtube",
                    "target_topic": category_name,
                    "payload": video,
                    "ingested_at": timestamp.isoformat()
                })
        except Exception as e:
            logging.error(f"Failed to fetch YouTube {category_name}: {e}")

    # Bulk Save YouTube
    if all_youtube_records:
        save_to_bronze_batch(all_youtube_records)
        logging.info(f"Successfully batch-saved {len(all_youtube_records)} YouTube records.")

    # --- 2. Bluesky Ingestion (Batching by Platform) ---
    logging.info("Fetching current Bluesky trends...")
    trending_topics = scraper.fetch_bluesky_topics()
    all_bluesky_records = []
    
    for topic in trending_topics:
        logging.info(f"Fetching Bluesky posts for topic: {topic}")
        try:
            posts = scraper.fetch_bluesky_by_topic(topic, max_results=50)
            for post in posts:
                all_bluesky_records.append({
                    "platform": "bluesky",
                    "target_topic": topic,
                    "payload": post.model_dump(), 
                    "ingested_at": timestamp.isoformat()
                })
        except Exception as e:
            logging.error(f"Failed to fetch Bluesky topic {topic}: {e}")

    # Bulk Save Bluesky
    if all_bluesky_records:
        save_to_bronze_batch(all_bluesky_records)
        logging.info(f"Successfully batch-saved {len(all_bluesky_records)} Bluesky records.")

    logging.info("--- Bronze Ingestion Complete ---")

if __name__ == "__main__":
    init_landing_table() 
    run_bronze_ingestion()
