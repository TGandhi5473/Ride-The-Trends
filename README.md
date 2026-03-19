# 🌊 Ride-The-Trends: Creative Intelligence Engine
High-Precision Trend Validation & AI Prompt Orchestration.

# 🎯 The Philosophy 
In modern creative workflows, AI is often used to find trends, leading to hallucinations and "echo-chamber" content. Ride-The-Trends flips this:

Deterministic Logic: SQL and Python calculate the "Score" (Confidence, Velocity, Cross-Platform Heat).

Generative Enrichment: LLMs are only used at the "Last Mile" to translate validated data into high-quality creative prompts.

# 🏗️ Architecture: The Medallion Intelligence Pipeline
This project uses a Serverless Medallion Architecture powered by Neon Postgres and dbt.

1. 🟫 Bronze (Ingestion) - Python OOP
Collectors: Modular, site-specific scrapers (YouTube, Bluesky) using the Factory Pattern.

Safety: Integrated Quota Guard logic to ensure zero-billing risk by tracking API unit consumption in real-time.

Storage: Raw JSONB landing tables in Neon.

2. ⬜ Silver (Transformation) - dbt
Staging: Flattening and type-casting raw JSON payloads into structured relational tables.

Intermediate: The "Brain" of the project. This layer performs Cross-Platform Validation. If a topic trends on both YT and Bluesky, its "Heat" score increases.

Governance: Automated dbt tests to ensure data integrity before any creative sees the output.

3. 🟨 Gold (Intelligence) - LLM Enrichment
Marts: Final analytical tables optimized for the UI.

The Prompt Engine: A specialized view that feeds validated trend data into an LLM (via LangChain/Ollama) to generate "Production-Ready" ad hooks and scripts.

# 🚀 The "Zero-Env" CI/CD Workflow
We leverage Neon Branching to treat our database like a Git branch.

PR Triggers: GitHub Actions tells Neon to create-branch (a 1:1 clone of Production).

Validation: dbt tests run against the ephemeral branch.

Cleanup: Once the PR is merged, the branch is deleted. No local .env files, no stale test data.
# Repo Structure
```text
Ride-The-Trends/
├── 1_ingestion/              # PYTHON: Collectors & Circuit Breakers
│   ├── base_scraper.py       # Abstract Base Class with Quota Logic
│   ├── youtube_scraper.py    # YT Data API v3 Implementation
│   ├── bluesky_scraper.py    # AT Protocol / Firehose Implementation
│   └── worker.py             # Orchestrator (The "Heartbeat")
├── 2_transformations/        # DBT: The "Umpire" (Logic & Validation)
│   ├── models/
│   │   ├── staging/          # stg_yt.sql, stg_bsky.sql (Flattening)
│   │   ├── intermediate/     # int_validated_trends.sql (The Brain)
│   │   └── marts/            # fct_creative_prompts.sql (The Output)
│   ├── macros/               # Reusable SQL (e.g., calculate_confidence.sql)
│   └── dbt_project.yml       # Project config & HML thresholds
├── 3_app/                    # STREAMLIT: The "Cockpit" (UI)
│   ├── app.py                # Main Discovery Dashboard
│   └── pages/                # 1_Trend_Discovery, 2_Audit_Hub
├── core/                     # SHARED: Infrastructure
│   └── database.py           # Pooled Neon Connections (psycopg2/SQLAlchemy)
├── .github/workflows/        # CI/CD: Neon Branching & Auto-Ingest
└── requirements.txt
```
🏛️ Architectural Integrity
This project is built with a "Production-First" mindset. For a deep dive into the trade-offs made regarding API safety, data governance, and CI/CD costs, see DECISIONS.md.
