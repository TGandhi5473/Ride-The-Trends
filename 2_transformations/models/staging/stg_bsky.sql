-- models/staging/stg_bsky.sql
with raw_source as (
    select * from {{ source('bronze', 'raw_ingestion') }}
    where platform = 'bluesky'
)

select
    payload->>'source_id' as source_id,
    target_topic,
    payload->>'text' as trend_text,
    payload->>'author' as creator_handle,
    (payload->>'created_at')::timestamp as occurred_at,
    (payload->>'like_count')::int as engagement_score,
    'bluesky' as platform
from raw_source
