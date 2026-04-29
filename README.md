# 🌊 Ride-The-Trends: Creative Intelligence Engine
High-Precision Trend Validation & AI Prompt Orchestration.
# Why I built this:
I built this to make prompting and prototyping faster. This engine is not meant to replace human creativity, but to leverage human output in a way that minimizes repetitive interactions with AI. It allows creative teams to prototype more passively by presenting only the highest-signal trends, pre-scored by an intelligent critic. The output of these results should then be fed into other AI tools like SeedDance to make the actual ad/shorts. 

# 🎯 The Philosophy
In modern creative workflows, AI is often used to find trends, leading to hallucinations and "echo-chamber" content. Ride-The-Trends flips this:

Deterministic Logic: SQL and Python calculate the "Score" (Confidence, Velocity, Cross-Platform Heat).

Generative Enrichment: LLMs are only used at the "Last Mile" to translate validated data into high-quality creative prompts.

# 🏗️ Architecture: The Medallion Intelligence Pipeline
This project uses a Serverless Medallion Architecture powered by Neon Postgres and dbt.

# 1. 🟫 Bronze (Ingestion) - Python OOP
Collectors: Modular, site-specific scrapers (YouTube, Bluesky) using the Factory Pattern.

Safety: Integrated Quota Guard logic to ensure zero-billing risk by tracking API unit consumption in real-time.

Storage: Raw JSONB landing tables in Neon.

# 2. ⬜ Silver (Transformation) - dbt
Governance: Automated dbt tests to ensure data integrity before any creative sees the output.

Staging: stg_human_feedback.sql – Flattening and type-casting raw JSON payloads into structured relational tables.
A new staging model that pulls raw "Approve/Reject" events and BERT scores from the Streamlit app. It initially returns an empty schema (using a UNION ALL with a dummy filter) until the first user interaction is logged.

Intermediate: int_model_performance.sql – The "Brain" of the project. This layer performs Cross-Platform Validation. If a topic trends on both YT and Bluesky, its "Heat" score increases.
Joins the stg_validated_trends with stg_human_feedback. This calculates the "delta" between what BERT predicted and what the human liked, effectively creating a "Correction Layer" for the trend scores.

# 3. 🟨 Gold (Intelligence) - LLM Enrichment
Marts: Final analytical tables optimized for the UI.

The Prompt Engine: A specialized view that feeds validated trend data into an LLM (via LangChain/Ollama) to generate "Production-Ready" ad hooks and scripts.

# 🧠 The Intelligence Loop (Actor-Critic Framework)
To prevent low-quality AI "slop," we implement a dual-model orchestration layer:

The Actor (Ollama 1B): Receives the dbt-validated trend and generates 3 creative ad hooks.

The Critic (DistilBERT): A fine-tuned classifier that scores each hook for "Viral Potential" and "Brand Alignment."

Human-in-the-Loop (HITL): Users "Approve" or "Reject" hooks in the Streamlit UI. This feedback is joined back to the dbt Gold layer and stored as training data.

Continuous Refinement: When 50+ new labels are collected, a GitHub Action triggers retrain_bert.py, fine-tuning the Critic to better match the user's creative taste.

# 🚀 The "Zero-Env" CI/CD Workflow
We leverage Neon Branching to treat our database like a Git branch.

PR Triggers: GitHub Actions tells Neon to create-branch (a 1:1 clone of Production).

Validation: dbt tests and smoke_tests.yml run against the ephemeral branch.

Cleanup: Once the PR is merged, the branch is deleted. No local .env files, no stale test data.

```
📂 Repo Structure
Ride-The-Trends/
├── 1_ingestion/              # BRONZE: Collectors & Circuit Breakers
│   ├── base_scraper.py       # Abstract Base Class with Quota Logic
│   ├── youtube_scraper.py    # YT Data API v3 Implementation
│   ├── bluesky_scraper.py    # AT Protocol Implementation
│   └── worker.py             # Orchestrator (The "Heartbeat")
├── 2_transformations/        # SILVER: dbt (Logic & Validation)
│   ├── models/
│   │   ├── staging/          # stg_yt.sql, stg_bsky.sql (Flattening)
│   │   ├── intermediate/     # int_validated_trends.sql (The Brain)
│   │   └── marts/            # fct_creative_prompts.sql (The Output)
│   └── dbt_project.yml       # Project config & HML thresholds
├── 3_app/                    # GOLD: STREAMLIT (The Cockpit)
│   ├── app.py                # Main Discovery Dashboard
│   └── pages/                # 1_Trend_Discovery, 2_Audit_Hub
├── core/                     # SHARED: The "Shield & Skeleton"
│   ├── __init__.py           # Package exports
│   ├── config.py             # Single source of truth (Env/Paths)
│   ├── database.py           # Pooled Neon/SQLAlchemy connections
│   ├── exceptions.py         # Custom error types (Quota, DB, etc.)
│   └── logger.py             # Structured logging for CI/CD
├── scripts/                  # HITL: Model Intelligence
│   └── retrain_bert.py       # 0-cost CPU Fine-tuning logic
├── .github/workflows/        # CI/CD: Automated Pipelines
│   ├── ingestion.yml         # Hourly pulse & retraining trigger
│   └── smoke_test.yml        # Connectivity & Schema validator
├── models/                   # Local storage for refined BERT weights
└── requirements.txt          # Production dependencies
```

🏛️ Architectural Integrity
This project is built with a "Production-First" mindset. For a deep dive into the trade-offs made regarding API safety, data governance, and CI/CD costs, see DECISIONS.md
└── requirements.txt          # Production Dependencies
🏛️ Architectural Integrity
This project is built with a "Production-First" mindset. For a deep dive into the trade-offs made regarding API safety, data governance, and CI/CD costs, see DECISIONS.md.
