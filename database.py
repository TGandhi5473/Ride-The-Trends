import os
import json
import logging
from contextlib import contextmanager

import psycopg2
from psycopg2 import pool
from psycopg2.extras import execute_values
from pgvector.psycopg2 import register_vector

import pandas as pd
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

load_dotenv()

# --- 1. Neon-Optimized Connection Setup ---

# We'll use SQLAlchemy for read operations (Pandas 3.0) 
# and psycopg2's ThreadedPool for high-speed writes.
DB_URL = os.getenv("HOT_DB_URL")
if DB_URL and DB_URL.startswith("postgres://"):
    DB_URL = DB_URL.replace("postgres://", "postgresql://", 1)

# Persistent engine for Pandas/Streamlit (SQLAlchemy handles the pool)
_engine = None

def get_engine():
    global _engine
    if _engine is None:
        _engine = create_engine(
            DB_URL,
            pool_size=5,
            max_overflow=10,
            pool_pre_ping=True, # Handles Neon cold starts/reconnects
            connect_args={"sslmode": "require"}
        )
    return _engine

# Threaded pool for Scrapers/Ingestors (psycopg2)
try:
    db_pool = psycopg2.pool.ThreadedConnectionPool(
        1, 15,
        dsn=DB_URL,
        sslmode="require"
    )
    logging.info("✅ Neon Threaded Pool active (SSL Required).")
except Exception as e:
    logging.error(f"❌ Connection pool error: {e}")

@contextmanager
def get_db_connection():
    """Context manager to ensure connections are always returned to the pool."""
    conn = db_pool.getconn()
    register_vector(conn)
    try:
        yield conn
    finally:
        db_pool.putconn(conn)

# --- 2. High-Performance Read/Write Logic ---

def run_query(query, params=None):
    """Refactored for SQLAlchemy + Pandas 3.0 + Arrow."""
    engine = get_engine()
    with engine.connect() as conn:
        # text() is required in Pandas 3.0+ for SQLAlchemy connectables
        return pd.read_sql(text(query), conn, params=params, dtype_backend="pyarrow")

def save_to_bronze_batch(records):
    """High-speed batch insert using ThreadedPool."""
    if not records:
        return

    data_tuples = [
        (r['platform'], r['target_topic'], json.dumps(r['payload'])) 
        for r in records
    ]
    
    query = "INSERT INTO bronze_social_feeds (platform, target_topic, payload) VALUES %s"
    
    with get_db_connection() as conn:
        with conn.cursor() as cur:
            try:
                execute_values(cur, query, data_tuples)
                conn.commit()
            except Exception as e:
                conn.rollback()
                logging.error(f"Batch insert failed: {e}")
                raise e

def init_db():
    """Initializes schema using a pool connection."""
    schema_path = os.path.join(os.path.dirname(__file__), 'schema.sql')
    if not os.path.exists(schema_path):
        logging.warning("schema.sql not found. Skipping init.")
        return

    with get_db_connection() as conn:
        with conn.cursor() as cur:
            try:
                with open(schema_path, 'r') as f:
                    cur.execute(f.read())
                conn.commit()
                logging.info("--- Bronze Schema Initialized ---")
            except Exception as e:
                logging.error(f"Init error: {e}")
                conn.rollback()
