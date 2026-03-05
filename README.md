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

## 🛠️ Project Structure
```text
├── data-ingestion/    # Python workers for Bluesky & YouTube
├── nlp-engine/        # Vector embedding & keyword logic
├── database/          # SQL migrations and init scripts
├── web-app/           # FastAPI backend & Next.js frontend
├── docker-compose.yml # Local Postgres + pgvector setup
└── .env.example       # Template for local development
```
## 🔐 Security & Production Setup

### 1. The GitHub Secrets Strategy
This repository is configured for **Zero-Leak Production**. All sensitive credentials must be added to **GitHub Secrets** (`Settings > Secrets and variables > Actions`):

| Secret Name | Description |
| :--- | :--- |
| **YOUTUBE_API_KEY** | Google Cloud Console V3 API Key |
| **BSKY_HANDLE** | Your Bluesky handle (e.g., tirth.bsky.social) |
| **BSKY_PASSWORD** | Bluesky "App Password" (Settings > App Passwords) |
| **DATABASE_URL** | Connection string for Postgres (Internal or Remote) |

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
