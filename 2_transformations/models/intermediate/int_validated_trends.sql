WITH combined_sources AS (
    SELECT 
        target_topic, 
        platform, 
        occurred_at 
    FROM {{ ref('stg_yt') }}
    
    UNION ALL
    
    SELECT 
        target_topic, 
        platform, 
        occurred_at 
    FROM {{ ref('stg_bsky') }}
),

combined_metrics AS (
    SELECT 
        target_topic,
        COUNT(DISTINCT platform) AS platform_count,
        COUNT(*) AS total_mentions,
        MAX(occurred_at) AS latest_pulse
    FROM combined_sources
    GROUP BY 1
)

SELECT
    -- 1. Create a unique ID for the specific 'pulse' of this trend
    {{ dbt_utils.generate_surrogate_key(['target_topic', 'latest_pulse']) }} AS trend_id,
    
    target_topic,
    platform_count,
    total_mentions,
    latest_pulse,
    
    -- 2. Define a base "Heat" score: Multi-platform presence is weighted heavily (2.0)
    -- vs individual mentions (0.5). This provides the 'raw_heat_score' for int_feedback_loop.
    (total_mentions * 0.5) + (platform_count * 2.0) AS raw_heat_score,
    
    -- 3. Deterministic Confidence Levels
    CASE 
        WHEN platform_count >= 2 THEN 'HIGH'
        WHEN total_mentions > 5 THEN 'MEDIUM'
        ELSE 'LOW'
    END AS confidence_level

FROM combined_metrics
