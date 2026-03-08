import streamlit as st

# 1. Global Page Configuration
# This carries over to all sub-pages defined in navigation
st.set_page_config(
    page_title="Ride The Trends | Anti-Slop Intelligence",
    page_icon="🌊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 2. Define Page Objects
# We point to the physical files in your /pages directory
trends = st.Page(
    "pages/1_📈_Trends.py", 
    title="Trend Intelligence", 
    icon=":material/trending_up:", 
    default=True
)

audit_hub = st.Page(
    "pages/2_🛡️_Audit_Hub.py", 
    title="Audit & Health", 
    icon=":material/shield_with_heart:"
)

semantic_briefing = st.Page(
    "pages/3_🎨_Semantic_Briefing.py", 
    title="Semantic Briefing", 
    icon=":material/psychology:"
)

# 3. Create Categorized Navigation
# Grouping by user intent: Analytics vs. Creative vs. Engineering
pg = st.navigation({
    "Market Intelligence": [trends, semantic_briefing],
    "Data Engineering": [audit_hub]
})

# 4. Global Sidebar Elements
# This content appears regardless of which page is currently active
with st.sidebar:
    st.title("Ride The Trends 🌊")
    st.markdown("---")
    st.overline("PIPELINE STATUS")
    st.success("Ingestion: Active")
    st.success("BERT Refiner: Online")
    
    st.markdown("---")
    st.info("""
    **Stack Overview:**
    - **Engine:** Pandas 3.0 (Arrow)
    - **Vector DB:** PostgreSQL + pgvector
    - **Models:** BERT (Local)
    """)

# 5. Execute Router
pg.run()
