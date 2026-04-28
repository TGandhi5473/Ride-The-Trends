-- models/marts/fct_creative_prompts.sql
{{ config(materialized='incremental', unique_key='target_topic') }}

with validated as (
    select * from {{ ref('int_validated_trends') }}
    where confidence_level in ('HIGH', 'MEDIUM') -- Filter for quality [cite: 28]
)

select
    {{ dbt_utils.generate_surrogate_key(['target_topic', 'latest_pulse']) }} as prompt_id,
    target_topic,
    confidence_level,
    latest_pulse as validated_at,
    -- Pre-structuring the context for the LLM [cite: 4, 14]
    'Act as a creative director. Generate 3 ad hooks for ' || target_topic || 
    ' based on trending discussions on YouTube and Bluesky.' as llm_prompt_template
from validated

{% if is_incremental() %}
    where latest_pulse > (select max(validated_at) from {{ this }})
{% endif %}
