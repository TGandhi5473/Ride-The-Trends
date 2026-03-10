-- Enable the vector extension for Semantic Search
CREATE EXTENSION IF NOT EXISTS vector;

-- 1. The Clean Silver Table
CREATE TABLE IF NOT EXISTS silver_social_posts (
    id SERIAL PRIMARY KEY,
    platform VARCHAR(50),
    source_id VARCHAR(255) UNIQUE,        -- Natural Key (YouTube ID / Bsky URI)
    author VARCHAR(255),
    content TEXT,
    view_count INT DEFAULT 0,
    raw_category VARCHAR(100),
    predicted_category VARCHAR(100),      -- For the BERT model
    confidence FLOAT DEFAULT 0.0,         -- NEW: Tracks BERT uncertainty for HITL
    embedding vector(768),                -- NEW: 768-dim BERT embeddings for pgvector
    ingested_at TIMESTAMP,                -- When it hit Bronze
    processed_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- 2. The Quarantine Table (No changes needed, but keeping for completeness)
CREATE TABLE IF NOT EXISTS silver_quarantine (
    id SERIAL PRIMARY KEY,
    bronze_id INT,                        -- Reference back to the original
    platform VARCHAR(50),
    error_reason TEXT,
    raw_payload JSONB,
    failed_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- 3. The Feedback Loop Table
-- Note: Changed reference to 'source_id' for better joining with external APIs
CREATE TABLE IF NOT EXISTS silver_human_labels (
    id SERIAL PRIMARY KEY,
    post_id VARCHAR(255) UNIQUE,          -- Maps to silver_social_posts.source_id
    original_label VARCHAR(50),
    corrected_label VARCHAR(50),
    corrected_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 4. PERFORMANCE INDEXES
-- HNSW Index for fast vector similarity search (Cosine Distance)
CREATE INDEX IF NOT EXISTS idx_silver_posts_embedding 
ON silver_social_posts USING hnsw (embedding vector_cosine_ops);

-- Index for human labels to speed up training data extraction
CREATE INDEX IF NOT EXISTS idx_human_labels_post_id ON silver_human_labels(post_id);
