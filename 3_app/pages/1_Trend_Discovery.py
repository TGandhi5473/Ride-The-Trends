import streamlit as st
import pandas as pd
from core import fetch_gold_prompts  # Centralized logic we built earlier
from utils.llm_engine import generate_creative_assets

st.set_page_config(page_title="Trend Discovery", page_icon="🎯", layout="wide")

def show_discovery():
    st.title("🎯 Validated Trend Discovery")
    st.markdown("""
        This view pulls from the **Gold Layer** (analytics.fct_creative_prompts). 
        These trends have been cross-validated via dbt and are ready for creative enrichment.
    """)

    # 1. Fetch from Gold Layer (Actual Database Call)
    with st.spinner("Fetching validated trends from Neon..."):
        trends_data = fetch_gold_prompts()

    if not trends_data:
        st.warning("No validated trends found in the Gold layer. Run your dbt pipeline to populate this view.")
        return

    # Convert to DataFrame for easy filtering/sorting if needed
    df = pd.DataFrame(trends_data)

    # UI Layout: Iterating through validated trends
    for _, trend in df.iterrows():
        # Using the unique topic + platform combination for the button key
        unique_key = f"{trend['target_topic']}_{trend.get('platform', 'cross-platform')}"
        
        with st.container(border=True):
            col1, col2 = st.columns([3, 1])
            
            with col1:
                st.subheader(f"Topic: {trend['target_topic']}")
                
                # Metadata Badges
                c1, c2, c3 = st.columns(3)
                c1.metric("Confidence", trend['confidence_level'])
                c2.metric("Source", trend.get('platform', 'Multi').title())
                if 'heat_score' in trend:
                    c3.metric("Heat Score", f"{trend['heat_score']}/100")
                
                with st.expander("View Raw Prompt Template"):
                    st.code(trend['llm_prompt_template'], language="markdown")
            
            with col2:
                st.write("### Actions")
                if st.button("✨ Generate Hooks", key=unique_key):
                    with st.spinner("Local LLM (Ollama) is orchestrating creative..."):
                        # Last-mile enrichment using local inference
                        enriched_content = generate_creative_assets(trend['llm_prompt_template'])
                        
                        if enriched_content:
                            st.toast("Hooks Generated!", icon="✅")
                            st.markdown("---")
                            st.markdown("**Creative Output:**")
                            st.write(enriched_content)
                        else:
                            st.error("Failed to generate hooks. Is Ollama running?")

if __name__ == "__main__":
    show_discovery()
