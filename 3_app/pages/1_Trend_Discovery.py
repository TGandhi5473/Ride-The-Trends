import streamlit as st
import pandas as pd
from core.database import get_neon_engine
from utils.llm_engine import generate_creative_assets, get_critic_score

st.set_page_config(page_title="Trend Discovery", page_icon="🎯", layout="wide")

def fetch_gold_prompts():
    """Helper to pull validated data from the Gold Layer."""
    engine = get_neon_engine()
    # Pulling from the specialized Marts view
    query = "SELECT * FROM analytics.fct_creative_prompts ORDER BY validated_at DESC"
    try:
        return pd.read_sql(query, engine)
    except Exception as e:
        st.error(f"DB Error: {e}")
        return pd.DataFrame()

def show_discovery():
    st.title("🎯 Validated Trend Discovery")
    st.markdown("---")

    df = fetch_gold_prompts()

    if df.empty:
        st.warning("No validated trends found. Check your dbt/Ingestion pipelines.")
        return

    for _, trend in df.iterrows():
        # Create a unique key for the button to prevent state conflicts
        unique_key = f"btn_{trend['prompt_id']}"
        
        with st.container(border=True):
            col1, col2 = st.columns([3, 1])
            
            with col1:
                st.subheader(f"Topic: {trend['target_topic']}")
                
                # Metadata Metrics
                m1, m2, m3 = st.columns(3)
                m1.metric("Confidence", trend['confidence_level'])
                m2.metric("Heat Score", f"{trend.get('heat_score', 0)}/100")
                m3.metric("Status", "Validated" if trend['confidence_level'] != 'Low' else "Draft")
                
                with st.expander("🔍 Show Logic & Prompt Template"):
                    st.caption("This template is fed into Ollama 1B for hook generation.")
                    st.code(trend['llm_prompt_template'], language="markdown")
            
            with col2:
                st.write("### AI Orchestration")
                if st.button("✨ Generate & Validate", key=unique_key, use_container_width=True):
                    with st.spinner("Ollama (Actor) + BERT (Critic) working..."):
                        
                        # 1. Generate via our Orchestrated Engine
                        hook = generate_creative_assets(trend['llm_prompt_template'])
                        
                        # 2. Extract specific BERT score for display
                        # This shows the user the 'Intelligence' in real-time
                        quality_score = get_critic_score(hook)
                        
                        st.session_state[f"hook_{unique_key}"] = hook
                        st.session_state[f"score_{unique_key}"] = quality_score

                # Display Results if they exist in state
                if f"hook_{unique_key}" in st.session_state:
                    score = st.session_state[f"score_{unique_key}"]
                    
                    st.markdown("---")
                    st.success("**Top Selection via BERT Critic:**")
                    st.info(st.session_state[f"hook_{unique_key}"])
                    
                    # Visual feedback for the BERT score
                    progress_color = "green" if score > 0.7 else "orange" if score > 0.4 else "red"
                    st.markdown(f"**BERT Quality Confidence:** :{progress_color}[{score:.2%}]")
                    st.progress(score)
                    
                    if st.button("👍 Log as Good", key=f"up_{unique_key}"):
                        st.toast("Feedback saved for next BERT retraining run!", icon="🧠")
                        # Here you would call a function to insert into gold.human_feedback

if __name__ == "__main__":
    show_discovery()
