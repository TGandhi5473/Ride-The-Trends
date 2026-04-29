-- models/intermediate/int_feedback_loop.sql

WITH feedback AS (
    SELECT * FROM {{ ref('stg_feedback') }}
),

agg_performance AS (
    SELECT
        trend_id,
        AVG(human_score) AS avg_human_preference,
        COUNT(interaction_id) AS total_votes,
        -- Calculate the 'Bias': Does BERT overhype or underplay this trend?
        AVG(human_score - bert_score) AS model_bias_correction
    FROM feedback
    WHERE interaction_id != 'dummy'
    GROUP BY 1
)

SELECT 
    t.trend_id,
    t.raw_heat_score,
    COALESCE(f.avg_human_preference, 0.5) AS human_preference_multiplier,
    COALESCE(f.model_bias_correction, 0) AS bias_adjustment
FROM {{ ref('int_validated_trends') }} t
LEFT JOIN agg_performance f ON t.trend_id = f.trend_id
