import pandas as pd
import streamlit as st
from database import get_connection

# NOTE: In Pandas 3.0.1+, Copy-on-Write is default. 
# Explicit setting is removed for cleaner production code.

@st.cache_data(ttl=600)
def get_trend_metrics():
    """Fetches Gold Layer trends using Arrow-backed memory efficiency."""
    conn = get_connection()
    query = "SELECT * FROM gold_trend_metrics"
    try:
        df = pd.read_sql(query, conn, dtype_backend="pyarrow")
    finally:
        conn.close()
    
    if not df.empty and 'trend_date' in df.columns:
        df['trend_date'] = pd.to_datetime(df['trend_date'])
    return df

@st.cache_data(ttl=300)
def get_audit_summary():
    """Aggregates pipeline health metrics for the Audit Hub."""
    conn = get_connection()
    cur = conn.cursor()
    try:
        cur.execute("SELECT COUNT(*) FROM silver_social_posts")
        silver_count = cur.fetchone()[0]
        cur.execute("SELECT COUNT(*) FROM silver_quarantine")
        fail_count = cur.fetchone()[0]
        
        total = silver_count + fail_count
        success_pct = round((silver_count / total * 100), 2) if total > 0 else 0
        
        return {
            "success_pct": success_pct,
            "total_count": total,
            "fail_count": fail_count
        }
    finally:
        cur.close()
        conn.close()

def get_quarantine_data():
    """Retrieves failures for Page 2 Audit inspection."""
    conn = get_connection()
    query = "SELECT id, platform, error_reason, raw_payload, failed_at FROM silver_quarantine ORDER BY failed_at DESC"
    try:
        return pd.read_sql(query, conn, dtype_backend="pyarrow")
    finally:
        conn.close()

@st.cache_data(ttl=3600)
def get_niche_trends():
    """
    NEW: Fetches recurring themes from the 'Other' exploration materialized view.
    Used for the Niche Discovery tab in the Audit Hub.
    """
    conn = get_connection()
    # Pulls from the Discovery View we added to the Gold Schema
    query = "SELECT raw_category, platform, mention_count, last_seen FROM gold_niche_discovery"
    try:
        return pd.read_sql(query, conn, dtype_backend="pyarrow")
    finally:
        conn.close()
