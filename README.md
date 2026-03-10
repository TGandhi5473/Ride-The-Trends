# 🌊 Ride The Trends: Anti-Slop Marketing Intelligence

**Ride The Trends** is a production-grade data engineering pipeline that transforms raw social signals (YouTube & Bluesky) into high-utility creative insights. By utilizing a **Medallion Architecture**, this project provides an auditable, human-grounded alternative to generic "AI Slop."



---

## 🏗️ Technical Architecture
This project implements a full-stack data lifecycle, optimized for local execution to minimize cloud costs and maximize privacy.

### 1. The Medallion Pipeline
* **🥉 Bronze (Ingestion):** Multi-threaded scrapers fetching raw JSON from **YouTube V3** and **Bluesky (AT Protocol)**. Implemented with a "Safety Net" approach—immutable copies of every API response.
* **🥈 Silver (Refinement):** The "Brain" of the operation. Uses a local **DistilBERT** model for NLP classification and **pgvector** for generating 768-dimension embeddings. Includes **Quarantine Logic** for schema-drift protection.
* **🥇 Gold (Intelligence):** Pre-calculated **SQL Views** and **Materialized Views** with **HNSW indexing**. This layer powers the dashboard with sub-100ms semantic search performance.

### 2. The "Hot/Cold" Storage Strategy
To balance high-speed retrieval with long-term research, the system utilizes **PostgreSQL Native Partitioning**:
* **Hot DB:** The most recent 30 days of social signals, indexed for real-time vector search.
* **Cold DB:** Monthly partitions detached and archived for long-term trend analysis and BERT retraining.

---

## 🧠 Core Features & Innovation

### 🕵️ Semantic Briefing (Vector-Native Search)
Unlike traditional keyword search, which fails if a user types "Eco-fashion" but the data says "Sustainable Techwear," this engine uses **Cosine Similarity** (`<=>`).
* **Context over Keywords:** Uses the same embedding space for both the query and the database to find *intent*, not just strings.
* **HNSW Powered:** Hierarchical Navigable Small World indices ensure that search scales linearly as the database grows to millions of records.



[Image of cosine similarity between two vectors]


### 🛡️ The Audit Hub (HITL)
A dedicated interface for **Human-in-the-Loop** machine learning.
* **Active Learning:** Users can manually correct low-confidence AI predictions (Confidence < 0.45).
* **Ground Truth Generation:** These corrections are logged to a feedback table, creating the dataset for the next model fine-tuning iteration.
* **Circuit Breakers:** Automated success-rate monitoring triggers warnings if API schemas change or model drift occurs.



---

## 🛠️ Technology Stack (2026 Standard)
* **Language:** Python 3.12+
* **Engine:** **Pandas 3.0** with **Apache Arrow** backend for high-speed memory management.
* **Database:** **PostgreSQL 17** + **pgvector** (HNSW Indexing).
* **Models:** Local **DistilBERT** (HuggingFace Transformers).
* **UI:** **Streamlit 1.55** (Multi-page navigation & custom HTML/CSS components).

---

## 📂 Repository Structure
```text
ride-the-trends/
├── 1_bronze/          # Stage 1: Raw Ingestion (YouTube/Bluesky Scrapers)
├── 2_silver/          # Stage 2: NLP Processing (BERT Classification)
├── 3_gold/            # Stage 3: Aggregate SQL Views & Vector Storage
├── app/               # UI LAYER (Streamlit)
│   ├── Main_Dashboard.py # Navigation & Global State
│   └── pages/         # Trends, Audit Hub, & Semantic Briefing
├── database.py        # Centralized Connection Pooler (psycopg2)
├── classifier.py      # Local BERT Inference & Vectorization
└── requirements.txt   # Pinned March 2026 Dependencies
```
🚀 Quick Start
Clone & Install:
```text
git clone [https://github.com/TGandhi5473/ride-the-trends.git](https://github.com/TGandhi5473/ride-the-trends.git)
cd ride-the-trends
pip install -r requirements.txt
```
Setup Database:
Ensure PostgreSQL is running with the pgvector extension, then run:
```text
psql -d your_db -f 3_gold/schema.sql
```
Run Dashboard:
```text
streamlit run app/Main_Dashboard.py
```
Engineer's Note: This isn't just another LLM wrapper. It's a Retrieval-Augmented Intelligence (RAI) tool designed for engineers who value data integrity and cost-efficiency. It prioritizes factual, human-generated social signals over machine-generated noise.
