import streamlit as st
import pandas as pd

st.set_page_config(page_title="Audit Hub", page_icon="🛡️")

def show_audit():
    st.title("🛡️ Governance Audit Hub")
    st.write("Cross-platform validation metrics from the Silver Layer.")

    # 1. Platform Breakdown
    st.subheader("Platform Heat Map")
    # Mocking the join from int_validated_trends
    audit_data = pd.DataFrame({
        'Topic': ['AI Video', 'Sustainable Tech', 'Minimalism'],
        'YouTube_Hits': [12, 5, 1],
        'Bluesky_Hits': [8, 0, 15],
        'Confidence': ['HIGH', 'LOW', 'LOW']
    })
    
    st.dataframe(audit_data, use_container_width=True)

    # 2. Logic Visualizer
    st.divider()
    st.markdown("""
    ### 🧠 How it works
    * **HIGH**: Found on both YT and Bluesky.
    * **MEDIUM**: High velocity on a single platform (>10 hits).
    * **LOW**: Noise / Insufficient cross-platform signal.
    """)

if __name__ == "__main__":
    show_audit()
