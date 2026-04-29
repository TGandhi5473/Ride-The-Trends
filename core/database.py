import json
from sqlalchemy import create_engine, text
from sqlalchemy.engine import Engine
from .config import Config
from .logger import setup_logger

logger = setup_logger("DatabaseCore")

try:
    engine: Engine = create_engine(
        Config.DATABASE_URL,
        pool_size=5,
        max_overflow=10,
        pool_pre_ping=True,
        connect_args={'sslmode': 'require'}
    )
    logger.info("✅ Database engine initialized successfully.")
except Exception as e:
    logger.error(f"❌ Failed to initialize database engine: {e}")
    raise

def get_neon_engine() -> Engine:
    return engine

def save_to_bronze_batch(records: list):
    """
    Expects a list of dicts: 
    [{'platform':..., 'target_topic':..., 'payload':..., 'ingested_at':...}]
    """
    if not records:
        return

    # We added 'ingested_at' in the scraper refactor, so we include it here
    query = text("""
        INSERT INTO bronze.raw_ingestion (platform, target_topic, payload, ingested_at)
        VALUES (:platform, :target_topic, :payload, :ingested_at)
    """)

    try:
        with engine.begin() as conn:
            # Simple transformation: just stringify the payload dict
            for r in records:
                if isinstance(r["payload"], (dict, list)):
                    r["payload"] = json.dumps(r["payload"])
            
            conn.execute(query, records)
            logger.info(f"💾 Committed {len(records)} records to Bronze.")
    except Exception as e:
        logger.error(f"❌ Batch insert failed: {e}")
        raise

def fetch_gold_prompts():
    query = text("SELECT * FROM analytics.fct_creative_prompts ORDER BY validated_at DESC")
    try:
        with engine.connect() as conn:
            result = conn.execute(query)
            # Refactored for SQLAlchemy 2.0 compatibility
            return [row._asdict() for row in result]
    except Exception as e:
        logger.error(f"❌ Failed to fetch gold prompts: {e}")
        return []
