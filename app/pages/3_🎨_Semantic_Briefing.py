import streamlit as st
from sentence_transformers import SentenceTransformer
from database import run_query
from utils.components import section_header, platform_badge

# 1. Page Configuration & Header
section_header("🎨 Semantic Briefing Assistant", "Ground your campaign ideas in real-world human discourse.")

# 2. Resource Caching
@st.cache_resource
def load_embedding_model():
    # Using the same 768-dim capable model as the refiner
    return SentenceTransformer('all-MiniLM-L6-v2')

model = load_embedding_model()

# 3. Sidebar Instructions & DNA
with st.sidebar:
    st.markdown("### 🧬 Vector Engine")
    st.info("""
    **How it works:**
    - BERT converts your concept into a **768-dimension vector**.
    - We use **pgvector** to bypass keyword matching and find *contextual* similarity.
    - This protects briefs from 'AI Slop' by grounding them in actual human sentiment.
    """)

# 4. Search Interface: Dual Input Modes
st.subheader("🕵️ Concept Matcher")
mode = st.radio("Search Mode", ["Short Concept/Headline", "Full Campaign Brief"], horizontal=True)

if mode == "Short Concept/Headline":
    brief_input = st.text_input("Paste a competitor's headline or a specific trend:", 
                                 placeholder="e.g., 'The rise of decentralized social media protocols'")
else:
    brief_input = st.text_area("Describe your campaign vibe/concept in detail:", 
                                placeholder="e.g., 'A sustainable fashion campaign focusing on upcycled techwear for Gen-Z urban explorers'",
                                help="More description leads to higher semantic accuracy.")

limit = st.slider("Signals to retrieve:", 3, 10, 5)

# 5. Execution Logic
if brief_input:
    with st.spinner("Analyzing human sentiment..."):
        # Step A: Vectorize the user input
        query_vector = model.encode(brief_input).tolist()
        
        # Step B: Perform Cosine Distance search via Gold View
        # Using (1 - distance) for a readable similarity percentage
        query = """
            SELECT 
                predicted_category, 
                content, 
                platform, 
                author,
                (1 - (embedding <=> %s::vector)) as similarity_score
            FROM gold_semantic_exploration
            ORDER BY embedding <=> %s::vector
            LIMIT %s
        """
        
        results = run_query(query, (query_vector, query_vector, limit))

        # 6. Display Results
        if not results.empty:
            st.success(f"Found {len(results)} relevant signals!")
            
            for _, row in results.iterrows():
                # Dynamic Border Color for Platform Identity
                border_color = "#0085ff" if row['platform'] == 'bluesky' else "#ff0000"
                
                with st.container():
                    st.markdown(f"""
                    <div style="
                        border-left: 5px solid {border_color}; 
                        padding: 15px; 
                        background-color: #f8f9fa; 
                        border-radius: 0 10px 10px 0; 
                        margin-bottom: 20px;
                    ">
                        <div style="display: flex; justify-content: space-between; align-items: center;">
                            <span style="font-size: 0.8em; color: gray;">
                                {row['platform'].upper()} | <b>{row['predicted_category']}</b>
                            </span>
                            <span style="font-weight: bold; color: {border_color};">
                                {row['similarity_score']:.1%} Match
                            </span>
                        </div>
                        <p style="font-style: italic; font-size: 1.1em; margin: 10px 0;">"{row['content']}"</p>
                        <div style="text-align: right;">
                            <span style="font-size: 0.8em; color: #555;">— {row['author']}</span>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                    # Use component badge for extra visual flair
                    platform_badge(row['platform'])
        else:
            st.error("No relevant signals found in the 30-day Hot DB.")

# 7. Footer
st.divider()
st.caption("This tool uses pgvector (HNSW) to find semantic overlaps in recent social signals.")
