from datetime import datetime, timezone

def normalize_date(date_str, platform):
    """Ensures all dates are UTC timestamps."""
    if not date_str:
        return datetime.now(timezone.utc)
    
    # Example: Handle different ISO formats or timestamps here
    try:
        dt = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
        return dt
    except:
        return datetime.now(timezone.utc)

def clean_text(text):
    """Basic text cleanup for BERT (removing extra whitespace, etc)."""
    if not text: return ""
    return " ".join(text.split())
