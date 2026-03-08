import json
import logging
from database import get_connection
from standardizers import normalize_date, clean_text
from classifier import SocialClassifier

def refine_bronze_to_silver():
    conn = get_connection()
    cur = conn.cursor()
    classifier = SocialClassifier() # Initialize BERT once
    
    # 1. INCREMENTAL LOAD
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

    valid_records = []
    
    for b_id, platform, topic, payload, ingested_at in rows:
        try:
            # 2. STANDARDIZATION & EXTRACTION
            if platform == 'youtube':
                raw_content = payload['snippet'].get('title', '')
                source_id = payload.get('id')
                author = payload['snippet'].get('channelTitle')
                views = int(payload['statistics'].get('viewCount', 0))
            else: # Bluesky
                raw_content = payload.get('text', '')
                source_id = payload.get('uri')
                author = payload['author'].get('handle')
                views = 0

            # Use our standardizer for cleaning
            content = clean_text(raw_content)
            norm_date = normalize_date(ingested_at, platform)

            # Quality Gate
            if not content or len(content) < 5:
                raise ValueError("Content too short after cleaning")

            valid_records.append({
                "b_id": b_id,
                "platform": platform,
                "source_id": source_id,
                "author": author,
                "content": content,
                "views": views,
                "raw_topic": topic,
                "ingested_at": norm_date
            })

        except Exception as e:
            cur.execute("""
                INSERT INTO silver_quarantine (bronze_id, platform, error_reason, raw_payload)
                VALUES (%s, %s, %s, %s)
            """, (b_id, platform, str(e), json.dumps(payload)))

    # 3. BATCH AI CLASSIFICATION
    if valid_records:
        texts = [r['content'] for r in valid_records]
        # One call to BERT for the whole batch
        predictions = classifier.predict_batch(texts)

        # 4. UPSERT INTO SILVER
        for i, record in enumerate(valid_records):
            predicted_cat = predictions[i]
            
            cur.execute("""
                INSERT INTO silver_social_posts 
                (platform, source_id, author, content, view_count, raw_category, predicted_category, ingested_at)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (source_id) DO UPDATE SET 
                    view_count = EXCLUDED.view_count,
                    predicted_category = EXCLUDED.predicted_category,
                    processed_at = CURRENT_TIMESTAMP;
            """, (
                record['platform'], record['source_id'], record['author'], 
                record['content'], record['views'], record['raw_topic'], 
                predicted_cat, record['ingested_at']
            ))

    conn.commit()
    cur.close()
    conn.close()
    logging.info(f"Refined {len(valid_records)} records, Quarantined {len(rows) - len(valid_records)}.")
