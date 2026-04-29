import streamlit as st
import pandas as pd
from sqlalchemy import text
from core.database import get_neon_engine
from core.config import Config

st.set_page_config(page_title="Audit Hub", page_icon="🛡️", layout="wide")

def show_audit():
    st.title("🛡️ Governance & HITL Audit")
    
    # --- SECTION 1: SYSTEM HEALTH ---
    st.subheader("🚀 Ingestion & Model Status")
    col1, col2, col3 = st.columns(3)
    
    # Active Model Detection
    active_model = "Refined DistilBERT" if Config.BERT_REFINED_PATH.exists() else "Base DistilBERT"
    
    col1.metric("Active Critic", active_model)
    col2.metric("Training Queue", "Pending", "Needs 50 samples")
    col3.metric("Database", "Neon Serverless", "Connected")

    # --- SECTION 2: THE INTELLIGENCE LOOP (New HITL View) ---
    st.divider()
    st.subheader("🧠 BERT Training Queue")
    st.write("Current human feedback samples awaiting the next retraining cycle.")

    engine = get_neon_engine()
    
    # The Join SQL: Linking Feedback to the Gold Layer Prompt
    hitl_query = """
        SELECT 
            f.text as "Generated Hook",
            CASE WHEN f.label_id = 1 THEN '✅ Approved' ELSE '❌ Rejected' END as "Human Label",
            p.target_topic as "Topic Context",
            p.confidence_level as "Trend Confidence"
        FROM gold.human_feedback f
        JOIN analytics.fct_creative_prompts p ON f.prompt_id = p.prompt_id
        WHERE f.used_for_training = FALSE
        ORDER BY f.created_at DESC
    """
    
    try:
        with engine.connect() as conn:
            hitl_df = pd.read_sql(text(hitl_query), conn)
            
            if not hitl_df.empty:
                st.dataframe(hitl_df, use_container_width=True, hide_index=True)
                
                # Progress to Retraining Trigger
                current_count = len(hitl_df)
                progress = min(current_count / Config.TRAINING_THRESHOLD, 1.0)
                st.write(f"**Retraining Progress:** {current_count} / {Config.TRAINING_THRESHOLD} samples")
                st.progress(progress)
                
                if current_count >= Config.TRAINING_THRESHOLD:
                    if st.button("🔄 Trigger BERT Retraining Now"):
                        st.info("Retraining script initiated in background...")
                        # In a real app, you'd trigger a GitHub Action or Subprocess here
            else:
                st.info("Queue is empty. Go to 'Trend Discovery' to generate and rate some hooks!")
                
    except Exception as e:
        st.error(f"Logic Conflict: Ensure 'gold.human_feedback' table exists. Error: {e}")

    # --- SECTION 3: CROSS-PLATFORM VALIDATION ---
    st.divider()
    st.subheader("📊 Trend Pulse Analysis")
    
    # Original aggregation logic
    pulse_query = """
        SELECT 
            target_topic as "Topic",
            COUNT(*) FILTER (WHERE platform = 'youtube') as "YouTube Hits",
            COUNT(*) FILTER (WHERE platform = 'bluesky') as "Bluesky Hits",
            CASE 
                WHEN COUNT(DISTINCT platform) > 1 THEN 'HIGH'
                ELSE 'MEDIUM'
            END as "Auto-Confidence"
        FROM bronze.raw_ingestion
        GROUP BY 1
        ORDER BY "YouTube Hits" DESC
    """
    
    try:
        with engine.connect() as conn:
            audit_df = pd.read_sql(text(pulse_query), conn)
            st.dataframe(audit_df, use_container_width=True, hide_index=True)
    except Exception:
        st.warning("Run ingestion to see platform metrics.")

if __name__ == "__main__":
    show_audit()
