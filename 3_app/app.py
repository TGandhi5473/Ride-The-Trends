import streamlit as st
import pandas as pd
from core.database import get_neon_engine # Assuming this exists in your core folder

st.set_page_config(
    page_title="Ride-The-Trends | Dashboard",
    page_icon="🌊",
    layout="wide"
)

def main():
    st.title("🌊 Ride-The-Trends")
    st.subheader("Creative Intelligence Engine")
    
    st.markdown("""
    Welcome to the Cockpit. This system uses **Deterministic Logic** (SQL) 
    to validate trends before allowing **Generative AI** to touch them.
    """)

    # Quick Stats Overview
    try:
        engine = get_neon_engine()
        with engine.connect() as conn:
            # Check how many High-Confidence trends we have
            count_query = "SELECT count(*) FROM analytics.fct_creative_prompts WHERE confidence_level = 'HIGH'"
            high_conf_count = pd.read_sql(count_query, conn).iloc[0,0]
            
            col1, col2, col3 = st.columns(3)
            col1.metric("High Confidence Trends", high_conf_count)
            col2.metric("System Status", "Live", delta="Healthy")
            col3.metric("Medallion Layer", "Gold (Intelligence)")
            
    except Exception as e:
        st.error(f"Failed to connect to Neon: {e}")

if __name__ == "__main__":
    main()
