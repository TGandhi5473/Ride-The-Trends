from core import (
    Config, 
    ScraperFactory, 
    save_to_bronze_batch, 
    setup_logger,
    QuotaExceededError,
    RideTheTrendsError
)

# 1. Standardized Observability via core.logger
logger = setup_logger("IngestionWorker")

def run_pipeline():
    """
    Main orchestration loop with merged Quota Guard logic.
    Refactored to use the 'core' library for Medallion Architecture compliance.
    """
    logger.info("🚀 Starting Trend Ingestion Pulse...")
    
    # Using your high-intent topics from the old worker
    target_topics = Config.DEFAULT_TOPICS 
    platform_names = ["youtube", "bluesky"]
    
    # Initialize Scrapers via Factory (Factory handles API keys internally)
    scrapers = [ScraperFactory.get_scraper(p) for p in platform_names]

    for topic in target_topics:
        logger.info(f"--- 🌊 Starting Topic Run: {topic} ---")
        
        for scraper in scrapers:
            # PRESERVED: Quota Guard logic from your previous version
            if hasattr(scraper, 'is_active') and not scraper.is_active:
                logger.warning(f"⏭️ Skipping {scraper.platform}: Quota limit reached.")
                continue

            try:
                logger.info(f"📡 Scraping {scraper.platform} for: {topic}")
                
                # The .run() method executes the logic and returns standardized list
                raw_data = scraper.run(topic)
                
                if raw_data:
                    # Map to Bronze schema: platform, topic, payload
                    batch_to_save = [
                        {
                            "platform": scraper.platform,
                            "target_topic": topic,
                            "payload": record
                        } for record in raw_data
                    ]
                    
                    # PRESERVED: High-speed batch insert into Neon
                    save_to_bronze_batch(batch_to_save)
                    logger.info(f"✅ Ingested {len(batch_to_save)} records from {scraper.platform}")
                else:
                    logger.warning(f"⚠️ No data found for {scraper.platform} on topic: {topic}")

            except QuotaExceededError as e:
                # If a specific scraper hits a limit, it marks itself inactive
                scraper.is_active = False 
                logger.error(f"🛑 {e}")
                continue
            
            except RideTheTrendsError as e:
                logger.error(f"⚠️ Specialized Error in {scraper.platform}: {e}")
                continue
            
            except Exception as e:
                logger.error(f"💀 Unexpected Failure: {e}")

    logger.info("🏁 Pipeline run complete. Connections pooled and safe.")

if __name__ == "__main__":
    run_pipeline()
