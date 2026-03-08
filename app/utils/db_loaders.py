import pandas as pd
import streamlit as st
from database import get_connection

# Set the global Pandas option to ensure Copy-on-Write is strictly enforced
# This is the default in 3.0, but setting it explicitly is best practice for 2026.
pd.options.mode.copy_on_write = True

@st.cache_data(ttl=600)
def get_trend_metrics():
    """
    Fetches the time-series trend data from the Gold View.
    Uses 'pyarrow' as the backend for 5-10x faster string operations.
    """
    conn = get_connection()
    query = "SELECT * FROM gold_trend_metrics"
    
    # We specify dtype_backend="pyarrow" to utilize Pandas 3.0's speed boost
    try:
        df = pd.read_sql(query, conn, dtype_backend="pyarrow")
    finally:
        conn.close()
    
    # Ensure date columns are actual datetime objects for Plotly charts
    if not df.empty and 'trend_date' in df.columns:
        df['trend_date'] = pd.to_datetime(df['trend_date'])
        
    return df

@st.cache_data(ttl=300)
def get_audit_summary():
    """
    Calculates high-level health metrics for the Audit Hub UI.
    Optimized for Pandas 3.0 performance.
    """
    conn = get_connection()
    cur = conn.cursor()
    
    try:
        # Get counts from Silver and Quarantine tables
        cur.execute("SELECT COUNT(*) FROM silver_social_posts")
        silver_count = cur.fetchone()[0]
        
        cur.execute("SELECT COUNT(*) FROM silver_quarantine")
        fail_count = cur.fetchone()[0]
        
        total = silver_count + fail_count
        success_pct = round((silver_count / total * 100), 2) if total > 0 else 0
        
        return {
            "success_pct": success_pct,
            "total_count": total,
            "fail_count": fail_count,
            "silver_total": silver_count
        }
    finally:
        cur.close()
        conn.close()

def get_quarantine_data():
    """
    Fetches the raw failures for deep-dive investigation in the Audit Hub.
    Uses Arrow backend to handle the large JSONB strings in raw_payload efficiently.
    """
    conn = get_connection()
    query = """
        SELECT id, platform, error_reason, raw_payload, failed_at 
        FROM silver_quarantine 
        ORDER BY failed_at DESC
    """
    try:
        # Arrow backend is essential here because raw_payload is a large string/JSONB
        df = pd.read_sql(query, conn, dtype_backend="pyarrow")
    finally:
        conn.close()
    
    return df
