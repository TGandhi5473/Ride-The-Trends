import streamlit as st
import pandas as pd
from sqlalchemy import text
from core import get_neon_engine, Config

st.set_page_config(page_title="Audit Hub", page_icon="🛡️", layout="wide")

def show_audit():
    st.title("🛡️ Governance & Pipeline Audit")
    
    # --- SECTION 1: PIPELINE HEALTH (The "Quota Guard" View) ---
    st.subheader("🚀 Ingestion Health")
    col1, col2, col3 = st.columns(3)
    
    # Real-time Quota Monitoring (Mocking the consumption logic)
    # In a full prod version, you'd store 'units_consumed' in a DB table
    col1.metric("YouTube Quota", "9,100 / 10,000", "-900 Left", delta_color="inverse")
    col2.metric("Bluesky Status", "Active", "Normal")
    col3.metric("Database", "Neon Serverless", "Connected")

    # --- SECTION 2: PLATFORM HEAT MAP (Silver Layer) ---
    st.divider()
    st.subheader("📊 Cross-Platform Validation")
    st.write("Aggregated hits from the Silver Layer (int_validated_trends).")

    engine = get_neon_engine()
    
    # Query to get platform breakdown (Requires your dbt Silver layer to be run)
    query = """
        SELECT 
            target_topic as "Topic",
            COUNT(*) FILTER (WHERE platform = 'youtube') as "YouTube Hits",
            COUNT(*) FILTER (WHERE platform = 'bluesky') as "Bluesky Hits",
            CASE 
                WHEN COUNT(DISTINCT platform) > 1 THEN 'HIGH'
                WHEN COUNT(*) > 10 THEN 'MEDIUM'
                ELSE 'LOW'
            END as "Confidence"
        FROM bronze.raw_ingestion
        GROUP BY 1
        ORDER BY "Confidence" DESC
    """
    
    try:
        with engine.connect() as conn:
            audit_df = pd.read_sql(text(query), conn)
            st.dataframe(audit_df, use_container_width=True, hide_index=True)
    except Exception as e:
        st.warning("Could not fetch real-time metrics. Displaying structural documentation instead.")
        # Fallback to your mock structure if DB isn't populated yet
        st.info("💡 Run your first ingestion worker to see live data here.")

    # --- SECTION 3: LOGIC VISUALIZER ---
    st.divider()
    with st.expander("🧠 Decision Logic Documentation"):
        st.markdown("""
        ### Validation Tiers
        * **🟢 HIGH (Cross-Verified)**: The signal appears on both **YouTube** (Visual/Long-form) and **Bluesky** (Textual/Real-time). This suggests a cultural shift rather than a single-platform algorithm fluke.
        * **🟡 MEDIUM (High Velocity)**: Found on only one platform but has extreme engagement (>10 hits in a 24hr window).
        * **🔴 LOW (Noise)**: Single hits or isolated posts. Filtered out of the Gold Layer.
        """)

if __name__ == "__main__":
    show_audit()
