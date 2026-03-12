import pandas as pd
import streamlit as st
from sqlalchemy import text
from database import get_engine, run_query

# NOTE: In Pandas 3.0.1+, Copy-on-Write is default.
# pyarrow backend is utilized for high-speed string operations in Neon.

@st.cache_data(ttl=600)
def get_trend_metrics():
    """Fetches Gold Layer trends using SQLAlchemy + Arrow backend."""
    # Using the centralized run_query from database.py for 6x faster string ops
    query = "SELECT * FROM gold_trend_metrics"
    df = run_query(query)
    
    if not df.empty and 'trend_date' in df.columns:
        df['trend_date'] = pd.to_datetime(df['trend_date'])
    return df

@st.cache_data(ttl=300)
def get_audit_summary():
    """Aggregates pipeline health metrics using SQLAlchemy connection context."""
    engine = get_engine()
    
    with engine.connect() as conn:
        # executing raw SQL via SQLAlchemy text() for Pandas 3.0 compatibility
        silver_count = conn.execute(text("SELECT COUNT(*) FROM silver_social_posts")).scalar()
        fail_count = conn.execute(text("SELECT COUNT(*) FROM silver_quarantine")).scalar()
        
        total = (silver_count or 0) + (fail_count or 0)
        success_pct = round((silver_count / total * 100), 2) if total > 0 else 0
        
        return {
            "success_pct": success_pct,
            "total_count": total,
            "fail_count": fail_count
        }

def get_quarantine_data():
    """Retrieves failures for Page 2 Audit inspection with Arrow optimization."""
    query = """
        SELECT id, platform, error_reason, raw_payload, failed_at 
        FROM silver_quarantine 
        ORDER BY failed_at DESC
    """
    return run_query(query)

@st.cache_data(ttl=3600)
def get_niche_trends():
    """
    Fetches recurring themes from the 'Other' exploration materialized view.
    Uses cached resource engine for stable long-polling.
    """
    query = "SELECT raw_category, platform, mention_count, last_seen FROM gold_niche_discovery"
    return run_query(query)
