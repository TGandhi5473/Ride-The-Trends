import pandas as pd
from database import run_query

def get_training_data():
    """Fetches human-corrected labels and pairs them with original text."""
    query = """
        SELECT b.content as text, h.corrected_label as label
        FROM silver_human_labels h
        JOIN bronze_social_posts b ON h.post_id = b.source_id
    """
    df = run_query(query)
    
    # Map your text labels to numeric IDs for the model
    label_map = {"Tech": 0, "Finance": 1, "Lifestyle": 2, "Slop/Spam": 3}
    df['label'] = df['label'].map(label_map)
    
    return df.dropna()
