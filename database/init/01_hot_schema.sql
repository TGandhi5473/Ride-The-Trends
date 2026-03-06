CREATE EXTENSION IF NOT EXISTS vector;

-- The parent table (cannot contain data itself)
CREATE TABLE IF NOT EXISTS trends (
    id SERIAL,
    platform VARCHAR(20),
    external_id TEXT,
    content TEXT,
    metadata JSONB,
    embedding vector(384),
    anti_slop_keywords TEXT[],
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (id, created_at) -- Partition key must be part of PK
) PARTITION BY RANGE (created_at);

-- Initial partition for March 2026
CREATE TABLE trends_march_2026 PARTITION OF trends
    FOR VALUES FROM ('2026-03-01') TO ('2026-04-01');

-- Initial partition for April 2026
CREATE TABLE trends_april_2026 PARTITION OF trends
    FOR VALUES FROM ('2026-04-01') TO ('2026-05-01');
