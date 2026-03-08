import streamlit as st
from sentence_transformers import SentenceTransformer
from database import run_query
from utils.components import section_header

# 1. Page Configuration & Header
section_header("🎨 Semantic Briefing Assistant", "Ground your campaign ideas in real-world human discourse.")

# 2. Resource Caching
# We cache the model so it doesn't reload every time the user types
@st.cache_resource
def load_embedding_model():
    return SentenceTransformer('all-MiniLM-L6-v2')

model = load_embedding_model()

# 3. Sidebar Instructions
with st.sidebar:
    st.info("""
    **How it works:**
    1. Enter a campaign "vibe" or concept.
    2. BERT converts your text into a **768-dimension vector**.
    3. We use **pgvector** to find the closest matches in our Gold Layer.
    """)

# 4. Input Area
brief_input = st.text_area(
    "Describe your campaign concept:",
    placeholder="e.g., 'Retro-futurism with a focus on sustainable urban gardening'",
    help="The more descriptive, the better the semantic match."
)

limit = st.slider("Number of signals to retrieve:", 3, 10, 5)

if st.button("🚀 Ground This Brief"):
    if not brief_input.strip():
        st.warning("Please enter a concept to search.")
    else:
        with st.spinner("Analyzing human sentiment..."):
            # Step A: Vectorize the user input
            query_vector = model.encode(brief_input).tolist()
            
            # Step B: Perform Cosine Distance search in SQL
            # We query the semantic exploration view created in the Gold Schema
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

            # 5. Display Results
            if not results.empty:
                st.success(f"Found {len(results)} relevant signals!")
                
                for _, row in results.iterrows():
                    # Color coding based on platform
                    border_color = "#0085ff" if row['platform'] == 'bluesky' else "#ff0000"
                    
                    with st.container():
                        st.markdown(f"""
                        <div style="border-left: 5px solid {border_color}; padding-left: 15px; margin-bottom: 20px;">
                            <p style="font-size: 0.8em; color: gray; margin-bottom: 0;">
                                {row['platform'].upper()} | Category: {row['predicted_category']}
                            </p>
                            <p style="font-style: italic; font-size: 1.1em;">"{row['content']}"</p>
                            <p style="font-size: 0.8em; text-align: right;">— {row['author']} (Match: {row['similarity_score']:.2%})</p>
                        </div>
                        """, unsafe_allow_html=True)
            else:
                st.error("No matches found. Ensure your Gold Layer has been populated.")

# 6. Next Steps
st.divider()
st.caption("This tool uses Vector Search to bypass the 'AI Slop' of generic LLMs and find real human voices.")
