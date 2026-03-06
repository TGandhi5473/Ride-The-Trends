CREATE EXTENSION IF NOT EXISTS vector;

CREATE TABLE IF NOT EXISTS trends_archive (
    id SERIAL PRIMARY KEY,
    platform VARCHAR(20),
    external_id TEXT UNIQUE,
    content TEXT,
    metadata JSONB,
    embedding vector(384),
    anti_slop_keywords TEXT[],
    created_at TIMESTAMP
);

CREATE INDEX ON trends_archive USING ivfflat (embedding vector_cosine_ops);
