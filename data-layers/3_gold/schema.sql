-- ==========================================
-- 0. INFRASTRUCTURE & EXTENSIONS
-- ==========================================
CREATE EXTENSION IF NOT EXISTS vector;

-- Ensure Silver is ready for Gold (Safeguard)
ALTER TABLE silver_social_posts ADD COLUMN IF NOT EXISTS confidence FLOAT DEFAULT 0.0;
ALTER TABLE silver_social_posts ADD COLUMN IF NOT EXISTS embedding vector(768);

-- HNSW Index for high-speed Semantic Search
CREATE INDEX IF NOT EXISTS idx_silver_posts_embedding 
ON silver_social_posts USING hnsw (embedding vector_cosine_ops)
WITH (m = 16, ef_construction = 64);

-- ==========================================
-- 1. SEMANTIC EXPLORATION (The Search Engine)
-- ==========================================
-- This view acts as the primary source for your Semantic Briefing.
-- It uses COALESCE to prioritize your manual corrections over AI predictions.
CREATE OR REPLACE VIEW gold_semantic_exploration AS
SELECT 
    s.id,
    s.content, 
    s.platform, 
    s.author,
    COALESCE(h.corrected_label, s.predicted_category) AS final_category,
    s.confidence,
    s.view_count,
    s.ingested_at,
    s.embedding
FROM silver_social_posts s
LEFT JOIN silver_human_labels h ON s.source_id = h.post_id;

-- ==========================================
-- 2. TREND & ENGAGEMENT METRICS
-- ==========================================
CREATE OR REPLACE VIEW gold_trend_metrics AS
SELECT 
    final_category,
    platform,
    COUNT(*) AS post_count,
    SUM(view_count) AS total_reach,
    ROUND(AVG(view_count), 2) AS avg_engagement,
    DATE_TRUNC('day', ingested_at) AS trend_date,
    -- Concept Centroid: The "average" vector representing this category on this day
    AVG(embedding) AS category_centroid 
FROM gold_semantic_exploration
GROUP BY 1, 2, 6
ORDER BY trend_date DESC;

-- ==========================================
-- 3. NICHE DISCOVERY ENGINE (Materialized)
-- ==========================================
-- Aggregates the 'OTHER' bucket to find recurring themes. 
-- Must be refreshed: REFRESH MATERIALIZED VIEW gold_niche_discovery;
CREATE MATERIALIZED VIEW IF NOT EXISTS gold_niche_discovery AS
SELECT 
    raw_category,
    platform,
    COUNT(*) AS mention_count,
    AVG(embedding) AS theme_centroid,
    MAX(ingested_at) AS last_seen
FROM gold_semantic_exploration
WHERE final_category = 'OTHER'
GROUP BY 1, 2
HAVING COUNT(*) > 5;

CREATE INDEX IF NOT EXISTS idx_gold_niche_centroid 
ON gold_niche_discovery USING hnsw (theme_centroid vector_cosine_ops);

-- ==========================================
-- 4. PIPELINE & AUDIT HEALTH
-- ==========================================
CREATE OR REPLACE VIEW gold_audit_summary AS
SELECT 
    final_category,
    platform,
    COUNT(*) AS total_records,
    ROUND(AVG(confidence), 4) AS avg_model_confidence,
    -- Tracks how many items in this category were manually corrected
    COUNT(h.corrected_label) AS human_correction_count
FROM silver_social_posts s
LEFT JOIN silver_human_labels h ON s.source_id = h.post_id
GROUP BY 1, 2;
