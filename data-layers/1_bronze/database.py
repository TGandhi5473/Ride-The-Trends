import os
import json
import psycopg2
from psycopg2.extras import execute_values
from dotenv import load_dotenv

load_dotenv()

def get_connection():
    """Establishes a connection to the PostgreSQL database."""
    return psycopg2.connect(
        host=os.getenv("DB_HOST", "localhost"),
        database=os.getenv("DB_NAME", "social_intelligence"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD")
    )

def init_db():
    """Executes the schema.sql file to set up the Bronze layer."""
    conn = get_connection()
    cur = conn.cursor()
    try:
        # Resolve path to schema.sql relative to this file
        schema_path = os.path.join(os.path.dirname(__file__), 'schema.sql')
        with open(schema_path, 'r') as f:
            cur.execute(f.read())
        conn.commit()
        print("--- Bronze Schema Initialized Successfully ---")
    except Exception as e:
        print(f"Error initializing database: {e}")
        conn.rollback()
    finally:
        cur.close()
        conn.close()

def save_to_bronze(record):
    """
    Saves a dictionary into the bronze_social_feeds table.
    Expected keys: platform, target_topic, payload
    """
    conn = get_connection()
    cur = conn.cursor()
    try:
        query = """
            INSERT INTO bronze_social_feeds (platform, target_topic, payload)
            VALUES (%s, %s, %s)
        """
        # Ensure payload is converted to a JSON string for the JSONB column
        cur.execute(query, (
            record['platform'], 
            record['target_topic'], 
            json.dumps(record['payload'])
        ))
        conn.commit()
    except Exception as e:
        print(f"Error saving to Bronze: {e}")
        conn.rollback()
    finally:
        cur.close()
        conn.close()
