import json
import logging
from database import get_connection

def refine_bronze_to_silver():
    conn = get_connection()
    cur = conn.cursor()
    
    # 1. INCREMENTAL LOAD: Get only rows not yet in Silver
    # We look for Bronze IDs that aren't in Silver or Quarantine
    query = """
        SELECT b.id, b.platform, b.target_topic, b.payload, b.ingested_at 
        FROM bronze_social_feeds b
        LEFT JOIN silver_social_posts s ON b.payload->>'id' = s.source_id
        LEFT JOIN silver_quarantine q ON b.id = q.bronze_id
        WHERE s.source_id IS NULL AND q.bronze_id IS NULL
        LIMIT 500;
    """
    cur.execute(query)
    rows = cur.fetchall()

    for b_id, platform, topic, payload, ingested_at in rows:
        try:
            # 2. DATA QUALITY GATE: Essential checks
            content = ""
            source_id = ""
            
            if platform == 'youtube':
                content = payload['snippet'].get('title', '')
                source_id = payload.get('id')
                author = payload['snippet'].get('channelTitle')
                views = int(payload['statistics'].get('viewCount', 0))
            else: # Bluesky
                content = payload.get('text', '')
                source_id = payload.get('uri')
                author = payload['author'].get('handle')
                views = 0 # Bsky doesn't have "views" the same way

            # Validation Rule: Content must be at least 5 chars
            if not content or len(content) < 5:
                raise ValueError("Content too short or missing")

            # 3. UPSERT INTO SILVER
            # (In reality, you'd call your BERT model here for predicted_category)
            cur.execute("""
                INSERT INTO silver_social_posts 
                (platform, source_id, author, content, view_count, raw_category, ingested_at)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (source_id) DO UPDATE SET 
                    view_count = EXCLUDED.view_count,
                    processed_at = CURRENT_TIMESTAMP;
            """, (platform, source_id, author, content, views, topic, ingested_at))

        except Exception as e:
            # 4. QUARANTINE: Save failures instead of crashing
            cur.execute("""
                INSERT INTO silver_quarantine (bronze_id, platform, error_reason, raw_payload)
                VALUES (%s, %s, %s, %s)
            """, (b_id, platform, str(e), json.dumps(payload)))

    conn.commit()
    cur.close()
    conn.close()
    logging.info(f"Refined {len(rows)} records.")
