-- ==========================================
-- GOLD LAYER: INSIGHTS & SEMANTIC INTERFACE
-- Location: 3_gold/schema.sql
-- ==========================================

-- 0. INFRASTRUCTURE & EXTENSIONS
CREATE EXTENSION IF NOT EXISTS vector;

-- ==========================================
-- 1. SEMANTIC EXPLORATION VIEW (The Search Engine)
-- ==========================================
-- This view is the primary source for the "Semantic Briefing" tab.
-- It prioritizes human-corrected labels over AI predictions (HITL Logic).
CREATE OR REPLACE VIEW gold_semantic_exploration AS
SELECT 
    s.id,
    s.platform, 
    s.source_id,
    s.author,
    s.content, 
    COALESCE(h.corrected_label, s.predicted_category) AS final_category,
    s.confidence,
    s.view_count,
    s.ingested_at,
    s.processed_at,
    s.embedding
FROM silver_social_posts s
LEFT JOIN silver_human_labels h ON s.source_id = h.post_id
WHERE s.is_quarantined = FALSE;

-- ==========================================
-- 2. TREND & ENGAGEMENT METRICS
-- ==========================================
-- Aggregates reach and engagement by category and platform.
-- Includes the "Concept Centroid" for tracking semantic drift over time.
CREATE OR REPLACE VIEW gold_trend_metrics AS
SELECT 
    final_category,
    platform,
    COUNT(*) AS post_count,
    SUM(view_count) AS total_reach,
    ROUND(AVG(view_count), 2) AS avg_engagement,
    DATE_TRUNC('day', ingested_at) AS trend_date,
    -- The "average" vector representing the 'vibe' of this topic on this day
    AVG(embedding) FILTER (WHERE embedding IS NOT NULL) AS category_centroid 
FROM gold_semantic_exploration
GROUP BY 1, 2, 6
ORDER BY trend_date DESC;

-- ==========================================
-- 3. NICHE DISCOVERY ENGINE (Materialized)
-- ==========================================
-- Aggregates 'OTHER' bucket items to find recurring themes not yet in the model.
-- This requires a refresh: REFRESH MATERIALIZED VIEW CONCURRENTLY gold_niche_discovery;
DROP MATERIALIZED VIEW IF EXISTS gold_niche_discovery;
CREATE MATERIALIZED VIEW gold_niche_discovery AS
SELECT 
    raw_category,
    platform,
    COUNT(*) AS mention_count,
    AVG(embedding) AS theme_centroid,
    MAX(ingested_at) AS last_seen
FROM gold_semantic_exploration
WHERE final_category = 'OTHER'
GROUP BY 1, 2
HAVING COUNT(*) >= 5;

-- UNIQUE INDEX is required for CONCURRENT refreshes (prevents table locking)
CREATE UNIQUE INDEX IF NOT EXISTS idx_gold_niche_unique ON gold_niche_discovery (raw_category, platform);

-- HNSW Index for finding posts similar to a newly discovered niche
CREATE INDEX IF NOT EXISTS idx_gold_niche_centroid 
ON gold_niche_discovery USING hnsw (theme_centroid vector_cosine_ops);

-- ==========================================
-- 4. PIPELINE & AUDIT HEALTH
-- ==========================================
-- Tracks model drift and accuracy for the "Audit Hub" dashboard.
CREATE OR REPLACE VIEW gold_audit_summary AS
SELECT 
    COALESCE(h.corrected_label, s.predicted_category) AS category,
    s.platform,
    COUNT(*) AS total_records,
    ROUND(AVG(s.confidence)::numeric, 4) AS avg_model_confidence,
    -- Calculate the "Disagreement Rate" (AI vs Human)
    COUNT(h.corrected_label) AS human_correction_count,
    ROUND((COUNT(h.corrected_label)::float / NULLIF(COUNT(*), 0) * 100)::numeric, 2) AS correction_rate_pct
FROM silver_social_posts s
LEFT JOIN silver_human_labels h ON s.source_id = h.post_id
GROUP BY 1, 2;
