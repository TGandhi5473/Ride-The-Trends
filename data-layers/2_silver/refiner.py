import pandas as pd
from database import get_connection # shared utility

def refine_bronze_to_silver():
    conn = get_connection()
    
    # 1. Read 'Unprocessed' Bronze data
    # (In a real pro-pipeline, you'd track which IDs you've already processed)
    df_raw = pd.read_sql("SELECT * FROM bronze_social_feeds", conn)

    # 2. Flattening Logic
    refined_data = []
    for _, row in df_raw.iterrows():
        payload = row['payload']
        
        if row['platform'] == 'youtube':
            refined_data.append({
                "source_id": payload.get('id'),
                "author": payload['snippet'].get('channelTitle'),
                "content": payload['snippet'].get('title'),
                "raw_category": row['target_topic'],
                "platform": "youtube"
            })
        elif row['platform'] == 'bluesky':
            refined_data.append({
                "source_id": payload.get('uri'),
                "author": payload['author'].get('handle'),
                "content": payload.get('text'),
                "raw_category": row['target_topic'],
                "platform": "bluesky"
            })

    # 3. Apply BERT (Placeholder for your model)
    # predicted_cat = bert_model.predict(content)
    
    # 4. Save to Silver using a MERGE (UPSERT)
    # This prevents duplicates!
