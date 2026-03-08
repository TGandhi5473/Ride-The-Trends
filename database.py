import os
import psycopg2
from psycopg2 import pool
from dotenv import load_dotenv

# Load variables from .env if running locally
load_dotenv()

# Centralized Connection Pool
# We keep 1-10 connections open to avoid the overhead of reconnecting
try:
    db_pool = psycopg2.pool.SimpleConnectionPool(
        1, 10,
        dsn=os.getenv("HOT_DB_URL")
    )
    print("✅ Database connection pool created.")
except Exception as e:
    print(f"❌ Error creating connection pool: {e}")

def get_connection():
    """Returns a connection from the pool."""
    return db_pool.getconn()

def release_connection(conn):
    """Returns a connection back to the pool."""
    db_pool.putconn(conn)

def execute_query(query, params=None, fetch=False):
    """Helper to run a query and handle connection lifecycle automatically."""
    conn = get_connection()
    cur = conn.cursor()
    try:
        cur.execute(query, params)
        if fetch:
            result = cur.fetchall()
            return result
        conn.commit()
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        cur.close()
        release_connection(conn)
