import os
import logging
from database import get_connection, release_connection

logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')

def refresh_gold_layer():
    sql_path = '3_gold/schema.sql'
    
    if not os.path.exists(sql_path):
        logging.error(f"❌ SQL file not found at {sql_path}")
        return

    conn = get_connection()
    cur = conn.cursor()
    
    try:
        logging.info("--- 🏗️  Rebuilding Gold Layer ---")
        
        with open(sql_path, 'r') as f:
            sql_script = f.read()
            
        # psycopg2 handles the entire script as one multi-statement string
        cur.execute(sql_script)
        
        conn.commit()
        logging.info("✅ Gold views and materialized indices refreshed.")
        
    except Exception as e:
        conn.rollback()
        logging.error(f"❌ Gold Layer Refresh Failed: {e}")
    finally:
        cur.close()
        release_connection(conn) # Return to pool

if __name__ == "__main__":
    refresh_gold_layer()
