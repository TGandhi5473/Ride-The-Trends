import streamlit as st
import pandas as pd
import json
from database import run_query, execute_action

# --- 1. PAGE CONFIG & HEADER ---
st.markdown("# 🛡️ Audit & Discovery Hub")
st.caption("Monitor pipeline health, inspect failures, and provide ground-truth labels for BERT retraining.")
st.divider()

# --- 2. TABS FOR SEPARATION OF CONCERNS ---
tab_health, tab_discovery, tab_feedback = st.tabs([
    "📊 Pipeline Health", 
    "🕵️ Niche Discovery", 
    "🧠 BERT Feedback Loop"
])

# --- TAB 1: PIPELINE HEALTH & QUARANTINE ---
with tab_health:
    # A. Global Metrics (Using Gold View)
    st.subheader("System Performance")
    health_df = run_query("SELECT * FROM gold_audit_summary;")
    
    if not health_df.empty:
        cols = st.columns(len(health_df))
        for i, row in health_df.iterrows():
            with cols[i]:
                st.metric(
                    label=f"{row['category']} ({row['platform']})",
                    value=row['total_records'],
                    delta=f"{row['avg_model_confidence']:.2%} Conf",
                    delta_color="normal"
                )
    
    st.markdown("---")
    
    # B. Quarantine Explorer
    st.subheader("🚩 Quarantine Inspection")
    st.write("Records that failed schema validation or BERT inference.")
    
    q_data = run_query("SELECT id, platform, error_reason, failed_at, raw_payload FROM silver_quarantine WHERE resolved = FALSE LIMIT 50;")

    if not q_data.empty:
        # Display table without the heavy JSON column first
        st.dataframe(q_data.drop(columns=['raw_payload']), use_container_width=True, hide_index=True)
        
        selected_id = st.selectbox("Select a Failure ID to inspect raw JSON:", q_data['id'])
        if selected_id:
            raw_json = q_data[q_data['id'] == selected_id]['raw_payload'].iloc[0]
            # Handle potential string/dict conversion for st.json
            payload_display = json.loads(raw_json) if isinstance(raw_json, str) else raw_json
            st.json(payload_display)
            
            if st.button("Mark as Resolved"):
                execute_action("UPDATE silver_quarantine SET resolved = TRUE WHERE id = %s", (selected_id,))
                st.toast(f"Error {selected_id} marked as resolved.")
                st.rerun()
    else:
        st.success("✅ Quarantine is empty! All systems nominal.")

# --- TAB 2: NICHE DISCOVERY (THE 'OTHER' BUCKET) ---
with tab_discovery:
    st.subheader("🔎 Emerging Niche Themes")
    st.write("Aggregated topics that the current BERT model labeled as 'OTHER'.")
    
    # Refreshing the Materialized View (Pro Tip: This could be moved to a button)
    if st.button("Refresh Discovery Engine"):
        with st.spinner("Refreshing Materialized View..."):
            execute_action("REFRESH MATERIALIZED VIEW CONCURRENTLY gold_niche_discovery;")
            st.success("Discovery view updated!")

    niche_df = run_query("SELECT raw_category, platform, mention_count, last_seen FROM gold_niche_discovery;")

    if not niche_df.empty:
        st.dataframe(niche_df, use_container_width=True, hide_index=True)
        st.info("💡 **Retraining Candidate:** If a 'raw_category' has high counts, add it to your BERT Label Map.")
    else:
        st.info("No significant recurring niches detected yet. Continue scraping to build density.")

# --- TAB 3: BERT FEEDBACK LOOP (HITL) ---
with tab_feedback:
    st.subheader("🛠️ Active Learning Queue")
    st.write("Human intervention for low-confidence AI predictions.")

    # Optimized Query: Pulls from Silver where human hasn't labeled yet
    review_queue = run_query("""
        SELECT s.source_id, s.content, s.predicted_category, s.platform
        FROM silver_social_posts s
        LEFT JOIN silver_human_labels h ON s.source_id = h.post_id
        WHERE s.predicted_category = 'OTHER' AND h.post_id IS NULL
        LIMIT 5
    """)

    if not review_queue.empty:
        for _, row in review_queue.iterrows():
            post_id = row['source_id']
            with st.container(border=True):
                st.caption(f"Platform: {row['platform'].upper()} | ID: {post_id}")
                st.write(f"**Content:** {row['content']}")
                
                col_sel, col_btn = st.columns([3, 1])
                with col_sel:
                    choice = st.selectbox(
                        "Correct Category:",
                        ["Tech", "Finance", "Gaming", "Politics", "Slop/Spam"],
                        key=f"hitl_{post_id}"
                    )
                with col_btn:
                    st.write(" ") # Spacer
                    if st.button("Submit", key=f"sub_{post_id}", use_container_width=True):
                        execute_action("""
                            INSERT INTO silver_human_labels (post_id, original_label, corrected_label)
                            VALUES (%s, %s, %s)
                            ON CONFLICT (post_id) DO UPDATE SET corrected_label = EXCLUDED.corrected_label
                        """, (post_id, row['predicted_category'], choice))
                        st.toast("Label Saved!")
                        st.rerun()
    else:
        st.success("✨ All 'OTHER' posts have been reviewed. Model is aligned with Human Intelligence.")

    st.divider()
    
    # Model Synchronization Section
    st.subheader("🔄 Model Deployment")
    col_v, col_sync = st.columns([2, 1])
    with col_v:
        st.write("**Current Version:** `refined_bert_v2.0` (Local)")
    with col_sync:
        if st.button("Sync Intelligence", use_container_width=True):
            st.warning("Triggering local retraining script... (Simulated)")
