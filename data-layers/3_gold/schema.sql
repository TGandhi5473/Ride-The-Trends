-- View for Trend Analysis (The 'Gold' Standard)
CREATE OR REPLACE VIEW gold_trend_metrics AS
SELECT 
    predicted_category,
    platform,
    COUNT(*) as post_count,
    SUM(view_count) as total_reach,
    AVG(view_count) as avg_engagement,
    DATE_TRUNC('day', ingested_at) as trend_date
FROM silver_social_posts
GROUP BY 1, 2, 6;

-- View for "The Other" Breakdown (Identifying new niche trends)
CREATE OR REPLACE VIEW gold_other_exploration AS
SELECT content, platform, raw_category, ingested_at
FROM silver_social_posts
WHERE predicted_category = 'OTHER';
