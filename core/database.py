import json
from sqlalchemy import create_engine, text
from sqlalchemy.engine import Engine
from .config import Config
from .logger import setup_logger

logger = setup_logger("DatabaseCore")

# 1. Initialize the Engine with Neon-Specific Optimization
# We use 'pool_pre_ping' because Neon can 'sleep'—this wakes it up safely.
try:
    engine: Engine = create_engine(
        Config.DATABASE_URL,
        pool_size=5,
        max_overflow=10,
        pool_pre_ping=True,
        connect_args={'sslmode': 'require'} # Critical for Neon/Postgres cloud security
    )
    logger.info("✅ Database engine initialized successfully.")
except Exception as e:
    logger.error(f"❌ Failed to initialize database engine: {e}")
    raise

def get_neon_engine() -> Engine:
    """Access point for the Streamlit App to get a DB connection."""
    return engine

def save_to_bronze_batch(records: list):
    """
    High-speed batch insert into the Bronze layer.
    Used by worker.py after scraping social platforms.
    """
    if not records:
        logger.warning("⚠️ No records provided for ingestion.")
        return

    # Using the 'payload' as JSONB for maximum flexibility in Bronze
    query = text("""
        INSERT INTO bronze.raw_ingestion (platform, target_topic, payload)
        VALUES (:platform, :target_topic, :payload)
    """)

    try:
        with engine.begin() as conn:
            # We must serialize the dict to a string so Postgres recognizes it as JSON
            formatted_batch = [
                {
                    "platform": r["platform"],
                    "target_topic": r["target_topic"],
                    "payload": json.dumps(r["payload"])
                } 
                for r in records
            ]
            conn.execute(query, formatted_batch)
            logger.info(f"💾 Successfully committed {len(records)} records to Bronze.")
    except Exception as e:
        logger.error(f"❌ Batch insert failed: {e}")
        raise

def fetch_gold_prompts():
    """
    Fetches the 'Gold' layer data for the UI.
    This pulls from the final analytical table created by dbt.
    """
    query = text("SELECT * FROM analytics.fct_creative_prompts ORDER BY validated_at DESC")
    
    try:
        with engine.connect() as conn:
            result = conn.execute(query)
            # Returning as list of dicts for easy Streamlit/Pandas conversion
            return [dict(row) for row in result]
    except Exception as e:
        logger.error(f"❌ Failed to fetch gold prompts: {e}")
        return []
