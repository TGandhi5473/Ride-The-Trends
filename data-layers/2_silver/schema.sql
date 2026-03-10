-- ==========================================
-- SILVER LAYER: REFINED & AUDITABLE SCHEMA
-- Location: 2_silver/schema.sql
-- ==========================================

-- Enable Vector Extension for Semantic Search
CREATE EXTENSION IF NOT EXISTS vector;

-- 1. The Clean Silver Table (The Source of Truth)
CREATE TABLE IF NOT EXISTS silver_social_posts (
    id SERIAL PRIMARY KEY,
    platform VARCHAR(50) NOT NULL,        -- 'youtube' or 'bluesky'
    source_id VARCHAR(255) UNIQUE NOT NULL, -- Natural Key (VideoID / Post URI)
    author VARCHAR(255),
    content TEXT NOT NULL,                 -- Cleaned text (no HTML/excess slop)
    view_count INT DEFAULT 0,
    raw_category VARCHAR(100),             -- Original metadata category
    predicted_category VARCHAR(100),       -- Output from your BERT model
    confidence FLOAT DEFAULT 0.0,          -- BERT Softmax score for uncertainty tracking
    
    -- 768-dimensions for all-MiniLM-L6-v2 or BERT-base
    embedding vector(768),                 
    
    -- Lineage & Audit Timestamps
    ingested_at TIMESTAMP NOT NULL,        -- Original Bronze arrival time
    processed_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    is_quarantined BOOLEAN DEFAULT FALSE   -- Flag for easy filtering in Audit Hub
);

-- 2. The Quarantine Table (For Pipeline Health Monitoring)
-- Used when JSON parsing fails or BERT returns null/error
CREATE TABLE IF NOT EXISTS silver_quarantine (
    id SERIAL PRIMARY KEY,
    bronze_id INT,                         -- Foreign reference for debugging
    platform VARCHAR(50),
    error_reason TEXT,                     -- e.g., 'Missing Content Field', 'BERT Timeout'
    raw_payload JSONB,                     -- Snapshot of the offending data
    resolved BOOLEAN DEFAULT FALSE,        -- NEW: Track if an engineer fixed the issue
    failed_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- 3. The Human-in-the-Loop (HITL) Feedback Loop
-- This table powers your "Model Re-training" narrative
CREATE TABLE IF NOT EXISTS silver_human_labels (
    id SERIAL PRIMARY KEY,
    post_id VARCHAR(255) UNIQUE REFERENCES silver_social_posts(source_id),
    original_label VARCHAR(100),
    corrected_label VARCHAR(100),
    reviewer_notes TEXT,
    corrected_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- ==========================================
-- PERFORMANCE & SEMANTIC INDICES
-- ==========================================

-- HNSW Index: Optimized for Cosine Distance (Semantic Search)
-- m=16, ef_construction=64 are standard balanced settings for 2026 local dev
CREATE INDEX IF NOT EXISTS idx_silver_posts_embedding 
ON silver_social_posts USING hnsw (embedding vector_cosine_ops);

-- Index for source_id to handle fast UPSETs during ingestion
CREATE INDEX IF NOT EXISTS idx_silver_source_id ON silver_social_posts(source_id);

-- Index for the Audit Hub to quickly find un-processed/quarantined records
CREATE INDEX IF NOT EXISTS idx_silver_audit_status ON silver_social_posts(is_quarantined, platform);

-- Index for high-confidence trend analysis
CREATE INDEX IF NOT EXISTS idx_silver_confidence ON silver_social_posts(confidence) WHERE confidence > 0.8;
