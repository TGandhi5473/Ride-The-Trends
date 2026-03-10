-- 1. Create the Raw Landing Table
CREATE TABLE IF NOT EXISTS bronze_social_feeds (
    id SERIAL PRIMARY KEY,
    platform VARCHAR(50) NOT NULL,        -- 'youtube' or 'bluesky'
    target_topic VARCHAR(100),            -- The category or trend name
    payload JSONB NOT NULL,               -- The raw API response
    ingested_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- 2. Performance Optimization: Indices
-- GIN Index allows for high-performance searching INSIDE the JSONB payload
CREATE INDEX IF NOT EXISTS idx_bronze_payload_gin ON bronze_social_feeds USING GIN (payload);

-- Standard B-Tree indices for fast filtering by platform and topic
CREATE INDEX IF NOT EXISTS idx_bronze_platform ON bronze_social_feeds(platform);
CREATE INDEX IF NOT EXISTS idx_bronze_topic ON bronze_social_feeds(target_topic);
-- Add an External ID to help with idempotency/deduplication
ALTER TABLE bronze_social_feeds 
ADD COLUMN IF NOT EXISTS source_id VARCHAR(255); 

-- Index for the source_id to prevent duplicates during the Silver transition
CREATE INDEX IF NOT EXISTS idx_bronze_source_id ON bronze_social_feeds(source_id);

-- Add a "Metadata" column for pipeline health (Optional but very "Senior")
ALTER TABLE bronze_social_feeds 
ADD COLUMN IF NOT EXISTS processing_status VARCHAR(20) DEFAULT 'pending'; -- 'pending', 'processed', 'quarantine'
