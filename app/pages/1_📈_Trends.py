import streamlit as st
import plotly.express as px
from utils.db_loaders import get_trend_metrics

st.title("📈 Trend Intelligence")

# Fetch pre-aggregated Gold data
df = get_trend_metrics()

# --- FILTERS ---
categories = st.multiselect("Filter by Category", df['predicted_category'].unique())
if categories:
    df = df[df['predicted_category'].isin(categories)]

# --- MAIN CHART ---
fig = px.line(df, x="trend_date", y="post_count", color="predicted_category", 
              title="Topic Volume Over Time (BERT Classified)")
st.plotly_chart(fig, use_container_width=True)
