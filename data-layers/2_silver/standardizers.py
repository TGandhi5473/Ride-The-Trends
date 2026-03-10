import re
from datetime import datetime, timezone
from dateutil import parser # Standard for robust date handling

def normalize_date(date_str):
    """
    Ensures all dates are UTC. 
    Handles YouTube (ISO 8601) and Bluesky (ISO 8601 with offset) seamlessly.
    """
    if not date_str:
        return datetime.now(timezone.utc)
    
    try:
        # dateutil.parser handles 'Z', '+00:00', and microsecond differences automatically
        dt = parser.isoparse(str(date_str))
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        return dt.astimezone(timezone.utc)
    except Exception:
        # Fallback to current time for the 'ingested_at' lineage
        return datetime.now(timezone.utc)

def clean_text(text):
    """
    Advanced cleanup for BERT. 
    Removes URLs and handles social media noise to prevent 'Slop' hallucinations.
    """
    if not text: 
        return ""
    
    # 1. Remove URLs (BERT doesn't need to 'read' a link)
    text = re.sub(r'http\S+|www\S+|https\S+', '', text, flags=re.MULTILINE)
    
    # 2. Remove extra whitespace/newlines
    text = " ".join(text.split())
    
    # 3. Optional: Remove @mentions if they aren't useful for trend analysis
    # text = re.sub(r'@\w+', '', text)
    
    return text.strip()
