# 🌊 Ride The Trends: Anti-Slop Marketing Intelligence

**Ride The Trends** is a production-grade data engineering pipeline designed to transform raw social signals (YouTube & Bluesky) into high-utility creative insights. 

By utilizing a **Medallion Architecture** (Bronze, Silver, Gold), this project solves the "trust gap" in AI. It provides a clear, auditable path from raw factual data to probabilistic generative insights, protecting creative teams from "AI Slop."

---
## 💼 Business Case: Why Creative Teams Need This
In a digital landscape saturated with generic, low-value content, marketing teams face a "Signal-to-Noise" crisis. This project provides a competitive edge:

* **Authenticity Mining:** By scraping the **AT Protocol (Bluesky)**, teams access raw, human-centric discourse that hasn't been sterilized by mainstream algorithmic filtering.
* **Contextual Grounding:** Instead of guessing "why" a topic is trending, the **Anti-Slop Engine** extracts high-utility keywords, allowing copywriters to use the specific language of a subculture accurately.
* **Semantic Briefing:** Creative directors use **Vector Search** to input a campaign idea and instantly see related real-world trends, ensuring every brief is grounded in current human sentiment.
* **Cost Efficiency & Privacy:** By running NLP models locally, the team avoids recurring per-token costs of LLM APIs while maintaining total data privacy for sensitive campaign planning.

---

## 🏗️ The Medallion Architecture
We organize data into three distinct layers to ensure both historical integrity and real-time performance:

| Layer | Component | Status | Purpose |
| :--- | :--- | :--- | :--- |
| **🥉 Bronze** | **Cold Storage** | Raw | **The Safety Net.** Immutable copies of original API payloads. |
| **🥈 Silver** | **NLP Engine** | Cleaned | **The Logic.** Filtered "Anti-Slop" data with extracted keywords. |
| **🥇 Gold** | **Hot Partitions** | Optimized | **The Insight.** Vector embeddings ready for semantic search. |

### 🚀 The "Hot/Cold" Storage Strategy
To balance high-speed retrieval with long-term ML research, the **Gold Layer** utilizes **PostgreSQL Native Partitioning**:
* **Hot DB (Production):** Stores the most recent 30 days of data. This keeps indices small and vector searches near-instant.
* **Cold DB (ML Archive):** At the end of each month, partitions are detached from the Hot DB and shipped to the heavyweight Archive DB for long-term trend analysis.

---

## 📂 Repository Structure
```text
ride-the-trends/
├── .github/workflows/   # Automation (GitHub Actions Hourly Ingestion)
├── data-layers/
│   ├── 1_bronze/        # Stage 1: Raw Ingestion (YouTube/Bluesky Scrapers)
│   ├── 2_silver/        # Stage 2: NLP Processing (KeyBERT Anti-Slop)
│   └── 3_gold/          # Stage 3: Vector Storage (Partitions & pgvector)
├── web-app/
│   ├── api/             # FastAPI Backend (The Brain)
│   └── dashboard/       # Streamlit Observability Funnel (The Face)
├── requirements.txt     # Dependencies (Python 3.10+)
└── README.md            # Technical Manifesto
```
## 🔐 Security & Production Setup

### 1. The GitHub Secrets Strategy
All sensitive credentials must be added to **GitHub Secrets** to prevent leaks in this public-facing project:

| Secret Name | Description |
| :--- | :--- |
| **YOUTUBE_API_KEY** | Google Cloud Console V3 API Key |
| **BSKY_HANDLE** | Your Bluesky handle |
| **BSKY_PASSWORD** | Bluesky App Password |
| **HOT_DB_URL** | Connection string for the 30-day Production DB |
| **COLD_DB_URL** | Connection string for the Heavyweight ML Archive DB |

# Clone and install
# Initialize database
# Launch layers
```text
pip install -r requirements.txt
psql -f data-layers/3_gold/schema.sql
uvicorn web-app.api.main:app --reload
streamlit run web-app.dashboard.dashboard.py
```
