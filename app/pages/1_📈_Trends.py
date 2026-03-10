import streamlit as st
import plotly.express as px
from database import run_query # Using our Arrow-optimized loader

st.title("📈 Trend Intelligence")
st.markdown("---")

# 1. Fetch from Gold Layer (Aggregated for Performance)
@st.cache_data(ttl=600) # Cache for 10 mins to save DB round-trips
def load_trends():
    # We pull from the view we built in 3_gold/schema.sql
    query = "SELECT * FROM gold_trend_metrics;"
    return run_query(query)

df = load_trends()

if df.empty:
    st.warning("No trend data found. Please run `refiner.py` and `gold_builder.py` first.")
    st.stop()

# 2. Sidebar Filters
with st.sidebar:
    st.header("Graph Controls")
    metric_choice = st.radio(
        "Select Metric:",
        ["Post Count", "Total Reach", "Avg Engagement"],
        index=0
    )
    
    # Map friendly names to SQL column names
    metric_map = {
        "Post Count": "post_count",
        "Total Reach": "total_reach",
        "Avg Engagement": "avg_engagement"
    }
    target_col = metric_map[metric_choice]

    all_categories = df['final_category'].unique()
    selected_cats = st.multiselect("Filter Topics", all_categories, default=all_categories)

# 3. Apply Filtering
filtered_df = df[df['final_category'].isin(selected_cats)]

# 4. Interactive Visualization
fig = px.line(
    filtered_df, 
    x="trend_date", 
    y=target_col, 
    color="final_category",
    line_shape="spline", # Smooths out the social media volatility
    title=f"Market Pulse: {metric_choice} by Topic",
    labels={target_col: metric_choice, "trend_date": "Date", "final_category": "Topic"},
    template="plotly_dark" # Matches a 'Night Mode' dashboard aesthetic
)

st.plotly_chart(fig, use_container_width=True)

# 5. Data Breakdown Table
with st.expander("📂 View Raw Trend Data"):
    st.dataframe(filtered_df.sort_values(by="trend_date", ascending=False), use_container_width=True)
