-- models/marts/fct_creative_prompts.sql
{{ config(
    materialized='incremental',
    unique_key='prompt_id',
    on_schema_change='sync_all_columns'
) }}

WITH validated_source AS (
    SELECT 
        target_topic,
        confidence_level,
        platform_count,
        total_mentions,
        latest_pulse,
        -- Add a 'primary_platform' to help BERT understand tone
        CASE WHEN platform_count > 1 THEN 'cross-platform' ELSE 'niche' END as trend_type
    FROM {{ ref('int_validated_trends') }}
    WHERE confidence_level IN ('HIGH', 'MEDIUM') 
),

final_enrichment AS (
    SELECT
        -- Unique ID derived from topic and time pulse
        {{ dbt_utils.generate_surrogate_key(['target_topic', 'latest_pulse']) }} AS prompt_id,
        target_topic,
        confidence_level,
        latest_pulse AS validated_at,
        
        -- STRUCTURAL FIX: Separate the "Instruction" from the "Data"
        -- This allows the Python engine to swap models easily
        'Act as a creative director. Target: Tech-savvy social media users.' as creative_guidance,

        -- THE PROMPT TEMPLATE
        'Generate 3 viral ad hooks for "' || target_topic || '". ' ||
        'Context: This is a ' || confidence_level || ' confidence trend seen on YouTube and Bluesky. ' ||
        'The content must feel ' || (CASE WHEN confidence_level = 'HIGH' THEN 'authoritative' ELSE 'experimental' END) || '.' 
        AS llm_prompt_template
        
    FROM validated_source
)

SELECT * FROM final_enrichment

{% if is_incremental() %}
    -- Incremental logic ensures we only generate new prompts for new trend pulses
    WHERE validated_at > (SELECT MAX(validated_at) FROM {{ this }})
{% endif %}
