import pandas as pd
import streamlit as st
from database import get_connection

@st.cache_data(ttl=600)  # Cache results for 10 minutes to save DB compute
def get_trend_metrics():
    """Fetches the time-series trend data from the Gold View."""
    conn = get_connection()
    query = "SELECT * FROM gold_trend_metrics"
    df = pd.read_sql(query, conn)
    conn.close()
    return df

@st.cache_data(ttl=300)
def get_audit_summary():
    """Calculates high-level health metrics for the Audit Hub."""
    conn = get_connection()
    cur = conn.cursor()
    
    # Get total processed vs quarantined
    cur.execute("SELECT COUNT(*) FROM silver_social_posts")
    silver_count = cur.fetchone()[0]
    cur.execute("SELECT COUNT(*) FROM silver_quarantine")
    fail_count = cur.fetchone()[0]
    
    total = silver_count + fail_count
    success_pct = round((silver_count / total * 100), 2) if total > 0 else 0
    
    conn.close()
    return {
        "success_pct": success_pct,
        "total_count": total,
        "fail_count": fail_count
    }

def get_quarantine_data():
    """Fetches the raw failures for deep-dive investigation."""
    conn = get_connection()
    query = "SELECT id, platform, error_reason, raw_payload, failed_at FROM silver_quarantine ORDER BY failed_at DESC"
    df = pd.read_sql(query, conn)
    conn.close()
    return df
