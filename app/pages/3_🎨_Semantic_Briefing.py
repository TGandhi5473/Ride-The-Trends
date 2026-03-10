import streamlit as st
from database import run_query
from utils.components import section_header, platform_badge
from silver.classifier import SocialClassifier # Shared model logic

# 1. Page Configuration
section_header("🎨 Semantic Briefing Assistant", "Ground your campaign ideas in real-world human discourse.")

# 2. Shared Resource Caching
@st.cache_resource
def load_shared_classifier():
    # This ensures we use the SAME 768-dim BERT model as the Refiner
    return SocialClassifier()

ai_engine = load_shared_classifier()

# 3. Sidebar: DNA & Performance Stats
with st.sidebar:
    st.markdown("### 🧬 Vector Engine")
    st.info("Using **DistilBERT (768-dim)** for 1:1 semantic alignment with the Silver Layer.")

# 4. Search Interface
st.subheader("🕵️ Concept Matcher")
brief_input = st.text_area("Describe your campaign vibe or paste a trend:", 
                            placeholder="e.g., 'Decentralized social media protocols for privacy-conscious users'")

limit = st.slider("Signals to retrieve:", 3, 10, 5)

if brief_input:
    with st.spinner("Calculating semantic similarity..."):
        # Use the SAME pooling strategy ([CLS] token) as the refiner
        _, _, query_embeddings = ai_engine.predict_batch_with_vectors([brief_input])
        query_vector = query_embeddings[0].tolist()
        
        # 5. Optimized SQL (Distance calculated once)
        query = """
            WITH similarity_search AS (
                SELECT 
                    final_category, content, platform, author,
                    (1 - (embedding <=> %s::vector)) as score
                FROM gold_semantic_exploration
            )
            SELECT * FROM similarity_search
            WHERE score > 0.15 -- Minimum 'Relevance' floor
            ORDER BY score DESC
            LIMIT %s
        """
        
        results = run_query(query, (query_vector, limit))

        # 6. Display Results
        if not results.empty:
            for _, row in results.iterrows():
                # Color coding for platform identity
                color = "#0085ff" if row['platform'] == 'bluesky' else "#ff0000"
                
                with st.container(border=True):
                    st.markdown(f"""
                        <div style="display: flex; justify-content: space-between;">
                            <span style="color: gray; font-size: 0.8em;">{row['platform'].upper()} | {row['final_category']}</span>
                            <span style="color: {color}; font-weight: bold;">{row['score']:.1%} Match</span>
                        </div>
                        <p style="font-size: 1.1em; margin: 10px 0;">"{row['content']}"</p>
                        <div style="text-align: right; color: #555; font-size: 0.8em;">— {row['author']}</div>
                    """, unsafe_allow_html=True)
        else:
            st.error("No relevant signals found. Try broadening your concept.")
