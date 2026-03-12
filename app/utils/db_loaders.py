import pandas as pd
import streamlit as st
from sqlalchemy import create_engine, text
from database import get_engine # We'll update database.py to provide this

# NOTE: In Pandas 3.0+, pyarrow backend is highly efficient for Neon's JSONB
# We use st.cache_resource for the engine to persist it across app runs

@st.cache_data(ttl=600)
def get_trend_metrics():
    """Fetches Gold Layer trends using SQLAlchemy + Arrow."""
    engine = get_engine()
    query = "SELECT * FROM gold_trend_metrics"
    
    # SQLAlchemy handles the connection checkout/checkin automatically
    with engine.connect() as conn:
        df = pd.read_sql(text(query), conn, dtype_backend="pyarrow")
    
    if not df.empty and 'trend_date' in df.columns:
        df['trend_date'] = pd.to_datetime(df['trend_date'])
    return df

@st.cache_data(ttl=300)
def get_audit_summary():
    """Aggregates pipeline health metrics using pooled execution."""
    engine = get_engine()
    
    with engine.connect() as conn:
        # executing raw SQL via SQLAlchemy text() for safety
        silver_count = conn.execute(text("SELECT COUNT(*) FROM silver_social_posts")).scalar()
        fail_count = conn.execute(text("SELECT COUNT(*) FROM silver_quarantine")).scalar()
        
        total = silver_count + fail_count
        success_pct = round((silver_count / total * 100), 2) if total > 0 else 0
        
        return {
            "success_pct": success_pct,
            "total_count": total,
            "fail_count": fail_count
        }

def get_quarantine_data():
    """Retrieves failures for Page 2 Audit inspection."""
    engine = get_engine()
    query = """
        SELECT id, platform, error_reason, raw_payload, failed_at 
        FROM silver_quarantine 
        ORDER BY failed_at DESC
    """
    with engine.connect() as conn:
        return pd.read_sql(text(query), conn, dtype_backend="pyarrow")

@st.cache_data(ttl=3600)
def get_niche_trends():
    """Fetches recurring themes from the materialized view."""
    engine = get_engine()
    query = "SELECT raw_category, platform, mention_count, last_seen FROM gold_niche_discovery"
    with engine.connect() as conn:
        return pd.read_sql(text(query), conn, dtype_backend="pyarrow")
