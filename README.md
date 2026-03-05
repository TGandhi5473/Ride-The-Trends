# Ride The Trends: Anti-Slop Marketing Intelligence

A professional-grade data pipeline that ingests trending topics from **YouTube** and **Bluesky**, processes them using **Local NLP (KeyBERT/Sentence-Transformers)**, and stores them in a **Postgres + pgvector** database for semantic search.

## 💼 Business Case: Why Creative Teams Need This
In a digital landscape saturated with "AI Slop"—generic, low-value content generated to farm algorithms—marketing and creative teams face a "Signal-to-Noise" crisis. Generic trend reports often recycle the same stale insights.

**This project provides a competitive edge by:**
* **Authenticity Mining:** By scraping the **AT Protocol (Bluesky)**, teams access raw, human-centric discourse that hasn't been sterilized by mainstream algorithmic filtering.
* **Contextual Grounding:** Instead of guessing "why" a topic is trending, the **Anti-Slop Engine** extracts high-utility keywords, allowing copywriters to use the specific language and "slang" of a subculture accurately.
* **Semantic Briefing:** Creative directors can use **Vector Search** to input a rough campaign idea and instantly see related real-world trends, ensuring every brief is grounded in current human sentiment rather than "hallucinated" AI trends.
* **Cost Efficiency:** By running NLP models locally, the team avoids the recurring per-token costs of high-end LLM APIs while maintaining total data privacy for sensitive campaign planning.



## 🚀 Features
- **BYOK (Bring Your Own Key) Architecture:** Securely managed via GitHub Secrets and environment variables.
- **Anti-Slop Engine:** Filters generic AI-generated trends to find unique, high-utility keywords.
- **Hybrid Search:** Combines traditional SQL filtering with Vector Semantic Search using `pgvector`.
- **Decentralized Ingestion:** Leverages the AT Protocol (Bluesky) and YouTube Data API v3.

### 🏗️ The "Hot/Cold" Storage Strategy

To balance high-speed retrieval with long-term ML research, this project utilizes **PostgreSQL Native Partitioning**:

* **The Hot DB (Production):** Only stores the most recent 30 days of data. This keeps the indices small and vector searches near-instant.
* **The Cold DB (ML Archive):** At the end of each month, the current partition is **detached** from the Hot DB and **shipped** to the heavyweight Archive DB for long-term trend analysis.

## 🛠️ Project Structure
```text
├── data-ingestion/          # Ingestion workers (YouTube/Bluesky)
│   └── worker.py            # Primary ingestion logic
├── nlp-engine/              # 'Anti-Slop' keyword & vector logic
│   └── processor.py         # Embedding & KeyBERT processing
├── database/                # Database orchestration
│   ├── init/                # Docker entrypoint SQL scripts
│   │   ├── 01_hot_schema.sql    # Partitioned 'Hot' table setup
│   │   └── 02_cold_schema.sql   # Unified 'Cold' archive table
│   └── archive_manager.py   # Strategy 2: Detach & Ship automation
├── web-app/                 # User interface
│   ├── backend/             # FastAPI (Connects to Hot DB)
│   └── frontend/            # Next.js Dashboard
├── docker-compose.yml       # Orchestrates Hot DB and Cold DB containers
├── .env.example             # Template for HOT_DB_URL and COLD_DB_URL
├── .gitignore               # Prevents .env and local caches from syncing
└── requirements.txt         # Project dependencies
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

### 2. Local Environment Protection
The `.gitignore` is configured to block `.env` files. To work locally, copy the example template:

```bash
cp .env.example .env
```
## 🛠️ Installation & Execution

### 1. Local Database Setup
Start the vector-enabled PostgreSQL instance using the pre-configured Docker image:

```bash
docker-compose up -d
```
# Install dependencies
pip install -r requirements.txt

# Run the ingestion worker to populate the database
python -m data_ingestion.worker

# Start FastAPI Backend
uvicorn web-app.backend.main:app --reload

# Start Next.js Frontend (in a separate terminal)
cd web-app/frontend
npm install
npm run dev
