-- The Clean Silver Table
CREATE TABLE IF NOT EXISTS silver_social_posts (
    id SERIAL PRIMARY KEY,
    platform VARCHAR(50),
    source_id VARCHAR(255) UNIQUE,        -- Natural Key (YouTube ID / Bsky URI)
    author VARCHAR(255),
    content TEXT,
    view_count INT DEFAULT 0,
    raw_category VARCHAR(100),
    predicted_category VARCHAR(100),      -- For the BERT model
    ingested_at TIMESTAMP,                -- When it hit Bronze
    processed_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- The Quarantine Table (For Debugging)
CREATE TABLE IF NOT EXISTS silver_quarantine (
    id SERIAL PRIMARY KEY,
    bronze_id INT,                        -- Reference back to the original
    platform VARCHAR(50),
    error_reason TEXT,
    raw_payload JSONB,
    failed_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);
