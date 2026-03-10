import json
import logging
import numpy as np
from psycopg2.extras import execute_values
from database import get_connection, release_connection
from standardizers import normalize_date, clean_text
from silver.classifier import SocialClassifier

def refine_bronze_to_silver():
    conn = get_connection()
    cur = conn.cursor()
    classifier = SocialClassifier() 
    
    # 1. INCREMENTAL LOAD (Optimized Join)
    # Joining on the source_id column we added to Bronze for performance
    query = """
        SELECT b.id, b.platform, b.target_topic, b.payload, b.ingested_at, b.source_id
        FROM bronze_social_feeds b
        LEFT JOIN silver_social_posts s ON b.source_id = s.source_id
        LEFT JOIN silver_quarantine q ON b.id = q.bronze_id
        WHERE s.source_id IS NULL AND q.bronze_id IS NULL
        LIMIT 500;
    """
    cur.execute(query)
    rows = cur.fetchall()

    if not rows:
        logging.info("✨ No new records to refine.")
        release_connection(conn)
        return

    valid_records = []
    
    for b_id, platform, topic, payload, ingested_at, b_source_id in rows:
        try:
            # 2. PLATFORM-SPECIFIC EXTRACTION
            if platform == 'youtube':
                raw_content = payload.get('snippet', {}).get('title', '')
                author = payload.get('snippet', {}).get('channelTitle')
                views = int(payload.get('statistics', {}).get('viewCount', 0))
            else: # Bluesky
                raw_content = payload.get('text', '')
                author = payload.get('author', {}).get('handle')
                views = 0

            content = clean_text(raw_content)
            
            # Quality Gate
            if not content or len(content) < 5:
                raise ValueError("Content too short after cleaning")

            valid_records.append({
                "source_id": b_source_id,
                "platform": platform,
                "author": author,
                "content": content,
                "views": views,
                "raw_topic": topic,
                "ingested_at": normalize_date(ingested_at)
            })

        except Exception as e:
            cur.execute("""
                INSERT INTO silver_quarantine (bronze_id, platform, error_reason, raw_payload)
                VALUES (%s, %s, %s, %s)
            """, (b_id, platform, str(e), json.dumps(payload)))

    # 3. BATCH AI PROCESSING
    if valid_records:
        texts = [r['content'] for r in valid_records]
        labels, confs, embeddings = classifier.predict_batch_with_vectors(texts)

        # Prepare data for Bulk Upsert
        upsert_data = []
        for i, r in enumerate(valid_records):
            predicted_cat = labels[i] if confs[i] >= 0.45 else "OTHER"
            vector = embeddings[i].tolist() if isinstance(embeddings[i], np.ndarray) else embeddings[i]
            
            upsert_data.append((
                r['platform'], r['source_id'], r['author'], r['content'], r['views'],
                r['raw_topic'], predicted_cat, confs[i], r['ingested_at'], vector
            ))

        # 4. BULK UPSERT (The 2026 Pro Move)
        upsert_query = """
            INSERT INTO silver_social_posts 
            (platform, source_id, author, content, view_count, raw_category, 
             predicted_category, confidence, ingested_at, embedding)
            VALUES %s
            ON CONFLICT (source_id) DO UPDATE SET 
                view_count = EXCLUDED.view_count,
                predicted_category = EXCLUDED.predicted_category,
                confidence = EXCLUDED.confidence,
                embedding = EXCLUDED.embedding,
                processed_at = CURRENT_TIMESTAMP;
        """
        execute_values(cur, upsert_query, upsert_data)

    conn.commit()
    cur.close()
    release_connection(conn)
    logging.info(f"✅ Refined {len(valid_records)} records using Bulk Upsert.")
