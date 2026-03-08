import logging
from database import get_connection

logging.basicConfig(level=logging.INFO)

def refresh_gold_layer():
    """
    In a simple setup, this just ensures the views are fresh.
    In a 'Pro' setup, you would use this to refresh Materialized Views.
    """
    conn = get_connection()
    cur = conn.cursor()
    
    try:
        logging.info("--- Refreshing Gold Layer Views ---")
        
        # We read the SQL file and execute it
        with open('3_gold/schema.sql', 'r') as f:
            cur.execute(f.read())
            
        conn.commit()
        logging.info("✅ Gold Layer Refreshed Successfully.")
        
    except Exception as e:
        logging.error(f"❌ Failed to refresh Gold Layer: {e}")
        conn.rollback()
    finally:
        cur.close()
        conn.close()

if __name__ == "__main__":
    refresh_gold_layer()
