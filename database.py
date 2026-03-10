import os
import json
import logging
import psycopg2
from psycopg2 import pool
from psycopg2.extras import execute_values
import pandas as pd
from dotenv import load_dotenv
from pgvector.psycopg2 import register_vector

load_dotenv()

# --- 1. Connection Pool Setup ---
try:
    # Using HOT_DB_URL for the 2026 "Hot/Cold" architecture
    db_pool = psycopg2.pool.SimpleConnectionPool(
        1, 10,
        dsn=os.getenv("HOT_DB_URL")
    )
    logging.info("✅ Database connection pool active (pgvector enabled).")
except Exception as e:
    logging.error(f"❌ Connection pool error: {e}")

def get_connection():
    conn = db_pool.getconn()
    register_vector(conn) # Ensures vector types are recognized immediately
    return conn

def release_connection(conn):
    db_pool.putconn(conn)

# --- 2. High-Performance Read/Write Logic ---

def run_query(query, params=None):
    """Optimized for Pandas 3.0 + Arrow for 6x faster string ops."""
    conn = get_connection()
    try:
        # dtype_backend="pyarrow" reduces memory overhead by ~50%
        return pd.read_sql(query, conn, params=params, dtype_backend="pyarrow")
    finally:
        release_connection(conn)

def save_to_bronze_batch(records):
    """
    High-speed batch insert using execute_values.
    Reduces 1000+ round-trips to a single database hit.
    """
    if not records:
        return

    conn = get_connection()
    cur = conn.cursor()
    try:
        # We assume the schema.sql columns: (platform, target_topic, payload)
        data_tuples = [
            (r['platform'], r['target_topic'], json.dumps(r['payload'])) 
            for r in records
        ]
        
        query = "INSERT INTO bronze_social_feeds (platform, target_topic, payload) VALUES %s"
        execute_values(cur, query, data_tuples)
        conn.commit()
    except Exception as e:
        conn.rollback()
        logging.error(f"Batch insert failed: {e}")
        raise e
    finally:
        cur.close()
        release_connection(conn)

def init_db():
    """Initializes schema using a connection from the pool."""
    conn = get_connection()
    cur = conn.cursor()
    try:
        schema_path = os.path.join(os.path.dirname(__file__), 'schema.sql')
        with open(schema_path, 'r') as f:
            cur.execute(f.read())
        conn.commit()
        logging.info("--- Bronze Schema Initialized ---")
    except Exception as e:
        logging.error(f"Init error: {e}")
        conn.rollback()
    finally:
        cur.close()
        release_connection(conn)
