import streamlit as st
import pandas as pd
from utils.db_loaders import get_audit_summary, get_quarantine_data, get_niche_trends
from utils.components import kpi_card, section_header

# 1. Page Header
section_header("🛡️ Audit & Discovery Hub", "Monitor pipeline health and explore emerging niche trends.")

# 2. Tabs for Separation of Concerns
tab_audit, tab_discovery = st.tabs(["📊 Pipeline Health", "🕵️ Niche Discovery"])

with tab_audit:
    # --- ROW 1: HEALTH METRICS ---
    summary = get_audit_summary()
    col1, col2, col3 = st.columns(3)
    
    with col1:
        kpi_card("Pipeline Success Rate", f"{summary['success_pct']}%")
    with col2:
        kpi_card("Total Processed", summary['total_count'])
    with col3:
        # Use red border if quarantine is high
        is_warning = summary['fail_count'] > 0
        kpi_card("Quarantine Count", summary['fail_count'], is_error=is_warning)

    st.divider()

    # --- ROW 2: QUARANTINE EXPLORER ---
    st.subheader("🚩 Quarantine Inspection")
    st.write("Data diverted here failed validation or classification.")
    
    q_data = get_quarantine_data()

    if not q_data.empty:
        # We use the Pandas 3.0 Arrow-backed dataframe here
        st.dataframe(q_data, use_container_width=True, hide_index=True)
        
        # Inspection Logic
        selected_id = st.selectbox("Select a Failure ID to inspect raw JSON:", q_data['id'])
        raw_json = q_data[q_data['id'] == selected_id]['raw_payload'].iloc[0]
        st.json(raw_json)
    else:
        st.success("Quarantine is empty! All systems nominal.")

with tab_discovery:
    st.subheader("🔎 Emerging 'Other' Trends")
    st.write("These clusters represent recurring topics that BERT labeled as 'Other'.")

    # This pulls from the Materialized View we created in the Gold Schema
    niche_df = get_niche_trends()

    if not niche_df.empty:
        st.dataframe(niche_df, use_container_width=True)
        
        # Semantic Discovery Feature
        st.info("💡 **Insight:** High mention counts in 'Other' often signal a shifting subculture. "
                "You can use these keywords to update your BERT classifier's label set.")
    else:
        st.info("No significant recurring niche trends detected in the 'Other' category yet.")
