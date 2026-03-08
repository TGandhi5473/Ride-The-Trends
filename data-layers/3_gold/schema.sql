-- 0. Infrastructure Setup
CREATE EXTENSION IF NOT EXISTS vector;

-- Update the Silver source table to hold the 768-dimension BERT embeddings
ALTER TABLE silver_social_posts 
ADD COLUMN IF NOT EXISTS embedding vector(768);

-- Create a high-performance HNSW index for the Semantic Briefing feature
CREATE INDEX ON silver_social_posts 
USING hnsw (embedding vector_cosine_ops)
WITH (m = 16, ef_construction = 64);

-- 1. Trend Analysis (The 'Gold' Standard)
-- Refined to include average sentiment if available in your Silver layer
CREATE OR REPLACE VIEW gold_trend_metrics AS
SELECT 
    predicted_category,
    platform,
    COUNT(*) as post_count,
    SUM(view_count) as total_reach,
    ROUND(AVG(view_count), 2) as avg_engagement,
    DATE_TRUNC('day', ingested_at) as trend_date,
    -- We include a representative embedding for category-level trend matching
    AVG(embedding) as category_centroid 
FROM silver_social_posts
GROUP BY 1, 2, 6
ORDER BY trend_date DESC;

-- 2. Platform Market Share
CREATE OR REPLACE VIEW gold_platform_market_share AS
SELECT 
    predicted_category,
    platform,
    COUNT(*) AS post_count,
    ROUND(100.0 * COUNT(*) / SUM(COUNT(*)) OVER(PARTITION BY predicted_category), 2) AS share_pct
FROM silver_social_posts
GROUP BY 1, 2;

-- 3. Semantic Briefing & "Other" Exploration
-- Merged to allow creative directors to search specifically for niche "Other" signals
CREATE OR REPLACE VIEW gold_semantic_exploration AS
SELECT 
    content, 
    platform, 
    author,
    raw_category, 
    ingested_at,
    embedding, -- Required for pgvector similarity search
    predicted_category
FROM silver_social_posts
ORDER BY ingested_at DESC;

-- 4. Pipeline Efficiency (Audit View)
CREATE OR REPLACE VIEW gold_audit_summary AS
SELECT 
    predicted_category,
    COUNT(*) as total_records,
    ROUND(100.0 * COUNT(*) / SUM(COUNT(*)) OVER(), 2) as distribution_pct
FROM silver_social_posts
GROUP BY 1;

-- 5. Niche Discovery Engine (Materialized for Performance)
-- This aggregates the 'OTHER' bucket to find recurring themes
CREATE MATERIALIZED VIEW gold_niche_discovery AS
SELECT 
    raw_category,
    platform,
    COUNT(*) as mention_count,
    AVG(embedding) as theme_centroid, -- The "average" vector of this niche
    MAX(ingested_at) as last_seen
FROM silver_social_posts
WHERE predicted_category = 'OTHER'
GROUP BY 1, 2
HAVING COUNT(*) > 5; -- Only surface recurring "Others"

-- Index for the Discovery Engine
CREATE INDEX ON gold_niche_discovery USING hnsw (theme_centroid vector_cosine_ops);
