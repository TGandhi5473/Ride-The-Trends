-- models/intermediate/int_validated_trends.sql
with yt as ( select * from {{ ref('stg_yt') }} ),
bsky as ( select * from {{ ref('stg_bsky') }} ),

combined_metrics as (
    select 
        t.target_topic,
        count(distinct t.platform) as platform_count,
        count(*) as total_mentions,
        max(t.occurred_at) as latest_pulse
    from (
        select target_topic, platform, occurred_at from yt
        union all
        select target_topic, platform, occurred_at from bsky
    ) t
    group by 1
)

select
    target_topic,
    platform_count,
    total_mentions,
    latest_pulse,
    -- Logic: If it's on 2+ platforms, it's High Confidence [cite: 41, 42]
    case 
        when platform_count >= 2 then 'HIGH'
        when total_mentions > 5 then 'MEDIUM'
        else 'LOW'
    end as confidence_level
from combined_metrics
