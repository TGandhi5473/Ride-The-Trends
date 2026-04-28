-- models/staging/stg_yt.sql
with raw_source as (
    select * from {{ source('bronze', 'raw_ingestion') }}
    where platform = 'youtube'
)

select
    payload->>'source_id' as source_id,
    target_topic,
    payload->>'title' as trend_title,
    payload->>'description' as trend_description,
    payload->>'channel' as creator_name,
    (payload->>'published_at')::timestamp as occurred_at,
    payload->>'thumbnails' as media_url,
    'youtube' as platform
from raw_source
