import streamlit as st
import pandas as pd
# These will be built in the next step
# from core.database import get_neon_engine 
# from utils.llm_engine import generate_creative_assets

st.set_page_config(page_title="Trend Discovery", page_icon="🎯")

def show_discovery():
    st.title("🎯 Validated Trend Discovery")
    st.info("Showing trends with MEDIUM to HIGH confidence only.")

    # 1. Fetch from Gold Layer
    # Logic: We'll eventually wrap this in a try-except with the engine
    # query = "SELECT * FROM analytics.fct_creative_prompts ORDER BY validated_at DESC"
    
    # Mock data for UI structure
    mock_trends = [
        {"target_topic": "AI Video Editing", "confidence_level": "HIGH", "llm_prompt_template": "Act as creative director..."},
        {"target_topic": "Sustainable Tech", "confidence_level": "MEDIUM", "llm_prompt_template": "Act as creative director..."}
    ]

    for trend in mock_trends:
        with st.container(border=True):
            col1, col2 = st.columns([3, 1])
            
            with col1:
                st.subheader(trend['target_topic'])
                st.caption(f"Confidence: {trend['confidence_level']}")
            
            with col2:
                if st.button("✨ Generate Hooks", key=trend['target_topic']):
                    with st.spinner("LLM is orchestrating creative..."):
                        # This is where the last-mile enrichment happens
                        # result = generate_creative_assets(trend['llm_prompt_template'])
                        st.success("Hooks Generated!")
                        st.write("**Hook 1:** Stop scrolling. This AI tool just changed editing forever.")

if __name__ == "__main__":
    show_discovery()
