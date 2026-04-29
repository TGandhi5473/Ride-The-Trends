import streamlit as st
import pandas as pd
from sqlalchemy import text
from core.database import get_neon_engine
from utils.llm_engine import generate_creative_assets, get_critic_score

st.set_page_config(page_title="Trend Discovery", page_icon="🎯", layout="wide")

def save_feedback(prompt_id, hook_text, is_good):
    """
    Persists user validation to the gold.human_feedback table.
    This data is the 'fuel' for the BERT retraining script.
    """
    engine = get_neon_engine()
    label = 1 if is_good else 0
    query = text("""
        INSERT INTO gold.human_feedback (prompt_id, text, label_id, used_for_training) 
        VALUES (:pid, :txt, :lbl, FALSE)
    """)
    try:
        with engine.begin() as conn:
            conn.execute(query, {"pid": prompt_id, "txt": hook_text, "lbl": label})
        return True
    except Exception as e:
        st.error(f"Failed to save feedback: {e}")
        return False

def fetch_gold_prompts():
    """Pulls validated trend data from the dbt Gold Layer."""
    engine = get_neon_engine()
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
        st.warning("No validated trends found. Ensure your dbt pipeline has run.")
        return

    for _, trend in df.iterrows():
        unique_key = f"btn_{trend['prompt_id']}"
        
        with st.container(border=True):
            col1, col2 = st.columns([3, 1])
            
            with col1:
                st.subheader(f"Topic: {trend['target_topic']}")
                
                # Metadata Badges
                m1, m2, m3 = st.columns(3)
                m1.metric("Confidence", trend['confidence_level'])
                m2.metric("Optimized Score", f"{trend.get('optimized_score', 0):.2f}")
                m3.metric("Status", "Validated" if trend['confidence_level'] != 'Low' else "Draft")
                
                with st.expander("🔍 View Prompt Logic"):
                    st.code(trend['llm_prompt_template'], language="markdown")
            
            with col2:
                st.write("### AI Orchestration")
                if st.button("✨ Generate & Validate", key=unique_key, use_container_width=True):
                    with st.spinner("Ollama (Actor) + BERT (Critic) working..."):
                        
                        # Phase 1 & 2: Generation + BERT Scoring
                        hook = generate_creative_assets(trend['llm_prompt_template'])
                        quality_score = get_critic_score(hook)
                        
                        # Store in session state to persist through feedback clicks
                        st.session_state[f"hook_{unique_key}"] = hook
                        st.session_state[f"score_{unique_key}"] = quality_score

                # --- Results & Feedback Section ---
                if f"hook_{unique_key}" in st.session_state:
                    hook = st.session_state[f"hook_{unique_key}"]
                    score = st.session_state[f"score_{unique_key}"]
                    
                    st.markdown("---")
                    st.success("**Top Selection via BERT Critic:**")
                    st.info(hook)
                    
                    # Sentiment/Quality Indicator
                    progress_color = "green" if score > 0.7 else "orange" if score > 0.4 else "red"
                    st.markdown(f"**BERT Confidence Score:** :{progress_color}[{score:.2%}]")
                    st.progress(score)
                    
                    # Human-in-the-Loop Feedback Buttons
                    fb_col1, fb_col2 = st.columns(2)
                    
                    if fb_col1.button("👍 Approved", key=f"up_{unique_key}", use_container_width=True):
                        if save_feedback(trend['prompt_id'], hook, is_good=True):
                            st.toast("Saved to Training Queue!", icon="🧠")
                            # Clear state so user can generate again if desired
                            del st.session_state[f"hook_{unique_key}"]
                            st.rerun()

                    if fb_col2.button("👎 Rejected", key=f"down_{unique_key}", use_container_width=True):
                        if save_feedback(trend['prompt_id'], hook, is_good=False):
                            st.toast("Rejection logged for model tuning.", icon="📉")
                            del st.session_state[f"hook_{unique_key}"]
                            st.rerun()

if __name__ == "__main__":
    show_discovery()
