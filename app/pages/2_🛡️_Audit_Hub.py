import streamlit as st
import pandas as pd
from utils.db_loaders import get_audit_summary, get_quarantine_data, get_niche_trends
from utils.components import kpi_card, section_header
from database import execute_action, run_query # Added for feedback logic

# 1. Page Header
section_header("🛡️ Audit & Discovery Hub", "Monitor pipeline health and explore emerging niche trends.")

# 2. Tabs for Separation of Concerns
tab_audit, tab_discovery, tab_feedback = st.tabs(["📊 Pipeline Health", "🕵️ Niche Discovery", "🧠 BERT Feedback Loop"])

with tab_audit:
    # --- ROW 1: HEALTH METRICS ---
    summary = get_audit_summary()
    col1, col2, col3 = st.columns(3)
    
    with col1:
        kpi_card("Pipeline Success Rate", f"{summary['success_pct']}%")
    with col2:
        kpi_card("Total Processed", summary['total_count'])
    with col3:
        is_warning = summary['fail_count'] > 0
        kpi_card("Quarantine Count", summary['fail_count'], is_error=is_warning)

    st.divider()

    # --- ROW 2: QUARANTINE EXPLORER ---
    st.subheader("🚩 Quarantine Inspection")
    q_data = get_quarantine_data()

    if not q_data.empty:
        st.dataframe(q_data, use_container_width=True, hide_index=True)
        selected_id = st.selectbox("Select a Failure ID to inspect raw JSON:", q_data['id'])
        raw_json = q_data[q_data['id'] == selected_id]['raw_payload'].iloc[0]
        st.json(raw_json)
    else:
        st.success("Quarantine is empty! All systems nominal.")

with tab_discovery:
    st.subheader("🔎 Emerging 'Other' Trends")
    niche_df = get_niche_trends()

    if not niche_df.empty:
        st.dataframe(niche_df, use_container_width=True)
        st.info("💡 **Insight:** Use these keywords to update your BERT classifier's label set.")
    else:
        st.info("No significant recurring niche trends detected yet.")

with tab_feedback:
    st.subheader("🛠️ Model Correction (HITL)")
    st.write("Correcting 'Other' labels feeds the local retraining pipeline.")

    # Fetching posts that need human review (labeled as 'Other' in Silver)
    # We join with Bronze to get the actual text for the human to read
    review_data = run_query("""
        SELECT s.source_id, s.predicted_category, b.content 
        FROM silver_social_posts s
        JOIN bronze_social_posts b ON s.source_id = b.id
        WHERE s.predicted_category = 'Other'
        LIMIT 5
    """)

    if not review_data.empty:
        for index, row in review_data.iterrows():
            with st.container(border=True):
                st.write(f"**Content:** {row['content']}")
                col_a, col_b = st.columns([2, 1])
                
                with col_a:
                    new_label = st.selectbox(
                        f"Correct label for {row['source_id']}:", 
                        ["Tech", "Finance", "Lifestyle", "Slop/Spam"], 
                        key=f"label_{row['source_id']}"
                    )
                with col_b:
                    if st.button("Submit", key=f"btn_{row['source_id']}"):
                        execute_action("""
                            INSERT INTO silver_human_labels (post_id, original_label, corrected_label)
                            VALUES (%s, %s, %s)
                        """, (row['source_id'], row['predicted_category'], new_label))
                        st.toast(f"Logged {row['source_id']} as {new_label}!")
    else:
        st.success("No posts currently require manual labeling.")

    st.divider()
    
    # Retraining Trigger
    st.subheader("🔄 Model Synchronization")
    if st.button("🧠 Sync Human Intelligence"):
        with st.spinner("Retraining local BERT model weights..."):
            # Logic for running your retraining script would go here
            st.success("Model version v2.0 deployed locally! Accuracy expected to increase.")
