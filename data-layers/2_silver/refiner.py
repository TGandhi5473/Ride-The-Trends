import json
import logging
import numpy as np
from database import get_connection
from standardizers import normalize_date, clean_text
from silver.classifier import SocialClassifier

def refine_bronze_to_silver():
    conn = get_connection()
    cur = conn.cursor()
    classifier = SocialClassifier() # Now checks for local refined weights automatically
    
    # 1. INCREMENTAL LOAD
    # Joins check if record is already in Silver or Quarantine
    query = """
        SELECT b.id, b.platform, b.target_topic, b.payload, b.ingested_at 
        FROM bronze_social_feeds b
        LEFT JOIN silver_social_posts s ON b.payload->>'id' = s.source_id OR b.payload->>'uri' = s.source_id
        LEFT JOIN silver_quarantine q ON b.id = q.bronze_id
        WHERE s.source_id IS NULL AND q.bronze_id IS NULL
        LIMIT 500;
    """
    cur.execute(query)
    rows = cur.fetchall()

    if not rows:
        logging.info("✨ No new records to refine.")
        return

    valid_records = []
    
    for b_id, platform, topic, payload, ingested_at in rows:
        try:
            # 2. PLATFORM-SPECIFIC EXTRACTION
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

            content = clean_text(raw_content)
            norm_date = normalize_date(ingested_at, platform)

            # Quality Gate: "Anti-Slop"
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

    # 3. BATCH AI PROCESSING (Classification + Confidence + Embeddings)
    if valid_records:
        texts = [r['content'] for r in valid_records]
        
        # New classifier returns three outputs: labels, scores, and vectors
        labels, confidences, embeddings = classifier.predict_batch_with_vectors(texts)

        # 4. UPSERT INTO SILVER
        for i, record in enumerate(valid_records):
            # Apply the 'OTHER' threshold for the Niche Discovery tab
            # If confidence < 0.45, we label as OTHER to trigger audit review
            predicted_cat = labels[i] if confidences[i] >= 0.45 else "OTHER"
            
            # Convert numpy vector to list for pgvector
            vector = embeddings[i].tolist() if isinstance(embeddings[i], np.ndarray) else embeddings[i]
            
            cur.execute("""
                INSERT INTO silver_social_posts 
                (platform, source_id, author, content, view_count, raw_category, 
                 predicted_category, confidence, ingested_at, embedding)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (source_id) DO UPDATE SET 
                    view_count = EXCLUDED.view_count,
                    predicted_category = EXCLUDED.predicted_category,
                    confidence = EXCLUDED.confidence,
                    embedding = EXCLUDED.embedding,
                    processed_at = CURRENT_TIMESTAMP;
            """, (
                record['platform'], record['source_id'], record['author'], 
                record['content'], record['views'], record['raw_topic'], 
                predicted_cat, confidences[i], record['ingested_at'], vector
            ))

    conn.commit()
    cur.close()
    conn.close()
    logging.info(f"✅ Refined {len(valid_records)} records. HITL Threshold applied.")
