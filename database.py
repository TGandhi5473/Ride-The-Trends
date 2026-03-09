import os
import psycopg2
from psycopg2 import pool
import pandas as pd
from dotenv import load_dotenv
from pgvector.psycopg2 import register_vector  # Added for vector support

load_dotenv()

# Centralized Connection Pool (1-10 connections)
try:
    db_pool = psycopg2.pool.SimpleConnectionPool(
        1, 10,
        dsn=os.getenv("HOT_DB_URL")
    )
    print("✅ Database connection pool active.")
except Exception as e:
    print(f"❌ Connection pool error: {e}")

def get_connection():
    conn = db_pool.getconn()
    # Registering vector type on the connection so pgvector works
    register_vector(conn)
    return conn

def release_connection(conn):
    db_pool.putconn(conn)

def run_query(query, params=None):
    """
    Optimized for Pandas 3.0 + Arrow.
    Now correctly handles pgvector types via registered connection.
    """
    conn = get_connection()
    try:
        # dtype_backend="pyarrow" utilizes the 2026 memory speed boost
        return pd.read_sql(query, conn, params=params, dtype_backend="pyarrow")
    finally:
        release_connection(conn)

def execute_action(query, params=None):
    """
    Use this for INSERT, UPDATE, or DELETE operations.
    """
    conn = get_connection()
    cur = conn.cursor()
    try:
        cur.execute(query, params)
        conn.commit()
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        cur.close()
        release_connection(conn)
