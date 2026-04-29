-- models/marts/fct_creative_prompts.sql
{{ config(
    materialized='incremental',
    unique_key='prompt_id',
    on_schema_change='sync_all_columns'
) }}

WITH intelligence_source AS (
    -- Bringing in the feedback-adjusted scores from Intermediate
    SELECT * FROM {{ ref('int_feedback_loop') }}
),

validated_source AS (
    SELECT 
        t.target_topic,
        t.confidence_level,
        t.platform_count,
        t.total_mentions,
        t.latest_pulse,
        -- Integrated feedback metrics
        i.human_preference_multiplier,
        i.bias_adjustment,
        -- The weighted score calculation
        ((t.raw_heat_score * 0.7) + (i.human_preference_multiplier * 0.3)) AS optimized_score,
        CASE WHEN t.platform_count > 1 THEN 'cross-platform' ELSE 'niche' END as trend_type
    FROM {{ ref('int_validated_trends') }} t
    LEFT JOIN intelligence_source i ON t.trend_id = i.trend_id
    WHERE t.confidence_level IN ('HIGH', 'MEDIUM') 
),

final_enrichment AS (
    SELECT
        {{ dbt_utils.generate_surrogate_key(['target_topic', 'latest_pulse']) }} AS prompt_id,
        target_topic,
        confidence_level,
        optimized_score,
        latest_pulse AS validated_at,
        
        'Act as a creative director. Target: Tech-savvy social media users.' as creative_guidance,

        -- DYNAMIC PROMPT TEMPLATE: Now reacts to the "Optimized Score"
        'Generate 3 viral ad hooks for "' || target_topic || '". ' ||
        'Context: This trend has an optimized quality score of ' || ROUND(optimized_score::numeric, 2) || '. ' ||
        'The content must feel ' || (
            CASE 
                WHEN optimized_score > 0.8 THEN 'authoritative and high-budget' 
                WHEN optimized_score > 0.5 THEN 'engaging and community-focused'
                ELSE 'experimental and edgy' 
            END
        ) || '.' 
        AS llm_prompt_template
        
    FROM validated_source
)

SELECT * FROM final_enrichment

{% if is_incremental() %}
    -- Only process pulses that haven't been turned into prompts yet
    WHERE validated_at > (SELECT MAX(validated_at) FROM {{ this }})
{% endif %}
