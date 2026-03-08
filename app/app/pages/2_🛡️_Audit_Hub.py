import streamlit as st
from utils.db_loaders import get_audit_summary, get_quarantine_data

st.title("🛡️ Pipeline Audit & Health")
st.write("Monitor BERT classification accuracy and data ingestion failures.")

# --- ROW 1: HEALTH METRICS ---
col1, col2, col3 = st.columns(3)
summary = get_audit_summary() # Pulls from your gold_audit_summary view

col1.metric("Pipeline Success Rate", f"{summary['success_pct']}%")
col2.metric("Total Processed", summary['total_count'])
col3.metric("Quarantine Count", summary['fail_count'], delta_color="inverse")

# --- ROW 2: QUARANTINE EXPLORER ---
st.subheader("🚩 Quarantine Inspection")
q_data = get_quarantine_data()

if not q_data.empty:
    st.dataframe(q_data, use_container_width=True)
    
    # Feature: Selection to see raw JSON payload
    selected_row = st.selectbox("Select a failure to inspect raw payload:", q_data.index)
    st.json(q_data.loc[selected_row, 'raw_payload'])
else:
    st.success("Quarantine is empty! All systems nominal.")
