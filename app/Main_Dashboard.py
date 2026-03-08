import streamlit as st
from utils.db_loaders import get_trend_metrics

# 1. Page Config (Global settings)
st.set_page_config(page_title="Ride The Trends", page_icon="🚀", layout="wide")

# 2. Define Pages using the new Navigation API
dashboard = st.Page("pages/1_📈_Trends.py", title="Trend Intelligence", icon=":material/trending_up:", default=True)
audit_hub = st.Page("pages/2_🛡️_Audit_Hub.py", title="Audit Hub", icon=":material/security:")

# 3. Create Navigation Sidebar
pg = st.navigation({
    "Analytics": [dashboard],
    "Operations": [audit_hub]
})

# 4. Shared Sidebar Elements (Visible on ALL pages)
st.sidebar.title("Ride The Trends 2026")
st.sidebar.info("Agentic RAG Pipeline: YouTube + Bluesky")

# 5. Run the selected page
pg.run()
