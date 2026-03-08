-- 1. Trend Analysis (The 'Gold' Standard)
-- Primary view for time-series charts and engagement metrics
CREATE OR REPLACE VIEW gold_trend_metrics AS
SELECT 
    predicted_category,
    platform,
    COUNT(*) as post_count,
    SUM(view_count) as total_reach,
    ROUND(AVG(view_count), 2) as avg_engagement,
    DATE_TRUNC('day', ingested_at) as trend_date
FROM silver_social_posts
GROUP BY 1, 2, 6
ORDER BY trend_date DESC;

-- 2. Platform Market Share
-- Calculates how much 'noise' vs 'value' each platform provides per topic
CREATE OR REPLACE VIEW gold_platform_market_share AS
SELECT 
    predicted_category,
    platform,
    COUNT(*) AS post_count,
    ROUND(100.0 * COUNT(*) / SUM(COUNT(*)) OVER(PARTITION BY predicted_category), 2) AS share_pct
FROM silver_social_posts
GROUP BY 1, 2;

-- 3. The "Other" Exploration (Identifying new niche trends)
-- This powers the 'Audit Hub' and 'Emerging Trends' discovery
CREATE OR REPLACE VIEW gold_other_exploration AS
SELECT 
    content, 
    platform, 
    author,
    raw_category, 
    ingested_at,
    source_id
FROM silver_social_posts
WHERE predicted_category = 'OTHER'
ORDER BY ingested_at DESC;

-- 4. Pipeline Efficiency (Audit View)
-- Quick summary for the Audit Hub UI to show if the BERT model is drifting
CREATE OR REPLACE VIEW gold_audit_summary AS
SELECT 
    predicted_category,
    COUNT(*) as total_records,
    ROUND(100.0 * COUNT(*) / SUM(COUNT(*)) OVER(), 2) as distribution_pct
FROM silver_social_posts
GROUP BY 1;
