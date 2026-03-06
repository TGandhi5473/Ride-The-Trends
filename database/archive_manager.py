import os
import psycopg2
from dotenv import load_dotenv

load_dotenv()

def manage_partitions(month_year):
    """
    Example: month_year = 'march_2026'
    1. Detaches the partition from 'trends' table in Hot DB.
    2. Since the data was 'dual-written' to Cold DB, we can safely drop it from Hot.
    """
    conn = psycopg2.connect(os.getenv("HOT_DB_URL"))
    conn.autocommit = True
    
    with conn.cursor() as cur:
        partition_name = f"trends_{month_year}"
        print(f"Detaching partition: {partition_name}")
        
        # Detach command (Instant, doesn't block reads)
        cur.execute(f"ALTER TABLE trends DETACH PARTITION {partition_name};")
        
        # In a real prod environment, you'd back this up to S3 here.
        # For now, we drop it because the Cold DB already has the data.
        cur.execute(f"DROP TABLE {partition_name};")
        
    print(f"Partition {partition_name} successfully archived and purged from Hot DB.")
    conn.close()

if __name__ == "__main__":
    # Usually triggered by a cron job at the end of the month
    manage_partitions("march_2026")
