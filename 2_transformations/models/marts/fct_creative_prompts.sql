-- models/marts/fct_creative_prompts.sql
{{ config(
    materialized='incremental',
    unique_key='prompt_id',
    on_schema_change='fail'
) }}

WITH validated_source AS (
    SELECT 
        target_topic,
        confidence_level,
        platform_count,
        total_mentions,
        latest_pulse
    FROM {{ ref('int_validated_trends') }}
    WHERE confidence_level IN ('HIGH', 'MEDIUM') -- Filter for quality
),

final_enrichment AS (
    SELECT
        -- Surrogate key ensures we track every unique trend pulse
        {{ dbt_utils.generate_surrogate_key(['target_topic', 'latest_pulse']) }} AS prompt_id,
        target_topic,
        confidence_level,
        latest_pulse AS validated_at,
        
        -- MERGED PROMPT: Combining your Creative Director role-play with deterministic data
        'Act as a creative director. Generate 3 ad hooks and a short script for "' || target_topic || '". ' ||
        'Context: This topic is trending with ' || confidence_level || ' confidence across ' || 
        platform_count || ' platforms (YouTube & Bluesky).' AS llm_prompt_template
        
    FROM validated_source
)

SELECT * FROM final_enrichment

{% if is_incremental() %}
    -- Only process pulses newer than the most recent one in the mart
    WHERE validated_at > (SELECT MAX(validated_at) FROM {{ this }})
{% endif %}
